#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to show usage
show_usage() {
    echo -e "${BLUE}Usage:${NC}"
    echo -e "  $0 <environment> [-y]"
    echo ""
    echo -e "${BLUE}Arguments:${NC}"
    echo -e "  environment    Environment to deploy (development, staging, or production)"
    echo ""
    echo -e "${BLUE}Options:${NC}"
    echo -e "  -y            Skip confirmation prompt (auto-approve)"
    echo ""
    echo -e "${BLUE}Examples:${NC}"
    echo -e "  $0 staging"
    echo -e "  $0 production -y"
    exit 1
}

# Validate arguments
if [ $# -lt 1 ] || [ $# -gt 2 ]; then
    echo -e "${RED}Error: Invalid number of arguments${NC}\n"
    show_usage
fi

ENVIRONMENT=""
AUTO_APPROVE=false

# Parse arguments in any order
for arg in "$@"; do
    if [ "$arg" == "-y" ]; then
        AUTO_APPROVE=true
    elif [[ "$arg" =~ ^(development|staging|production)$ ]]; then
        ENVIRONMENT="$arg"
    else
        echo -e "${RED}Error: Invalid argument '$arg'${NC}\n"
        show_usage
    fi
done

# Validate that environment was provided
if [ -z "$ENVIRONMENT" ]; then
    echo -e "${RED}Error: Environment not specified${NC}"
    echo -e "${RED}Must be one of: development, staging, production${NC}\n"
    show_usage
fi

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Docker Swarm Deployment Script${NC}"
echo -e "${YELLOW}========================================${NC}"
echo -e "${BLUE}Environment: ${ENVIRONMENT}${NC}\n"

# Variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR/.."
TERRAFORM_DIR="$PROJECT_ROOT/terraform"
ENV_DIR="$TERRAFORM_DIR/environments/$ENVIRONMENT"
SSH_KEY="$TERRAFORM_DIR/environments/$ENVIRONMENT/ssh-keys/$ENVIRONMENT-swarm-key.pem"

# Check if environment directory exists
if [ ! -d "$ENV_DIR" ]; then
    echo -e "${RED}Error: Environment directory not found: $ENV_DIR${NC}"
    exit 1
fi

# Check if terraform.tfvars exists
if [ ! -f "$ENV_DIR/terraform.tfvars" ]; then
    echo -e "${RED}Error: terraform.tfvars not found in $ENV_DIR${NC}"
    echo -e "${YELLOW}Run setup.sh first to initialize the environment${NC}"
    exit 1
fi

# Step 1: Initialize Terraform
echo -e "${YELLOW}[STEP 1/3]${NC} Initializing Terraform..."
cd "$ENV_DIR"
terraform init

# Step 2: Validate Terraform
echo -e "${YELLOW}[STEP 2/3]${NC} Validating Terraform configuration..."
terraform validate
echo -e "${GREEN}✓ Terraform configuration is valid${NC}\n"

# Show plan
echo -e "${YELLOW}Generating deployment plan...${NC}\n"
terraform plan

# Confirm deployment (unless -y flag is set)
if [ "$AUTO_APPROVE" = false ]; then
    echo ""
    read -p "Do you want to apply these changes to ${ENVIRONMENT}? (yes/no): " confirm
    
    if [ "$confirm" != "yes" ]; then
        echo -e "${YELLOW}Deployment cancelled${NC}"
        exit 0
    fi
else
    echo -e "\n${YELLOW}Auto-approve enabled, skipping confirmation...${NC}\n"
fi

# Step 3: Create infrastructure
echo -e "${YELLOW}[STEP 3/3]${NC} Deploying infrastructure..."
echo -e "${YELLOW}This will create EC2 instances, install Docker, and initialize Swarm...${NC}\n"

if [ "$AUTO_APPROVE" = true ]; then
    terraform apply -auto-approve
else
    terraform apply
fi

echo -e "\n${GREEN}✓ Infrastructure deployed successfully${NC}\n"

# Display summary
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment completed successfully!${NC}"
echo -e "${GREEN}========================================${NC}\n"

echo -e "${YELLOW}Cluster Information:${NC}"
terraform output

# Get manager IP for quick access instructions
if terraform output swarm_manager_ip &>/dev/null; then
    MANAGER_IP=$(terraform output -raw swarm_manager_ip)
    
    echo -e "\n${YELLOW}Quick Access Commands:${NC}"
    echo -e "${BLUE}Connect to primary manager:${NC}"
    echo -e "  ssh -i $SSH_KEY ubuntu@$MANAGER_IP"
    
    echo -e "\n${BLUE}View cluster status:${NC}"
    echo -e "  ssh -i $SSH_KEY ubuntu@$MANAGER_IP docker node ls"
    
    echo -e "\n${BLUE}Deploy a test service:${NC}"
    echo -e "  ssh -i $SSH_KEY ubuntu@$MANAGER_IP docker service create --name test-nginx --replicas 3 --publish 80:80 nginx"
fi

echo ""
