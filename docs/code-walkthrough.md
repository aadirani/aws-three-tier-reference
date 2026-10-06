# Code walkthrough

A plain-language guide to the code, so it can be explained in an interview without being a programmer.

## Part 1: Terraform (`terraform/`)

Terraform is a tool that reads text files describing infrastructure ("I want a network, two servers, a database") and creates or updates them in AWS to match. Each `resource "type" "name" { ... }` block is one thing in AWS. Files are split by topic only for readability. Terraform reads them all together.

| File | What it creates | Key points to explain |
|---|---|---|
| `versions.tf` | Which Terraform and AWS provider versions to use; default tags | Every resource gets `Project` and `ManagedBy` tags, which helps with cost reports |
| `variables.tf` | The knobs: region, sizes, Multi-AZ, NAT per AZ… | Sensible, cheap defaults; a `validation` rule refuses fewer than 2 AZs |
| `network.tf` | VPC, 3 subnet types × 2 AZs, internet gateway, NAT, route tables, S3 endpoint | `cidrsubnet()` carves the /16 into /24s: public `10.0.0-1`, app `10.0.10-11`, data `10.0.20-21`. The data subnets' route table has **no internet route at all** |
| `security.tf` | Three security groups and the rules between them | Rules point at *other security groups*, not IP addresses: "app accepts port 80 only from the ALB group" |
| `app.tf` | Server role, launch template, load balancer, Auto Scaling group, scaling policy | Launch template = the recipe for a server. Auto Scaling group = "keep 2–4 of these healthy, spread over both AZs". Target tracking = "keep average CPU around 50%" |
| `user_data.sh` | Script each new server runs at first boot | Installs nginx and writes a page showing which AZ answered. That's an easy way to *see* load balancing working |
| `database.tf` | RDS PostgreSQL | `multi_az = true` keeps a standby. `manage_master_user_password = true` means no password in code. `deletion_protection` and the final snapshot prevent accidents |
| `waf.tf` | Web firewall attached to the load balancer | A `dynamic "rule"` block loops over three AWS-managed rule groups instead of repeating the same code three times. Plus a rate limit per IP |
| `monitoring.tf` | Email topic and 4 alarms | Server errors, unhealthy servers, database CPU, database disk space |
| `outputs.tf` | Values printed after deploy | The website address, database hostname, and *where* the password is stored (not the password itself) |

**Two Terraform tricks worth understanding**
- `count = var.az_count` creates one copy per AZ, and `count.index` (0, 1) picks which AZ and subnet range each copy gets.
- `condition ? a : b` is an inline "if". For example, the HTTP listener forwards to the app when there's no certificate, and redirects to HTTPS when there is one.

## Part 2: The cost model (`cost/`)

**The idea:** keep *prices* and *usage* in two separate data files, and let a tiny script multiply them.

- `pricing.json` lists the unit price of each AWS item, e.g. `"nat_hour": 0.045 per hour`.
- `scenarios.json` lists how much of each item a scenario uses, e.g. `NAT gateway: quantity 1`.
- `cost_model.py` works out, for each line, **price × quantity**, multiplied by **730 hours** when the price is hourly (AWS's standard month = 24 × 365 ÷ 12). It adds the lines up and prints a table sorted from most to least expensive.

Example: one NAT gateway = $0.045 × 1 × 730 = **$32.85/month**, about 22% of the small scenario's ≈ $148.

**Why split data from code?** Changing a price or adding a scenario means editing a data file, not the program. Anyone can review the assumptions without reading Python.

**The tests** (`tests/test_cost_model.py`) check the arithmetic on hand-calculated examples, reject bad input (negative quantities, unknown price names), and **pin the two published totals**. If someone changes a price but forgets to update `ARCHITECTURE.md`, the tests fail.

## Likely interview questions

- **"Why three tiers?"** Each layer can scale and be secured on its own. The database is never exposed to the internet, and a compromised web tier can't reach the data directly.
- **"What happens if an Availability Zone goes down?"** See the failure table in ARCHITECTURE.md §4: the ALB routes around it, Auto Scaling replaces capacity, and RDS promotes the standby within about 1–2 minutes.
- **"Why is NAT such a big cost?"** It's charged per hour *and* per GB, and it needs a public IP, which AWS also charges for. At low traffic, those fixed hourly costs dominate.
- **"Why not Kubernetes?"** It's too much to run for one application and a small team. EC2 Auto Scaling is simpler, and ECS Fargate is the next step once the app is in containers (ADR-001).
- **"Have you deployed it?"** Be honest: the code is validated automatically, but it hasn't been deployed from this repository. Deploying and destroying it in a personal account costs about $5 a day and is a good way to back up the claim.
