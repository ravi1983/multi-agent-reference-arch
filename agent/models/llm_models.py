from enum import Enum
from pydantic import BaseModel, Field
from typing import List


### Planner models ###
class PlanType(str, Enum):
    # Cart node
    CART_MANAGER = "cart_manager"

    # Order node
    STARK_AGENT = "stark_agent"
    ACME_AGENT = "acme_agent"


class PlanCartOperation(str, Enum):
    ADD_TO_CART = "add_to_cart"
    REMOVE_FROM_CART = "remove_from_cart"
    GET_CART = "get_cart"
    CLEAR_CART = "clear_cart"


class Plan(BaseModel):
    plan: str
    plan_type: PlanType

    plan_cart_operation: PlanCartOperation


class PlannerOutput(BaseModel):
    plans: List[Plan]
    reason: str


### Item lookup models ###
class ItemLookupOutput(BaseModel):
    item_id: str
    description: str
    price: float


### Cart & Item models ###
class System(str, Enum):
    ACME = "ACME"
    STARK = "STARK"


class Item(BaseModel):
    item_id: str
    description: str
    price: float

    inventory: int
    source: System


class Cart(BaseModel):
    items: List[Item]


### Order models ###
class OrderNumber(BaseModel):
    order_number: str
    source: System
