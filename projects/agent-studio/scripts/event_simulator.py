#!/usr/bin/env python3
"""
Event stream simulator for testing event-driven architectures.
Generates realistic AI Agent events at configurable rate.
"""
import argparse
import json
import random
import time
from datetime import datetime, timezone

EVENT_TYPES = [
    'user.message',
    'agent.reasoning.start',
    'agent.reasoning.complete',
    'agent.tool.call',
    'agent.output',
    'agent.error',
]

USERS = [f'user-{i:03d}' for i in range(1, 21)]
AGENTS = ['reasoning-agent', 'code-agent', 'creative-agent', 'data-agent']

TOOLS = ['web_search', 'file_write', 'code_execute', 'api_call', 'db_query', 'tts']

def generate_event():
    event_type = random.choice(EVENT_TYPES)
    user_id = random.choice(USERS)
    agent_id = random.choice(AGENTS)

    event = {
        'event_id': f"{int(time.time()*1000)}-{random.randint(1000,9999)}",
        'event_type': event_type,
        'user_id': user_id,
        'agent_id': agent_id,
        'timestamp': datetime.now(timezone.utc).isoformat(),
    }

    if event_type == 'user.message':
        event['payload'] = {
            'text': f"User message from {user_id}",
            'channel': random.choice(['slack', 'discord', 'web', 'api']),
        }
    elif event_type == 'agent.tool.call':
        event['payload'] = {
            'tool': random.choice(TOOLS),
            'args': {'query': 'sample query'},
            'duration_ms': random.randint(50, 2000),
        }
    elif event_type == 'agent.error':
        event['payload'] = {
            'error': random.choice(['timeout', 'rate_limit', 'api_error', 'invalid_input']),
            'retry': random.choice([True, False]),
        }

    return event

def main():
    parser = argparse.ArgumentParser(description='Simulate AI Agent event stream')
    parser.add_argument('--rate', type=int, default=5, help='Events per second')
    parser.add_argument('--count', type=int, default=0, help='Total events (0 = infinite)')
    parser.add_argument('--kafka', action='store_true', help='Send to Kafka')
    parser.add_argument('--kafka-brokers', default='localhost:9092', help='Kafka brokers')
    args = parser.parse_args()

    print(f"[EventSimulator] Generating ~{args.rate} events/sec...")

    if args.kafka:
        try:
            from kafka import KafkaProducer
            producer = KafkaProducer(
                bootstrap_servers=args.kafka_brokers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            )
            topic = 'ai-agent-events'
            print(f"[EventSimulator] Publishing to Kafka: {topic}")
        except ImportError:
            print("⚠️ kafka-python not installed. Install: pip install kafka-python")
            args.kafka = False

    count = 0
    interval = 1.0 / args.rate

    try:
        while True:
            event = generate_event()
            if args.kafka:
                producer.send(topic, event)
            else:
                print(f"[EVENT] {event['event_type']} | {event['user_id']} → {event['agent_id']} | {json.dumps(event.get('payload', {}))}")
            count += 1
            if args.count > 0 and count >= args.count:
                break
            time.sleep(interval)
    except KeyboardInterrupt:
        print(f"\n[EventSimulator] Stopped after {count} events")
    finally:
        if args.kafka:
            producer.flush()
            producer.close()

if __name__ == '__main__':
    main()
