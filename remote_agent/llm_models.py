from enum import Enum
from typing import List

from pydantic import BaseModel


class System(str, Enum):
    ACME = "ACME"


class Item(BaseModel):
    item_id: str
    description: str
    price: float

    inventory: int
    source: System


class Items(BaseModel):
    items: List[Item]

    order_number: str | None = None
    source: System
