# Infrastructure as Code Automation

## Overview
AI-powered IaC generation using Terraform, Pulumi, and Ansible — convert requirements to infrastructure configs, validate existing configs, and auto-fix errors.

## What It Does
- Converts natural language requirements → Terraform HCL / Pulumi Python/TypeScript
- Generates Ansible playbooks from server requirements
- Validates IaC configs (terraform validate, checkov security scan)
- Auto-fixes common misconfigurations
- Plans and applies infrastructure via n8n pipeline

## Files
- `n8n-iac-workflow.json` — Requirements → AI → IaC generator pipeline
- `terraform_gen.py` — AI Terraform generator with provider support
- `ansible_gen.py` — AI Ansible playbook generator
- `iac_validator.py` — IaC validator (Terraform, Pulumi, Ansible)

## Supported Providers
- AWS, GCP, Azure (Terraform)
- AWS, GCP, Azure, Kubernetes (Pulumi)
- Ubuntu, CentOS, Debian (Ansible)

## Setup
1. Import `n8n-iac-workflow.json` into n8n
2. Configure OpenAI/Anthropic API for code generation
3. Add Terraform/Pulumi/Ansible CLI paths
4. Set default provider (AWS/GCP/Azure)

## Usage
Requirements doc → n8n → AI → Terraform/Pulumi/Ansible → validate → post as PR
