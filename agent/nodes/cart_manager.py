from langchain.agents import create_agent
from langchain.agents.structured_output import ProviderStrategy
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool

from agent.model.graph_models import B2BGraphState
from agent.model.llm_models import Cart, Item, PlanType
from agent.nodes.common.find_plan_for_agent import find_plan_for_agent
from agent.nodes.common.model import llm

@tool
def add_item_to_cart(cart: Cart, item: Item) -> Cart:
    """
    Adds the provided item to cart.

    :param cart: Current cart and cart items
    :param item: Item that needs to be added
    :return: Updated cart whose items contains the new item
    """
    cart.items = cart.items + [item]
    return cart

@tool
def remove_item_from_cart(cart: Cart, item: Item) -> Cart:
    """
    Removes the provided item from cart
    :param cart: Current cart and cart items
    :param item: Item that needs to be removed
    :return: Updated cart whose items does not contain the provided item
    """
    new_items = []
    for current_item in cart.items: # Terrible loop. Needs to be optimized
        if current_item.item_id != item.item_id:
            new_items.append(current_item)

    cart.items = new_items
    return cart

@tool
def view_cart(cart: Cart) -> Cart:
    """
    Provides the latest cart and cart items
    :param cart: Current cart and cart items
    :return: Current cart and cart items
    """
    return cart

@tool
def clear_cart() -> Cart:
    """
    Clears the cart contents
    :return: Cleared cart
    """
    return Cart(items=[])

def cart_manager(state: B2BGraphState):
    system_prompt=f"""You are an cart management agent. You need to understand what user said and perform the 
    corresponding action using the provided tools, on the provided cart and items.
    
    input: {find_plan_for_agent(state['plans'], PlanType.CART_MANAGER)}
    cart: {state.get("cart", [])} 
    items: {state.get("items", [])}
    """

    cart_mgmt_agent = create_agent(
        model=llm,
        system_prompt=system_prompt,
        tools=[add_item_to_cart, remove_item_from_cart, view_cart, clear_cart],
        response_format=ProviderStrategy(Cart)
    )
    response = cart_mgmt_agent.invoke(
        {'messages': [HumanMessage(state['input'])]}
    )

    return {
        'messages': response['messages'],
        'cart': response['structured_response']
    }