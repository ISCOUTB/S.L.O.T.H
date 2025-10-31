#!/bin/bash

# Script to get your public IP and configure Terraform

echo "======================================"
echo "Docker Swarm AWS Configuration"
echo "======================================"
echo ""

# Get public IP
PUBLIC_IP=$(curl -s https://api.ipify.org)
echo "Your public IP is: $PUBLIC_IP"
echo ""

# Create terraform.tfvars if it doesn't exist
TFVARS_FILE="terraform/terraform.tfvars"

if [ ! -f "$TFVARS_FILE" ]; then
    echo "Creating $TFVARS_FILE..."
    cat > "$TFVARS_FILE" << EOF
# Docker Swarm Configuration
# Auto-generated - $(date)

# Number of managers (must be odd: 1, 3, 5)
manager_count = 1

# Number of workers
worker_count = 2

# Your public IP for SSH (replace if necessary)
allowed_ssh_cidr = "$PUBLIC_IP/32"

# Instance type (t3.micro is free with free tier)
instance_type = "t3.micro"
EOF
    echo "✓ $TFVARS_FILE created with your IP: $PUBLIC_IP"
else
    echo "⚠ $TFVARS_FILE already exists. Check the configuration."
    echo ""
    echo "Current content:"
    cat "$TFVARS_FILE"
fi
