#!/usr/bin/env python3
from typing import Dict, Any, Optional
import requests
from langchain_core.tools import tool

class ObservabilityTool:
    """Tool for executing observability-related commands."""
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url

    def execute_kubectl(self, command: str, namespace: Optional[str] = None) -> Dict[str, Any]:
        """Execute a kubectl command through the API."""
        try:
            response = requests.post(
                f"{self.api_url}/execute",
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

@tool("get_prometheus_metrics")
def get_prometheus_metrics(namespace: str = "monitoring") -> str:
    """Get Prometheus metrics endpoints and targets."""
    tool = ObservabilityTool()
    commands = [
        "get pods -l app=prometheus",
        "get services -l app=prometheus",
        "describe service prometheus-server"
    ]
    
    output = []
    for cmd in commands:
        result = tool.execute_kubectl(cmd, namespace)
        if "output" in result:
            output.append(result["output"])
    
    return "\n".join(output) or "Failed to get Prometheus metrics"

@tool("get_grafana_dashboards")
def get_grafana_dashboards(namespace: str = "monitoring") -> str:
    """Get Grafana dashboards and status."""
    tool = ObservabilityTool()
    commands = [
        "get pods -l app=grafana",
        "get services -l app=grafana",
        "describe service grafana"
    ]
    
    output = []
    for cmd in commands:
        result = tool.execute_kubectl(cmd, namespace)
        if "output" in result:
            output.append(result["output"])
    
    return "\n".join(output) or "Failed to get Grafana information"

@tool("get_jaeger_traces")
def get_jaeger_traces(namespace: str = "observability") -> str:
    """Get Jaeger tracing information."""
    tool = ObservabilityTool()
    commands = [
        "get pods -l app=jaeger",
        "get services -l app=jaeger",
        "describe service jaeger-query"
    ]
    
    output = []
    for cmd in commands:
        result = tool.execute_kubectl(cmd, namespace)
        if "output" in result:
            output.append(result["output"])
    
    return "\n".join(output) or "Failed to get Jaeger information"

@tool("get_application_logs")
def get_application_logs(app_label: str, namespace: Optional[str] = None) -> str:
    """Get logs from all pods with a specific app label."""
    tool = ObservabilityTool()
    
    # First, get all pods with the specified label
    get_pods_cmd = f"get pods -l app={app_label}"
    pods_result = tool.execute_kubectl(get_pods_cmd, namespace)
    
    if "error" in pods_result:
        return f"Failed to find pods with label app={app_label}"
    
    # Get logs from each pod
    output = []
    pod_lines = pods_result["output"].split("\n")[1:]  # Skip header
    for line in pod_lines:
        if not line.strip():
            continue
        pod_name = line.split()[0]
        logs_result = tool.execute_kubectl(f"logs {pod_name}", namespace)
        if "output" in logs_result:
            output.append(f"=== Logs from {pod_name} ===")
            output.append(logs_result["output"])
    
    return "\n".join(output) or f"No logs found for app={app_label}"

# Create the tools list
observability_tools = [
    get_prometheus_metrics,
    get_grafana_dashboards,
    get_jaeger_traces,
    get_application_logs
] 