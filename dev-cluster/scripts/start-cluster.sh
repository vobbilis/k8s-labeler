#!/bin/bash

set -e

# Source utilities
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "${SCRIPT_DIR}/utils.sh"

# Check required tools
required_tools=("kind" "kubectl" "helm")
for tool in "${required_tools[@]}"; do
    if ! check_command "$tool"; then
        log_error "Required tool $tool is not installed"
        exit 1
    fi
done

# Create temporary kind config with resolved paths
TMP_CONFIG="${PROJECT_ROOT}/tmp/kind-config.yaml"
mkdir -p "${PROJECT_ROOT}/tmp"
sed "s|\${PROJECT_ROOT}|${PROJECT_ROOT}|g" "${PROJECT_ROOT}/config/kind-config.yaml" > "${TMP_CONFIG}"

# Create cluster if it doesn't exist
if ! kind get clusters | grep -q "^${CLUSTER_NAME}$"; then
    log_info "Creating cluster ${CLUSTER_NAME}..."
    kind create cluster --config "${TMP_CONFIG}"
else
    log_warn "Cluster ${CLUSTER_NAME} already exists"
fi

# Clean up temporary config
rm -f "${TMP_CONFIG}"

# Export environment variables
export_env_vars

# Check cluster health
if ! check_cluster_health; then
    log_error "Cluster health check failed"
    exit 1
fi

# Install OpenTelemetry Operator
log_info "Installing OpenTelemetry Operator..."
kubectl apply -f https://github.com/open-telemetry/opentelemetry-operator/releases/latest/download/opentelemetry-operator.yaml

# Wait for OpenTelemetry Operator
if ! kubectl wait --for=condition=available --timeout=300s deployment/opentelemetry-operator-controller-manager -n opentelemetry-operator-system; then
    log_error "OpenTelemetry Operator installation failed"
    exit 1
fi

# Add Helm repositories
log_info "Adding Helm repositories..."
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo add open-telemetry https://open-telemetry.github.io/opentelemetry-helm-charts
helm repo update

log_info "Cluster setup completed successfully"
log_info "Cluster Status:"
kubectl cluster-info
kubectl get nodes
kubectl get pods -A

# Print access information
log_info "Access Information:"
echo "- Dashboard: http://localhost:30000"
echo "- Grafana: http://localhost:3000"
echo "- Prometheus: http://localhost:9090"
echo "- Jaeger UI: http://localhost:16686" 