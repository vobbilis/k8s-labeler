#!/bin/bash

set -e

# Source utilities
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "${SCRIPT_DIR}/utils.sh"

# Check if cluster exists
if ! kind get clusters | grep -q "^${CLUSTER_NAME}$"; then
    log_error "Cluster ${CLUSTER_NAME} does not exist"
    exit 1
fi

# Export environment variables
export_env_vars

# Print cluster information
log_info "Cluster Information:"
echo "------------------------"
kubectl cluster-info

# Print node status
log_info "Node Status:"
echo "------------------------"
kubectl get nodes -o wide

# Print namespace status
log_info "Namespace Status:"
echo "------------------------"
kubectl get namespaces

# Print pod status for important namespaces
important_namespaces=("kube-system" "monitoring" "opentelemetry-operator-system")
for ns in "${important_namespaces[@]}"; do
    if kubectl get namespace "$ns" &>/dev/null; then
        log_info "Pods in namespace: $ns"
        echo "------------------------"
        kubectl get pods -n "$ns"
        echo
    fi
done

# Print resource usage
log_info "Resource Usage:"
echo "------------------------"
kubectl top nodes 2>/dev/null || echo "Metrics not available"
echo

# Check component health
log_info "Component Health:"
echo "------------------------"

# Check API Server
if kubectl get --raw='/healthz' &>/dev/null; then
    log_info "API Server: Healthy"
else
    log_error "API Server: Unhealthy"
fi

# Check etcd
if kubectl get --raw='/healthz/etcd' &>/dev/null; then
    log_info "etcd: Healthy"
else
    log_error "etcd: Unhealthy"
fi

# Check CoreDNS
if kubectl get pods -n kube-system -l k8s-app=kube-dns --no-headers | grep -q "Running"; then
    log_info "CoreDNS: Healthy"
else
    log_error "CoreDNS: Unhealthy"
fi

# Print service endpoints
log_info "Service Endpoints:"
echo "------------------------"
echo "- Dashboard: http://localhost:30000"
echo "- Grafana: http://localhost:3000"
echo "- Prometheus: http://localhost:9090"
echo "- Jaeger UI: http://localhost:16686"

# Print persistent volume status
log_info "Persistent Volume Status:"
echo "------------------------"
kubectl get pv,pvc --all-namespaces

# Print events
log_info "Recent Events:"
echo "------------------------"
kubectl get events --all-namespaces --sort-by='.metadata.creationTimestamp' | tail -n 10 