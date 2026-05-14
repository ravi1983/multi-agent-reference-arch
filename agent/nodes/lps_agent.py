import logging
import random

from langchain.agents import create_agent
from langchain.agents.structured_output import ProviderStrategy
from langchain.tools import tool
from langchain_core.messages import HumanMessage

from agent.model.graph_models import B2BGraphState
from agent.model.llm_models import Item, Items, OrderNumber, Cart, System, PlanType
from agent.nodes.common.find_plan_for_agent import find_plan_for_agent
from agent.nodes.common.model import llm

mock_items = [
    {
        "item_id": '123777',
        "description": 'Top load washer',
        "price": 100.10,
        "inventory": 1,
        "source": 'LPS'
    },
    {
        "item_id": '1234777',
        "description": 'Side load washer',
        "price":  47.91,
        "inventory": 15,
        "source": 'LPS'
    },
    {
        "item_id": '12345777',
        "description": 'Washer that can fit in your closet',
        "price": 31.91,
        "inventory": 50,
        "source": 'LPS'
    }
]

@tool
def lookup_item(item_id: str) -> Items:
    """
    Look up the item in the catalog and return the item details.

    :param item_id: Item identifier. Could be simple string such as "washer" or actual item id such as "1234".
    :return: List of items that match the item id.
    """

    logging.info(f'Looking up item: {item_id}')
    # Cast to Item
    return Items(items=[Item(**i) for i in mock_items], source=System.LPS)

@tool
def place_order(cart: Cart) -> Items:
    """
    Place a LPS order for the given cart.
    :param cart: Cart for which order needs to placed.
    :return: Items
    """

    logging.info(f'Placing order for cart {cart}')
    # Generates a random 10-digit string
    num = str(random.randint(10**9, 10**10 - 1))
    return1 = Items(items=cart.items, order_number = num, source = System.LPS)
    logging.info(f'Going to return {return1}')
    return return1
    

def lps_agent(state: B2BGraphState):
    system_prompt=f"""You are an order management agent for LPS. You need to understand what user said and perform the 
    corresponding action using the provided tools using the provided cart.
    
    You need to create ONE order for the given cart. Make sure you take only the items sourced from LPS.
    
    input: {find_plan_for_agent(state['plans'], PlanType.LPS_AGENT)}
    cart: {state.get("cart", [])} 
    """
    cart_mgmt_agent = create_agent(
        model=llm,
        system_prompt=system_prompt,
        tools=[lookup_item, place_order],
        response_format=ProviderStrategy(Items)
    )
    response = cart_mgmt_agent.invoke(
        {'messages': state['messages'] + [HumanMessage(state['input'])]}
    )

    result = {
        'messages': response['messages'],
        'items': response['structured_response'].items
    }
    if response["structured_response"].order_number is not None:
        result["order_numbers"] = [response["structured_response"].order_number]

    return result
