import logging
import random
from typing import List

from google.adk.agents.llm_agent import LlmAgent
from google.adk.a2a.utils.agent_to_a2a import to_a2a

from remote_agent.llm_models import Item, Items, System

mock_items = [
    {
        "item_id": "123999",
        "description": "Large HE asher",
        "price": 110.10,
        "inventory": 10,
        "source": "ACME",
    },
    {
        "item_id": "1234999",
        "description": "Maytag washer",
        "price": 147.91,
        "inventory": 51,
        "source": "ACME",
    },
    {
        "item_id": "123459991",
        "description": "Apartment sized washer",
        "price": 689.91,
        "inventory": 10,
        "source": "ACME",
    },
]


def lookup_item(item_id: str) -> Items:
    """
    Look up the item in the catalog and return the item details.

    :param item_id: Item identifier. Could be simple string such as "washer" or actual item id such as "1234".
    :return: List of items that match the item id.
    """

    logging.info(f"Looking up item: {item_id}")
    return Items(items=[Item(**i) for i in mock_items], source=System.ACME)


def place_order(items: List[Item]) -> Items:
    """
    Place a Acme order for the given cart.
    :param cart: Cart for which order needs to placed.
    :return: OrderNumber
    """

    logging.info(f"Placing order for cart {items}")
    # Generates a random 10-digit string
    num = str(random.randint(10**9, 10**10 - 1))
    print(f"Order number: {num}")
    return Items(items=items, order_number=num, source=System.ACME)


acme_agent = LlmAgent(
    name="acme_agent",
    model="openai/gpt-4.1",
    description="You are a Acme corp agent. You are able to look up items in the catalog and place an order for them.",
    instruction="""You are an item lookup and order management agent for Acme. You need to understand what user said and perform the
corresponding action using the provided tools.
You need to create ONE order for the given cart.
You can only use the following tools:
1. lookup_item
2. place_order
""",
    tools=[lookup_item, place_order],
    output_schema=Items,
)

root_agent = to_a2a(acme_agent, port=9095)
# root_agent = acme_agent


# uvicorn remote_agent.main_agent:root_agent --port 9095
