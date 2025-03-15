#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
CLUSTER_NAME="k8s-labeler-dev"

# Log functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if a command exists
check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "$1 could not be found"
        return 1
    fi
}

# Wait for pods in a namespace to be ready
wait_for_pods() {
    local namespace=$1
    local timeout=${2:-300} # Default timeout of 5 minutes
    local start_time=$(date +%s)

    log_info "Waiting for pods in namespace '$namespace' to be ready..."
    
    while true; do
        local current_time=$(date +%s)
        local elapsed_time=$((current_time - start_time))
        
        if [ $elapsed_time -gt $timeout ]; then
            log_error "Timeout waiting for pods in namespace '$namespace'"
            return 1
        fi

        local not_ready=$(kubectl get pods -n "$namespace" --no-headers 2>/dev/null | grep -v "Running\|Completed" | wc -l)
        
        if [ "$not_ready" -eq 0 ]; then
            log_info "All pods in namespace '$namespace' are ready"
            return 0
        fi

        sleep 5
    done
}

# Check cluster health
check_cluster_health() {
    log_info "Checking cluster health..."
    
    # Check if cluster exists
    if ! kind get clusters | grep -q "^${CLUSTER_NAME}$"; then
        log_error "Cluster ${CLUSTER_NAME} does not exist"
        return 1
    fi

    # Check if kubectl can connect
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to cluster"
        return 1
    fi

    # Check node status
    if ! kubectl get nodes | grep -q "Ready"; then
        log_error "No nodes are ready"
        return 1
    fi

    # Check core components
    local core_namespaces=("kube-system")
    for ns in "${core_namespaces[@]}"; do
        if ! wait_for_pods "$ns" 60; then
            log_error "Core components in $ns are not ready"
            return 1
        fi
    done

    log_info "Cluster is healthy"
    return 0
}

# Export environment variables
export_env_vars() {
    export KUBECONFIG="$(kind get kubeconfig --name=${CLUSTER_NAME})"
    export CLUSTER_NAME="${CLUSTER_NAME}"
} 