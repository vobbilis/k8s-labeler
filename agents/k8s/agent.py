#!/usr/bin/env python3
from typing import Dict, Any, Optional, List
import requests
from langchain_core.tools import tool
import json
from datetime import datetime, timedelta

class K8sControlPlaneAgent:
    """Agent for managing and monitoring Kubernetes control plane components."""
    
    def __init__(self):
        self.k8s_api_url = "http://localhost:8000"

    def execute_kubectl(self, command: str, namespace: Optional[str] = None) -> Dict[str, Any]:
        """Execute a kubectl command through the API."""
        try:
            response = requests.post(
                f"{self.k8s_api_url}/execute",
                json={
                    "command": command,
                    "namespace": namespace
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    @tool("get_control_plane_status")
    def get_control_plane_status(self) -> Dict[str, Any]:
        """Get the status of all control plane components."""
        components = [
            "kube-apiserver",
            "kube-controller-manager",
            "kube-scheduler",
            "etcd"
        ]
        
        status = {}
        for component in components:
            result = self.execute_kubectl(f"get pods -n kube-system -l component={component} -o json")
            if "error" in result:
                status[component] = {"status": "error", "message": result["error"]}
                continue
            
            pods = result.get("items", [])
            component_status = {
                "pods": len(pods),
                "ready": 0,
                "not_ready": 0,
                "restarts": 0,
                "issues": []
            }
            
            for pod in pods:
                pod_status = pod.get("status", {})
                container_statuses = pod_status.get("containerStatuses", [])
                
                # Check readiness
                ready = all(status.get("ready", False) for status in container_statuses)
                if ready:
                    component_status["ready"] += 1
                else:
                    component_status["not_ready"] += 1
                
                # Count restarts
                restarts = sum(status.get("restartCount", 0) for status in container_statuses)
                component_status["restarts"] += restarts
                
                # Check for issues
                if restarts > 5:
                    component_status["issues"].append(f"High restart count ({restarts}) for pod {pod['metadata']['name']}")
                
                # Check container states
                for container in container_statuses:
                    state = container.get("state", {})
                    if "waiting" in state or "terminated" in state:
                        reason = state.get("waiting", {}).get("reason") or state.get("terminated", {}).get("reason")
                        component_status["issues"].append(
                            f"Container {container['name']} in pod {pod['metadata']['name']} is {reason}"
                        )
            
            status[component] = component_status
        
        return status

    @tool("analyze_etcd_health")
    def analyze_etcd_health(self) -> Dict[str, Any]:
        """Analyze the health of the etcd cluster."""
        # Get etcd endpoints health
        result = self.execute_kubectl("exec -n kube-system etcd-control-plane -- etcdctl endpoint health --cluster")
        
        health_status = {
            "healthy_endpoints": 0,
            "unhealthy_endpoints": 0,
            "endpoints": [],
            "issues": []
        }
        
        if "error" not in result:
            lines = result.get("output", "").split("\n")
            for line in lines:
                if line.strip():
                    endpoint, status = line.split(":", 1)
                    is_healthy = "healthy" in status.lower()
                    health_status["endpoints"].append({
                        "endpoint": endpoint.strip(),
                        "healthy": is_healthy
                    })
                    if is_healthy:
                        health_status["healthy_endpoints"] += 1
                    else:
                        health_status["unhealthy_endpoints"] += 1
                        health_status["issues"].append(f"Unhealthy etcd endpoint: {endpoint}")
        
        # Get etcd metrics
        result = self.execute_kubectl("exec -n kube-system etcd-control-plane -- etcdctl endpoint status -w json")
        if "error" not in result:
            try:
                metrics = json.loads(result.get("output", "[]"))
                for endpoint in metrics:
                    # Check for concerning metrics
                    if endpoint.get("dbSize", 0) > 8 * 1024 * 1024 * 1024:  # 8GB
                        health_status["issues"].append(f"Large etcd database size: {endpoint['dbSize']} bytes")
                    if endpoint.get("raftTerm", 0) > 1000:
                        health_status["issues"].append("High raft term number indicates frequent leader elections")
            except json.JSONDecodeError:
                health_status["issues"].append("Failed to parse etcd metrics")
        
        return health_status

    @tool("check_api_server_metrics")
    def check_api_server_metrics(self) -> Dict[str, Any]:
        """Check key metrics from the Kubernetes API server."""
        result = self.execute_kubectl("get --raw /metrics")
        
        metrics = {
            "request_latency": {},
            "request_rate": {},
            "errors": {},
            "etcd_requests": {},
            "issues": []
        }
        
        if "error" not in result:
            lines = result.get("output", "").split("\n")
            for line in lines:
                if line.startswith("#"):
                    continue
                
                # Parse request latency metrics
                if "apiserver_request_duration_seconds" in line:
                    self._parse_latency_metric(line, metrics)
                
                # Parse error rate metrics
                if "apiserver_request_total" in line and 'code="5' in line:
                    self._parse_error_metric(line, metrics)
                
                # Parse etcd request metrics
                if "etcd_request_duration_seconds" in line:
                    self._parse_etcd_metric(line, metrics)
        
        # Analyze metrics for issues
        self._analyze_metrics_issues(metrics)
        
        return metrics

    @tool("analyze_scheduler_decisions")
    def analyze_scheduler_decisions(self) -> Dict[str, Any]:
        """Analyze recent scheduler decisions and identify potential issues."""
        # Get scheduler logs
        result = self.execute_kubectl("logs -n kube-system -l component=kube-scheduler --tail=1000")
        
        analysis = {
            "scheduling_attempts": 0,
            "successful_schedules": 0,
            "failed_schedules": 0,
            "common_failure_reasons": {},
            "node_utilization": {},
            "issues": []
        }
        
        if "error" not in result:
            logs = result.get("output", "").split("\n")
            for log in logs:
                if "Successfully bound pod" in log:
                    analysis["successful_schedules"] += 1
                elif "Failed to schedule pod" in log:
                    analysis["failed_schedules"] += 1
                    # Extract failure reason
                    reason = self._extract_scheduling_failure_reason(log)
                    analysis["common_failure_reasons"][reason] = analysis["common_failure_reasons"].get(reason, 0) + 1
            
            analysis["scheduling_attempts"] = analysis["successful_schedules"] + analysis["failed_schedules"]
            
            # Get node utilization
            result = self.execute_kubectl("get nodes -o json")
            if "error" not in result:
                nodes = result.get("items", [])
                for node in nodes:
                    name = node["metadata"]["name"]
                    allocatable = node["status"]["allocatable"]
                    capacity = node["status"]["capacity"]
                    
                    cpu_alloc = float(allocatable["cpu"].rstrip("m")) / 1000
                    cpu_cap = float(capacity["cpu"].rstrip("m")) / 1000
                    mem_alloc = int(allocatable["memory"].rstrip("Ki")) / (1024 * 1024)
                    mem_cap = int(capacity["memory"].rstrip("Ki")) / (1024 * 1024)
                    
                    analysis["node_utilization"][name] = {
                        "cpu_utilization": (cpu_cap - cpu_alloc) / cpu_cap * 100,
                        "memory_utilization": (mem_cap - mem_alloc) / mem_cap * 100
                    }
            
            # Analyze for issues
            if analysis["failed_schedules"] > analysis["successful_schedules"] * 0.1:  # >10% failure rate
                analysis["issues"].append("High scheduling failure rate detected")
            
            for node, util in analysis["node_utilization"].items():
                if util["cpu_utilization"] > 80:
                    analysis["issues"].append(f"High CPU utilization on node {node}")
                if util["memory_utilization"] > 80:
                    analysis["issues"].append(f"High memory utilization on node {node}")
        
        return analysis

    def _parse_latency_metric(self, line: str, metrics: Dict) -> None:
        """Parse API server latency metrics."""
        if "bucket" in line:
            parts = line.split("{")[1].split("}")[0].split(",")
            resource = next((p.split("=")[1].strip('"') for p in parts if "resource=" in p), "")
            verb = next((p.split("=")[1].strip('"') for p in parts if "verb=" in p), "")
            
            if resource and verb:
                key = f"{resource}/{verb}"
                value = float(line.split(" ")[-1])
                metrics["request_latency"][key] = value

    def _parse_error_metric(self, line: str, metrics: Dict) -> None:
        """Parse API server error metrics."""
        parts = line.split("{")[1].split("}")[0].split(",")
        resource = next((p.split("=")[1].strip('"') for p in parts if "resource=" in p), "")
        code = next((p.split("=")[1].strip('"') for p in parts if "code=" in p), "")
        
        if resource and code:
            key = f"{resource}/{code}"
            value = float(line.split(" ")[-1])
            metrics["errors"][key] = value

    def _parse_etcd_metric(self, line: str, metrics: Dict) -> None:
        """Parse etcd request metrics."""
        if "operation" in line:
            parts = line.split("{")[1].split("}")[0].split(",")
            operation = next((p.split("=")[1].strip('"') for p in parts if "operation=" in p), "")
            
            if operation:
                value = float(line.split(" ")[-1])
                metrics["etcd_requests"][operation] = value

    def _analyze_metrics_issues(self, metrics: Dict) -> None:
        """Analyze metrics and identify potential issues."""
        # Check for high latency
        for endpoint, latency in metrics["request_latency"].items():
            if latency > 1.0:  # 1 second
                metrics["issues"].append(f"High latency for {endpoint}: {latency:.2f}s")
        
        # Check for high error rates
        total_requests = sum(metrics["request_rate"].values())
        if total_requests > 0:
            error_rate = sum(metrics["errors"].values()) / total_requests
            if error_rate > 0.05:  # 5% error rate
                metrics["issues"].append(f"High API server error rate: {error_rate:.2%}")
        
        # Check etcd request issues
        for operation, duration in metrics["etcd_requests"].items():
            if duration > 0.1:  # 100ms
                metrics["issues"].append(f"Slow etcd {operation} operations: {duration:.3f}s")

    def _extract_scheduling_failure_reason(self, log: str) -> str:
        """Extract the reason for a scheduling failure from a log line."""
        common_reasons = [
            "insufficient cpu",
            "insufficient memory",
            "node(s) had taint",
            "node(s) didn't match node selector",
            "0/1 nodes are available"
        ]
        
        log_lower = log.lower()
        for reason in common_reasons:
            if reason in log_lower:
                return reason
        return "unknown"

# Create the agent instance
k8s_agent = K8sControlPlaneAgent()

# List of available tools
k8s_tools = [
    k8s_agent.get_control_plane_status,
    k8s_agent.analyze_etcd_health,
    k8s_agent.check_api_server_metrics,
    k8s_agent.analyze_scheduler_decisions
] 