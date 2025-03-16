#!/usr/bin/env python3
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from uuid import uuid4
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import JsonOutputParser
from langgraph.graph import StateGraph, END
import json
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

from ..k8s.agent import K8sControlPlaneAgent
from ..tracing.agent import TracingAgent, TraceRequest

# Load environment variables
load_dotenv()

@dataclass
class Entity:
    """Represents an identified entity in user input."""
    type: str  # service, pod, trace, metric, error
    name: str
    namespace: Optional[str] = None
    confidence: float = 1.0

@dataclass
class TaskContext:
    """Context for a specific task in the workflow."""
    task_id: str
    entities: List[Entity]
    previous_actions: List[Dict]
    conversation_id: str
    priority: str = "normal"

@dataclass
class AnalysisRequest:
    """Request for system analysis."""
    service_name: Optional[str] = None
    operation_name: Optional[str] = None
    time_window: Optional[int] = None  # in minutes
    include_control_plane: bool = True
    include_tracing: bool = True

class OrchestratorAgent:
    """Agent for coordinating between K8s Control Plane and Tracing agents."""
    
    def __init__(self):
        self.k8s_agent = K8sControlPlaneAgent()
        self.tracing_agent = TracingAgent()
        self.llm = ChatAnthropic(
            model="claude-3-sonnet-20240307",
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            temperature=0
        )
        self.entity_classifier = self._create_entity_classifier()
        self.cot_reasoner = self._create_cot_reasoner()
        self.result_synthesizer = self._create_result_synthesizer()

    def _create_entity_classifier(self) -> ChatPromptTemplate:
        """Creates the entity classifier prompt."""
        return ChatPromptTemplate.from_messages([
            ("system", """You are an entity classifier for Kubernetes operations.
Identify entities in user queries and classify them with high precision.
Entity types: service, pod, trace, metric, error

Output JSON format:
{
    "entities": [
        {
            "type": "entity_type",
            "name": "entity_name",
            "namespace": "optional_namespace",
            "confidence": 0.9
        }
    ]
}"""),
            ("user", "{input}"),
        ])

    def _create_cot_reasoner(self) -> ChatPromptTemplate:
        """Creates the chain of thought reasoning prompt."""
        return ChatPromptTemplate.from_messages([
            ("system", """You are a reasoning engine for Kubernetes operations.
Break down complex queries into logical steps and determine required actions.

Output JSON format:
{
    "reasoning_steps": [
        {
            "step": 1,
            "action": "action_name",
            "agent": "agent_name",
            "parameters": {},
            "rationale": "why this step is needed"
        }
    ]
}"""),
            ("user", "{input}"),
            ("user", "Entities found: {entities}"),
        ])

    def _create_result_synthesizer(self) -> ChatPromptTemplate:
        """Creates the result synthesis prompt."""
        return ChatPromptTemplate.from_messages([
            ("system", """You are a result synthesizer for Kubernetes operations.
Combine technical data into clear, actionable insights.
Prioritize critical information and maintain conversation coherence.

Output format: Natural language response that:
1. Summarizes the findings
2. Highlights important details
3. Provides actionable recommendations
4. Maintains context from previous interactions"""),
            ("user", "Previous context: {context}"),
            ("user", "Agent results: {results}"),
        ])

    async def classify_entities(self, query: str) -> List[Entity]:
        """Identifies and classifies entities in the user query."""
        response = await self.llm.ainvoke(
            self.entity_classifier.format_messages(input=query)
        )
        
        try:
            result = json.loads(response.content)
            return [Entity(**entity) for entity in result["entities"]]
        except Exception as e:
            print(f"Error parsing entity classification: {e}")
            return []

    async def generate_reasoning_steps(self, query: str, entities: List[Entity]) -> List[Dict]:
        """Generates chain of thought reasoning steps."""
        response = await self.llm.ainvoke(
            self.cot_reasoner.format_messages(
                input=query,
                entities=json.dumps([vars(e) for e in entities])
            )
        )
        
        try:
            result = json.dumps(response.content)
            return json.loads(result)["reasoning_steps"]
        except Exception as e:
            print(f"Error parsing reasoning steps: {e}")
            return []

    async def synthesize_results(
        self,
        context: TaskContext,
        agent_results: Dict[str, Any]
    ) -> str:
        """Synthesizes results from multiple agents into a coherent response."""
        response = await self.llm.ainvoke(
            self.result_synthesizer.format_messages(
                context=json.dumps(vars(context)),
                results=json.dumps(agent_results)
            )
        )
        return response.content

    async def process_query(self, query: str, conversation_id: Optional[str] = None) -> Dict:
        """Process a user query through the full orchestration pipeline."""
        # Create or use existing conversation ID
        conv_id = conversation_id or str(uuid4())
        
        # Step 1: Entity Classification
        entities = await self.classify_entities(query)
        
        # Step 2: Chain of Thought Reasoning
        reasoning_steps = await self.generate_reasoning_steps(query, entities)
        
        # Step 3: Create Task Context
        context = TaskContext(
            task_id=str(uuid4()),
            entities=entities,
            previous_actions=[],
            conversation_id=conv_id
        )
        
        # Step 4: Execute Reasoning Steps
        agent_results = {}
        for step in reasoning_steps:
            # TODO: Implement agent execution based on reasoning steps
            pass
        
        # Step 5: Synthesize Results
        response = await self.synthesize_results(context, agent_results)
        
        return {
            "conversation_id": conv_id,
            "task_id": context.task_id,
            "entities": [vars(e) for e in entities],
            "reasoning_steps": reasoning_steps,
            "response": response
        }

    def analyze_system_health(self, request: AnalysisRequest) -> Dict[str, Any]:
        """
        Perform a comprehensive system health analysis using both K8s and tracing data.
        This is the main entry point for system analysis.
        """
        analysis = {
            "timestamp": datetime.utcnow().isoformat(),
            "control_plane_status": None,
            "tracing_analysis": None,
            "correlated_issues": [],
            "recommendations": []
        }

        # Gather control plane metrics if requested
        if request.include_control_plane:
            analysis["control_plane_status"] = self._analyze_control_plane()

        # Gather tracing data if requested
        if request.include_tracing and request.service_name:
            analysis["tracing_analysis"] = self._analyze_tracing(request)

        # Correlate issues and generate recommendations
        if analysis["control_plane_status"] and analysis["tracing_analysis"]:
            self._correlate_issues(analysis)
        
        return analysis

    def _analyze_control_plane(self) -> Dict[str, Any]:
        """Analyze Kubernetes control plane health."""
        analysis = {
            "component_status": self.k8s_agent.get_control_plane_status(),
            "etcd_health": self.k8s_agent.analyze_etcd_health(),
            "api_server_metrics": self.k8s_agent.check_api_server_metrics(),
            "scheduler_analysis": self.k8s_agent.analyze_scheduler_decisions(),
            "overall_health": "healthy",
            "critical_issues": []
        }

        # Analyze component status
        for component, status in analysis["component_status"].items():
            if status.get("not_ready", 0) > 0 or len(status.get("issues", [])) > 0:
                analysis["critical_issues"].extend(
                    [f"{component}: {issue}" for issue in status.get("issues", [])]
                )

        # Analyze etcd health
        if analysis["etcd_health"]["unhealthy_endpoints"] > 0:
            analysis["critical_issues"].extend(analysis["etcd_health"]["issues"])

        # Analyze API server metrics
        if analysis["api_server_metrics"]["issues"]:
            analysis["critical_issues"].extend(analysis["api_server_metrics"]["issues"])

        # Analyze scheduler decisions
        if analysis["scheduler_analysis"]["issues"]:
            analysis["critical_issues"].extend(analysis["scheduler_analysis"]["issues"])

        # Determine overall health
        if analysis["critical_issues"]:
            analysis["overall_health"] = "degraded" if len(analysis["critical_issues"]) < 3 else "critical"

        return analysis

    def _analyze_tracing(self, request: AnalysisRequest) -> Dict[str, Any]:
        """Analyze application tracing data."""
        # Prepare trace request
        trace_request = TraceRequest(
            service_name=request.service_name,
            operation_name=request.operation_name,
            start_time=(datetime.utcnow() - timedelta(minutes=request.time_window or 60)).isoformat() if request.time_window else None,
            end_time=datetime.utcnow().isoformat(),
            limit=100
        )

        # Get service dependencies
        dependencies = self.tracing_agent.get_service_dependencies(request.service_name)
        
        # Analyze traces
        trace_analysis = self.tracing_agent.analyze_service_traces(trace_request)
        
        analysis = {
            "service_health": {
                "name": request.service_name,
                "status": "healthy",
                "issues": []
            },
            "dependencies": dependencies,
            "latency_analysis": trace_analysis.get("latency_stats", {}),
            "error_analysis": trace_analysis.get("error_traces", []),
            "operation_stats": {}
        }

        # Analyze for issues
        if trace_analysis.get("issues"):
            analysis["service_health"]["issues"].extend(trace_analysis["issues"])
            if len(trace_analysis["issues"]) > 2:
                analysis["service_health"]["status"] = "degraded"
            if len(trace_analysis["issues"]) > 5:
                analysis["service_health"]["status"] = "critical"

        # Add dependency health information
        dep_analysis = dependencies.get("analysis", {})
        if dep_analysis.get("error_prone_dependencies"):
            analysis["service_health"]["issues"].extend([
                f"High error rate in dependency: {dep['source']} -> {dep['target']}"
                for dep in dep_analysis["error_prone_dependencies"]
            ])

        return analysis

    def _correlate_issues(self, analysis: Dict[str, Any]) -> None:
        """Correlate issues between control plane and tracing data."""
        control_plane = analysis["control_plane_status"]
        tracing = analysis["tracing_analysis"]
        
        if not control_plane or not tracing:
            return

        # Correlation patterns to check
        self._check_scheduling_impact(analysis)
        self._check_api_server_impact(analysis)
        self._check_etcd_impact(analysis)
        self._generate_recommendations(analysis)

    def _check_scheduling_impact(self, analysis: Dict[str, Any]) -> None:
        """Check for correlations between scheduling issues and service performance."""
        scheduler = analysis["control_plane_status"]["scheduler_analysis"]
        tracing = analysis["tracing_analysis"]
        
        if scheduler["failed_schedules"] > 0 and tracing["service_health"]["status"] != "healthy":
            analysis["correlated_issues"].append({
                "type": "scheduling_impact",
                "description": "Service degradation may be related to pod scheduling issues",
                "evidence": {
                    "failed_schedules": scheduler["failed_schedules"],
                    "service_status": tracing["service_health"]["status"]
                }
            })

    def _check_api_server_impact(self, analysis: Dict[str, Any]) -> None:
        """Check for correlations between API server issues and service performance."""
        api_metrics = analysis["control_plane_status"]["api_server_metrics"]
        tracing = analysis["tracing_analysis"]
        
        high_latency_endpoints = [
            endpoint for endpoint, latency in api_metrics.get("request_latency", {}).items()
            if latency > 1.0
        ]
        
        if high_latency_endpoints and tracing["latency_analysis"].get("p95", 0) > 1000:
            analysis["correlated_issues"].append({
                "type": "api_server_latency_impact",
                "description": "Service latency may be affected by API server performance",
                "evidence": {
                    "high_latency_endpoints": high_latency_endpoints,
                    "service_p95_latency": tracing["latency_analysis"]["p95"]
                }
            })

    def _check_etcd_impact(self, analysis: Dict[str, Any]) -> None:
        """Check for correlations between etcd issues and service performance."""
        etcd = analysis["control_plane_status"]["etcd_health"]
        tracing = analysis["tracing_analysis"]
        
        if etcd["issues"] and tracing["service_health"]["status"] != "healthy":
            analysis["correlated_issues"].append({
                "type": "etcd_impact",
                "description": "Service issues may be related to etcd problems",
                "evidence": {
                    "etcd_issues": etcd["issues"],
                    "service_issues": tracing["service_health"]["issues"]
                }
            })

    def _generate_recommendations(self, analysis: Dict[str, Any]) -> None:
        """Generate recommendations based on correlated issues."""
        for issue in analysis["correlated_issues"]:
            if issue["type"] == "scheduling_impact":
                analysis["recommendations"].append({
                    "priority": "high",
                    "action": "Review node resources and pod resource requests/limits",
                    "details": "High scheduling failure rate is affecting service performance"
                })
            
            elif issue["type"] == "api_server_latency_impact":
                analysis["recommendations"].append({
                    "priority": "medium",
                    "action": "Consider scaling API server resources",
                    "details": "API server latency is impacting service response times"
                })
            
            elif issue["type"] == "etcd_impact":
                analysis["recommendations"].append({
                    "priority": "high",
                    "action": "Investigate etcd health issues",
                    "details": "etcd problems are affecting overall system stability"
                })

        # Add general recommendations based on service health
        service_health = analysis["tracing_analysis"]["service_health"]
        if service_health["status"] == "critical":
            analysis["recommendations"].append({
                "priority": "critical",
                "action": "Consider rolling back recent deployments",
                "details": "Service is in critical state with multiple issues"
            })

# Create the orchestrator instance
orchestrator = OrchestratorAgent()

# Example usage:
# analysis = orchestrator.analyze_system_health(
#     AnalysisRequest(
#         service_name="my-service",
#         time_window=30,
#         include_control_plane=True,
#         include_tracing=True
#     )
# ) 