# Event-Driven Architecture Skill

## 概述
事件驱动架构（EDA）设计与实现：Kafka / RabbitMQ / Redis Streams / Serverless Events。适用于微服务解耦、实时数据管道、AI 事件响应系统。

## 核心能力
- 🔄 **事件建模**：事件溯源（Event Sourcing）、CQRS 模式设计
- 📨 **消息队列**：Kafka Topic 管理、Consumer Group 负载均衡、死信队列（DLQ）
- ⚡ **实时流处理**：Flink / Spark Structured Streaming / Redis Streams
- 🤖 **AI 事件响应**：事件 → LLM 推理 → 自动化操作闭环
- 📊 **可观测性**：事件追踪（OpenTelemetry）、结构化日志、告警

## 典型场景
- **AI Agent 事件流**：用户消息 → Agent 推理 → 工具调用 → 结果写入
- **数据管道**：GitHub Webhook → Kafka → 实时分析 → 仪表盘
- **微服务解耦**：订单服务 → 事件 → 通知/库存/分析
- **Serverless 触发**：定时事件 / S3 事件 → Lambda / Cloudflare Workers AI

## 快速开始
```javascript
// Kafka Producer（Node.js）
const { Kafka } = require('kafkajs')
const kafka = new Kafka({ brokers: ['localhost:9092'] })
const producer = kafka.producer()

await producer.connect()
await producer.send({
  topic: 'ai-agent-events',
  messages: [
    { key: 'user-123', value: JSON.stringify({
      event: 'agent.reasoning.complete',
      userId: 'user-123',
      result: { summary: '...' },
      timestamp: new Date().toISOString()
    })}
  ]
})

// Kafka Consumer（AI 响应）
const consumer = kafka.consumer({ groupId: 'ai-responder' })
await consumer.subscribe({ topic: 'ai-agent-events' })
await consumer.run({
  eachMessage: async ({ topic, partition, message }) => {
    const event = JSON.parse(message.value.toString())
    if (event.event === 'agent.reasoning.complete') {
      // 触发 AI 后续操作
      await triggerFollowUp(event)
    }
  }
})
```

## n8n 集成
- `integrations/event-driven-architecture/kafka-event-router.json`
- 支持：Kafka / RabbitMQ / Redis Streams / Webhook 触发器

## 脚本
- `scripts/setup_kafka.js`：本地 Kafka 环境快速搭建
- `scripts/event_simulator.py`：模拟事件流用于测试
- `scripts/event_monitor.py`：监控事件管道健康状态

## 参考资料
- Apache Kafka: https://kafka.apache.org/
- Event Sourcing: https://martinfowler.com/eaaDev/EventSourcing.html
- CloudEvents: https://cloudevents.io/
