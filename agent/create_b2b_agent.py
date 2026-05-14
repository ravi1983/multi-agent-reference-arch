import logging

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph

from agent.models.graph_models import B2BGraphState
from agent.nodes.cart_manager import cart_manager
from agent.nodes.acme_agent import acme_agent
from agent.nodes.stark_agent import stark_agent
from agent.nodes.planner import planner
from agent.nodes.summarizer import summarizer


def planner_condition(state: B2BGraphState):
    # The enum value is same as the node names. So the planner output can be directly mapped to node.
    nodes = [plan.plan_type.value for plan in state["plans"]]
    logging.info(f"Nodes to be invoked are: {nodes}")
    return nodes


def create_b2b_agent():
    agent_builder = StateGraph(B2BGraphState)

    # Add nodes
    agent_builder.add_node("planner", planner)
    agent_builder.add_node("summarizer", summarizer)
    agent_builder.add_node("cart_manager", cart_manager)
    agent_builder.add_node("stark_agent", stark_agent)
    agent_builder.add_node("acme_agent", acme_agent)

    # Add edges (conditions)
    agent_builder.add_edge(START, "planner")
    agent_builder.add_edge(START, "summarizer")
    agent_builder.add_conditional_edges(
        "planner", planner_condition, ["cart_manager", "stark_agent", "acme_agent"]
    )

    # Add end edges
    agent_builder.add_edge("cart_manager", END)
    agent_builder.add_edge("stark_agent", END)
    agent_builder.add_edge("acme_agent", END)
    agent_builder.add_edge("summarizer", END)

    return agent_builder.compile(checkpointer=InMemorySaver())
