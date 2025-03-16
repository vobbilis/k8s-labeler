#!/usr/bin/env python3
from typing import Dict, List, Tuple, Any, Annotated
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_anthropic import ChatAnthropic
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
import os
from dotenv import load_dotenv

# Import our agent tools
from k8s.agent import k8s_tools
from observability.agent import observability_tools

# Load environment variables
load_dotenv()

# Initialize the LLM
llm = ChatAnthropic(
    model="claude-3-sonnet-20240307",
    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
    temperature=0
)

class AgentState(dict):
    """State object for the multi-agent system."""
    messages: List[BaseMessage]
    current_agent: str
    context: Dict[str, Any]

def create_agent_executor(name: str, tools: List[Any]) -> AgentExecutor:
    """Create an agent executor with specific tools."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"""You are the {name} agent, specialized in {name}-related tasks in a Kubernetes environment.
You have access to the following tools:
{[tool.name + ": " + tool.description for tool in tools]}

Use these tools to help users understand and manage their Kubernetes cluster.
Always provide clear, concise responses and explain your actions.
If you encounter errors, explain them in user-friendly terms."""),
        MessagesPlaceholder(variable_name="messages"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    agent = create_openai_tools_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools)

def route_to_agent(state: AgentState) -> str:
    """Route the request to the appropriate agent based on the context."""
    last_message = state["messages"][-1]
    content = last_message.content.lower()
    
    # Basic routing logic
    if any(word in content for word in ["pod", "deployment", "service", "namespace"]):
        return "k8s"
    elif any(word in content for word in ["monitor", "metrics", "logs", "trace", "prometheus", "grafana", "jaeger"]):
        return "observability"
    elif any(word in content for word in ["security", "rbac", "policy", "network"]):
        return "security"
    elif any(word in content for word in ["deploy", "release", "update", "rollback"]):
        return "deployment"
    else:
        return "k8s"  # Default to k8s agent

def setup_multi_agent_system() -> StateGraph:
    """Set up the multi-agent system with LangGraph."""
    # Initialize tools for each agent
    security_tools = []  # TODO: Add security tools
    deployment_tools = []  # TODO: Add deployment tools
    
    # Create agent executors
    agents = {
        "k8s": create_agent_executor("Kubernetes", k8s_tools),
        "observability": create_agent_executor("Observability", observability_tools),
        "security": create_agent_executor("Security", security_tools),
        "deployment": create_agent_executor("Deployment", deployment_tools),
    }
    
    # Create the graph
    workflow = StateGraph(AgentState)
    
    # Add the routing node
    workflow.add_node("route", route_to_agent)
    
    # Add agent nodes
    for name, agent in agents.items():
        workflow.add_node(name, agent)
    
    # Add edges
    workflow.add_edge("route", "k8s")
    workflow.add_edge("route", "observability")
    workflow.add_edge("route", "security")
    workflow.add_edge("route", "deployment")
    
    # Set entry point
    workflow.set_entry_point("route")
    
    # Add edges from agents to end
    for name in agents:
        workflow.add_edge(name, END)
    
    return workflow

def main():
    """Main function to run the multi-agent system."""
    workflow = setup_multi_agent_system()
    app = workflow.compile()
    
    print("🤖 Multi-Agent Kubernetes Assistant Ready!")
    print("Available agents: Kubernetes, Observability")
    print("Type 'exit' to quit")
    
    while True:
        try:
            user_input = input("\nWhat would you like to know about your cluster? ")
            if user_input.lower() == 'exit':
                break
            
            # Initialize state
            state = AgentState(
                messages=[HumanMessage(content=user_input)],
                current_agent="",
                context={}
            )
            
            # Run the workflow
            result = app.invoke(state)
            print("\nResponse:", result["messages"][-1].content)
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")

if __name__ == "__main__":
    main() 