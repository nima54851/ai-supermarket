#!/usr/bin/env python3
"""
AI Terraform Generator
Converts natural language requirements to Terraform HCL.
"""
import json
import os
import sys

try:
    from openai import OpenAI
except ImportError:
    print("pip install openai")
    sys.exit(1)

PROVIDER_TEMPLATES = {
    "aws": {"region": "us-east-1", "provider": "aws"},
    "gcp": {"region": "us-central1", "provider": "google"},
    "azure": {"region": "eastus", "provider": "azurerm"},
}

def generate_terraform(requirements: str, provider: str = "aws", output_dir: str = "./infrastructure/terraform"):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    prompt = f"""Generate a complete Terraform HCL configuration for:

Requirements: {requirements}
Provider: {provider}

Include:
- main.tf (resources)
- variables.tf (input vars)
- outputs.tf (output values)
- versions.tf (provider version constraints)
- README.md (deployment instructions)

Follow Terraform best practices. Use modules where appropriate."""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    
    content = response.choices[0].message.content
    
    # Extract code blocks
    files = {}
    current_file = None
    for line in content.split("\n"):
        if line.startswith("```"):
            if current_file and current_file not in files:
                files[current_file] = []
            current_file = line.replace("```", "").strip()
        elif current_file and current_file != "hcl":
            files.setdefault(current_file, []).append(line)
    
    # Write files
    import os
    os.makedirs(output_dir, exist_ok=True)
    for filename, lines in files.items():
        if filename.endswith(".tf") or filename.endswith(".md"):
            path = os.path.join(output_dir, filename if not filename.startswith("`") else filename.strip("`"))
            with open(path, "w") as f:
                f.write("\n".join(lines))
            print(f"✅ Written: {path}")
    
    return files

if __name__ == "__main__":
    req = sys.argv[1] if len(sys.argv) > 1 else "EC2 instance with RDS database and ALB"
    prov = sys.argv[2] if len(sys.argv) > 2 else "aws"
    generate_terraform(req, prov)
