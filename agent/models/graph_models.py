from operator import add
from typing import TypedDict, Annotated, List

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

from agent.models.llm_models import Cart, Item, OrderNumber, Plan


class B2BGraphState(TypedDict):
    input: str
    messages: Annotated[List[AnyMessage], add_messages]
    a2a_context_id: str

    plans: List[Plan]

    items: Annotated[List[Item], add]

    cart: Cart
    order_numbers: Annotated[List[OrderNumber], add]

    summary: str
