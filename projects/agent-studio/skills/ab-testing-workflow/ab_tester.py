#!/usr/bin/env python3
"""
A/B Testing Framework for n8n Workflows & OpenClaw Prompts
"""
import json, random, time, os, argparse, statistics
from datetime import datetime

class ABTest:
    def __init__(self, name, variants):
        self.name = name
        self.variants = {k: {"data": v, "views": 0, "successes": 0, "latencies": []} for k, v in variants.items()}
        self.started = datetime.now().isoformat()

    def select_variant(self):
        keys = list(self.variants.keys())
        return random.choice(keys)

    def record(self, variant, success, latency_ms):
        self.variants[variant]["views"] += 1
        if success:
            self.variants[variant]["successes"] += 1
        self.variants[variant]["latencies"].append(latency_ms)

    def report(self):
        print(f"\n=== A/B Test Report: {self.name} ===")
        for k, v in self.variants.items():
            rate = v["successes"] / v["views"] if v["views"] > 0 else 0
            avg_lat = statistics.mean(v["latencies"]) if v["latencies"] else 0
            print(f"  {k}: {v['views']} views, {rate:.1%} success, {avg_lat:.0f}ms avg latency")

    def winner(self, threshold=0.95):
        results = [(k, v["successes"] / v["views"] if v["views"] > 0 else 0) for k, v in self.variants.items()]
        winner_key = max(results, key=lambda x: x[1])[0]
        print(f"\n🏆 Winner: {winner_key}")
        return winner_key

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--name", default="workflow-test")
    p.add_argument("--variants", nargs=2, default=["variant_a.json", "variant_b.json"])
    args = p.parse_args()

    test = ABTest(args.name, {"A": {}, "B": {}})
    # Simulate some data
    for i in range(100):
        v = test.select_variant()
        test.record(v, random.random() > 0.3, random.randint(50, 500))
    test.report()
    test.winner()
