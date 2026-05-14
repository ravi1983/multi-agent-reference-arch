import logging

from agent.model.graph_models import B2BGraphState
from agent.model.llm_models import PlannerOutput
from agent.nodes.common.model import llm

planner_model = llm.with_structured_output(PlannerOutput)

def planner(state: B2BGraphState):
    out = planner_model.invoke([f""" You are a planner for a B2B e-commerce platform. You need to break down the user's 
    request into a series of steps. Use the following rules to break down the request:
    1. If the user is looking to do any cart operation, use the CART_MANAGER plan. But if you dont know price for the item, first use LOWES_AGENT AND LPS_AGENT 
    plan to get item details AND then use the CART_MANAGER plan.
    2. If the user is looking to do item lookup or order operation, use the LOWES_AGENT AND LPS_AGENT rule.
    3. If use is referring to previous conversations, ensure the plan contains the actual data they are referring to.
      
    You need to make decisions ONLY based on user's conversational context, their new input, cart, and items already looked up:
    Conversational context: {state["messages"]}
    New input: {state["input"]}
    Cart: {state.get("cart", [])}
    Items: {state.get("items", [])}
    """]
    )

    logging.info(f'Plans determined by planner is: {out.plans}')
    return {
        'plans': out.plans,
        'items': [],
        'order_numbers': []
    }