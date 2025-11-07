#!/bin/bash
set -e

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${YELLOW}========================================${NC}"
echo -e "${RED}Docker Swarm Cleanup Script${NC}"
echo -e "${YELLOW}========================================${NC}\n"

read -p "Are you sure you want to destroy all resources? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo -e "${YELLOW}Operation cancelled${NC}"
    exit 0
fi

TERRAFORM_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../terraform" && pwd)"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo -e "${RED}Destroying resources...${NC}"
cd "$TERRAFORM_DIR"
terraform destroy -auto-approve

echo -e "${RED}Removing local files...${NC}"
rm -f "$PROJECT_ROOT/keys/swarm-key.pem"
rm -f "$PROJECT_ROOT/ansible/inventory.ini"
rm -f "$PROJECT_ROOT/ansible/*.txt"

echo -e "${GREEN}✓ Cleanup completed${NC}"
