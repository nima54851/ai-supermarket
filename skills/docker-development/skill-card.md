## Description: <br>
Docker Development helps agents optimize Dockerfiles, improve Docker Compose configurations, implement multi-stage builds, and audit container security. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[alirezarezvani](https://clawhub.ai/user/alirezarezvani) <br>

### License/Terms of Use: <br>
MIT-0 <br>


## Use Case: <br>
Developers and engineers use this skill to containerize projects, reduce Docker image size and build time, improve Docker Compose setups, and review container security before applying changes. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: Generated Dockerfile or Compose changes may alter exposed ports, mounts, environment files, restart policies, or runtime commands. <br>
Mitigation: Review proposed Docker and Compose edits before running them, with special attention to externally exposed ports, sensitive mounts, env_file usage, and restart policies. <br>
Risk: The bundled validators may be invoked against local project Dockerfile or Compose files. <br>
Mitigation: Run validator commands only on intended project files and review any shell command before execution. <br>


## Reference(s): <br>
- [Docker Development ClawHub Page](https://clawhub.ai/alirezarezvani/docker-development) <br>
- [Docker Compose Patterns Reference](artifact/references/compose-patterns.md) <br>
- [Dockerfile Best Practices Reference](artifact/references/dockerfile-best-practices.md) <br>


## Skill Output: <br>
**Output Type(s):** [text, markdown, code, shell commands, configuration, guidance] <br>
**Output Format:** [Markdown with Dockerfile, Compose YAML, JSON, and shell command blocks] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [May include local Python validator commands and suggested Docker or Compose changes for user review.] <br>

## Skill Version(s): <br>
2.1.1 (source: server release evidence) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
