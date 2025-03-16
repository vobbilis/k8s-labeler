# Training Data Directory

This directory contains labeled training data for the k8s-labeler project. The data is organized into different categories based on the type of observation.

## Directory Structure

```
training-data/
├── performance/           # Performance-related observations and incidents
│   └── perf-2025031607-oom-observability.json    # OOM issues in observability stack
├── troubleshooting/      # General troubleshooting scenarios
├── deployment/           # Deployment-related issues
├── dependencies/         # Dependency and versioning issues
└── mesh/                # Service mesh related observations
```

## Categories

### Performance Labels
Located in `performance/` directory. These labels capture performance-related issues, metrics, and resolutions in Kubernetes environments. Examples include:
- Memory-related issues (OOM kills)
- CPU throttling
- Network latency
- Storage I/O bottlenecks
- Resource contention

Each performance label includes:
- Baseline and degraded metrics
- Resource utilization data
- Impact assessment
- Resolution steps
- Prevention measures

### Troubleshooting Labels
Located in `troubleshooting/` directory. Contains general troubleshooting scenarios and their resolutions.

### Deployment Labels
Located in `deployment/` directory. Focuses on issues related to application deployments and updates.

### Dependency Labels
Located in `dependencies/` directory. Covers dependency management and versioning issues.

### Mesh Labels
Located in `mesh/` directory. Contains service mesh related observations and issues.

## Label Format
Each label follows a standardized JSON format with the following main sections:
- perf_observation: Unique identifier
- timestamp: Time of observation
- environment: Cluster and environment details
- context: Specific components and conditions
- metrics: Relevant metrics and measurements
- analysis: Root cause and impact analysis
- resolution: Both immediate and long-term solutions
- metadata: Categorization and tagging

## Contributing
When adding new labels:
1. Place them in the appropriate category directory
2. Follow the standard JSON format
3. Include comprehensive metrics and context
4. Document both the problem and solution
5. Add relevant tags in metadata

## Usage
These labels are used to train models for:
- Problem identification
- Root cause analysis
- Resolution recommendation
- Prevention strategies 