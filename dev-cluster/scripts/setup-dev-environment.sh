#!/bin/bash

# Source utility functions
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "${SCRIPT_DIR}/utils.sh"

# Constants
CLUSTER_NAME="k8s-labeler"
MONITORING_NAMESPACE="monitoring"
OBSERVABILITY_NAMESPACE="observability"
OTEL_DEMO_NAMESPACE="otel-demo"

# Function to check if a Helm repository exists
check_helm_repo() {
    local repo_name="$1"
    local repo_url="$2"
    if ! helm repo list | grep -q "^${repo_name}"; then
        echo "Adding Helm repository ${repo_name}..."
        helm repo add "${repo_name}" "${repo_url}"
    fi
}

# Function to create namespace if it doesn't exist
create_namespace() {
    local namespace="$1"
    if ! kubectl get namespace "${namespace}" &> /dev/null; then
        echo "Creating namespace ${namespace}..."
        kubectl create namespace "${namespace}"
    fi
}

# Function to wait for pods in a namespace to be ready
wait_for_pods() {
    local namespace="$1"
    local timeout="300s"  # 5 minutes timeout
    echo "Waiting for pods in namespace ${namespace} to be ready..."
    kubectl wait --for=condition=Ready pods --all -n "${namespace}" --timeout="${timeout}" || {
        echo "Warning: Not all pods are ready in namespace ${namespace} after ${timeout}"
        kubectl get pods -n "${namespace}"
    }
}

# Main setup function
main() {
    echo "Starting development environment setup..."

    # 1. Create Kind cluster if it doesn't exist
    if ! kind get clusters | grep -q "^${CLUSTER_NAME}$"; then
        echo "Creating Kind cluster..."
        kind create cluster --name "${CLUSTER_NAME}" --config "${SCRIPT_DIR}/../config/kind-config.yaml"
    else
        echo "Cluster ${CLUSTER_NAME} already exists"
    fi

    # 2. Add required Helm repositories
    check_helm_repo "prometheus-community" "https://prometheus-community.github.io/helm-charts"
    check_helm_repo "jaegertracing" "https://jaegertracing.github.io/helm-charts"
    check_helm_repo "open-telemetry" "https://open-telemetry.github.io/opentelemetry-helm-charts"
    helm repo update

    # 3. Create required namespaces
    create_namespace "${MONITORING_NAMESPACE}"
    create_namespace "${OBSERVABILITY_NAMESPACE}"
    create_namespace "${OTEL_DEMO_NAMESPACE}"

    # 4. Deploy Prometheus Stack
    echo "Deploying Prometheus Stack..."
    helm upgrade --install prometheus prometheus-community/kube-prometheus-stack \
        --namespace "${MONITORING_NAMESPACE}" \
        --create-namespace \
        --values "${SCRIPT_DIR}/../config/prometheus/values.yaml" \
        --wait

    # 5. Deploy Jaeger
    echo "Deploying Jaeger..."
    helm upgrade --install jaeger jaegertracing/jaeger \
        --namespace "${OBSERVABILITY_NAMESPACE}" \
        --create-namespace \
        --values "${SCRIPT_DIR}/../config/jaeger-values.yaml" \
        --wait

    # 6. Deploy OpenTelemetry Demo
    echo "Deploying OpenTelemetry Demo..."
    helm upgrade --install otel-demo open-telemetry/opentelemetry-demo \
        --namespace "${OTEL_DEMO_NAMESPACE}" \
        --create-namespace \
        --set default.replicas=1 \
        --set serviceAccount.create=true \
        --values "${SCRIPT_DIR}/../config/otel-demo/values.yaml" \
        --wait

    # 7. Wait for all pods to be ready
    wait_for_pods "${MONITORING_NAMESPACE}"
    wait_for_pods "${OBSERVABILITY_NAMESPACE}"
    wait_for_pods "${OTEL_DEMO_NAMESPACE}"

    # 8. Set up port forwarding
    echo "Setting up port forwarding..."
    "${SCRIPT_DIR}/manage-port-forwards.sh" start

    # 9. Print access information
    echo "
Development environment setup complete!

Access URLs:
- Grafana: http://localhost:3001 (default credentials: admin/prom-operator)
- Jaeger UI: http://localhost:30686
- Frontend UI: http://localhost:8081

To manage port forwarding:
- Start: ./manage-port-forwards.sh start
- Stop: ./manage-port-forwards.sh stop
- Status: ./manage-port-forwards.sh status

To check cluster status:
- ./cluster-status.sh

To stop the environment:
- ./stop-cluster.sh
"
}

# Run main function
main "$@" 