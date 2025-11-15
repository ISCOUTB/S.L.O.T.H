#!/bin/bash

# Script to get your public IP and configure Terraform for all environments

set -e

echo "======================================"
echo "Docker Swarm AWS Configuration"
echo "======================================"
echo ""

# Get public IP
PUBLIC_IP=$(curl -s https://api.ipify.org)
echo "Your public IP is: $PUBLIC_IP"
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$SCRIPT_DIR/../terraform"
ENVIRONMENTS_DIR="$TERRAFORM_DIR/environments"

# Environments to configure
ENVIRONMENTS=("development" "staging" "production")

# Function to create terraform.tfvars for an environment
create_tfvars() {
    local env=$1
    local env_dir="$ENVIRONMENTS_DIR/$env"
    local tfvars_file="$env_dir/terraform.tfvars"
    
    # Create environment directory if it doesn't exist
    mkdir -p "$env_dir"
    
    if [ -f "$tfvars_file" ]; then
        echo "$env/terraform.tfvars already exists. Skipping..."
        return
    fi
    
    # Set environment-specific defaults
    local manager_count=1
    local worker_count=2
    local instance_type="t3.micro"
    local vpc_cidr="10.0.0.0/16"
    local purpose="ETL Design Project"

    case $env in
        development)
            manager_count=1
            worker_count=1
            instance_type="t3.micro"
            vpc_cidr="10.1.0.0/16"
            purpose="Development Environment for ETL Design Project"
            ;;
        staging)
            manager_count=1
            worker_count=2
            instance_type="t3.micro"
            vpc_cidr="10.2.0.0/16"
            purpose="Staging Environment for ETL Design Project"
            ;;
        production)
            manager_count=3
            worker_count=3
            instance_type="t3.small"
            vpc_cidr="10.3.0.0/16"
            purpose="Production Environment for ETL Design Project"
            ;;
    esac

    echo "Creating $env/terraform.tfvars..."

    cat > "$tfvars_file" << EOF
# ============================================
# ${env^} Environment Configuration
# ============================================
# Auto-generated on $(date)

# Environment name (used for tagging and naming resources)
environment = "$env"

# Project name (used as prefix for all resources)
project_name = "etl-design"

# ============================================
# Cluster Configuration
# ============================================

# Number of manager nodes (must be odd: 1, 3, 5)
manager_count = $manager_count

# Number of worker nodes
worker_count = $worker_count

# ============================================
# EC2 Instance Configuration
# ============================================

# Instance type (t3.micro is free tier eligible)
# Options: t3.micro, t3.small, t3.medium, t3.large
instance_type = "$instance_type"

# ============================================
# Network Configuration
# ============================================

# VPC CIDR block (shouldn't conflict with other VPCs)
vpc_cidr = "$vpc_cidr"

# Availability zones to use
availability_zones = [
  "us-east-1a",
  "us-east-1b"
]

# ============================================
# Security Configuration
# ============================================

# SSH access configuration
# Your current public IP: $PUBLIC_IP
# Options:
#   - ["$PUBLIC_IP/32"]           # Only your current IP
#   - ["0.0.0.0/0"]               # Allow from anywhere (requires SSH key)
#   - ["IP1/32", "IP2/32"]        # Multiple specific IPs
allowed_ssh_cidr = ["0.0.0.0/0"]

# ============================================
# Additional Tags
# ============================================

# Custom tags to apply to all resources
tags = {
  Team       = "DevOps"
  CostCenter = "Engineering"
  ManagedBy  = "Terraform"
  Purpose    = "$purpose"
}
EOF
    
    echo "$env/terraform.tfvars created"
    echo ""
}

echo "Configuring Terraform for all environments..."
echo ""

# Create terraform.tfvars for each environment
for env in "${ENVIRONMENTS[@]}"; do
    create_tfvars "$env"
done

echo "======================================"
echo "Configuration complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Review and adjust the generated terraform.tfvars files in:"
for env in "${ENVIRONMENTS[@]}"; do
    echo "   - terraform/environments/$env/terraform.tfvars"
done
echo ""
echo "2. Initialize and apply Terraform for the desired environment:"
echo "   cd terraform/environments/staging"
echo "   terraform init"
echo "   terraform plan"
echo "   terraform apply"
echo ""
echo "Note: SSH is currently open to 0.0.0.0/0 (any IP) but requires SSH key authentication."
echo "To restrict access, update 'allowed_ssh_cidr' in the terraform.tfvars file."
