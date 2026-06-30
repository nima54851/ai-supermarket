#!/usr/bin/env python3
"""
Ticket Triage Classifier
Classifies incoming support tickets by intent and priority.
"""
import json
import re
from datetime import datetime


# Priority keywords
PRIORITY_KEYWORDS = {
    "high": ["refund", "cancel", "urgent", "outage", "down", "crash", "data loss", "legal", "breach", "hacked", "500", "error", "can't access", "locked out", "money back"],
    "medium": ["bug", "broken", "slow", "issue", "problem", "not working", "wrong", "incorrect", "feature request", "wish", "would be nice"],
    "low": ["how to", "tutorial", "guide", "documentation", "faq", "example", "question", "clarification"]
}

# Intent categories
INTENT_PATTERNS = {
    "bug": [r"error\b", r"crash", r"broken", r"bug\b", r"doesn.?t work", r"not working", r"fail", r"500\b", r"exception"],
    "billing": [r"invoice", r"payment", r"charge", r"refund", r"billing", r"subscription", r"price", r"cost\b"],
    "cancellation": [r"cancel", r"unsubscribe", r"delete account", r"close account", r"data export", r"gdpr"],
    "feature": [r"feature request", r"suggest", r"would be nice", r"wish", r"add.*functionality", r"could you add"],
    "complaint": [r"terrible", r"worst", r"disappointed", r"unacceptable", r"complaint", r"frustrated", r"angry"],
    "general": []
}


def classify_intent(subject: str, body: str) -> str:
    """Detect the primary intent of a ticket."""
    text = (subject + " " + body).lower()
    
    for intent, patterns in INTENT_PATTERNS.items():
        if intent == "general":
            continue
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return intent
    
    return "general"


def classify_priority(subject: str, body: str, intent: str) -> str:
    """Determine ticket priority level."""
    text = (subject + " " + body).lower()
    
    # High-priority intents always escalate
    if intent in ("cancellation", "billing", "complaint"):
        return "high"
    
    for kw in PRIORITY_KEYWORDS["high"]:
        if kw in text:
            return "high"
    
    for kw in PRIORITY_KEYWORDS["medium"]:
        if kw in text:
            return "medium"
    
    return "low"


def extract_sentiment_score(body: str) -> float:
    """Simple sentiment score from -1.0 (negative) to 1.0 (positive)."""
    negative_words = ["terrible", "awful", "horrible", "worst", "angry", "frustrated", "disappointed", "hate", "useless"]
    positive_words = ["thank", "great", "awesome", "love", "perfect", "amazing", "helpful", "great"]
    
    text = body.lower()
    neg = sum(1 for w in negative_words if w in text)
    pos = sum(1 for w in positive_words if w in text)
    
    total = neg + pos
    if total == 0:
        return 0.0
    return round((pos - neg) / total, 2)


def classify_ticket(ticket: dict) -> dict:
    """
    Main triage function.
    
    Args:
        ticket: dict with keys: subject (str), body (str), sender_email (str), timestamp (str, optional)
    
    Returns:
        dict: {"intent", "priority", "category", "sentiment", "escalate"}
    """
    subject = ticket.get("subject", "")
    body = ticket.get("body", "")
    
    intent = classify_intent(subject, body)
    priority = classify_priority(subject, body, intent)
    sentiment = extract_sentiment_score(body)
    
    # Escalation rule: high priority OR negative sentiment
    escalate = priority == "high" or sentiment < -0.3
    
    return {
        "intent": intent,
        "priority": priority,
        "category": f"{intent}/{priority}",
        "sentiment": sentiment,
        "escalate": escalate,
        "timestamp": ticket.get("timestamp", datetime.now().isoformat())
    }


if __name__ == "__main__":
    # Demo
    test_tickets = [
        {"subject": "Can't log in", "body": "I've been trying to log in for 2 hours. Getting a 500 error. Very frustrated!", "sender_email": "angry@user.com"},
        {"subject": "Feature request: dark mode", "body": "Would love a dark mode for the dashboard. Would be nice to have.", "sender_email": "user@corp.com"},
        {"subject": "Need invoice", "body": "Can you send me an invoice for last month's subscription?", "sender_email": "finance@corp.com"},
    ]
    
    for t in test_tickets:
        result = classify_ticket(t)
        print(f"\n📩 {t['subject']}")
        print(f"   Intent: {result['intent']} | Priority: {result['priority']} | Sentiment: {result['sentiment']} | Escalate: {result['escalate']}")
