variable "region" {
  description = "AWS region to deploy into."
  type        = string
  default     = "us-east-1"
}

variable "project" {
  description = "Short name used as a prefix for all resources."
  type        = string
  default     = "three-tier"
}

variable "vpc_cidr" {
  description = "Address range of the VPC."
  type        = string
  default     = "10.0.0.0/16"
}

variable "az_count" {
  description = "Number of Availability Zones to spread across."
  type        = number
  default     = 2

  validation {
    condition     = var.az_count >= 2
    error_message = "Use at least two Availability Zones for high availability."
  }
}

variable "nat_gateway_per_az" {
  description = "true = one NAT gateway per AZ (production), false = a single shared NAT gateway (cheaper)."
  type        = bool
  default     = false
}

variable "app_instance_type" {
  description = "EC2 instance type for the app tier (Graviton/arm64)."
  type        = string
  default     = "t4g.small"
}

variable "app_min_size" {
  description = "Minimum number of app servers."
  type        = number
  default     = 2
}

variable "app_max_size" {
  description = "Maximum number of app servers."
  type        = number
  default     = 4
}

variable "db_instance_class" {
  description = "RDS instance class for PostgreSQL."
  type        = string
  default     = "db.t4g.micro"
}

variable "db_allocated_storage" {
  description = "Initial database storage in GB (grows automatically up to 5x)."
  type        = number
  default     = 20
}

variable "db_multi_az" {
  description = "Keep a synchronous standby database in a second AZ."
  type        = bool
  default     = true
}

variable "db_deletion_protection" {
  description = "Block accidental deletion of the database. Set to false only for short-lived demos."
  type        = bool
  default     = true
}

variable "certificate_arn" {
  description = "ACM certificate ARN for HTTPS. Leave empty to run the demo over HTTP only."
  type        = string
  default     = ""
}

variable "alarm_email" {
  description = "Email address that receives alarm notifications. Leave empty to skip."
  type        = string
  default     = ""
}
