# Schema Review Prompt

Analyze database schemas and provide actionable improvement recommendations.

## Review Criteria
1. Normalization (1NF, 2NF, 3NF)
2. Index coverage for WHERE/JOIN clauses
3. Constraint completeness (PK, FK, NOT NULL, UNIQUE)
4. Data type efficiency
5. Missing audit columns (created_at, updated_at)
6. Partitioning opportunities for large tables

## Output Format
```markdown
## Schema: <table_name>
### Issues
- [HIGH] ...
- [MEDIUM] ...
### Recommendations
1. ...
```
