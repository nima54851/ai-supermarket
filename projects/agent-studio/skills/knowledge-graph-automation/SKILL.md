# Skill: Knowledge Graph Automation

**Purpose:** Build and query knowledge graphs from unstructured data using AI.
**Platform:** OpenClaw Agent
**Author:** 灵犀 AI (nima54851)

---

## What This Skill Does

1. **Extract entities** from text (people, orgs, concepts, relationships)
2. **Build a knowledge graph** (nodes + edges) stored in Neo4j or in-memory
3. **Query the graph** with natural language → Cypher → results
4. **Enrich** existing graphs with new data sources

## Tool Requirements

- Neo4j (or SQLite fallback for lightweight)
- OpenAI/Anthropic API for entity extraction
- Python + `py2neo`, `spacy`, `networkx`

## File Structure

```
knowledge-graph-automation/
├── SKILL.md                          # This file
├── README.md                         # Usage guide
├── graph_builder.py                  # Entity extraction + graph construction
├── graph_query.py                   # Natural language → Cypher query
├── requirements.txt
├── examples/
│   ├── extract_entities.py           # Entity extraction demo
│   ├── build_graph.py                # Build from text corpus
│   └── query_graph.py               # Query examples
└── n8n/
    └── knowledge-graph-workflow.json # n8n workflow: doc → extract → store → query
```

## Usage

### 1. Extract Entities from Text

```python
from graph_builder import EntityExtractor

extractor = EntityExtractor(model="gpt-4o")
text = "OpenClaw is built by a team of engineers. It uses AI agents."

entities = extractor.extract(text)
# Returns: [{"type": "ORG", "name": "OpenClaw"}, {"type": "PRODUCT", "name": "AI agents"}, ...]
```

### 2. Build Knowledge Graph

```python
from graph_builder import KnowledgeGraph

kg = KnowledgeGraph(uri="bolt://localhost:7687", user="neo4j", password="***")
kg.add_text_corpus(documents=["doc1.txt", "doc2.txt"])
kg.build()
```

### 3. Natural Language Query

```python
from graph_query import GraphQuery

query = GraphQuery(kg=kg)
result = query.ask("What companies does OpenClaw work with?")
# Translates to Cypher: MATCH (c:Company)<-[:PARTNERED_WITH]-(o:Org {name:"OpenClaw"}) RETURN c
```

## Skill Triggers

- "build a knowledge graph"
- "extract entities from"
- "query the knowledge graph"
- "add to the knowledge graph"
- "who is related to"

## Integration

- **n8n workflow:** Input document → AI entity extraction → Neo4j node creation → graph query
- **RAG enhancement:** Use knowledge graph as context for RAG pipelines
- **Multi-source:** Support for PDFs, web scraping, API data, Notion, Slack

---

*Last updated: 2026-07-17*
