## Description: <br>
Design and build custom Claude Code agents with effective descriptions, tool access patterns, self-documenting prompts, Task tool delegation, model selection, memory guidance, and declarative instruction design. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[Veeramanikandanr48](https://clawhub.ai/user/Veeramanikandanr48) <br>

### License/Terms of Use: <br>
MIT <br>


## Use Case: <br>
Developers and engineers use this skill to create, improve, and troubleshoot Claude Code agents, including auto-delegation descriptions, tool permissions, memory limits, prompt structure, and multi-agent workflows. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: The skill recommends broad agent permissions that can let future agents edit files, run shell commands, and fetch from any website with fewer prompts. <br>
Mitigation: Review recommended settings before applying them and scope WebFetch domains, Bash commands, Write/Edit access, and proactive delegation to each specific agent and project. <br>
Risk: Copying the broad .claude/settings.json allowlist as a global default can reduce approval prompts across unrelated projects. <br>
Mitigation: Use project-specific allowlists and grant only the commands and tools required by the intended agent workflow. <br>


## Reference(s): <br>
- [README](README.md) <br>
- [Agent Memory Limits](rules/agent-memory-limits.md) <br>
- [Agent Implementation Pattern](rules/agent-pattern.md) <br>
- [Agent Self-Documentation Principle](rules/agent-self-documentation.md) <br>
- [Custom Agent Description Pattern](rules/custom-agent-descriptions.md) <br>
- [Custom Agent Instructions Pattern](rules/custom-agent-instructions.md) <br>


## Skill Output: <br>
**Output Type(s):** [text, markdown, code, shell commands, configuration, guidance] <br>
**Output Format:** [Markdown guidance with YAML, JSON, TypeScript, and shell command examples] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Guidance may include prompt templates, permission allowlists, memory settings, and agent workflow checklists.] <br>

## Skill Version(s): <br>
0.1.0 (source: ClawHub release metadata) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
