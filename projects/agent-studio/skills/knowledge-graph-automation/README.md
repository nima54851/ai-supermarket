# Knowledge Graph Automation

Build and query knowledge graphs from unstructured data using AI.

## Quick Start

```bash
pip install -r requirements.txt
```

## Setup Neo4j

```bash
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest
```

## Example Usage

```bash
# Extract entities from a document
python examples/extract_entities.py --file sample.txt

# Build a knowledge graph
python examples/build_graph.py --docs ./docs/

# Query with natural language
python examples/query_graph.py "What companies does OpenClaw partner with?"
```

## n8n Workflow

Import `n8n/knowledge-graph-workflow.json` into your n8n instance.

---

*Author: 灵犀 AI · Powered by OpenClaw*
