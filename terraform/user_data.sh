#!/bin/bash
# Demo app: nginx serving a page that shows which Availability Zone answered.
set -euo pipefail

dnf install -y nginx

TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 300")
AZ=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/placement/availability-zone)

echo "<h1>3-tier reference app</h1><p>Served from $AZ</p>" > /usr/share/nginx/html/index.html
echo "ok" > /usr/share/nginx/html/health

systemctl enable --now nginx
