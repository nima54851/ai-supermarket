#!/usr/bin/env python3
"""
Knowledge Graph Builder - Extract entities and build knowledge graphs
Author: 灵犀 AI
"""

import sys
import json
import argparse
from typing import List, Dict, Any

# Simulated entity extraction (replace with OpenAI/Anthropic call in production)
def extract_entities(text: str, model: str = "gpt-4o") -> List[Dict[str, str]]:
    """
    Extract named entities from text using AI.
    Returns list of {type, name, description} dicts.
    """
    # Placeholder: in production, call OpenAI/Anthropic API
    # Example prompt: "Extract entities from: {text}. Return JSON array."
    print(f"[INFO] Extracting entities from text ({len(text)} chars) using {model}...")
    
    # Mock: extract obvious patterns
    entities = []
    words = text.split()
    for i, word in enumerate(words):
        if word[0].isupper() and len(word) > 1:
            entities.append({
                "name": word,
                "type": "ENTITY",
                "confidence": 0.8
            })
    return entities[:20]  # Limit to 20


def build_graph(entities: List[Dict], output_path: str = "graph.json"):
    """
    Convert entities to a graph structure (nodes + edges).
    """
    nodes = []
    edges = []
    seen = set()
    
    for e in entities:
        if e["name"] not in seen:
            nodes.append({
                "id": e["name"].lower().replace(" ", "_"),
                "label": e["name"],
                "type": e["type"],
                "confidence": e.get("confidence", 0.8)
            })
            seen.add(e["name"])
    
    # Create edges between consecutive nodes (simplified)
    for i in range(len(nodes) - 1):
        edges.append({
            "source": nodes[i]["id"],
            "target": nodes[i+1]["id"],
            "relation": "RELATED_TO"
        })
    
    graph = {"nodes": nodes, "edges": edges}
    
    with open(output_path, "w") as f:
        json.dump(graph, f, indent=2)
    
    print(f"[OK] Graph saved: {output_path}")
    print(f"     Nodes: {len(nodes)}, Edges: {len(edges)}")
    return graph


def query_graph(graph: Dict, question: str) -> str:
    """
    Natural language query against the knowledge graph.
    """
    print(f"[INFO] Processing query: {question}")
    # Placeholder: translate NL to graph traversal
    # In production, use LLM to generate Cypher or graph traversal code
    nodes = graph.get("nodes", [])
    return f"Found {len(nodes)} nodes. Key entities: {[n['label'] for n in nodes[:5]]}"


def main():
    parser = argparse.ArgumentParser(description="Knowledge Graph Builder")
    parser.add_argument("--file", help="Input text file")
    parser.add_argument("--text", help="Input text directly")
    parser.add_argument("--model", default="gpt-4o", help="AI model for extraction")
    parser.add_argument("--output", default="graph.json", help="Output graph file")
    parser.add_argument("--query", help="Query the graph after building")
    args = parser.parse_args()
    
    if args.file:
        with open(args.file) as f:
            text = f.read()
    elif args.text:
        text = args.text
    else:
        print("Error: Provide --file or --text")
        sys.exit(1)
    
    entities = extract_entities(text, args.model)
    graph = build_graph(entities, args.output)
    
    if args.query:
        result = query_graph(graph, args.query)
        print(f"Answer: {result}")


if __name__ == "__main__":
    main()
