#!/bin/bash
set -e

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Function to show usage
show_usage() {
    echo -e "${BLUE}Usage:${NC}"
    echo -e "  $0 <environment> [-y]"
    echo ""
    echo -e "${BLUE}Arguments:${NC}"
    echo -e "  environment    Environment to cleanup (development, staging, or production)"
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
echo -e "${RED}Docker Swarm Cleanup Script${NC}"
echo -e "${YELLOW}========================================${NC}"
echo -e "${BLUE}Environment: ${ENVIRONMENT}${NC}\n"

# Confirm destruction (unless -y flag is set)
if [ "$AUTO_APPROVE" = false ]; then
    read -p "Are you sure you want to destroy all ${ENVIRONMENT} resources? (yes/no): " confirm

    if [ "$confirm" != "yes" ]; then
        echo -e "${YELLOW}Operation cancelled${NC}"
        exit 0
    fi
else
    echo -e "${YELLOW}Auto-approve enabled, skipping confirmation...${NC}\n"
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$SCRIPT_DIR/../terraform"
PROJECT_ROOT="$SCRIPT_DIR/.."
ENV_DIR="$TERRAFORM_DIR/environments/$ENVIRONMENT"

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

echo -e "${RED}Destroying Terraform resources...${NC}"
cd "$ENV_DIR"
terraform destroy -auto-approve

echo -e "${RED}Removing local token files...${NC}"
rm -f "$PROJECT_ROOT/ansible/manager-token-${ENVIRONMENT}.txt"
rm -f "$PROJECT_ROOT/ansible/worker-token-${ENVIRONMENT}.txt"

echo -e "\n${GREEN}✓ Cleanup completed for ${ENVIRONMENT} environment${NC}"
