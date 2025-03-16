#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Port configurations
declare -A services=(
    ["grafana"]="monitoring/svc/prometheus-grafana:3001:80"
    ["jaeger"]="observability/pod/jaeger-7d866889b-cch75:30686:16686"
    ["frontend"]="otel-demo/svc/frontend-proxy:8081:8080"
    ["boutique"]="boutique/svc/frontend-external:8082:80"
    ["sock-shop"]="sock-shop/svc/front-end:8083:80"
    ["bank-of-anthos"]="bank-of-anthos/svc/frontend:8084:80"
)

# Node IP for NodePort services
NODE_IP="172.18.0.2"  # k8s-labeler-dev-worker where Jaeger is running

check_port() {
    local port=$1
    if lsof -i :$port > /dev/null 2>&1; then
        return 0 # Port is in use
    else
        return 1 # Port is free
    fi
}

kill_port_forward() {
    local port=$1
    echo -e "${YELLOW}Killing processes using port $port...${NC}"
    # Kill any process using the port
    lsof -ti :$port | xargs -r kill -9
    # Kill any kubectl port-forward for this port specifically
    pkill -f "kubectl.*:$port"
}

setup_port_forward() {
    local service_name=$1
    local service_config=$2
    
    # Parse service configuration
    IFS=':' read -r namespace_path port target_port <<< "$service_config"
    IFS='/' read -r namespace resource_type resource_name <<< "$namespace_path"
    
    # Check if port is in use
    if check_port $port; then
        echo -e "${YELLOW}Port $port is in use. Cleaning up...${NC}"
        kill_port_forward $port
        sleep 2 # Wait for port to be released
    fi
    
    echo -e "${GREEN}Setting up port forward for $service_name...${NC}"
    kubectl port-forward --address 0.0.0.0 "$resource_type/$resource_name" "$port:$target_port" -n "$namespace" > /dev/null 2>&1 &
    
    # Wait a moment and verify
    sleep 2
    if check_port $port; then
        echo -e "${GREEN}✓ $service_name is accessible on port $port${NC}"
    else
        echo -e "${RED}✗ Failed to set up port forward for $service_name${NC}"
    fi
}

cleanup_all() {
    echo -e "${YELLOW}Cleaning up all port forwards...${NC}"
    for service_config in "${services[@]}"; do
        IFS=':' read -r _ port _ <<< "$service_config"
        kill_port_forward $port
    done
    sleep 2 # Wait for all ports to be released
}

setup_all() {
    cleanup_all
    echo -e "${GREEN}Setting up all port forwards...${NC}"
    for service_name in "${!services[@]}"; do
        setup_port_forward "$service_name" "${services[$service_name]}"
    done
}

# Main execution
case "${1:-}" in
    "cleanup")
        cleanup_all
        ;;
    "check")
        for service_name in "${!services[@]}"; do
            IFS=':' read -r _ port _ <<< "${services[$service_name]}"
            if check_port $port; then
                echo -e "${GREEN}✓ $service_name is accessible on port $port${NC}"
            else
                echo -e "${RED}✗ $service_name is not accessible on port $port${NC}"
            fi
        done
        ;;
    *)
        setup_all
        ;;
esac

echo -e "\n${GREEN}Service endpoints:${NC}"
echo -e "Grafana: http://localhost:3001"
echo -e "Jaeger:  http://localhost:30686"
echo -e "Frontend: http://localhost:8081"
echo -e "Boutique: http://localhost:8082"
echo -e "Sock Shop: http://localhost:8083"
echo -e "Bank of Anthos: http://localhost:8084" 