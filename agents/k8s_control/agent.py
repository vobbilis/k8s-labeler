#!/usr/bin/env python3
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import requests
from langchain_core.tools import tool

@dataclass
class ResourceRequest:
    """Request for Kubernetes resource information."""
    resource_type: str
    name: Optional[str] = None
    namespace: Optional[str] = None
    label_selector: Optional[str] = None
    field_selector: Optional[str] = None

class K8sControlAgent:
    """Agent for interacting with Kubernetes control plane components."""
    
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

    @tool("get_resource_status")
    def get_resource_status(self, request: ResourceRequest) -> str:
        """Get status of Kubernetes resources matching the request."""
        cmd_parts = ["get", request.resource_type]
        
        if request.name:
            cmd_parts.append(request.name)
        
        if request.label_selector:
            cmd_parts.extend(["-l", request.label_selector])
        
        if request.field_selector:
            cmd_parts.extend(["--field-selector", request.field_selector])
        
        command = " ".join(cmd_parts)
        result = self.execute_kubectl(command, request.namespace)
        return result.get("output", "") or result.get("error", f"Failed to get {request.resource_type}")

    @tool("describe_resource")
    def describe_resource(self, request: ResourceRequest) -> str:
        """Get detailed information about a specific Kubernetes resource."""
        if not request.name:
            return "Resource name is required for describe operation"
        
        command = f"describe {request.resource_type} {request.name}"
        result = self.execute_kubectl(command, request.namespace)
        return result.get("output", "") or result.get("error", f"Failed to describe {request.resource_type}")

    @tool("get_resource_metrics")
    def get_resource_metrics(self, request: ResourceRequest) -> str:
        """Get metrics for the specified resource."""
        if request.resource_type not in ["nodes", "pods"]:
            return "Metrics are only available for nodes and pods"
        
        command = f"top {request.resource_type}"
        if request.name:
            command += f" {request.name}"
        
        result = self.execute_kubectl(command, request.namespace)
        return result.get("output", "") or result.get("error", f"Failed to get metrics for {request.resource_type}")

    @tool("get_resource_logs")
    def get_resource_logs(self, request: ResourceRequest) -> str:
        """Get logs from a pod or deployment."""
        if not request.name:
            return "Resource name is required for logs operation"
        
        if request.resource_type not in ["pod", "deployment"]:
            return "Logs are only available for pods and deployments"
        
        command = f"logs {request.name}"
        result = self.execute_kubectl(command, request.namespace)
        return result.get("output", "") or result.get("error", f"Failed to get logs for {request.name}")

    @tool("check_resource_health")
    def check_resource_health(self, request: ResourceRequest) -> Dict[str, Any]:
        """Comprehensive health check for a Kubernetes resource."""
        health_info = {
            "status": "unknown",
            "details": {},
            "events": [],
            "warnings": []
        }
        
        # Get basic status
        status_result = self.get_resource_status(request)
        if "error" not in status_result:
            health_info["status"] = "healthy" if "Running" in status_result else "unhealthy"
            health_info["details"]["status"] = status_result
        
        # Get detailed information
        describe_result = self.describe_resource(request)
        if "error" not in describe_result:
            health_info["details"]["describe"] = describe_result
        
        # Get metrics if applicable
        if request.resource_type in ["nodes", "pods"]:
            metrics_result = self.get_resource_metrics(request)
            if "error" not in metrics_result:
                health_info["details"]["metrics"] = metrics_result
        
        # Get recent events
        events_cmd = f"get events --field-selector involvedObject.name={request.name}"
        events_result = self.execute_kubectl(events_cmd, request.namespace)
        if "error" not in events_result:
            health_info["events"] = events_result.get("output", "").split("\n")
        
        return health_info

# Create the agent instance
k8s_control_agent = K8sControlAgent()

# List of available tools
k8s_control_tools = [
    k8s_control_agent.get_resource_status,
    k8s_control_agent.describe_resource,
    k8s_control_agent.get_resource_metrics,
    k8s_control_agent.get_resource_logs,
    k8s_control_agent.check_resource_health
] 