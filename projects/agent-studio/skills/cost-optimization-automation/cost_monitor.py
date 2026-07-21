#!/usr/bin/env python3
"""
Cloud Cost Optimization Monitor
Author: 灵犀 AI
"""

import json
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class CostMonitor:
    def __init__(self):
        self.providers = {}
    
    def add_openai(self, api_key: str):
        self.providers["openai"] = {"api_key": api_key, "type": "ai_api"}
    
    def add_aws(self, profile: str):
        self.providers["aws"] = {"profile": profile, "type": "cloud"}
    
    def get_openai_usage(self, days: int = 30) -> Dict:
        """Fetch OpenAI API usage and cost."""
        # Placeholder: call OpenAI API
        # In production: https://api.openai.com/v1/usage
        return {
            "provider": "openai",
            "period_days": days,
            "total_cost_usd": 0.0,
            "breakdown": {},
            "note": "Connect your API key to fetch real usage"
        }
    
    def get_spend(self, days: int = 30) -> Dict:
        """Aggregate spend across all providers."""
        total = 0.0
        breakdown = {}
        
        for name, config in self.providers.items():
            if name == "openai":
                data = self.get_openai_usage(days)
                cost = data.get("total_cost_usd", 0)
                total += cost
                breakdown[name] = cost
        
        return {
            "total": total,
            "breakdown": breakdown,
            "period_days": days,
            "date": datetime.utcnow().isoformat()
        }

def detect_anomalies(spend_data: Dict, threshold: float = 2.0) -> List[Dict]:
    """Simple anomaly detection on spend data."""
    # Placeholder: real implementation would use time-series anomaly detection
    anomalies = []
    if spend_data["total"] > 100:
        anomalies.append({
            "date": datetime.utcnow().date().isoformat(),
            "spend": spend_data["total"],
            "threshold": threshold,
            "reason": "High total spend detected"
        })
    return anomalies

def get_recommendations(spend_data: Dict) -> List[Dict]:
    """AI-driven cost optimization recommendations."""
    recommendations = []
    
    total = spend_data["total"]
    
    if total > 0:
        recommendations.append({
            "action": "enable_response_caching",
            "category": "ai_api",
            "estimated_savings": f"${total * 0.3:.2f}/mo",
            "impact": "medium",
            "description": "Cache LLM responses to reduce API calls by 30%"
        })
    
    if any("openai" in k for k in spend_data["breakdown"]):
        recommendations.append({
            "action": "switch_to_batch_api",
            "category": "ai_api",
            "estimated_savings": f"${total * 0.5:.2f}/mo",
            "impact": "high",
            "description": "Use OpenAI Batch API for non-real-time tasks (50% discount)"
        })
    
    return recommendations

def main():
    parser = argparse.ArgumentParser(description="Cost Optimization Monitor")
    parser.add_argument("--days", type=int, default=30, help="Number of days to analyze")
    parser.add_argument("--output", default="cost_report.json", help="Output file")
    parser.add_argument("--anomalies", action="store_true", help="Detect anomalies")
    parser.add_argument("--recommend", action="store_true", help="Get recommendations")
    args = parser.parse_args()
    
    monitor = CostMonitor()
    # In production: monitor.add_openai("sk-..."), monitor.add_aws("production")
    
    spend = monitor.get_spend(args.days)
    print(f"💰 Total spend (last {args.days} days): ${spend['total']:.4f}")
    print(f"   Breakdown: {spend['breakdown']}")
    
    if args.anomalies:
        anomalies = detect_anomalies(spend)
        print(f"\n🔍 Anomalies found: {len(anomalies)}")
        for a in anomalies:
            print(f"   - {a['reason']}: ${a['spend']}")
    
    if args.recommend:
        recs = get_recommendations(spend)
        print(f"\n💡 Optimization recommendations: {len(recs)}")
        for r in recs:
            print(f"   - [{r['impact'].upper()}] {r['action']}: save ~{r['estimated_savings']}")
    
    # Save report
    report = {
        "spend": spend,
        "anomalies": detect_anomalies(spend) if args.anomalies else [],
        "recommendations": get_recommendations(spend) if args.recommend else []
    }
    with open(args.output, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n[OK] Report saved: {args.output}")

if __name__ == "__main__":
    main()
