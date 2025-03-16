# Label Design for Performance Issues

## Overview
This document outlines the structure and examples of performance-related labels used for training LLMs in Kubernetes observability scenarios. Each label captures detailed information about performance issues, their context, analysis, and resolution.

## Label Structure

### Basic Structure
```json
{
    "perf_observation": "string",
    "timestamp": "ISO-8601 string",
    "environment": {
        "cluster_type": "string",
        "k8s_version": "string",
        "node_count": "integer",
        "resource_quotas": {}
    },
    "context": {},
    "metrics": {},
    "analysis": {},
    "resolution": {},
    "metadata": {}
}
```

## Real-World Examples

### 1. Memory Leak in Java Microservice

```json
{
    "perf_observation": "perf-2025031601",
    "timestamp": "2025-03-16T01:15:00Z",
    "environment": {
        "cluster_type": "production",
        "k8s_version": "1.28.4",
        "node_count": 8,
        "resource_quotas": {
            "cpu_limit": "64",
            "memory_limit": "256Gi"
        }
    },
    "context": {
        "service": "payment-processor",
        "namespace": "financial",
        "pod_pattern": "payment-processor-*",
        "container": "payment-api",
        "application": {
            "language": "Java",
            "version": "17.0.9",
            "framework": "Spring Boot 3.2.1"
        },
        "duration": "72h",
        "affected_pods": 5
    },
    "metrics": {
        "initial_state": {
            "memory_usage": "512Mi",
            "cpu_usage": "0.2",
            "response_time_p95": "150ms",
            "error_rate": "0.1%"
        },
        "degraded_state": {
            "memory_usage": "3.8Gi",
            "cpu_usage": "0.8",
            "response_time_p95": "2500ms",
            "error_rate": "12%",
            "oom_kills": 23
        },
        "heap_dumps": {
            "location": "s3://debug-artifacts/heap-20250316/",
            "size": "4.2GB"
        }
    },
    "analysis": {
        "root_cause": "Memory leak in connection pool",
        "evidence": [
            "Steady memory growth over 72 hours",
            "No memory release after GC",
            "Connection objects accumulation in heap dumps",
            "Increasing response times correlating with memory usage"
        ],
        "affected_components": [
            "Database connection pool",
            "Transaction processor",
            "Caching layer"
        ],
        "impact": {
            "user_experience": "Severe degradation",
            "business_metrics": {
                "failed_transactions": 1250,
                "financial_impact": "Estimated $50,000"
            }
        },
        "investigation_tools": [
            "JProfiler heap analysis",
            "Prometheus memory metrics",
            "Grafana dashboards",
            "ELK logs analysis"
        ]
    },
    "resolution": {
        "immediate_action": {
            "type": "Pod restart",
            "effect": "Temporary relief",
            "downtime": "30s per pod"
        },
        "root_cause_fix": {
            "type": "Code fix",
            "changes": [
                "Connection pool configuration update",
                "Resource leak patch in transaction handler",
                "Implementation of connection timeout"
            ],
            "commit": "abc123def456",
            "pr_link": "https://github.com/org/repo/pull/789"
        },
        "verification": {
            "duration": "168h",
            "metrics_observed": [
                "Memory stability",
                "Response time normalization",
                "Error rate reduction"
            ]
        },
        "prevention": {
            "monitoring_additions": [
                "Connection pool alerts",
                "Memory trend analysis",
                "Transaction duration tracking"
            ],
            "documentation_updates": [
                "Connection pool best practices",
                "Memory management guidelines",
                "Incident response playbook"
            ]
        }
    },
    "metadata": {
        "label_type": "performance",
        "severity": "critical",
        "component_type": "microservice",
        "tags": [
            "memory-leak",
            "java",
            "connection-pool",
            "production",
            "financial-impact",
            "high-priority"
        ]
    }
}
```

### 2. Network Latency in Service Mesh

```json
{
    "perf_observation": "perf-2025031602",
    "timestamp": "2025-03-16T02:30:00Z",
    "environment": {
        "cluster_type": "staging",
        "k8s_version": "1.29.0",
        "node_count": 12,
        "resource_quotas": {
            "cpu_limit": "96",
            "memory_limit": "384Gi"
        }
    },
    "context": {
        "service_mesh": "Istio",
        "mesh_version": "1.20.1",
        "affected_services": [
            "product-catalog",
            "inventory-service",
            "pricing-service"
        ],
        "network_topology": {
            "regions": ["us-west-2", "us-east-1"],
            "availability_zones": ["a", "b", "c"],
            "cross_zone_traffic": true
            }
        },
        "metrics": {
        "baseline": {
            "latency_p50": "45ms",
            "latency_p95": "120ms",
            "latency_p99": "200ms",
            "requests_per_second": 1200,
            "error_rate": "0.05%"
        },
        "degraded": {
            "latency_p50": "180ms",
            "latency_p95": "450ms",
            "latency_p99": "800ms",
            "requests_per_second": 1200,
            "error_rate": "3.5%"
        },
        "network": {
            "packet_loss": "0.8%",
            "retransmission_rate": "2.1%",
            "bandwidth_utilization": "78%"
        }
    },
    "analysis": {
        "root_cause": "Envoy proxy CPU throttling",
        "evidence": [
            "Correlation between proxy CPU usage and latency",
            "Increased connection timeouts",
            "TCP retransmission spikes",
            "Proxy worker thread saturation"
        ],
        "contributing_factors": [
            "Insufficient proxy resources",
            "Aggressive keepalive settings",
            "Suboptimal circuit breaking configuration"
        ],
        "impact": {
            "service_level_objectives": {
                "availability": "99.8% (below 99.9% target)",
                "latency_breach": "15% of requests"
            },
            "user_experience": "Moderate degradation",
            "downstream_effects": [
                "Cart abandonment increase",
                "Search results timeout"
            ]
        }
    },
    "resolution": {
        "immediate_actions": [
            {
                "action": "Proxy resource increase",
                "change": "CPU limit from 0.5 to 1.0",
                "effect": "30% latency reduction"
            },
            {
                "action": "Connection pool tuning",
                "change": "Max connections from 1000 to 2000",
                "effect": "Reduced connection queuing"
            }
        ],
        "long_term_fixes": [
            {
                "type": "Architecture change",
                "description": "Implementation of service mesh gateway sharding",
                "benefits": [
                    "Better resource isolation",
                    "Improved fault tolerance",
                    "Reduced blast radius"
                ]
            },
            {
                "type": "Monitoring enhancement",
                "description": "Advanced proxy metrics collection",
                "tools_added": [
                    "Proxy-level tracing",
                    "Detailed connection metrics",
                    "Resource utilization alerts"
                ]
            }
        ],
        "validation": {
            "duration": "72h",
            "success_criteria": [
                "P95 latency under 150ms",
                "Error rate below 0.1%",
                "No proxy CPU throttling"
            ]
        }
    },
    "metadata": {
        "label_type": "performance",
        "severity": "high",
        "component_type": "service-mesh",
        "tags": [
            "network-latency",
            "istio",
            "envoy",
            "proxy",
            "resource-contention",
            "cross-zone"
        ]
    }
}
```

### 3. Etcd Performance Degradation

```json
{
    "perf_observation": "perf-2025031603",
    "timestamp": "2025-03-16T03:45:00Z",
    "environment": {
        "cluster_type": "production",
        "k8s_version": "1.28.5",
        "node_count": 15,
        "control_plane": {
            "etcd_version": "3.5.9",
            "api_server_count": 3,
            "etcd_node_count": 5
        }
    },
    "context": {
        "component": "etcd",
        "namespace": "kube-system",
        "duration": "4h",
        "cluster_size": {
            "nodes": 15,
            "pods": 850,
            "namespaces": 12
        }
    },
    "metrics": {
        "etcd_metrics": {
            "normal": {
                "write_latency_p99": "10ms",
                "read_latency_p99": "5ms",
                "fsync_duration_p99": "8ms",
                "db_size": "2.8GB"
            },
            "degraded": {
                "write_latency_p99": "250ms",
                "read_latency_p99": "150ms",
                "fsync_duration_p99": "200ms",
                "db_size": "6.2GB"
            }
        },
        "api_server": {
            "normal": {
                "request_latency_p99": "150ms",
                "error_rate": "0.01%"
            },
            "degraded": {
                "request_latency_p99": "2500ms",
                "error_rate": "5%"
            }
        },
        "system": {
            "disk_iops": {
                "normal": 1000,
                "degraded": 5000
            },
            "disk_throughput": {
                "normal": "50MB/s",
                "degraded": "200MB/s"
            }
        }
    },
    "analysis": {
        "root_cause": "Excessive etcd compaction load",
        "evidence": [
            "Large number of key changes",
            "Frequent compaction triggers",
            "High disk I/O on etcd volumes",
            "Increasing database size"
        ],
        "contributing_factors": [
            "Rapid pod churn in CI/CD namespace",
            "Frequent ConfigMap updates",
            "Large number of custom resources",
            "Insufficient etcd storage class IOPS"
        ],
        "impact": {
            "cluster_operations": {
                "deployment_time": "Increased by 300%",
                "api_server_latency": "Increased by 400%",
                "failed_operations": 250
            },
            "affected_workloads": [
                "CI/CD pipelines",
                "Autoscaling operations",
                "Service mesh updates"
            ]
        }
    },
    "resolution": {
        "immediate_actions": [
            {
                "action": "Increase etcd storage IOPS",
                "details": "Changed storage class to io2 with 10000 IOPS",
                "effect": "50% latency reduction"
            },
            {
                "action": "Optimize compaction",
                "settings": {
                    "auto_compaction_mode": "revision",
                    "auto_compaction_retention": "5000",
                    "quota_backend_bytes": "8589934592"
                }
            }
        ],
        "long_term_solutions": [
            {
                "type": "Architecture changes",
                "changes": [
                    "Implement namespace quotas",
                    "Separate CI/CD to dedicated cluster",
                    "Implement ConfigMap versioning strategy"
                ]
            },
            {
                "type": "Monitoring improvements",
                "additions": [
                    "Etcd operation metrics",
                    "Compaction monitoring",
                    "Database size trending"
                ]
            }
        ],
        "validation_criteria": {
            "metrics": [
                "Write latency P99 < 20ms",
                "Read latency P99 < 10ms",
                "API server latency P99 < 200ms",
                "Compaction duration < 30s"
            ],
            "monitoring_period": "168h"
        }
    },
    "metadata": {
        "label_type": "performance",
        "severity": "critical",
        "component_type": "control-plane",
        "tags": [
            "etcd",
            "control-plane",
            "storage",
            "compaction",
            "high-priority",
            "production"
        ]
    }
}
```

### 4. Prometheus AlertManager Firing Storm

```json
{
    "perf_observation": "perf-2025031604",
    "timestamp": "2025-03-16T04:30:00Z",
    "environment": {
        "cluster_type": "production",
        "k8s_version": "1.28.5",
        "node_count": 20,
        "monitoring_stack": {
            "prometheus_version": "2.45.0",
            "alertmanager_version": "0.26.0",
            "grafana_version": "10.2.0",
            "prometheus_operator_version": "0.70.0"
        }
    },
    "context": {
        "component": "alertmanager",
        "namespace": "monitoring",
        "duration": "45m",
        "alert_volume": {
            "normal_rate": "5 alerts/hour",
            "incident_rate": "1200 alerts/hour",
            "unique_alerts": 15,
            "affected_services": 8
        },
        "notification_targets": [
            "slack-prod-alerts",
            "pagerduty-critical",
            "email-ops-team"
        ]
    },
    "metrics": {
        "alertmanager": {
            "normal": {
                "alerts_received_total": "120/day",
                "alerts_invalid_total": "1/day",
                "notification_latency_p99": "500ms",
                "integration_timeout_total": "0",
                "memory_usage": "256Mi"
            },
            "degraded": {
                "alerts_received_total": "1200/hour",
                "alerts_invalid_total": "50/hour",
                "notification_latency_p99": "15s",
                "integration_timeout_total": "125",
                "memory_usage": "1.8Gi"
            }
        },
        "prometheus": {
            "normal": {
                "query_duration_p99": "0.5s",
                "memory_usage": "4Gi",
                "active_series": "1.2M"
            },
            "degraded": {
                "query_duration_p99": "5s",
                "memory_usage": "7.8Gi",
                "active_series": "2.8M"
            }
        },
        "notification_systems": {
            "slack_api_latency": "2.5s",
            "pagerduty_throttling": true,
            "email_queue_depth": 500
        }
    },
    "analysis": {
        "root_cause": "Recursive alert generation due to misconfigured recording rules",
        "evidence": [
            "Exponential growth in alert volume",
            "High cardinality in alert labels",
            "Duplicate alerts with slightly different labels",
            "Memory pressure in AlertManager pods"
        ],
        "contributing_factors": [
            "Recent prometheus recording rules update",
            "Missing alert aggregation rules",
            "Insufficient rate limiting on alert routes",
            "Alert fan-out due to label combinations"
        ],
        "impact": {
            "operational": {
                "notification_delays": "Up to 15 minutes",
                "missed_critical_alerts": 3,
                "false_positives": 850
            },
            "system_resources": {
                "alertmanager_cpu": "Throttled at 200% utilization",
                "prometheus_memory": "Near OOM conditions"
            },
            "team_impact": {
                "alert_fatigue": "Severe",
                "incident_response_delay": "20 minutes average",
                "false_escalations": 12
            }
        }
    },
    "resolution": {
        "immediate_actions": [
            {
                "action": "Silence storm alerts",
                "implementation": {
                    "method": "alertmanager_silence",
                    "matcher": "severity=~\"warning|info\",alert_type=\"metric_anomaly\"",
                    "duration": "2h"
                }
            },
            {
                "action": "Scale AlertManager resources",
                "changes": {
                    "replicas": "3 to 5",
                    "memory_limit": "512Mi to 2Gi",
                    "cpu_limit": "1 to 2"
                }
            }
        ],
        "root_cause_fix": {
            "recording_rules": [
                {
                    "action": "Fix rule recursion",
                    "file": "prometheus/rules/service-metrics.yaml",
                    "change": "Add aggregation step to prevent self-reference"
                },
                {
                    "action": "Add rate limiting",
                    "file": "alertmanager/config.yaml",
                    "change": "Implement group_wait and group_interval"
                }
            ],
            "alert_routing": {
                "changes": [
                    "Implement alert grouping by service and severity",
                    "Add rate limiting per notification channel",
                    "Create escalation paths based on alert age"
                ]
            }
        },
        "prevention": {
            "monitoring_improvements": [
                {
                    "type": "Alert volume monitoring",
                    "implementation": "New recording rules for alert metrics",
                    "thresholds": {
                        "warning": "100 alerts/10min",
                        "critical": "500 alerts/10min"
                    }
                },
                {
                    "type": "Cardinality tracking",
                    "metrics": [
                        "prometheus_tsdb_head_series_created_total",
                        "alertmanager_alerts_received_total"
                    ]
                }
            ],
            "process_changes": [
                "Mandatory review of recording rules",
                "Testing alerts in staging environment",
                "Regular alert configuration audits"
            ],
            "documentation": [
                "Alert design guidelines",
                "Runbook for alert storms",
                "Recording rules best practices"
            ]
        },
        "validation": {
            "metrics_thresholds": [
                "Alert volume < 10 alerts/minute",
                "Notification latency < 1s",
                "No duplicate alerts",
                "Memory usage < 512Mi"
            ],
            "monitoring_period": "72h"
        }
    },
    "metadata": {
        "label_type": "performance",
        "severity": "critical",
        "component_type": "monitoring",
        "tags": [
            "alertmanager",
            "prometheus",
            "alert-storm",
            "recording-rules",
            "high-cardinality",
            "production"
        ]
    }
}
```

### 5. Silent Alert Failure

```json
{
    "perf_observation": "perf-2025031605",
    "timestamp": "2025-03-16T05:15:00Z",
    "environment": {
        "cluster_type": "production",
        "k8s_version": "1.28.5",
        "node_count": 25,
        "monitoring_stack": {
            "prometheus_version": "2.45.0",
            "alertmanager_version": "0.26.0",
            "thanos_version": "0.32.0"
        }
    },
    "context": {
        "component": "alertmanager",
        "namespace": "monitoring",
        "duration": "8h",
        "incident_discovery": "Manual observation of missed alerts",
        "affected_alerts": [
            "KubernetesPodCrashLooping",
            "KubernetesContainerOOMKilled",
            "PrometheusTargetMissing"
        ]
    },
        "metrics": {
        "alertmanager_operational": {
            "normal": {
                "alerts_successfully_sent": "98%",
                "notification_latency_p95": "200ms",
                "config_reload_success": true
            },
            "degraded": {
                "alerts_successfully_sent": "0%",
                "notification_latency_p95": "N/A",
                "config_reload_success": true
            }
        },
        "prometheus_health": {
            "normal": {
                "rule_evaluation_duration_p95": "250ms",
                "rule_evaluation_failures": "0"
            },
            "degraded": {
                "rule_evaluation_duration_p95": "250ms",
                "rule_evaluation_failures": "0"
            }
        },
        "missed_alerts": {
            "critical": 15,
            "warning": 45,
            "info": 120
        }
    },
    "analysis": {
        "root_cause": "TLS certificate expiration for webhook receiver",
        "evidence": [
            "Zero successful notifications despite active alerts",
            "TLS handshake failures in AlertManager logs",
            "Expired certificate for webhook-receiver.monitoring.svc",
            "No error metrics due to silent failure mode"
        ],
        "contributing_factors": [
            "Missing certificate expiration monitoring",
            "Insufficient alert delivery validation",
            "No redundant notification paths",
            "Alert success rate monitoring gap"
        ],
        "impact": {
            "missed_notifications": {
                "critical_alerts": 15,
                "service_disruptions": 3,
                "detection_delay": "8 hours"
            },
            "business_impact": {
                "customer_facing_incidents": 2,
                "sla_violations": 1
            }
        }
    },
    "resolution": {
        "immediate_actions": [
            {
                "action": "Certificate renewal",
                "implementation": {
                    "method": "cert-manager",
                    "duration": "1 year",
                    "domains": ["webhook-receiver.monitoring.svc"]
                }
            },
            {
                "action": "Alert recovery",
                "steps": [
                    "Manual review of 8h alert history",
                    "Retroactive incident creation",
                    "Stakeholder notification"
                ]
            }
        ],
        "long_term_fixes": [
            {
                "type": "Monitoring enhancement",
                "changes": [
                    {
                        "component": "Certificate monitoring",
                        "implementation": "cert-manager alerts",
                        "threshold": "30 days before expiry"
                    },
                    {
                        "component": "Alert delivery validation",
                        "implementation": "End-to-end synthetic alerts",
                        "frequency": "Every 5 minutes"
                    }
                ]
            },
            {
                "type": "Architecture improvements",
                "changes": [
                    "Implement redundant notification paths",
                    "Add fallback email notifications",
                    "Deploy alert delivery monitoring"
                ]
            }
        ],
        "prevention": {
            "automation": [
                "Automatic certificate renewal",
                "Alert delivery verification",
                "Configuration validation hooks"
            ],
            "process_updates": [
                "Weekly certificate review",
                "Monthly notification path testing",
                "Quarterly DR exercises"
            ]
        },
        "validation": {
            "success_criteria": [
                "All notifications delivered < 30s",
                "Certificate expiry > 60 days",
                "Redundant paths verified",
                "End-to-end tests passing"
            ],
            "monitoring_period": "168h"
        }
    },
    "metadata": {
        "label_type": "performance",
        "severity": "critical",
        "component_type": "monitoring",
        "tags": [
            "alertmanager",
            "certificate-expiry",
            "silent-failure",
            "notification-delivery",
            "production",
            "sla-violation"
        ]
    }
}
```

### 6. Kafka Consumer Lag Alert Investigation

```json
{
    "perf_observation": "perf-2025031606",
    "timestamp": "2025-03-16T06:45:00Z",
    "environment": {
        "cluster_type": "production",
        "k8s_version": "1.28.5",
        "node_count": 15,
        "kafka_cluster": {
            "version": "3.6.1",
            "brokers": 5,
            "partitions_per_topic": 24,
            "replication_factor": 3
        }
    },
    "context": {
        "alert_name": "KafkaConsumerLagCritical",
        "alert_query": "sum(kafka_consumergroup_lag{group=~\"order-processor-.*\"}) by (topic, partition) > 100000",
        "service": "order-processor",
        "topic": "customer-orders",
        "consumer_group": "order-processor-group-1",
        "detection_time": "2025-03-16T06:45:00Z",
        "affected_components": [
            "order-processor-service",
            "payment-validation-service",
            "inventory-update-service"
        ]
    },
    "metrics": {
        "kafka_metrics": {
            "normal": {
                "consumer_lag": {
                    "max": 5000,
                    "avg": 1200,
                    "affected_partitions": 0
                },
                "messages_per_sec": {
                    "incoming": 2000,
                    "processed": 2000
                },
                "processing_time_ms": {
                    "p95": 150,
                    "p99": 250
                }
            },
            "degraded": {
                "consumer_lag": {
                    "max": 250000,
                    "avg": 125000,
                    "affected_partitions": 8
                },
                "messages_per_sec": {
                    "incoming": 3500,
                    "processed": 1200
                },
                "processing_time_ms": {
                    "p95": 850,
                    "p99": 1500
                }
            }
        },
        "application_metrics": {
            "normal": {
                "order_processing_time_ms": {
                    "p95": 200,
                    "p99": 400
                },
                "database_connection_pool": {
                    "active": 20,
                    "idle": 10,
                    "max": 50
                },
                "thread_pool_metrics": {
                    "active_threads": 15,
                    "queue_size": 0,
                    "rejected_tasks": 0
                }
            },
            "degraded": {
                "order_processing_time_ms": {
                    "p95": 1200,
                    "p99": 2500
                },
                "database_connection_pool": {
                    "active": 48,
                    "idle": 0,
                    "max": 50
                },
                "thread_pool_metrics": {
                    "active_threads": 50,
                    "queue_size": 200,
                    "rejected_tasks": 45
                }
            }
        },
        "resource_metrics": {
            "cpu_usage_percent": {
                "normal": 45,
                "degraded": 92
            },
            "memory_usage_gb": {
                "normal": 6,
                "degraded": 7.8
            },
            "gc_metrics": {
                "normal": {
                    "gc_time_percent": 2,
                    "full_gc_count": 0
                },
                "degraded": {
                    "gc_time_percent": 12,
                    "full_gc_count": 5
                }
            }
        }
    },
    "analysis": {
        "root_cause": "Database connection pool saturation causing slow message processing",
        "evidence": [
            "Database connection pool at 96% utilization",
            "Increased thread pool queue size and rejected tasks",
            "Correlation between processing time and connection wait time",
            "GC pressure indicating memory churn from queued requests"
        ],
        "contributing_factors": [
            "20% increase in incoming message rate",
            "Inefficient database query patterns",
            "Undersized connection pool",
            "Missing database index on frequently queried column"
        ],
        "impact": {
            "business_metrics": {
                "order_processing_delay": "Up to 15 minutes",
                "affected_orders": 12500,
                "failed_orders": 150
            },
            "system_health": {
                "cpu_saturation": "92% average",
                "thread_pool_saturation": "100%",
                "database_connections": "96% utilized"
            },
            "downstream_effects": [
                "Delayed inventory updates",
                "Stale order status for customers",
                "Increased customer support tickets"
            ]
        }
    },
    "resolution": {
        "immediate_actions": [
            {
                "action": "Scale consumer pods",
                "change": {
                    "replicas": "5 to 8",
                    "effect": "Increased processing capacity"
                }
            },
            {
                "action": "Increase DB connection pool",
                "change": {
                    "max_connections": "50 to 75",
                    "idle_timeout": "300s to 600s"
                }
            },
            {
                "action": "Add missing index",
                "details": {
                    "table": "order_items",
                    "columns": ["status", "created_at"],
                    "type": "btree"
                }
            }
        ],
        "long_term_fixes": [
            {
                "type": "Database optimization",
                "changes": [
                    "Implement query caching",
                    "Batch database operations",
                    "Optimize frequently used queries"
                ]
            },
            {
                "type": "Application changes",
                "changes": [
                    "Implement adaptive batch processing",
                    "Add circuit breaker for database calls",
                    "Improve connection pool management"
                ]
            },
            {
                "type": "Infrastructure updates",
                "changes": [
                    "Implement database read replicas",
                    "Set up database connection pooling proxy",
                    "Configure auto-scaling based on lag metrics"
                ]
            }
        ],
        "prevention": {
            "monitoring_improvements": [
                {
                    "type": "Early warning system",
                    "metrics": [
                        "Connection pool saturation rate",
                        "Message processing time trend",
                        "Database query performance"
                    ],
                    "thresholds": {
                        "connection_pool_usage": "80%",
                        "processing_time_increase": "50%",
                        "consumer_lag_growth_rate": "1000/minute"
                    }
                }
            ],
            "process_changes": [
                "Regular database index analysis",
                "Periodic query performance review",
                "Load testing with production traffic patterns"
            ]
        },
        "validation": {
            "metrics_thresholds": [
                "Consumer lag < 5000 messages",
                "Processing time p95 < 200ms",
                "Connection pool utilization < 70%",
                "No task rejections in thread pool"
            ],
            "monitoring_period": "72h",
            "success_criteria": [
                "Zero order processing delays",
                "No customer impact",
                "Stable resource utilization"
            ]
        }
    },
    "metadata": {
        "label_type": "performance",
        "severity": "critical",
        "component_type": "application",
        "tags": [
            "kafka",
            "consumer-lag",
            "database",
            "connection-pool",
            "production",
            "order-processing"
        ]
    }
}
```

## Label Categories

### Performance Issue Types
1. Resource Contention
   - Memory leaks
   - CPU throttling
   - I/O bottlenecks
   - Network congestion

2. Scalability Issues
   - Pod startup latency
   - Service mesh overhead
   - Control plane bottlenecks
   - Auto-scaling delays

3. Database Performance
   - Connection pool exhaustion
   - Query performance
   - Replication lag
   - Storage I/O

4. Network Performance
   - Service mesh latency
   - DNS resolution issues
   - Load balancer bottlenecks
   - Cross-zone latency

5. Application Performance
   - Memory management
   - Thread pool saturation
   - Cache efficiency
   - Connection handling

## Best Practices for Label Creation

1. **Metric Collection**
   - Include baseline and degraded metrics
   - Use percentile-based measurements
   - Document resource utilization
   - Track business impact

2. **Context Documentation**
   - Environment details
   - Component versions
   - System architecture
   - Dependencies

3. **Analysis Documentation**
   - Clear root cause identification
   - Evidence collection
   - Impact assessment
   - Investigation tools used

4. **Resolution Documentation**
   - Immediate actions
   - Long-term fixes
   - Validation steps
   - Prevention measures

## Using Labels for Training

1. **Pattern Recognition**
   - Symptom correlation
   - Common root causes
   - Effective solutions
   - Prevention strategies

2. **Automated Response**
   - Initial diagnostic steps
   - Remediation actions
   - Validation procedures
   - Escalation criteria

3. **Knowledge Base Building**
   - Solution templates
   - Troubleshooting guides
   - Best practices
   - Architecture recommendations 