## AI Automation Decision Framework

This tool evaluates architectural fit using organizational readiness,
problem structure, output requirements, and governance constraints.

<img width="1595" height="8740" alt="mermaid-diagram" src="https://github.com/user-attachments/assets/94dc777a-b4b7-494e-b37e-992e74d77b75" />

## Deploying with Spacelift

The `infra/` directory defines a Google Cloud Run service for this app. Configure the
Spacelift stack with `infra` as the project root, then provide Terraform variables for:

- `project_id`
- `region`
- `image`
- `service_name`
- `allow_unauthenticated`

See `infra/terraform.tfvars.example` for sample values. The container image should be
built from the included `Dockerfile` and pushed to Artifact Registry before Spacelift
runs `terraform apply`.
