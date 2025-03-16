# Basic Kubernetes Cluster Overview Questions

## Cluster Health and Status
1. What is the overall health status of my Kubernetes cluster?
2. Are all nodes in the cluster running and healthy?
3. How many nodes are currently in the cluster?
4. What is the current resource utilization across the cluster?
5. Are there any nodes that are under heavy load?

## Namespace and Resource Overview
1. What namespaces exist in the cluster?
2. How many pods are running across all namespaces?
3. What is the total number of deployments in the cluster?
4. Are there any namespaces with unusually high resource usage?
5. What is the distribution of pods across different namespaces?

## Resource Utilization
1. What is the current CPU usage across the cluster?
2. How much memory is being used by all pods?
3. Are there any pods that are close to their resource limits?
4. What is the storage usage across the cluster?
5. Are there any resource bottlenecks in the cluster?

## Application Status
1. What applications are currently deployed in the cluster?
2. Are all deployments running at their desired replica count?
3. What is the status of all running pods?
4. Are there any pods in a failed state?
5. What is the uptime of the longest-running pods?

## Network and Services
1. What services are exposed in the cluster?
2. Are all services properly configured and accessible?
3. What is the current network traffic pattern?
4. Are there any network policies in place?
5. What is the status of the cluster's DNS resolution?

## Security and Access
1. What service accounts are being used in the cluster?
2. Are there any pods running with elevated privileges?
3. What RBAC policies are currently active?
4. Are there any security contexts defined for pods?
5. What secrets are being used across the cluster?

## Maintenance and Updates
1. When was the last time the cluster was updated?
2. Are there any pending updates or upgrades?
3. What is the current version of the Kubernetes control plane?
4. Are there any deprecated API versions in use?
5. What is the status of the cluster's certificate expiration?

## Monitoring and Logging
1. What monitoring tools are currently active in the cluster?
2. Are all pods properly configured for logging?
3. What metrics are being collected from the cluster?
4. Are there any alerting rules configured?
5. What is the current state of the cluster's observability stack?

## Storage and Volumes
1. What types of storage are being used in the cluster?
2. Are there any persistent volumes that are near capacity?
3. What storage classes are available in the cluster?
4. Are there any storage-related issues?
5. What is the status of volume snapshots?

## Workload Management
1. What types of workloads are running in the cluster?
2. Are there any jobs or cronjobs scheduled?
3. What is the current state of the cluster's workload scheduler?
4. Are there any pods that are pending scheduling?
5. What is the distribution of workloads across nodes?

## Troubleshooting
1. Are there any events that need attention in the cluster?
2. What is the current state of the cluster's error logs?
3. Are there any pods that are constantly restarting?
4. What is the status of the cluster's health checks?
5. Are there any components that are reporting warnings? 