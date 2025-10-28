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
Usage: $0 <environment> [OPTIONS]

Setup Kubernetes cluster with namespaces and configurations.

ARGUMENTS:
    environment         The environment to set up (development, staging, production)

OPTIONS:
    --env-file FILE     Path to the .env file to use for secrets
    --create-namespaces Create all namespaces (development, staging, production)
    --create-namespace  Create only the specified namespace
    -h, --help          Show this help message

EXAMPLES:
    $0 development
    $0 staging --env-file /path/to/.env
    $0 production --create-namespace
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

# Create a single namespace
create_namespace() {
    local namespace="$1"
    log_info "Creating namespace: $namespace"
    
    if kubectl create namespace "$namespace" 2>/dev/null; then
        log_info "Namespace $namespace created successfully"
        return 0
    else
        log_warn "Namespace $namespace already exists or could not be created"
        return 0  # Return 0 to continue execution
    fi
}

# Create all namespaces
create_namespaces() {
    log_info "Creating Kubernetes namespaces..."
    create_namespace "development" || true
    create_namespace "staging" || true
    create_namespace "production" || true
    return 0
}

# Deploy a regular file (ConfigMap, etc.)
deploy_file() {
    local file_path="$1"
    local namespace="$2"
    
    if kubectl apply -f "$file_path" -n "$namespace" >/dev/null 2>&1; then
        log_info "Deployed $file_path to namespace $namespace" >&2
        return 0
    else
        log_error "Failed to deploy $file_path to namespace $namespace" >&2
        return 1
    fi
}

# Find .env file
find_env_file() {
    local base_dir="$1"
    local environment="$2"
    
    # Check for .env in base directory
    if [[ -f "$base_dir/.env" ]]; then
        echo "$base_dir/.env"
        return 0
    fi
    
    # Check for .env in environment subdirectory
    if [[ -f "$base_dir/$environment/.env" ]]; then
        echo "$base_dir/$environment/.env"
        return 0
    fi
    
    # Check for .env.{environment}
    if [[ -f "$base_dir/.env.$environment" ]]; then
        echo "$base_dir/.env.$environment"
        return 0
    fi
    
    return 1
}

# Deploy secrets with environment variable substitution
deploy_secrets() {
    local secret_file="$1"
    local environment="$2"
    local env_file="$3"
    
    # Find env file if not provided
    if [[ -z "$env_file" ]]; then
        if env_file=$(find_env_file "$BASE_DIR" "$environment"); then
            log_info "Found .env file: $env_file" >&2
        elif env_file=$(find_env_file "$(dirname "$BASE_DIR")" "$environment"); then
            log_info "Found .env file: $env_file" >&2
        else
            log_error "Could not find .env file for environment $environment" >&2
            return 1
        fi
    fi
    
    # Verify env file exists
    if [[ ! -f "$env_file" ]]; then
        log_error "Environment file not found: $env_file" >&2
        return 1
    fi
    
    # Apply secrets with environment variable substitution
    if (
        set -a
        source "$env_file"
        set +a
        envsubst < "$secret_file" | kubectl apply -n "$environment" -f -
    ) >/dev/null 2>&1; then
        log_info "Deployed secrets from $secret_file to namespace $environment" >&2
        return 0
    else
        log_error "Failed to deploy secrets from $secret_file to namespace $environment" >&2
        return 1
    fi
}

# Process a single YAML file (may contain multiple documents)
process_yaml_file() {
    local file="$1"
    local environment="$2"
    local env_file="$3"
    local has_secret=0
    local has_configmap=0
    
    # Get the number of documents in the file
    local doc_count
    doc_count=$(yq eval-all '. | select(. != null) | documentIndex' "$file" 2>/dev/null | wc -l)
    
    if [[ $doc_count -eq 0 ]]; then
        log_warn "No valid YAML documents found in $file" >&2
        return 0
    fi
    
    # Process each document
    for ((i=0; i<doc_count; i++)); do
        # Get the kind of the current document
        local kind
        kind=$(yq eval "select(documentIndex == $i) | .kind" "$file" 2>/dev/null)
        
        if [[ -z "$kind" ]] || [[ "$kind" == "null" ]]; then
            continue
        fi
        
        case "$kind" in
            Secret)
                deploy_secrets "$file" "$environment" "$env_file" || true
                has_secret=1
                ;;
            ConfigMap)
                deploy_file "$file" "$environment" || true
                has_configmap=1
                ;;
            *)
                deploy_file "$file" "$environment" || true
                ;;
        esac
    done
    
    # Return flags as comma-separated values
    echo "$has_secret,$has_configmap"
}

# Prepare cluster for the specified environment
prepare_cluster() {
    local environment="$1"
    local env_file="$2"
    
    log_info "Preparing cluster for environment: $environment"
    
    local environment_dir="$BASE_DIR/$environment"
    
    if [[ ! -d "$environment_dir" ]]; then
        log_error "Environment directory not found: $environment_dir"
        return 1
    fi
    
    # Find all YAML files
    local yaml_files=("$environment_dir"/*.yaml)
    
    # Check if we have at least 2 files
    if [[ ${#yaml_files[@]} -lt 2 ]]; then
        log_error "No configuration files found in $environment_dir (need at least 2: secrets and configmap)"
        return 1
    fi
    
    local found_secret=0
    local found_configmap=0
    
    # Process each YAML file
    for file in "${yaml_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            continue
        fi
        
        log_info "Processing file: $file"
        
        # Process the file and get flags (only capture stdout, let stderr pass through)
        local result=""
        if result=$(process_yaml_file "$file" "$environment" "$env_file"); then
            # Parse the result using parameter expansion
            local has_secret=0
            local has_configmap=0
            
            # Split by comma - more robust approach
            if [[ "$result" =~ ^([0-9]+),([0-9]+)$ ]]; then
                has_secret="${BASH_REMATCH[1]}"
                has_configmap="${BASH_REMATCH[2]}"
            elif [[ "$result" =~ ^([0-9]+),?$ ]]; then
                has_secret="${BASH_REMATCH[1]}"
                has_configmap=0
            fi
            
            # Update global flags
            [[ "$has_secret" -eq 1 ]] && found_secret=1
            [[ "$has_configmap" -eq 1 ]] && found_configmap=1
        else
            log_error "Error processing YAML file: $file (continuing...)"
        fi
    done
    
    # Verify both Secret and ConfigMap were found
    if [[ $found_secret -eq 0 ]] || [[ $found_configmap -eq 0 ]]; then
        log_error "Both ConfigMap and Secret files must be present in $environment_dir"
        return 1
    fi
    
    log_info "Cluster preparation completed successfully for environment: $environment"
    return 0
}

# Main script
main() {
    local environment=""
    local env_file=""
    local create_namespaces_flag=0
    local create_namespace_flag=0
    
    # Parse arguments
    if [[ $# -eq 0 ]]; then
        usage
    fi
    
    # First argument should be environment
    case "$1" in
        development|staging|production)
            environment="$1"
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            log_error "Invalid environment: $1"
            log_error "Must be one of: development, staging, production"
            exit 1
            ;;
    esac
    
    # Parse optional flags
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --env-file)
                if [[ -z "${2:-}" ]]; then
                    log_error "--env-file requires an argument"
                    exit 1
                fi
                env_file="$(realpath "$2")"
                shift 2
                ;;
            --create-namespaces)
                create_namespaces_flag=1
                shift
                ;;
            --create-namespace)
                create_namespace_flag=1
                shift
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
    
    # Check if yq is installed
    if ! command -v yq &> /dev/null; then
        log_error "yq is not installed. Please install it first."
        log_error "Visit: https://github.com/mikefarah/yq"
        exit 1
    fi
    
    # Check if kubectl is installed
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed. Please install it first."
        exit 1
    fi
    
    # Check if envsubst is installed
    if ! command -v envsubst &> /dev/null; then
        log_error "envsubst is not installed. Please install gettext or gettext-base package."
        exit 1
    fi
    
    log_info "Setting up cluster for environment: $environment"
    if [[ -n "$env_file" ]]; then
        log_info "Using .env file: $env_file"
    else
        log_info "Using .env file: default search locations"
    fi
    
    # Create namespaces if requested
    if [[ $create_namespaces_flag -eq 1 ]]; then
        create_namespaces
    fi
    
    # Create single namespace if requested (and not already created all)
    if [[ $create_namespace_flag -eq 1 ]] && [[ $create_namespaces_flag -eq 0 ]]; then
        create_namespace "$environment"
    fi
    
    # Prepare the cluster
    if prepare_cluster "$environment" "$env_file"; then
        log_info "Setup completed successfully!"
        exit 0
    else
        log_error "Setup failed!"
        exit 1
    fi
}

# Run main function
main "$@"
