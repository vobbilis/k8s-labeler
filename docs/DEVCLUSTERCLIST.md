# Development Cluster Setup Checklist

## Status Overview
- [ ] Pre-flight Checks
- [ ] Cluster Creation and Basic Setup
- [ ] Observability Stack Deployment
- [ ] Sample Applications Deployment
- [ ] Verification Steps
- [ ] Load Generation
- [ ] Final Validation

## Detailed Checklist

### 1. Pre-flight Checks
- [x] Docker daemon running and healthy
  ```bash
  # Verified:
  - Docker version: 24.0.7
  - Status: Running
  - Resources: 12 CPUs, 7.662GiB Memory
  - Storage Driver: overlay2
  ```

- [x] Required tools installed and verified:
  - [x] Go >= 1.21 (Found: 1.24.0)
  - [x] kubectl >= 1.25 (Found: 1.30.9)
  - [x] kind >= 0.20 (Found: 0.27.0)
  - [x] helm >= 3.12 (Found: 3.13.3)
  ```bash
  # All tools verified and meet version requirements
  # No additional installations needed
  ```

- [x] System resources available:
  - [x] CPU: 4+ cores (Found: 12 cores)
  - [x] Memory: 8GB+ (Found: 31GB total with 153M unused)
  - [x] Disk: 20GB+ free space (Found: 545GB available)
  ```bash
  # System meets all resource requirements
  # Note: Memory usage is high, consider closing unnecessary applications
  ```

### Next Steps:
1. ✅ All pre-flight checks completed successfully
2. Ready to proceed with cluster creation
3. Begin with creating the kind cluster configuration file

### 2. Cluster Creation and Basic Setup

#### Development Cluster Directory Structure
```bash
dev-cluster/
├── config/           # Configuration files
│   ├── kind-config.yaml
│   ├── prometheus/   # Prometheus configuration
│   ├── grafana/      # Grafana dashboards and config
│   └── otel/         # OpenTelemetry collector config
├── tmp/             # Persistent storage for containers
└── manifests/       # Kubernetes manifests for sample apps
    ├── monitoring/
    ├── otel-demo/
    ├── boutique/
    ├── sock-shop/
    └── bank-of-anthos/
```

#### 2.1 Directory Setup
- [x] Create development cluster directory structure
  ```bash
  mkdir -p dev-cluster/{config,tmp,manifests}/{monitoring,otel-demo,boutique,sock-shop,bank-of-anthos}
  ```
- [x] Move kind configuration
  ```bash
  mv kind-config.yaml dev-cluster/config/
  ```
- [ ] Create .gitignore for temporary files
  ```bash
  echo "tmp/" >> dev-cluster/.gitignore
  echo "*.log" >> dev-cluster/.gitignore
  ```

#### 2.2 Cluster Creation
- [ ] Create kind cluster with proper configuration
  ```bash
  kind create cluster --config dev-cluster/config/kind-config.yaml
  ```
- [ ] Verify cluster health
  - [ ] Cluster info accessible
  - [ ] Nodes ready
  - [ ] Core services running
  ```bash
  kubectl cluster-info
  kubectl get nodes
  kubectl get pods -A
  ```

#### 2.3 Basic Setup
- [ ] Install OpenTelemetry Operator
  ```bash
  kubectl apply -f https://github.com/open-telemetry/opentelemetry-operator/releases/latest/download/opentelemetry-operator.yaml
  ```
- [ ] Verify operator installation
  ```bash
  kubectl get pods -n opentelemetry-operator-system
  kubectl get crds | grep opentelemetry
  ```

#### 2.4 Configuration Management
- [ ] Create configuration directories
  ```bash
  # Create directories for each component
  mkdir -p dev-cluster/config/{prometheus,grafana,otel}
  ```
- [ ] Download and customize configurations
  - [ ] Prometheus configuration
  - [ ] Grafana dashboards
  - [ ] OpenTelemetry collector config

#### 2.5 Persistent Storage
- [ ] Set up persistent storage directory
  ```bash
  # Ensure proper permissions
  chmod 777 dev-cluster/tmp
  ```
- [ ] Verify storage mounting
  ```bash
  # Check mount points in kind container
  docker exec k8s-labeler-dev-control-plane mount | grep containerd
  ```

### Notes:
- All development cluster artifacts will be contained in `dev-cluster/` directory
- Configuration files are version controlled (except secrets)
- Temporary files and logs are in .gitignore
- Each sample application has its own manifests directory
- Monitoring configurations are separated by component

### 3. Observability Stack Deployment
- [ ] Prometheus Stack
  - [ ] Namespace created
  - [ ] Pods running
  - [ ] Services accessible
  ```bash
  # Status:
  kubectl get pods -n monitoring
  ```

- [ ] Grafana
  - [ ] Deployment successful
  - [ ] Service accessible
  - [ ] Admin credentials secured
  ```bash
  # Credentials stored:
  # Username: admin
  # Password: [Insert after generation]
  ```

- [ ] Jaeger
  - [ ] Operator running
  - [ ] Instance deployed
  - [ ] UI accessible
  ```bash
  # Status:
  kubectl get pods -n observability
  ```

- [ ] OpenTelemetry Collector
  - [ ] Configuration applied
  - [ ] Pods running
  - [ ] Receiving data
  ```bash
  # Status:
  kubectl get pods -n monitoring | grep otel-collector
  ```

### 4. Sample Applications Deployment
- [ ] OpenTelemetry Demo
  - [ ] Namespace created
  - [ ] All pods running
  - [ ] Frontend accessible
  ```bash
  # Status:
  kubectl get pods -n otel-demo
  ```

- [ ] Online Boutique
  - [ ] All services deployed
  - [ ] Frontend accessible
  - [ ] OpenTelemetry instrumentation active
  ```bash
  # Status:
  kubectl get pods -n default
  ```

- [ ] Sock Shop
  - [ ] All components running
  - [ ] Frontend accessible
  - [ ] Telemetry flowing
  ```bash
  # Status:
  kubectl get pods -n sock-shop
  ```

- [ ] Bank of Anthos
  - [ ] Services deployed
  - [ ] Frontend accessible
  - [ ] Monitoring enabled
  ```bash
  # Status:
  kubectl get pods -n bank-of-anthos
  ```

### 5. Verification Steps
- [ ] Namespace verification
  ```bash
  # Expected namespaces:
  - monitoring
  - otel-demo
  - sock-shop
  - bank-of-anthos
  ```

- [ ] Pod status verification
  - [ ] All pods running
  - [ ] No crashlooping pods
  - [ ] Resource requests/limits set

- [ ] OpenTelemetry data flow
  - [ ] Metrics flowing
  - [ ] Traces visible
  - [ ] Logs collected

### 6. Load Generation
- [ ] OpenTelemetry Demo load generator active
- [ ] Online Boutique traffic simulation running
- [ ] Sock Shop load test executing
- [ ] Bank of Anthos synthetic transactions

### 7. Final Validation
- [ ] Resource usage within limits
  - [ ] Node resources
  - [ ] Pod resources
  - [ ] Network bandwidth

- [ ] Telemetry validation
  - [ ] Prometheus metrics
  - [ ] Jaeger traces
  - [ ] Grafana dashboards

- [ ] Application health
  - [ ] All frontends responding
  - [ ] Services communicating
  - [ ] Error rates acceptable

### Notes and Issues
```
# Add any issues encountered and their resolutions here
1. 
2. 
3. 
```

### Completion Status
- Start Date: [Insert Date]
- Completion Date: [Insert Date]
- Verified By: [Insert Name]

### Additional Tasks
- [ ] Document cluster access details
- [ ] Share monitoring dashboard URLs
- [ ] Record baseline performance metrics
- [ ] Create backup of working configuration 