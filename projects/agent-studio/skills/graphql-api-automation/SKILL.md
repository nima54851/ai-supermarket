# GraphQL API Automation

> AI-powered GraphQL API design, schema generation, resolver development, and monitoring.

## What This Does

Automates the creation and maintenance of GraphQL APIs:
- Schema design from natural language descriptions
- Resolver generation from schema definitions
- Apollo Server / GraphQL Yoga setup
- Query optimization and cost analysis
- Federation-ready schema stitching

## When to Use

- Building a new GraphQL API from scratch
- Migrating REST APIs to GraphQL
- Setting up Apollo Federation for microservices
- Adding real-time subscriptions to existing APIs

## Core Capabilities

### Schema Design
```graphql
# Generated from natural language:
# "Users can post articles and comment on them"
type User {
  id: ID!
  name: String!
  articles: [Article!]!
  comments: [Comment!]!
}

type Article {
  id: ID!
  title: String!
  content: String!
  author: User!
  comments: [Comment!]!
  createdAt: DateTime!
}

type Comment {
  id: ID!
  content: String!
  author: User!
  article: Article!
  createdAt: DateTime!
}
```

### AI Schema Generation Prompt
```
Design a GraphQL schema for [description].
Include:
- All necessary types with proper nullability
- Queries, mutations, and optional subscriptions
- Proper pagination (Relay-style cursor or offset)
- Input types for mutations
- Enums where appropriate
- Descriptions on all fields
```

### Cost Analysis Query
```graphql
# Expensive query that AI can flag
query expensiveQuery {
  users {
    articles {
      comments {
        author {
          articles {
            comments { author { articles { comments { author { name }}}}}}}}}}}
```

## n8n Integration

See `integrations/graphql-api-automation/` for the n8n workflow that:
1. Receives schema description via webhook
2. Generates GraphQL schema with LLM
3. Creates Apollo Server project scaffold
4. Writes TypeScript resolvers
5. Deploys to Railway/Vercel

## Tech Stack

- **Runtime:** Apollo Server 4, GraphQL Yoga, Envelop
- **Language:** TypeScript, Node.js
- **Auth:** JWT, API Key, OAuth 2.0 with Apollo plugin
- **Federation:** Apollo Federation 2, schema stitching
- **Monitoring:** Apollo Studio, GraphQL Telemetry
- **Deployment:** Vercel, Railway, Fly.io

## Quick Start

```bash
npm init -y
npm install @apollo/server graphql graphql-yoga
```

```typescript
import { ApolloServer } from '@apollo/server';
import { startStandaloneServer } from '@apollo/server/standalone';

const typeDefs = `#graphql
  type Book {
    title: String
    author: String
  }
  type Query {
    books: [Book]
  }
`;

const resolvers = {
  Query: {
    books: () => [{ title: 'AI Agent Handbook', author: 'Auto Generated' }],
  },
};

const server = new ApolloServer({ typeDefs, resolvers });
const { url } = await startStandaloneServer(server);
console.log(`🚀 GraphQL server ready at ${url}`);
```

## Best Practices

- **Schema-first:** Design schema before writing resolvers
- **DataLoader:** Batch and cache DB calls in resolvers
- **Cost limits:** Set query complexity limits (maxDepth, fieldCount)
- **Pagination:** Always paginate lists (Connection pattern)
- **Auth:** Use schema directives for @auth on fields

---

*Part of agent-studio | AI Agent Automation Toolkit*
