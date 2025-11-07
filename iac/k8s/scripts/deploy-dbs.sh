#!/bin/bash

set -uo pipefail

# Get the base directory (parent of scripts/)
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Usage function
usage() {
    cat << EOF
Usage: $0 --resource <resource> --environment <environment>

Deploy database resources to Kubernetes.

OPTIONS:
    --resource RESOURCE         The database resource to deploy (e.g., 'postgres', 'redis', 'mongo', 'rabbitmq')
    --environment ENVIRONMENT   The target environment (development, staging, production)
    -h, --help                  Show this help message

EXAMPLES:
    $0 --resource postgres --environment development
    $0 --resource redis --environment staging
    $0 --resource mongo --environment production
EOF
    exit 0
}

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Deploy database function
deploy_database() {
    local resource="$1"
    local environment="$2"

    local workdir="$BASE_DIR/$environment"

    if [[ ! -d "$workdir" ]]; then
        log_error "Environment directory not found: $workdir"
        return 1
    fi

    # Find all YAML files matching the resource name
    local found_files=0

    while IFS= read -r -d '' resource_file; do
        found_files=1
        log_info "Applying $resource_file to $environment environment..."
        
        if kubectl apply -f "$resource_file" 2>/dev/null; then
            log_info "Successfully applied $resource_file"
        else
            log_error "Failed to apply $resource_file"
            return 1
        fi
    done < <(find "$workdir" -type f -name "${resource}.yaml" -print0)

    if [[ $found_files -eq 0 ]]; then
        log_warn "No files found matching pattern '${resource}.yaml' in $workdir"
        return 1
    fi

    return 0
}

# Main script
main() {
    local resource=""
    local environment=""

    # Parse arguments
    if [[ $# -eq 0 ]]; then
        usage
    fi

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --resource)
                if [[ -z "${2:-}" ]]; then
                    log_error "--resource requires an argument"
                    exit 1
                fi
                resource="$2"
                shift 2
                ;;
            --environment)
                if [[ -z "${2:-}" ]]; then
                    log_error "--environment requires an argument"
                    exit 1
                fi
                case "$2" in
                    development|staging|production)
                        environment="$2"
                        shift 2
                        ;;
                    *)
                        log_error "Invalid environment: $2"
                        log_error "Must be one of: development, staging, production"
                        exit 1
                        ;;
                esac
                ;;
            -h|--help)
                usage
                ;;
            *)
                log_error "Unknown option: $1"
                usage
                ;;
        esac
    done

    # Validate required arguments
    if [[ -z "$resource" ]]; then
        log_error "Missing required argument: --resource"
        usage
    fi

    if [[ -z "$environment" ]]; then
        log_error "Missing required argument: --environment"
        usage
    fi

    # Check if kubectl is installed
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed. Please install it first."
        exit 1
    fi

    log_info "Deploying $resource to $environment environment..."

    # Deploy the database
    if deploy_database "$resource" "$environment"; then
        log_info "Deployment completed successfully!"
        exit 0
    else
        log_error "Deployment failed!"
        exit 1
    fi
}

# Run main function
main "$@"
