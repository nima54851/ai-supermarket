## Description: <br>
Designs relational database schemas from requirements and helps produce migrations, types, seed data, RLS policies, indexes, and ERDs. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[alirezarezvani](https://clawhub.ai/user/alirezarezvani) <br>

### License/Terms of Use: <br>
MIT-0 <br>


## Use Case: <br>
Developers and data engineers use this skill to turn product requirements into relational schemas, migrations, ORM types, seed data, RLS policies, index plans, and ERD documentation. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: Generated migrations, RLS policies, indexes, and seed data can affect production data behavior if applied without review. <br>
Mitigation: Review generated database changes, test them in staging, keep backups, and validate access policies before applying them to a real database. <br>
Risk: The artifact includes a disposable sample admin password in seed data examples. <br>
Mitigation: Do not reuse example passwords outside local development; replace seed credentials with environment-specific secrets or generated values. <br>


## Reference(s): <br>
- [Full schema examples](references/full-schema-examples.md) <br>


## Skill Output: <br>
**Output Type(s):** [text, markdown, code, shell commands, configuration, guidance] <br>
**Output Format:** [Markdown with SQL, TypeScript, Python, Prisma, Drizzle, Alembic, Mermaid, and shell command examples] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [May include proposed schemas, migrations, ORM types, RLS policies, index plans, seed data, and ERD diagrams for human review.] <br>

## Skill Version(s): <br>
1.0.0 (source: ClawHub release evidence) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
