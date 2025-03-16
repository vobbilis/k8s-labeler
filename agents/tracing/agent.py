#!/usr/bin/env python3
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import requests
from langchain_core.tools import tool
import json

@dataclass
class TraceRequest:
    """Request for tracing information."""
    service_name: str
    operation_name: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    min_duration: Optional[str] = None
    max_duration: Optional[str] = None
    tags: Optional[Dict[str, str]] = None
    limit: int = 20

class JaegerClient:
    """Client for interacting with Jaeger's Query API."""
    
    def __init__(self, base_url: str = "http://localhost:30686"):
        self.base_url = base_url.rstrip("/")
    
    def get_services(self) -> List[str]:
        """Get list of available services."""
        try:
            response = requests.get(f"{self.base_url}/api/services")
            response.raise_for_status()
            return response.json()["data"]
        except Exception as e:
            return []
    
    def get_operations(self, service: str) -> List[str]:
        """Get list of operations for a service."""
        try:
            response = requests.get(f"{self.base_url}/api/operations", params={"service": service})
            response.raise_for_status()
            return response.json()["data"]
        except Exception as e:
            return []
    
    def find_traces(self, request: TraceRequest) -> List[Dict]:
        """Find traces matching the request criteria."""
        params = {
            "service": request.service_name,
            "limit": request.limit
        }
        
        if request.operation_name:
            params["operation"] = request.operation_name
        if request.start_time:
            params["start"] = request.start_time
        if request.end_time:
            params["end"] = request.end_time
        if request.min_duration:
            params["minDuration"] = request.min_duration
        if request.max_duration:
            params["maxDuration"] = request.max_duration
        if request.tags:
            params["tags"] = json.dumps(request.tags)
        
        try:
            response = requests.get(f"{self.base_url}/api/traces", params=params)
            response.raise_for_status()
            return response.json()["data"]
        except Exception as e:
            return []
    
    def get_trace(self, trace_id: str) -> Dict:
        """Get a specific trace by ID."""
        try:
            response = requests.get(f"{self.base_url}/api/traces/{trace_id}")
            response.raise_for_status()
            return response.json()["data"][0]
        except Exception as e:
            return {}

class TracingAgent:
    """Agent for application-level tracing through Jaeger."""
    
    def __init__(self):
        self.jaeger = JaegerClient()
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

    @tool("list_traced_services")
    def list_traced_services(self) -> str:
        """List all services that are being traced in Jaeger."""
        services = self.jaeger.get_services()
        if not services:
            return "No traced services found or unable to connect to Jaeger"
        
        return "Traced services:\n" + "\n".join(f"- {service}" for service in services)

    @tool("get_service_operations")
    def get_service_operations(self, service_name: str) -> str:
        """Get all traced operations for a specific service."""
        operations = self.jaeger.get_operations(service_name)
        if not operations:
            return f"No operations found for service {service_name}"
        
        return f"Operations for {service_name}:\n" + "\n".join(f"- {op}" for op in operations)

    @tool("analyze_service_traces")
    def analyze_service_traces(self, request: TraceRequest) -> Dict[str, Any]:
        """Analyze traces for a service and provide insights."""
        traces = self.jaeger.find_traces(request)
        if not traces:
            return {
                "status": "error",
                "message": f"No traces found for service {request.service_name}"
            }
        
        # Analyze trace data
        analysis = {
            "service": request.service_name,
            "trace_count": len(traces),
            "latency_stats": self._analyze_latencies(traces),
            "error_traces": self._find_error_traces(traces),
            "dependencies": self._analyze_dependencies(traces),
            "insights": self._generate_insights(traces)
        }
        
        return analysis

    @tool("get_service_dependencies")
    def get_service_dependencies(self, service_name: str) -> Dict[str, Any]:
        """Get and analyze service dependencies from traces."""
        request = TraceRequest(service_name=service_name, limit=50)
        traces = self.jaeger.find_traces(request)
        
        dependencies = self._analyze_dependencies(traces)
        return {
            "service": service_name,
            "dependencies": dependencies,
            "dependency_count": len(dependencies),
            "analysis": self._analyze_dependency_health(dependencies)
        }

    def _analyze_latencies(self, traces: List[Dict]) -> Dict[str, Any]:
        """Analyze latency patterns in traces."""
        durations = [trace.get("duration", 0) for trace in traces]
        if not durations:
            return {}
        
        return {
            "min": min(durations),
            "max": max(durations),
            "avg": sum(durations) / len(durations),
            "p95": sorted(durations)[int(len(durations) * 0.95)],
            "p99": sorted(durations)[int(len(durations) * 0.99)]
        }

    def _find_error_traces(self, traces: List[Dict]) -> List[Dict]:
        """Find traces containing errors."""
        error_traces = []
        for trace in traces:
            for span in trace.get("spans", []):
                if any(tag.get("key") == "error" for tag in span.get("tags", [])):
                    error_traces.append({
                        "trace_id": trace.get("traceID"),
                        "service": span.get("serviceName"),
                        "operation": span.get("operationName"),
                        "error_type": self._get_error_type(span)
                    })
        return error_traces

    def _analyze_dependencies(self, traces: List[Dict]) -> List[Dict]:
        """Analyze service dependencies from traces."""
        dependencies = {}
        for trace in traces:
            for span in trace.get("spans", []):
                service = span.get("serviceName")
                refs = span.get("references", [])
                for ref in refs:
                    parent_span = self._find_span_by_id(traces, ref.get("spanID"))
                    if parent_span:
                        parent_service = parent_span.get("serviceName")
                        key = f"{parent_service}->{service}"
                        if key not in dependencies:
                            dependencies[key] = {
                                "source": parent_service,
                                "target": service,
                                "count": 0,
                                "errors": 0
                            }
                        dependencies[key]["count"] += 1
                        if self._has_error(span):
                            dependencies[key]["errors"] += 1
        
        return list(dependencies.values())

    def _analyze_dependency_health(self, dependencies: List[Dict]) -> Dict[str, Any]:
        """Analyze the health of service dependencies."""
        return {
            "total_dependencies": len(dependencies),
            "error_prone_dependencies": [
                dep for dep in dependencies
                if dep["errors"] / dep["count"] > 0.1
            ],
            "healthy_dependencies": [
                dep for dep in dependencies
                if dep["errors"] / dep["count"] <= 0.1
            ]
        }

    def _generate_insights(self, traces: List[Dict]) -> List[str]:
        """Generate insights from trace analysis."""
        insights = []
        latency_stats = self._analyze_latencies(traces)
        error_traces = self._find_error_traces(traces)
        
        if latency_stats.get("p95", 0) > 1000:  # 1 second
            insights.append("High latency detected (p95 > 1s)")
        
        if len(error_traces) > len(traces) * 0.1:  # 10% error rate
            insights.append("High error rate detected (>10%)")
        
        dependencies = self._analyze_dependencies(traces)
        for dep in dependencies:
            if dep["errors"] / dep["count"] > 0.1:
                insights.append(f"High error rate in dependency {dep['source']} -> {dep['target']}")
        
        return insights

    def _get_error_type(self, span: Dict) -> str:
        """Extract error type from span tags."""
        for tag in span.get("tags", []):
            if tag.get("key") == "error.type":
                return tag.get("value", "unknown")
        return "unknown"

    def _find_span_by_id(self, traces: List[Dict], span_id: str) -> Optional[Dict]:
        """Find a span by its ID across all traces."""
        for trace in traces:
            for span in trace.get("spans", []):
                if span.get("spanID") == span_id:
                    return span
        return None

    def _has_error(self, span: Dict) -> bool:
        """Check if a span contains an error."""
        return any(
            tag.get("key") == "error" and tag.get("value", False)
            for tag in span.get("tags", [])
        )

# Create the agent instance
tracing_agent = TracingAgent()

# List of available tools
tracing_tools = [
    tracing_agent.list_traced_services,
    tracing_agent.get_service_operations,
    tracing_agent.analyze_service_traces,
    tracing_agent.get_service_dependencies
] 