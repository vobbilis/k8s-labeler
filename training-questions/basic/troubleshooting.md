# Basic Kubernetes Troubleshooting Questions

## Pod Issues
1. Why is a pod stuck in the Pending state?
2. What causes a pod to be in ImagePullBackOff state?
3. Why is a pod showing CrashLoopBackOff errors?
4. What does it mean when a pod is in the Evicted state?
5. Why is a pod showing OOMKilled errors?

## Network Problems
1. Why can't pods communicate with each other?
2. What causes a service to be unreachable?
3. Why are pods unable to resolve DNS names?
4. What causes network policy violations?
5. Why is a service's external IP pending?

## Resource Issues
1. Why is a pod failing to schedule?
2. What causes a node to be in NotReady state?
3. Why are pods being evicted from a node?
4. What causes a pod to exceed its resource limits?
5. Why is a persistent volume claim pending?

## Application Problems
1. Why is an application not receiving traffic?
2. What causes a deployment rollout to fail?
3. Why is a service not balancing load properly?
4. What causes a pod to fail its readiness probe?
5. Why is an application showing high latency?

## Storage Issues
1. Why is a persistent volume claim not binding?
2. What causes a volume mount to fail?
3. Why is a pod unable to write to its volume?
4. What causes storage capacity issues?
5. Why is a volume showing read-only errors?

## Security Concerns
1. Why is a pod failing to pull an image?
2. What causes a pod to fail its security context?
3. Why is a service account not working?
4. What causes RBAC permission issues?
5. Why is a pod unable to access secrets?

## Configuration Problems
1. Why is a configmap not being mounted?
2. What causes environment variables to be missing?
3. Why is a pod using incorrect configuration?
4. What causes deployment strategy issues?
5. Why is a pod not picking up configuration changes?

## Monitoring and Logging
1. Why are metrics not being collected?
2. What causes log aggregation to fail?
3. Why are alerts not triggering?
4. What causes monitoring gaps?
5. Why is a pod not generating logs?

## Cluster Health
1. Why is the control plane not responding?
2. What causes etcd to be unavailable?
3. Why is the API server timing out?
4. What causes node communication issues?
5. Why is the cluster showing degraded state?

## Update and Maintenance
1. Why is a node update failing?
2. What causes a cluster upgrade to stall?
3. Why are pods not draining properly?
4. What causes certificate rotation issues?
5. Why is a maintenance window failing?

## Performance Issues
1. Why is the cluster showing high latency?
2. What causes API server throttling?
3. Why are pods experiencing high CPU usage?
4. What causes memory pressure issues?
5. Why is the cluster showing poor performance? 