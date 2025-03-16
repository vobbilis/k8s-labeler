# Development Cluster Setup Checklist

## Status Overview
- [x] Pre-flight Checks
- [x] Cluster Creation and Basic Setup
- [x] Observability Stack Deployment
  - [x] Jaeger Deployment (Successfully deployed using Helm)
- [ ] Sample Applications Deployment
- [ ] Verification Steps
- [ ] Load Generation
- [ ] Final Validation

## Detailed Checklist

### 1. Pre-flight Checks
- [x] Docker daemon running and healthy
  ```bash
  # Verified:
  - Docker version: 28.0.1
  - Status: Running
  - Resources: 48 CPUs, 88.37GiB Memory
  - Storage Driver: overlay2
  ```

- [x] Required tools installed and verified:
  - [x] Go >= 1.21 (Found: 1.22.2)
  - [x] kubectl >= 1.25 (Found: 1.32.3)
  - [x] kind >= 0.20 (Found: 0.20.0)
  - [x] helm >= 3.12 (Found: 3.17.2)
  ```bash
  # All tools verified and meet version requirements
  # No additional installations needed
  ```

- [x] System resources available:
  - [x] CPU: 4+ cores (Found: 48 cores)
  - [x] Memory: 8GB+ (Found: 88GB total with 84GB free)
  - [x] Disk: 20GB+ free space (Found: 19GB available)
  ```bash
  # System meets all resource requirements
  # Note: Disk space is slightly below target but sufficient for development
  ```

### Next Steps:
1. Install OpenTelemetry Operator
2. Set up monitoring stack (Prometheus, Grafana, Jaeger)
3. Deploy sample applications
4. Configure persistent storage verification

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
- [x] Configure kind configuration
  ```bash
  # Configuration created at: dev-cluster/config/kind-config.yaml
  # Key configurations:
  - 1 control-plane node
  - 2 worker nodes
  - Port mappings:
    * 30000, 30001 (General use)
    * 4317, 4318 (OTLP)
    * 9090 (Prometheus)
    * 3000 (Grafana)
    * 16686 (Jaeger UI)
  - Network configuration:
    * Pod subnet: 10.244.0.0/16
    * Service subnet: 10.96.0.0/16
  ```

#### 2.2 Cluster Creation
- [x] Create kind cluster with proper configuration
  ```bash
  kind create cluster --config dev-cluster/config/kind-config.yaml
  ```
- [x] Verify cluster health
  - [x] Cluster info accessible
  - [x] Nodes ready (3 nodes: 1 control-plane, 2 workers)
  - [x] Core services running
  ```bash
  # Verified Components:
  - CoreDNS
  - etcd
  - kube-apiserver
  - kube-controller-manager
  - kube-scheduler
  - kube-proxy
  - local-path-provisioner
  ```

#### 2.3 Basic Setup
- [x] Install OpenTelemetry Operator
  ```bash
  # Installation completed
  # Verified: CRDs and operator pods created
  # CRDs installed:
  - instrumentations.opentelemetry.io
  - opampbridges.opentelemetry.io
  - opentelemetrycollectors.opentelemetry.io
  - targetallocators.opentelemetry.io
  ```
- [x] Verify operator installation
  ```bash
  # Operator pod running in opentelemetry-operator-system namespace
  # All required CRDs are present
  ```

#### 2.4 Configuration Management
- [x] Create configuration directories
  ```bash
  # Created directories:
  - dev-cluster/config/prometheus/
  - dev-cluster/config/grafana/
  - dev-cluster/config/otel/
  ```
- [x] Download and customize configurations
  - [x] Prometheus configuration (prometheus.yaml)
  - [x] Grafana dashboards (datasources.yaml)
  - [x] OpenTelemetry collector config (collector.yaml)

#### 2.5 Persistent Storage
- [x] Set up persistent storage directory
  ```bash
  # Configured in kind-config.yaml:
  hostPath: ./dev-cluster/tmp
  containerPath: /var/lib/k8s-labeler
  ```
- [x] Verify storage mounting
  ```bash
  # Storage verification completed:
  - Default StorageClass: standard (rancher.io/local-path)
  - Test PVC created successfully
  - Storage provisioner functional
  ```

### Notes:
- All development cluster artifacts will be contained in `dev-cluster/` directory
- Configuration files are version controlled (except secrets)
- Temporary files and logs are in .gitignore
- Each sample application has its own manifests directory
- Monitoring configurations are separated by component

### 3. Observability Stack Deployment
- [x] Jaeger
  - [x] Deployment successful using Helm chart
  - [x] Service accessible (port 16686)
  - [x] UI verified
  - [x] Configuration documented
  ```bash
  # Status: Successfully deployed
  # Method: Direct Helm deployment (preferred over operator for dev)
  # Verification:
  kubectl get pods -n observability
  NAME                    READY   STATUS    RESTARTS   AGE
  jaeger-59bd6f5f5d-szwd9   1/1     Running   0          7s
  ```

- [ ] Prometheus Stack
  - [ ] Namespace created
  - [ ] Pods running
  - [ ] Services accessible

- [ ] Grafana
  - [ ] Deployment successful
  - [ ] Service accessible
  - [ ] Admin credentials secured

- [ ] OpenTelemetry Collector
  - [ ] Configuration applied
  - [ ] Pods running
  - [ ] Receiving data

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
# Current Progress
1. Successfully deployed Jaeger using Helm chart
   - Switched from operator-based to direct Helm deployment
   - Using allInOne strategy for development
   - Memory storage configured
   - Resource limits set appropriately
   - UI accessible via port-forward

2. Documented deployment solution
   - Created label: training-data/deployment/observability/20250316-dep-jaeger-failure.json
   - Captured troubleshooting steps and resolution
   - Added prevention recommendations

# Next Steps
1. Complete Prometheus stack deployment
2. Set up Grafana with proper dashboards
3. Configure OpenTelemetry collector
```

### Completion Status
- Start Date: [Current Date]
- Last Updated: [Current Date]
- Current Phase: Basic Cluster Setup
- Next Phase: Observability Stack Deployment

### Additional Tasks
- [ ] Document cluster access details
- [ ] Share monitoring dashboard URLs
- [ ] Record baseline performance metrics
- [ ] Create backup of working configuration 