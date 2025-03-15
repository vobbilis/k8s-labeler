#!/bin/bash

set -e

# Source utilities
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "${SCRIPT_DIR}/utils.sh"

# Check if cluster exists
if ! kind get clusters | grep -q "^${CLUSTER_NAME}$"; then
    log_warn "Cluster ${CLUSTER_NAME} does not exist"
    exit 0
fi

# Save any important logs or data before shutdown
log_info "Saving cluster logs..."
LOGS_DIR="${SCRIPT_DIR}/../logs/$(date +%Y%m%d_%H%M%S)"
mkdir -p "${LOGS_DIR}"

# Save pod logs from important namespaces
namespaces=("kube-system" "monitoring" "opentelemetry-operator-system")
for ns in "${namespaces[@]}"; do
    if kubectl get namespace "$ns" &>/dev/null; then
        log_info "Saving logs from namespace: $ns"
        mkdir -p "${LOGS_DIR}/${ns}"
        kubectl get pods -n "$ns" --no-headers | awk '{print $1}' | while read -r pod; do
            kubectl logs "$pod" -n "$ns" > "${LOGS_DIR}/${ns}/${pod}.log" 2>/dev/null || true
        done
    fi
done

# Save cluster info
log_info "Saving cluster info..."
kubectl cluster-info dump > "${LOGS_DIR}/cluster-info.txt" 2>/dev/null || true
kubectl get all -A > "${LOGS_DIR}/resources.txt" 2>/dev/null || true

# Delete the cluster
log_info "Stopping cluster ${CLUSTER_NAME}..."
kind delete cluster --name "${CLUSTER_NAME}"

log_info "Cluster stopped successfully"
log_info "Cluster logs saved to: ${LOGS_DIR}"

# Clean up environment variables
unset KUBECONFIG
unset CLUSTER_NAME

# Optional: Clean up temporary files
log_info "Cleaning up temporary files..."
rm -rf "${SCRIPT_DIR}/../tmp/*" 