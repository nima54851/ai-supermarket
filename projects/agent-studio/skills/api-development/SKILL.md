# API Development Skill

> Build, test, document and deploy REST/RESTful APIs with AI-powered code generation, automated testing, and CI/CD pipelines.

## Overview

From OpenAPI spec → production-ready API in minutes. Covers design, implementation, testing, documentation, and deployment.

## Workflow

```
OpenAPI/Swagger Design
        ↓
AI Code Generation (Express/FastAPI/Go)
        ↓
Automated Tests (Jest/pytest)
        ↓
API Documentation (Swagger UI / ReDoc)
        ↓
Deploy (Docker / Railway / Render)
```

## API Design Principles

### RESTful Best Practices

| Resource | GET | POST | PUT | DELETE |
|---|---|---|---|---|
| `/users` | List users | Create user | Bulk update | — |
| `/users/:id` | Get user | — | Update user | Delete user |

### Status Codes

- `200` OK — Success
- `201` Created — Resource created
- `400` Bad Request — Validation error
- `401` Unauthorized — Auth required
- `403` Forbidden — Permission denied
- `404` Not Found — Resource missing
- `429` Too Many Requests — Rate limited
- `500` Internal Server Error — Server fault

## Implementation Example (Node.js/Express)

```javascript
const express = require('express');
const router = express.Router();

// GET /api/v1/users
router.get('/users', async (req, res) => {
  const { page = 1, limit = 20 } = req.query;
  const users = await db.users.findAll({
    offset: (page - 1) * limit,
    limit: parseInt(limit)
  });
  res.json({ data: users, page: +page, limit: +limit });
});

// GET /api/v1/users/:id
router.get('/users/:id', async (req, res) => {
  const user = await db.users.findById(req.params.id);
  if (!user) return res.status(404).json({ error: 'User not found' });
  res.json({ data: user });
});

// POST /api/v1/users
router.post('/users', async (req, res) => {
  const { name, email } = req.body;
  if (!name || !email) {
    return res.status(400).json({ error: 'name and email required' });
  }
  const user = await db.users.create({ name, email });
  res.status(201).json({ data: user });
});

module.exports = router;
```

## API Testing (Jest + Supertest)

```javascript
const request = require('supertest');
const app = require('../app');

describe('Users API', () => {
  it('GET /api/v1/users returns 200', async () => {
    const res = await request(app).get('/api/v1/users');
    expect(res.status).toBe(200);
    expect(Array.isArray(res.body.data)).toBe(true);
  });

  it('POST /api/v1/users creates user', async () => {
    const res = await request(app)
      .post('/api/v1/users')
      .send({ name: 'Test User', email: 'test@example.com' });
    expect(res.status).toBe(201);
    expect(res.body.data.email).toBe('test@example.com');
  });
});
```

## OpenAPI 3.0 Spec

```yaml
openapi: 3.0.3
info:
  title: Agent Studio API
  version: 1.0.0
paths:
  /users:
    get:
      summary: List users
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            default: 1
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserList'
```

## n8n Integration

See `integrations/api-development/rest-api-generator.json` for the n8n workflow that:
- Generates CRUD API endpoints from schema
- Sets up authentication middleware
- Creates test cases
- Deploys to Railway/Render

## Resources

- [OpenAPI 3.0 Guide](https://swagger.io/specification/)
- [REST API Design Best Practices](https://github.com/nima54851/agent-studio/blob/main/best-practices/rest-api-design.md)
- [Express.js Docs](https://expressjs.com)
- [FastAPI Docs](https://fastapi.tiangolo.com)
