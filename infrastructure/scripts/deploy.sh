#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Docker Swarm Deployment Script${NC}"
echo -e "${YELLOW}========================================${NC}\n"

# Variables
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TERRAFORM_DIR="$PROJECT_ROOT/terraform"
ANSIBLE_DIR="$PROJECT_ROOT/ansible"
SSH_KEY="$PROJECT_ROOT/keys/swarm-key.pem"

# Step 1: Initialize Terraform
echo -e "${YELLOW}[STEP 1/4]${NC} Initializing Terraform..."
cd "$TERRAFORM_DIR"
terraform init

# Step 2: Validate Terraform
echo -e "${YELLOW}[STEP 2/4]${NC} Validating Terraform configuration..."
terraform validate

# Step 3: Create infrastructure
echo -e "${YELLOW}[STEP 3/4]${NC} Creating EC2 infrastructure (VPC, instances, security groups)..."
terraform apply -auto-approve

# Get outputs
MANAGER_IP=$(terraform output -raw swarm_manager_ip)
echo -e "${GREEN}✓ Infrastructure created successfully${NC}"
echo -e "  Manager Primary IP: ${MANAGER_IP}"

# Wait for instances to be ready
echo -e "${YELLOW}[STEP 4/4]${NC} Waiting for instances to be ready (60 seconds)..."
sleep 60

# Verify SSH access and run initial Ansible playbook (Docker installation)
echo -e "${YELLOW}[STEP 5/5]${NC} Installing Docker on all nodes..."
cd "$PROJECT_ROOT"
ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i ./ansible/inventory.ini \
  --private-key "$SSH_KEY" \
  ./ansible/docker.yaml

echo -e "${GREEN}✓ Docker installed on all nodes${NC}"

# Step 6: Initialize Swarm
echo -e "${YELLOW}[STEP 6/6]${NC} Initializing Docker Swarm cluster..."
ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i ./ansible/inventory.ini \
  --private-key "$SSH_KEY" \
  ./ansible/swarm-init.yaml

echo -e "${GREEN}✓ Docker Swarm cluster initialized successfully${NC}\n"

# Display summary
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment completed successfully!${NC}"
echo -e "${GREEN}========================================${NC}\n"

echo -e "${YELLOW}Cluster Information:${NC}"
cd "$TERRAFORM_DIR"
terraform output

echo -e "\n${YELLOW}To connect to the primary manager:${NC}"
echo -e "  ssh -i $SSH_KEY ubuntu@$MANAGER_IP"

echo -e "\n${YELLOW}To view cluster status:${NC}"
echo -e "  ssh -i $SSH_KEY ubuntu@$MANAGER_IP docker node ls"

echo -e "\n${YELLOW}To deploy a test service:${NC}"
echo -e "  ssh -i $SSH_KEY ubuntu@$MANAGER_IP docker service create --name test-nginx --replicas 3 --publish 80:80 nginx"
