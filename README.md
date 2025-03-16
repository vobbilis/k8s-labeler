# K8s-Labeler

K8s-Labeler is an intelligent Kubernetes labeling system that generates and maintains meaningful labels for Kubernetes resources based on runtime behavior, dependencies, and operational patterns.

## Overview

K8s-Labeler observes your Kubernetes cluster in real-time and automatically generates meaningful labels that help with:
- Resource organization and discovery
- Operational insights
- Dependency mapping
- Security policy enforcement
- Cost allocation
- Troubleshooting and debugging

## Features

- **Intelligent Label Generation**: Automatically generates meaningful labels based on:
  - Runtime behavior
  - Resource relationships
  - Network patterns
  - Resource utilization
  - Application dependencies
  
- **Label Categories**:
  - Basic QA labels (environment, tier, criticality)
  - Deployment-related (release, version, update-strategy)
  - Network-related (ingress-type, egress-rules, protocol)
  - Resource utilization (resource-profile, scaling-pattern)
  - Multi-cluster (cluster-role, geo-location, failover-region)
  - Service mesh integration (mesh-enabled, traffic-policy)
  - Troubleshooting (debug-level, trace-enabled)

- **Flexible Configuration**:
  - Customizable labeling rules
  - Label inheritance patterns
  - Namespace-based policies
  - Exclusion rules

- **Integration**:
  - Prometheus metrics
  - OpenTelemetry instrumentation
  - Kubernetes events
  - Audit logging

## Getting Started

### Prerequisites

- Go >= 1.21
- Kubernetes >= 1.25
- Docker >= 24.0
- Kind >= 0.20 (for local development)
- Helm >= 3.12

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/vobbilis/k8s-labeler.git
   cd k8s-labeler
   ```

2. **Set up development environment**:
   ```bash
   ./dev-cluster/scripts/setup-dev-environment.sh
   ```
   This script will:
   - Create a Kind cluster with proper configuration
   - Deploy the observability stack (Prometheus, Grafana, Jaeger)
   - Deploy the OpenTelemetry Demo application
   - Set up port forwarding for UI access

3. **Access Development Tools**:
   - Grafana: http://localhost:3001 (default credentials: admin/prom-operator)
   - Jaeger UI: http://localhost:30686
   - Frontend UI: http://localhost:8081

### Development Environment

The project includes a comprehensive development environment with:
- Local Kubernetes cluster (Kind)
- Monitoring stack (Prometheus, Grafana)
- Tracing (Jaeger, OpenTelemetry)
- Sample applications for testing

For detailed setup instructions, see [DEVELOPMENT.md](docs/DEVELOPMENT.md).

## Architecture

K8s-Labeler consists of several components:
- Label Generator Engine
- Resource Watchers
- Pattern Analyzers
- Policy Engine
- API Server
- Storage Backend

For detailed architecture information, see [ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Documentation

- [Development Guide](docs/DEVELOPMENT.md)
- [Technical Design](docs/TECHNICAL_DESIGN.md)
- [Label Design](docs/LABELDESIGN.md)
- [Architecture](docs/ARCHITECTURE.md)

## Development Cluster

The project includes scripts and configurations for a local development cluster:

```bash
dev-cluster/
├── config/           # Configuration files
│   └── kind-config.yaml
├── scripts/         # Management scripts
│   ├── utils.sh
│   ├── start-cluster.sh
│   ├── stop-cluster.sh
│   └── cluster-status.sh
├── manifests/       # Kubernetes manifests
└── tmp/            # Temporary storage
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

### Code Style

- Follow Go best practices
- Use `gofmt` for formatting
- Run `golangci-lint` before committing

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Support

- Create an issue for bug reports or feature requests
- Join our [Slack channel](#) for community support
- Check our [FAQ](docs/FAQ.md) for common questions

## Roadmap

- [ ] Initial release with basic labeling functionality
- [ ] Advanced pattern recognition
- [ ] Machine learning integration
- [ ] Multi-cluster support
- [ ] Custom label rules engine
- [ ] Integration with popular service meshes
- [ ] Enhanced security labeling
- [ ] Cost optimization labeling

## Acknowledgments

- Kubernetes community
- OpenTelemetry project
- Contributors and maintainers 