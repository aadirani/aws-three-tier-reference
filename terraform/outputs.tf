output "alb_dns_name" {
  description = "Open this address in a browser to reach the demo app."
  value       = aws_lb.app.dns_name
}

output "db_endpoint" {
  description = "Private database hostname (reachable only from the app tier)."
  value       = aws_db_instance.main.address
}

output "db_secret_arn" {
  description = "Secrets Manager secret holding the database master password (managed by RDS)."
  value       = aws_db_instance.main.master_user_secret[0].secret_arn
}
