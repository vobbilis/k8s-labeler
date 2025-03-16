#!/bin/bash

# Source utility functions
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "${SCRIPT_DIR}/utils.sh"

# Constants
CLUSTER_NAME="k8s-labeler-dev"
MONITORING_NAMESPACE="monitoring"
OBSERVABILITY_NAMESPACE="observability"
OTEL_DEMO_NAMESPACE="otel-demo"

# Required tool versions
MIN_GO_VERSION="1.21"
MIN_KUBECTL_VERSION="1.25"
MIN_KIND_VERSION="0.20"
MIN_HELM_VERSION="3.12"

# Resource requirements
MIN_CPU_CORES=4
MIN_MEMORY_GB=8
MIN_DISK_GB=15

# Function to compare versions
version_gt() {
    # $1 is the required version, $2 is the actual version
    local IFS=.
    local i ver1=($1) ver2=($2)
    # fill empty fields in ver1 with zeros
    for ((i=${#ver2[@]}; i<${#ver1[@]}; i++)); do
        ver2[i]=0
    done
    # fill empty fields in ver2 with zeros
    for ((i=${#ver1[@]}; i<${#ver2[@]}; i++)); do
        ver1[i]=0
    done
    # compare version numbers
    for ((i=0; i<${#ver1[@]}; i++)); do
        if [[ -z ${ver2[i]} ]]; then
            ver2[i]=0
        fi
        if ((10#${ver1[i]} > 10#${ver2[i]})); then
            return 0
        fi
        if ((10#${ver1[i]} < 10#${ver2[i]})); then
            return 1
        fi
    done
    return 1
}

# Function to extract version number
extract_version() {
    echo "$1" | grep -oE '[0-9]+\.[0-9]+(\.[0-9]+)?'
}

# Function to check system resources
check_system_resources() {
    echo "Checking system resources..."
    local errors=0

    # Check CPU cores
    local cpu_cores=$(nproc)
    if [ "${cpu_cores}" -lt "${MIN_CPU_CORES}" ]; then
        echo "❌ Insufficient CPU cores: ${cpu_cores} (minimum: ${MIN_CPU_CORES})"
        errors=$((errors + 1))
    else
        echo "✅ CPU cores: ${cpu_cores}"
    fi

    # Check memory
    local total_memory_kb=$(grep MemTotal /proc/meminfo | awk '{print $2}')
    local total_memory_gb=$((total_memory_kb / 1024 / 1024))
    if [ "${total_memory_gb}" -lt "${MIN_MEMORY_GB}" ]; then
        echo "❌ Insufficient memory: ${total_memory_gb}GB (minimum: ${MIN_MEMORY_GB}GB)"
        errors=$((errors + 1))
    else
        echo "✅ Memory: ${total_memory_gb}GB"
    fi

    # Check disk space
    local disk_space_gb=$(df -BG "${SCRIPT_DIR}" | awk 'NR==2 {print $4}' | tr -d 'G')
    if [ "${disk_space_gb}" -lt "${MIN_DISK_GB}" ]; then
        echo "❌ Insufficient disk space: ${disk_space_gb}GB (minimum: ${MIN_DISK_GB}GB)"
        errors=$((errors + 1))
    else
        echo "✅ Disk space: ${disk_space_gb}GB"
    fi

    return ${errors}
}

# Function to check required tools and versions
check_required_tools() {
    echo "Checking required tools..."
    local errors=0

    # Check Docker
    if ! docker info &>/dev/null; then
        echo "❌ Docker daemon is not running"
        errors=$((errors + 1))
    else
        echo "✅ Docker daemon is running"
    fi

    # Check Go
    if ! command -v go &>/dev/null; then
        echo "❌ Go is not installed"
        errors=$((errors + 1))
    else
        local go_version=$(extract_version "$(go version)")
        if version_gt "${MIN_GO_VERSION}" "${go_version}"; then
            echo "❌ Go version ${go_version} is older than required ${MIN_GO_VERSION}"
            errors=$((errors + 1))
        else
            echo "✅ Go version ${go_version}"
        fi
    fi

    # Check kubectl
    if ! command -v kubectl &>/dev/null; then
        echo "❌ kubectl is not installed"
        errors=$((errors + 1))
    else
        local kubectl_version=$(extract_version "$(kubectl version --client -o yaml | grep -i gitVersion)")
        if version_gt "${MIN_KUBECTL_VERSION}" "${kubectl_version}"; then
            echo "❌ kubectl version ${kubectl_version} is older than required ${MIN_KUBECTL_VERSION}"
            errors=$((errors + 1))
        else
            echo "✅ kubectl version ${kubectl_version}"
        fi
    fi

    # Check kind
    if ! command -v kind &>/dev/null; then
        echo "❌ kind is not installed"
        errors=$((errors + 1))
    else
        local kind_version=$(extract_version "$(kind version)")
        if version_gt "${MIN_KIND_VERSION}" "${kind_version}"; then
            echo "❌ kind version ${kind_version} is older than required ${MIN_KIND_VERSION}"
            errors=$((errors + 1))
        else
            echo "✅ kind version ${kind_version}"
        fi
    fi

    # Check helm
    if ! command -v helm &>/dev/null; then
        echo "❌ helm is not installed"
        errors=$((errors + 1))
    else
        local helm_version=$(extract_version "$(helm version)")
        if version_gt "${MIN_HELM_VERSION}" "${helm_version}"; then
            echo "❌ helm version ${helm_version} is older than required ${MIN_HELM_VERSION}"
            errors=$((errors + 1))
        else
            echo "✅ helm version ${helm_version}"
        fi
    fi

    return ${errors}
}

# Function to check port availability
check_port_availability() {
    echo "Checking port availability..."
    local errors=0
    local ports=(3001 30686 8081)

    for port in "${ports[@]}"; do
        if ss -tuln | grep -q ":${port} "; then
            echo "❌ Port ${port} is already in use"
            errors=$((errors + 1))
        else
            echo "✅ Port ${port} is available"
        fi
    done

    return ${errors}
}

# Function to run all pre-flight checks
run_preflight_checks() {
    echo "Running pre-flight checks..."
    echo "=========================="
    local total_errors=0

    echo -e "\n1. System Resources"
    echo "----------------"
    check_system_resources
    total_errors=$((total_errors + $?))

    echo -e "\n2. Required Tools"
    echo "---------------"
    check_required_tools
    total_errors=$((total_errors + $?))

    echo -e "\n3. Port Availability"
    echo "------------------"
    check_port_availability
    total_errors=$((total_errors + $?))

    echo -e "\nPre-flight check summary:"
    if [ ${total_errors} -eq 0 ]; then
        echo "✅ All checks passed successfully!"
        return 0
    else
        echo "❌ Found ${total_errors} issue(s) that need to be resolved"
        return 1
    fi
}

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

# Function to check cluster and component status
check_status() {
    echo "Checking development environment status..."
    echo "----------------------------------------"

    # Check cluster status
    echo "1. Cluster Status:"
    if kind get clusters | grep -q "^${CLUSTER_NAME}$"; then
        echo "✅ Kind cluster '${CLUSTER_NAME}' is running"
        
        # Check node status
        echo -e "\nNode Status:"
        kubectl get nodes -o wide
    else
        echo "❌ Kind cluster '${CLUSTER_NAME}' is not running"
        return 1
    fi

    # Check Helm repositories
    echo -e "\n2. Helm Repositories:"
    local repos=("prometheus-community" "jaegertracing" "open-telemetry")
    for repo in "${repos[@]}"; do
        if helm repo list | grep -q "^${repo}"; then
            echo "✅ ${repo} repository is configured"
        else
            echo "❌ ${repo} repository is missing"
        fi
    done

    # Check namespace status
    echo -e "\n3. Namespace Status:"
    local namespaces=("${MONITORING_NAMESPACE}" "${OBSERVABILITY_NAMESPACE}" "${OTEL_DEMO_NAMESPACE}")
    for ns in "${namespaces[@]}"; do
        if kubectl get namespace "${ns}" &> /dev/null; then
            echo "✅ Namespace ${ns} exists"
        else
            echo "❌ Namespace ${ns} is missing"
        fi
    done

    # Check Helm releases
    echo -e "\n4. Helm Releases:"
    local releases=(
        "prometheus:${MONITORING_NAMESPACE}"
        "jaeger:${OBSERVABILITY_NAMESPACE}"
        "otel-demo:${OTEL_DEMO_NAMESPACE}"
    )
    for release in "${releases[@]}"; do
        local name="${release%%:*}"
        local namespace="${release#*:}"
        if helm status "${name}" -n "${namespace}" &> /dev/null; then
            echo "✅ ${name} is deployed in ${namespace}"
        else
            echo "❌ ${name} is not deployed in ${namespace}"
        fi
    done

    # Check pod status in each namespace
    echo -e "\n5. Pod Status:"
    for ns in "${namespaces[@]}"; do
        echo -e "\nNamespace: ${ns}"
        kubectl get pods -n "${ns}" -o wide
    done

    # Check port forwards
    echo -e "\n6. Port Forward Status:"
    local ports=("3001:Grafana" "30686:Jaeger" "8081:Frontend")
    for port in "${ports[@]}"; do
        local port_number="${port%%:*}"
        local service="${port#*:}"
        if ss -tuln | grep -q ":${port_number} "; then
            echo "✅ ${service} port forward is active (${port_number})"
        else
            echo "❌ ${service} port forward is not active (${port_number})"
        fi
    done

    # Print resource usage
    echo -e "\n7. Resource Usage:"
    echo "Node Resource Usage:"
    kubectl top nodes 2>/dev/null || echo "❌ Metrics not available (metrics-server may not be ready)"
    
    echo -e "\nPod Resource Usage (Top 10):"
    kubectl top pods -A --sort-by=cpu 2>/dev/null | head -n 10 || echo "❌ Metrics not available"

    echo -e "\nDevelopment environment status check complete!"
}

# Function to print usage
print_usage() {
    echo "Usage: $0 [command]"
    echo "Commands:"
    echo "  setup     Set up the development environment (default)"
    echo "  status    Check the status of the development environment"
    echo "  preflight Run pre-flight checks only"
    echo "  help      Show this help message"
}

# Main setup function
setup_environment() {
    echo "Starting development environment setup..."

    # Run pre-flight checks first
    if ! run_preflight_checks; then
        echo "❌ Pre-flight checks failed. Please resolve the issues and try again."
        exit 1
    fi

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
- $0 status

To stop the environment:
- ./stop-cluster.sh
"
}

# Main function
main() {
    local command="${1:-setup}"

    case "${command}" in
        setup)
            setup_environment
            ;;
        status)
            check_status
            ;;
        preflight)
            run_preflight_checks
            ;;
        help)
            print_usage
            ;;
        *)
            echo "Error: Unknown command '${command}'"
            print_usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@" 