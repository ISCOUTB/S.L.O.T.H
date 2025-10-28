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
Usage: $0 --resource <resource> --environment <environment> [OPTIONS]

Deploy Helm charts to Kubernetes.

OPTIONS:
    --resource RESOURCE         The Helm chart to deploy (e.g., 'etl-api', 'formula-parser', 'sql-builder')
    --environment ENVIRONMENT   The target environment (development, staging, production)
    --template                  Render the chart template without installing (output to ./rendered-charts/)
    -h, --help                  Show this help message

EXAMPLES:
    $0 --resource etl-api --environment development
    $0 --resource formula-parser --environment staging
    $0 --resource sql-builder --environment production --template
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

# Get environment nickname
get_environment_nick() {
    local environment="$1"

    case "$environment" in
        development)
            echo "dev"
            ;;
        staging)
            echo "stag"
            ;;
        production)
            echo "prod"
            ;;
        *)
            echo ""
            ;;
    esac
}

# Deploy Helm chart function
deploy_helm_chart() {
    local resource="$1"
    local environment="$2"
    local template_only="$3"

    # Get environment nickname
    local env_nick
    env_nick=$(get_environment_nick "$environment")

    if [[ -z "$env_nick" ]]; then
        log_error "Invalid environment: $environment"
        return 1
    fi

    # Define paths
    local chart_dir="$BASE_DIR/charts/$resource"
    local values_file="$chart_dir/values-${env_nick}.yaml"

    # Verify chart directory exists
    if [[ ! -d "$chart_dir" ]]; then
        log_error "Chart directory not found: $chart_dir"
        return 1
    fi

    # Verify values file exists
    if [[ ! -f "$values_file" ]]; then
        log_error "Values file not found: $values_file"
        return 1
    fi

    if [[ "$template_only" == "true" ]]; then
        # Template mode: render without installing
        local rendered_dir="$BASE_DIR/rendered-charts"
        local output_file="$rendered_dir/${resource}.yaml"

        # Create rendered-charts directory if it doesn't exist
        if [[ ! -d "$rendered_dir" ]]; then
            log_info "Creating rendered-charts directory: $rendered_dir"
            mkdir -p "$rendered_dir"
        fi

        log_info "Rendering Helm chart: $resource"
        log_info "Environment: $environment (nick: $env_nick)"
        log_info "Chart directory: $chart_dir"
        log_info "Values file: $values_file"
        log_info "Output file: $output_file"

        # Execute helm template command
        if helm template "$resource" "$chart_dir" \
            -f "$values_file" >| "$output_file" 2>&1; then
            log_info "Successfully rendered $resource chart to $output_file"
            return 0
        else
            log_error "Failed to render $resource chart"
            return 1
        fi
    else
        # Install mode: deploy to cluster
        log_info "Installing Helm chart: $resource"
        log_info "Environment: $environment (nick: $env_nick)"
        log_info "Chart directory: $chart_dir"
        log_info "Values file: $values_file"
        log_info "Namespace: $environment"

        # Execute helm install command
        if helm install "$resource" "$chart_dir" \
            -f "$values_file" \
            --namespace "$environment" 2>&1; then
            log_info "Successfully installed $resource chart"
            return 0
        else
            log_error "Failed to install $resource chart"
            return 1
        fi
    fi
}

# Main script
main() {
    local resource=""
    local environment=""
    local template_only="false"

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
            --template)
                template_only="true"
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

    # Validate required arguments
    if [[ -z "$resource" ]]; then
        log_error "Missing required argument: --resource"
        usage
    fi

    if [[ -z "$environment" ]]; then
        log_error "Missing required argument: --environment"
        usage
    fi

    # Check if helm is installed
    if ! command -v helm &> /dev/null; then
        log_error "helm is not installed. Please install it first."
        exit 1
    fi

    # Check if kubectl is installed (only for install mode)
    if [[ "$template_only" == "false" ]] && ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed. Please install it first."
        exit 1
    fi

    if [[ "$template_only" == "true" ]]; then
        log_info "Rendering Helm chart $resource for $environment environment..."
    else
        log_info "Deploying Helm chart $resource to $environment environment..."
    fi

    # Deploy or render the Helm chart
    if deploy_helm_chart "$resource" "$environment" "$template_only"; then
        if [[ "$template_only" == "true" ]]; then
            log_info "Render completed successfully!"
        else
            log_info "Deployment completed successfully!"
        fi
        exit 0
    else
        if [[ "$template_only" == "true" ]]; then
            log_error "Render failed!"
        else
            log_error "Deployment failed!"
        fi
        exit 1
    fi
}

# Run main function
main "$@"
