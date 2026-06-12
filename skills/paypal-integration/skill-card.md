## Description: <br>
PayPal integration for managing accounts and interacting with PayPal data through Membrane. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[gora050](https://clawhub.ai/user/gora050) <br>

### License/Terms of Use: <br>
MIT-0 <br>


## Use Case: <br>
Developers and agent users use this skill to connect PayPal through Membrane, discover available PayPal actions, and run account, invoice, order, subscription, payout, and raw API requests. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: The security review flags broad money-moving and account-changing instructions without clear confirmation guardrails. <br>
Mitigation: Install only for intentional PayPal-through-Membrane use, verify the CLI package, prefer sandbox or least-privilege PayPal access, and require clear per-action confirmation for payouts, refunds, captures, cancellations, invoice sends, deletions, subscription changes, and raw API requests. <br>


## Reference(s): <br>
- [ClawHub Skill Page](https://clawhub.ai/gora050/paypal-integration) <br>
- [Membrane](https://getmembrane.com) <br>
- [PayPal API Documentation](https://developer.paypal.com/docs/api/) <br>


## Skill Output: <br>
**Output Type(s):** [Guidance, Shell commands, Configuration, API calls] <br>
**Output Format:** [Markdown with inline shell commands and JSON examples] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Requires network access, a valid Membrane account, and explicit review for money-moving or account-changing actions.] <br>

## Skill Version(s): <br>
1.0.2 (source: server release evidence) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
