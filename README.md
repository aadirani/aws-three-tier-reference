# AWS 3-Tier Reference Architecture

![checks](https://github.com/aadirani/aws-three-tier-reference/actions/workflows/checks.yml/badge.svg)

A classic, production-style layout for a web application on AWS, written as **Terraform code** with a **cost model** and **decision records** behind every major choice.

## The idea in one paragraph

Split the application into three layers, each in its own part of the network. The **web tier** (a load balancer behind a web firewall) is the only part the internet can reach. It passes requests to the **app tier**, servers in private subnets that add or remove capacity automatically. They talk to the **data tier**, a managed PostgreSQL database with a live standby copy in a second data center (Availability Zone). If a server, the database or a whole data center fails, the system keeps running.

## What's inside

| Path | What it is |
|---|---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Diagrams, security design, failure scenarios, 7 ADRs, risk register, cost summary |
| [terraform/](terraform/) | The infrastructure as code: network, security groups, servers, load balancer, database, WAF, alarms |
| [cost/](cost/) | A small Python cost model: unit prices + usage scenarios → monthly estimate |
| [docs/code-walkthrough.md](docs/code-walkthrough.md) | Plain-language explanation of the Terraform and the cost model |

## Status: honest summary

- ✅ Terraform passes `terraform fmt` and `terraform validate` automatically on every change (badge above).
- ✅ The cost model is covered by unit tests.
- ⚠️ The infrastructure has **not been deployed** from this repository. `validate` checks that the code is well-formed, not that AWS would accept every setting.
- ⚠️ Prices are approximate and entered by hand. Confirm them in the [AWS Pricing Calculator](https://calculator.aws/).

## Cost at a glance

```bash
python cost/cost_model.py
```

| Scenario | Estimated USD / month |
|---|---|
| Small (Terraform defaults) | ≈ 148 |
| Moderate production | ≈ 427 |

Surprise finding: at small scale, **networking (NAT gateway, public IPs, load balancer) costs more than the servers and database combined.**

## Deploying it yourself (optional)

Needs an AWS account, the AWS CLI configured, and Terraform ≥ 1.6. **This creates billable resources** (about $5 a day with the defaults).

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan
terraform apply
```

Open the `alb_dns_name` output in a browser. The page shows which Availability Zone answered. Remove everything afterwards with `terraform destroy`. `db_deletion_protection` must be `false` for that, as set in the example file.

