## Description: <br>
Use when users need to implement, integrate, debug, build, deploy, or validate a Web frontend after the product direction is already clear, especially for React, Vue, Vite, browser flows, or CloudBase Web integration. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[binggg](https://clawhub.ai/user/binggg) <br>

### License/Terms of Use: <br>
MIT-0 <br>


## Use Case: <br>
Developers and engineering agents use this skill to implement, debug, validate, and deploy Web frontends using existing React, Vue, Vite, browser-testing, and CloudBase Web project conventions. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: The skill may guide dependency installation, authentication setup, static hosting changes, or CloudBase deployment actions that affect a live Web application. <br>
Mitigation: Review proposed dependency, credential, hosting, and deployment changes before approving them, and require the documented build and browser validation checks before release. <br>
Risk: Browser or deployment workflows may require OAuth tokens or other sensitive credentials. <br>
Mitigation: Use scoped credentials, avoid exposing secrets in client-side code or logs, and confirm CloudBase environment identifiers and hosting settings before executing deployment commands. <br>


## Reference(s): <br>
- [ClawHub skill page](https://clawhub.ai/binggg/web-development) <br>
- [Framework Guidance](artifact/frameworks.md) <br>
- [Browser Validation](artifact/browser-testing.md) <br>
- [CloudBase Integration Documentation](https://docs.cloudbase.net/integration/introduce/index.md) <br>


## Skill Output: <br>
**Output Type(s):** [guidance, code, shell commands, configuration, markdown] <br>
**Output Format:** [Markdown with code snippets, shell commands, configuration guidance, and validation notes] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [May require OAuth tokens or sensitive credentials for CloudBase authentication, deployment, or browser validation workflows.] <br>

## Skill Version(s): <br>
1.27.0 (source: server release metadata; artifact frontmatter reports 2.21.1) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
