# Label Design for Kubernetes LLM Training Data

This document outlines various label structures for generating high-quality training data to fine-tune LLMs for Kubernetes-based applications.

## 1. Basic QA Format

The simplest format focusing on direct question-answer pairs:

```json
{
    "question": "Why is pod nginx-7844d4b86f-2j8xc in CrashLoopBackOff state?",
    "answer": "The pod is in CrashLoopBackOff because it's failing its liveness probe. The HTTP probe to path /healthz is returning a 500 status code.",
    "context": {
        "pod_name": "nginx-7844d4b86f-2j8xc",
        "namespace": "default",
        "timestamp": "2024-03-15T14:23:00Z",
        "events": ["Liveness probe failed: HTTP probe failed with statuscode: 500"]
    }
}
```

## 2. Comprehensive Troubleshooting Format

Extended format including evidence and resolution steps:

```json
{
    "incident_id": "inc-2024031501",
    "question": "What's causing high latency in the payment-service?",
    "analysis": {
        "symptoms": [
            "Average response time increased from 100ms to 2s",
            "Error rate increased to 5%",
            "CPU throttling events observed"
        ],
        "root_cause": "The payment-service pods are experiencing CPU throttling due to insufficient CPU requests and limits",
        "evidence": {
            "metrics": {
                "cpu_throttling": "25% of CPU time throttled",
                "cpu_usage": "averaging 950m out of 1000m limit"
            },
            "logs": [
                "2024-03-15T14:20:00Z CPU throttled for 30s",
                "2024-03-15T14:20:30Z Response time degraded"
            ],
            "events": [
                "Pod payment-service-7d8f9b7c5-2j8xc throttled due to CPU constraints"
            ]
        },
        "resolution": {
            "steps": [
                "Increase CPU request from 500m to 750m",
                "Increase CPU limit from 1000m to 1500m",
                "Apply new resource configuration using kubectl"
            ],
            "verification": "Latency returned to normal after resource adjustment"
        }
    },
    "metadata": {
        "service": "payment-service",
        "namespace": "production",
        "cluster": "prod-east-1",
        "timestamp": "2024-03-15T14:23:00Z"
    }
}
```

## 3. Resource Management Format

Specialized format for resource optimization scenarios:

```json
{
    "observation_id": "res-2024031502",
    "scenario": "Resource Optimization",
    "question": "How should we optimize the resource allocation for the recommendation-service?",
    "current_state": {
        "resources": {
            "requests": {
                "cpu": "500m",
                "memory": "512Mi"
            },
            "limits": {
                "cpu": "1000m",
                "memory": "1Gi"
            }
        },
        "metrics": {
            "cpu_usage_p95": "300m",
            "memory_usage_p95": "750Mi",
            "cpu_throttling": "0%",
            "oom_events": "0"
        }
    },
    "analysis": {
        "findings": [
            "CPU usage consistently below requests",
            "Memory usage approaching limits during peak",
            "No throttling or OOM events observed"
        ],
        "recommendation": "Decrease CPU requests to 300m and increase memory limits to 1.5Gi based on actual usage patterns",
        "predicted_impact": {
            "cost_savings": "30% reduction in CPU costs",
            "performance": "No negative impact expected",
            "risk": "Low - based on 30-day usage patterns"
        }
    }
}
```

## 4. Deployment Troubleshooting Format

Format focused on deployment and rollout issues:

```json
{
    "deployment_incident": "dep-2024031503",
    "question": "Why did the recent deployment of auth-service fail to roll out?",
    "deployment_context": {
        "service": "auth-service",
        "old_version": "v1.5.0",
        "new_version": "v1.6.0",
        "rollout_strategy": "RollingUpdate",
        "timestamp": "2024-03-15T15:00:00Z"
    },
    "analysis": {
        "status": {
            "desired_replicas": 5,
            "updated_replicas": 2,
            "available_replicas": 3,
            "unavailable_replicas": 2
        },
        "events": [
            {
                "type": "Warning",
                "reason": "FailedCreate",
                "message": "Pod auth-service-7d8f9b7c5-2j8xc failed readiness probe",
                "timestamp": "2024-03-15T15:01:00Z"
            }
        ],
        "pod_conditions": [
            {
                "type": "Ready",
                "status": "False",
                "reason": "ContainerNotReady",
                "message": "readiness probe failed: connection refused"
            }
        ],
        "logs": [
            "Failed to connect to database at startup",
            "Application failed health check"
        ]
    },
    "resolution": {
        "root_cause": "New version contains incorrect database connection string in configuration",
        "fix": "Update ConfigMap with correct database URL",
        "verification": "Deployment succeeded after configuration update"
    }
}
```

## 5. Network Policy Analysis Format

Format for network-related issues and security:

```json
{
    "network_incident": "net-2024031504",
    "question": "Why can't the frontend-service communicate with the backend-api?",
    "network_context": {
        "source": {
            "service": "frontend-service",
            "namespace": "frontend",
            "labels": {
                "app": "frontend",
                "env": "prod"
            }
        },
        "destination": {
            "service": "backend-api",
            "namespace": "backend",
            "labels": {
                "app": "api",
                "env": "prod"
            }
        }
    },
    "analysis": {
        "connectivity_test": {
            "protocol": "TCP",
            "port": 8080,
            "result": "timeout"
        },
        "network_policies": [
            {
                "name": "backend-api-policy",
                "namespace": "backend",
                "spec": {
                    "ingress": [
                        {
                            "from": [
                                {
                                    "namespaceSelector": {
                                        "matchLabels": {
                                            "env": "prod"
                                        }
                                    },
                                    "podSelector": {
                                        "matchLabels": {
                                            "app": "frontend"
                                        }
                                    }
                                }
                            ]
                        }
                    ]
                }
            }
        ],
        "diagnosis": "Network policy is missing port specification for ingress rules",
        "solution": "Add port 8080 to the ingress rules in the network policy"
    }
}
```

## 6. Service Mesh Observability Format

Format for service mesh related observations:

```json
{
    "mesh_observation": "mesh-2024031505",
    "question": "What's causing the increased error rate in service-to-service communication?",
    "mesh_context": {
        "source_service": "order-service",
        "destination_service": "inventory-service",
        "mesh_platform": "Istio",
        "observed_period": "2024-03-15T14:00:00Z to 2024-03-15T15:00:00Z"
    },
    "telemetry": {
        "metrics": {
            "error_rate": "15%",
            "latency_p95": "2.5s",
            "requests_per_second": "50"
        },
        "traces": [
            {
                "trace_id": "abc123",
                "spans": [
                    {
                        "service": "order-service",
                        "operation": "PlaceOrder",
                        "duration": "100ms",
                        "status": "OK"
                    },
                    {
                        "service": "inventory-service",
                        "operation": "CheckStock",
                        "duration": "2.5s",
                        "status": "ERROR",
                        "error": "deadline exceeded"
                    }
                ]
            }
        ]
    },
    "analysis": {
        "root_cause": "Circuit breaker threshold too low for inventory service",
        "evidence": "Consistent pattern of timeout errors when RPS exceeds 40",
        "solution": "Increase circuit breaker threshold and timeout settings in VirtualService"
    }
}
```

## 7. Multi-Cluster Operations Format

Format for multi-cluster scenarios:

```json
{
    "multi_cluster_incident": "mc-2024031506",
    "question": "Why is cross-cluster service discovery failing between prod-east and prod-west clusters?",
    "cluster_context": {
        "clusters": [
            {
                "name": "prod-east",
                "region": "us-east-1",
                "status": "Healthy"
            },
            {
                "name": "prod-west",
                "region": "us-west-1",
                "status": "Healthy"
            }
        ],
        "federation_type": "KubeFed",
        "service_discovery": "Multi-cluster DNS"
    },
    "analysis": {
        "symptoms": [
            "Services in prod-west unable to resolve prod-east endpoints",
            "CoreDNS errors in prod-west cluster"
        ],
        "diagnostics": {
            "dns_checks": [
                {
                    "query": "service.prod-east.global",
                    "status": "NXDOMAIN",
                    "expected": "NOERROR"
                }
            ],
            "federation_status": {
                "kubefed_controller": "Running",
                "sync_status": "Error",
                "error": "Unable to sync service registry"
            }
        },
        "root_cause": "KubeFed service sync controller lacks necessary RBAC permissions in prod-east cluster",
        "resolution": "Add required RBAC roles and bindings for KubeFed controller in prod-east cluster"
    }
}
```

## Label Quality Guidelines

1. **Completeness**
   - Include all relevant context
   - Provide clear evidence
   - Document both problem and solution

2. **Accuracy**
   - Use precise technical terms
   - Include specific resource names
   - Reference actual metrics and logs

3. **Consistency**
   - Follow standard format
   - Use consistent terminology
   - Maintain consistent detail level

4. **Usefulness**
   - Focus on practical scenarios
   - Include actionable information
   - Provide verification steps

## Label Categories

1. **Operational Issues**
   - Resource constraints
   - Configuration errors
   - State inconsistencies

2. **Performance Problems**
   - Latency issues
   - Scaling problems
   - Resource utilization

3. **Security Concerns**
   - Access control issues
   - Network policy problems
   - Secret management

4. **Deployment Challenges**
   - Rollout failures
   - Version conflicts
   - Configuration issues

5. **Networking Issues**
   - Service discovery
   - Load balancing
   - Connectivity problems

6. **Storage Problems**
   - Volume mounting
   - Persistence issues
   - Capacity problems

## Best Practices for Label Generation

1. **Real-world Correlation**
   - Base labels on actual incidents
   - Include real metrics and logs
   - Reference common scenarios

2. **Context Preservation**
   - Maintain temporal information
   - Include environmental context
   - Preserve causal relationships

3. **Solution Quality**
   - Provide complete solutions
   - Include verification steps
   - Document alternatives

4. **Scalability Consideration**
   - Consider cluster size
   - Account for load patterns
   - Include resource impacts 