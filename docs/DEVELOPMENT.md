# Development Guide: K8s-Labeler

## Table of Contents
1. [Development Setup](#development-setup)
2. [Project Structure](#project-structure)
3. [Development Workflow](#development-workflow)
4. [Testing Guidelines](#testing-guidelines)
5. [Code Style and Standards](#code-style-and-standards)
6. [Building and Running](#building-and-running)
7. [Debugging](#debugging)
8. [Contributing](#contributing)

## Development Setup

### Prerequisites

#### Required Tools
```bash
# Core requirements
go >= 1.21
kubectl >= 1.25
docker >= 24.0
kind >= 0.20 (for local development)

# Additional tools
helm >= 3.12
kustomize >= 5.0
golangci-lint >= 1.54
delve >= 1.21 (for debugging)
```

#### Environment Setup
1. **Go Environment**
```bash
# Set GOPATH and add to PATH
export GOPATH=$HOME/go
export PATH=$PATH:$GOPATH/bin

# Enable Go modules
export GO111MODULE=on

# Set private repo access (if needed)
git config --global url."ssh://git@github.com/".insteadOf "https://github.com/"
```

2. **Docker Configuration**
```bash
# Ensure Docker daemon is running
systemctl status docker

# Configure Docker for local registry
cat << EOF > /etc/docker/daemon.json
{
  "insecure-registries" : ["localhost:5000"],
  "debug" : true,
  "experimental" : true
}
EOF

# Restart Docker daemon
systemctl restart docker
```

3. **Kubernetes Tools**
```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# Install kind
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
chmod +x kind
sudo mv kind /usr/local/bin/
```

### Initial Setup

The project uses a script-based approach to manage the local development cluster. All cluster management operations are handled through scripts in the `dev-cluster/scripts` directory.

1. **Initial Setup**
```bash
# Create development cluster directory structure
mkdir -p dev-cluster/{config,logs,scripts,tmp,manifests}

# Make management scripts executable
chmod +x dev-cluster/scripts/*.sh
```

2. **Cluster Lifecycle Management**
```bash
# Start the development cluster
./dev-cluster/scripts/start-cluster.sh

# Check cluster status
./dev-cluster/scripts/cluster-status.sh

# Stop the cluster and save logs
./dev-cluster/scripts/stop-cluster.sh
```

3. **Sample Applications**
The `start-cluster.sh` script automatically deploys the following sample applications:
- OpenTelemetry Demo
- Online Boutique (Microservices Demo)
- Sock Shop
- Bank of Anthos

Each application is deployed with OpenTelemetry instrumentation and proper monitoring configuration.

4. **Monitoring Stack**
The cluster comes pre-configured with:
- Prometheus for metrics collection
- Grafana for visualization
- Jaeger for distributed tracing
- OpenTelemetry Collector for telemetry processing

Access the monitoring stack through:
- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090
- Jaeger UI: http://localhost:16686

5. **Logs and Debugging**
```bash
# View cluster status and health
./dev-cluster/scripts/cluster-status.sh

# Access logs directory
cd dev-cluster/logs/$(ls -t dev-cluster/logs | head -1)

# View specific component logs
less kube-system/kube-apiserver.log
```

6. **Common Operations**
```bash
# Restart the cluster
./dev-cluster/scripts/stop-cluster.sh
./dev-cluster/scripts/start-cluster.sh

# Check component health
./dev-cluster/scripts/cluster-status.sh

# View real-time logs
kubectl logs -f -n <namespace> <pod-name>
```

7. **Troubleshooting**
If you encounter issues:
1. Check cluster status using `cluster-status.sh`
2. Review logs in `dev-cluster/logs/`
3. Verify Docker resources and system requirements
4. Ensure no port conflicts with required services
5. Check the troubleshooting section in this document

### Sample Applications Deployment

1. **OpenTelemetry Demo Application**
```bash
# Add OpenTelemetry Helm repository
helm repo add open-telemetry https://open-telemetry.github.io/opentelemetry-helm-charts

# Deploy OpenTelemetry Demo
helm install otel-demo open-telemetry/opentelemetry-demo \
  --namespace otel-demo \
  --create-namespace \
  --set collector.mode=deployment

# Verify deployment
kubectl get pods -n otel-demo
```

2. **Microservices-Demo (Online Boutique)**
```bash
# Clone the repository
git clone https://github.com/GoogleCloudPlatform/microservices-demo.git
cd microservices-demo

# Deploy with OpenTelemetry instrumentation
kubectl apply -f ./release/kubernetes-manifests.yaml
kubectl apply -f ./release/opentelemetry-manifests.yaml

# Verify deployment
kubectl get pods -n default
```

3. **Sock Shop**
```bash
# Clone the repository
git clone https://github.com/microservices-demo/microservices-demo.git sock-shop
cd sock-shop

# Deploy application
kubectl apply -f deploy/kubernetes/complete-demo.yaml

# Apply OpenTelemetry instrumentation
kubectl apply -f deploy/kubernetes/otel-instrumentation.yaml

# Verify deployment
kubectl get pods -n sock-shop
```

4. **Bank of Anthos**
```bash
# Clone the repository
git clone https://github.com/GoogleCloudPlatform/bank-of-anthos.git
cd bank-of-anthos

# Deploy with OpenTelemetry
kubectl apply -f ./kubernetes-manifests
kubectl apply -f ./extras/opentelemetry

# Verify deployment
kubectl get pods -n bank-of-anthos
```

### Sample Applications Overview

1. **OpenTelemetry Demo**
   - Multi-service application with built-in telemetry
   - Services in multiple languages (Go, Python, Node.js, Java)
   - Complete observability signals (traces, metrics, logs)
   - Simulated user and system load

2. **Online Boutique**
   - 10+ microservices in different languages
   - Real-world e-commerce scenarios
   - gRPC communication
   - Cloud-native patterns

3. **Sock Shop**
   - Classic microservices demo
   - Mix of synchronous and asynchronous communication
   - Multiple databases (MongoDB, MySQL)
   - Service mesh integration

4. **Bank of Anthos**
   - Financial services simulation
   - Python and Java microservices
   - REST API communication
   - Kubernetes-native security patterns

### Development Cluster Checklist

#### 1. Pre-flight Checks
- [ ] Docker daemon running and healthy
  ```bash
  docker info
  ```
- [ ] Required tools installed and verified:
  ```bash
  go version        # >= 1.21
  kubectl version   # >= 1.25
  kind version      # >= 0.20
  helm version      # >= 3.12
  ```
- [ ] Sufficient system resources:
  ```bash
  # Minimum requirements
  CPU: 4 cores
  Memory: 8GB
  Disk: 20GB free space
  ```

#### 2. Cluster Creation and Basic Setup

#### Development Cluster Directory Structure
```bash
dev-cluster/
├── config/           # Configuration files
│   ├── kind-config.yaml
│   ├── prometheus/   # Prometheus configuration
│   ├── grafana/      # Grafana dashboards and config
│   └── otel/         # OpenTelemetry collector config
├── logs/            # Cluster and component logs
├── scripts/         # Cluster management scripts
│   ├── utils.sh     # Common utilities and functions
│   ├── start-cluster.sh
│   ├── stop-cluster.sh
│   └── cluster-status.sh
├── tmp/             # Persistent storage for containers
└── manifests/       # Kubernetes manifests for sample apps
    ├── monitoring/
    ├── otel-demo/
    ├── boutique/
    ├── sock-shop/
    └── bank-of-anthos/
```

#### Cluster Management Scripts

The development cluster is managed through a set of shell scripts located in `dev-cluster/scripts/`:

1. **utils.sh** - Common utilities and functions
   - Logging functions with color output
   - Health check functions
   - Pod readiness checks
   - Environment variable management
   ```bash
   # Example utility functions
   log_info "Information message"
   log_warn "Warning message"
   log_error "Error message"
   check_cluster_health
   wait_for_pods "namespace-name"
   ```

2. **start-cluster.sh** - Cluster creation and initialization
   - Verifies required tools (kind, kubectl, helm)
   - Creates the kind cluster if it doesn't exist
   - Sets up OpenTelemetry Operator
   - Configures Helm repositories
   - Performs health checks
   ```bash
   # Start the development cluster
   ./dev-cluster/scripts/start-cluster.sh
   ```

3. **stop-cluster.sh** - Graceful cluster shutdown
   - Saves important logs before shutdown
   - Archives pod logs from critical namespaces
   - Saves cluster state information
   - Removes the cluster
   - Cleans up environment variables
   ```bash
   # Stop the development cluster
   ./dev-cluster/scripts/stop-cluster.sh
   ```

4. **cluster-status.sh** - Comprehensive status checking
   - Cluster information and health
   - Node status
   - Namespace status
   - Component health checks
   - Resource usage
   - Service endpoints
   - Recent events
   ```bash
   # Check cluster status
   ./dev-cluster/scripts/cluster-status.sh
   ```

#### Script Features

1. **Logging and Monitoring**
   - Colored output for different message types
   - Detailed component health checks
   - Resource usage monitoring
   - Event tracking

2. **Error Handling**
   - Graceful failure handling
   - Detailed error messages
   - Timeout management for operations
   - State validation

3. **Data Persistence**
   - Log archiving before cluster shutdown
   - Persistent storage configuration
   - State preservation between restarts

4. **Health Checks**
   - API server health
   - etcd status
   - CoreDNS functionality
   - Pod readiness
   - Node status

#### Using the Scripts

1. **Initial Setup**
   ```bash
   # Make scripts executable
   chmod +x dev-cluster/scripts/*.sh
   ```

2. **Cluster Lifecycle**
   ```bash
   # Start cluster
   ./dev-cluster/scripts/start-cluster.sh

   # Check status
   ./dev-cluster/scripts/cluster-status.sh

   # Stop cluster
   ./dev-cluster/scripts/stop-cluster.sh
   ```

3. **Accessing Services**
   After cluster startup, the following endpoints are available:
   - Dashboard: http://localhost:30000
   - Grafana: http://localhost:3000
   - Prometheus: http://localhost:9090
   - Jaeger UI: http://localhost:16686

4. **Log Management**
   - Logs are saved in `dev-cluster/logs/` with timestamp-based directories
   - Each namespace's logs are organized in separate subdirectories
   - Cluster state is preserved in JSON format
   ```bash
   # Log directory structure
   dev-cluster/logs/YYYYMMDD_HHMMSS/
   ├── cluster-info.txt
   ├── resources.txt
   ├── kube-system/
   ├── monitoring/
   └── opentelemetry-operator-system/
   ```

#### Troubleshooting

1. **Common Issues**
   - If cluster creation fails, check Docker resources
   - For port conflicts, verify no other services use required ports
   - If pods fail to start, check logs using cluster-status.sh

2. **Debug Commands**
   ```bash
   # Check cluster existence
   kind get clusters

   # Verify environment
   echo $KUBECONFIG

   # Check component logs
   kubectl logs -n namespace pod-name
   ```

3. **Recovery Steps**
   - For cluster issues: Stop and restart the cluster
   - For component issues: Check specific component logs
   - For persistent issues: Check the archived logs

### Development Environment Configuration

a. **Local Configuration**
```bash
# Copy and customize configuration
cp config/example.yaml config/dev.yaml

# Set up environment variables
cat << EOF > .env.development
KUBERNETES_CONTEXT=kind-k8s-labeler-dev
LOG_LEVEL=debug
METRICS_PORT=9090
API_PORT=8080
EOF
```

b. **IDE Setup (VS Code)**
```json
// .vscode/settings.json
{
    "go.lintTool": "golangci-lint",
    "go.lintFlags": ["--fast"],
    "go.testFlags": ["-v", "-race"],
    "go.buildFlags": ["-tags=development"],
    "go.delveConfig": {
        "dlvLoadConfig": {
            "followPointers": true,
            "maxVariableRecurse": 1,
            "maxStringLen": 500,
            "maxArrayValues": 500
        }
    }
}
```

### Verification Steps

1. **Build and Test**
```bash
# Build project
make build

# Run tests
make test

# Check code quality
make lint
```

2. **Local Deployment**
```bash
# Deploy to local cluster
make deploy-local

# Verify deployment
kubectl get pods -n k8s-labeler
```

3. **Access Services**
```bash
# Port forward API service
kubectl port-forward svc/k8s-labeler-api 8080:8080 -n k8s-labeler

# Test API endpoint
curl http://localhost:8080/api/v1/health
```

### Troubleshooting

1. **Common Issues**

a. **Go Module Issues**
```bash
# Clear module cache
go clean -modcache

# Verify and tidy dependencies
go mod verify
go mod tidy
```

b. **Kubernetes Connection Issues**
```bash
# Check cluster status
kubectl get nodes
kubectl cluster-info

# Reset kind cluster
kind delete cluster --name k8s-labeler-dev
kind create cluster --name k8s-labeler-dev --config kind-config.yaml
```

c. **Build Issues**
```bash
# Clean build artifacts
make clean

# Rebuild with verbose output
make build-verbose
```

2. **Development Tools**

a. **Debugging Tools**
```bash
# Install/update Delve
go install github.com/go-delve/delve/cmd/dlv@latest

# Debug binary
dlv debug ./cmd/controller/main.go
```

b. **Linting Tools**
```bash
# Update golangci-lint
curl -sSfL https://raw.githubusercontent.com/golangci/golangci-lint/master/install.sh | sh -s -- -b $(go env GOPATH)/bin

# Run specific linters
golangci-lint run --disable-all --enable=gofmt,golint,govet
```

### Next Steps

After completing the setup:
1. Review the [Architecture Document](./ARCHITECTURE.md)
2. Explore the [Technical Design](./TECHNICAL_DESIGN.md)
3. Check [Examples](../examples/) directory
4. Start with a small feature implementation

## Project Structure
```
k8s-labeler/
├── cmd/                    # Command-line entry points
│   ├── controller/        # Main controller binary
│   └── cli/              # CLI tool
├── pkg/
│   ├── types/            # Core type definitions
│   ├── watchers/         # K8s resource watchers
│   ├── collectors/       # Metric and log collectors
│   ├── processors/       # Event processing pipeline
│   ├── generator/        # Label generation engine
│   ├── storage/          # Data persistence layer
│   ├── api/             # REST API implementation
│   └── utils/           # Common utilities
├── internal/             # Internal packages
├── test/                # Test files and test utilities
├── deploy/              # Deployment manifests
├── docs/                # Documentation
└── examples/            # Example configurations and usage
```

## Development Workflow

### 1. Branch Management
```
main           # Stable release branch
├── develop    # Development branch
└── feature/*  # Feature branches
```

### 2. Development Process
1. Create feature branch:
```bash
git checkout -b feature/your-feature-name
```

2. Implement changes following TDD:
   - Write tests first
   - Implement functionality
   - Ensure tests pass
   - Update documentation

3. Submit PR:
   - Rebase on develop
   - Ensure CI passes
   - Get code review
   - Merge after approval

## Testing Guidelines

### 1. Unit Tests
```go
// Example test structure
func TestLabelGenerator_GenerateLabels(t *testing.T) {
    tests := []struct {
        name    string
        event   *AnalyzedEvent
        want    []Label
        wantErr bool
    }{
        // Test cases
    }
    
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            // Test implementation
        })
    }
}
```

### 2. Integration Tests
- Located in `test/integration/`
- Requires running K8s cluster
- Tests full workflow

### 3. Running Tests
```bash
# Run unit tests
make test

# Run integration tests
make integration-test

# Run all tests with coverage
make test-coverage
```

## Code Style and Standards

### 1. Go Standards
- Follow [Effective Go](https://golang.org/doc/effective_go)
- Use `gofmt` for formatting
- Run `golangci-lint` before commits

### 2. Documentation
- Document all exported types and functions
- Include examples for complex functionality
- Keep README.md up to date

### 3. Commit Messages
```
type(scope): description

[optional body]

[optional footer]
```

## Building and Running

### 1. Local Development
```bash
# Build binaries
make build

# Run locally
make run-local

# Run with specific config
make run-local CONFIG=config/dev.yaml
```

### 2. Docker Development
```bash
# Build container
make docker-build

# Run in container
make docker-run
```

### 3. Deployment to K8s
```bash
# Deploy to current context
make deploy

# Deploy to specific context
make deploy KUBE_CONTEXT=my-context
```

## Debugging

### 1. Local Debugging
- Use delve for Go debugging
- Configure VS Code launch.json
- Enable debug logs

### 2. Remote Debugging
```bash
# Enable remote debugging
make debug-pod

# Attach debugger
dlv connect localhost:2345
```

### 3. Logging
```go
// Log levels
log.Debug()  // Development details
log.Info()   // Normal operations
log.Warn()   // Warning conditions
log.Error()  // Error conditions
```

## Contributing

### 1. Contribution Process
1. Fork repository
2. Create feature branch
3. Implement changes
4. Submit PR

### 2. PR Requirements
- Tests included
- Documentation updated
- Follows code style
- CI passes

### 3. Review Process
1. Code review by maintainers
2. Address feedback
3. Final approval
4. Merge

### 4. Release Process
1. Version bump
2. Update CHANGELOG.md
3. Create release tag
4. Build and publish artifacts 