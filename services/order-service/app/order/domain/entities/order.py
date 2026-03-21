from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class OrderStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    DELIVERING = "delivering"
    ARRIVED = "arrived"


@dataclass
class OrderedItem:
    item_id: str
    quantity: int
    base_price: float
    price_at_order: float

    @property
    def total_price_for_item(self) -> float:
        return self.quantity * self.price_at_order

    @classmethod
    def to_entity(cls, doc: Dict) -> "OrderedItem":
        return cls(
            item_id=str(doc["item_id"]),
            quantity=int(doc["quantity"]),
            base_price=float(doc["base_price"]),
            price_at_order=float(doc["price_at_order"]),
        )

    def from_entity(self) -> Dict:
        return {
            "item_id": self.item_id,
            "quantity": self.quantity,
            "base_price": self.base_price,
            "price_at_order": self.price_at_order,
            "total_price_for_item": self.total_price_for_item,
        }


@dataclass
class Order:
    id: Optional[str]
    supplier_id: str
    business_id: str
    estimated_eta: Optional[datetime]
    ordered_items: List[OrderedItem]
    total_price: float
    status: OrderStatus
    created_at: datetime
    updated_at: datetime

    @classmethod
    def new(
        cls,
        *,
        supplier_id: str,
        business_id: str,
        estimated_eta: Optional[datetime],
        ordered_items: List[OrderedItem],
        total_price: float,
        now: Optional[datetime] = None,
    ) -> "Order":
        now = now or datetime.now()
        return cls(
            id=None,
            supplier_id=supplier_id,
            business_id=business_id,
            estimated_eta=estimated_eta,
            ordered_items=ordered_items,
            total_price=total_price,
            status=OrderStatus.PENDING,
            created_at=now,
            updated_at=now,
        )

    @classmethod
    def to_entity(cls, doc: Dict) -> "Order":
        total = doc.get("total_price", doc.get("totalPrice"))
        return cls(
            id=str(doc["_id"]),
            supplier_id=str(doc["supplier_id"]),
            business_id=str(doc["business_id"]),
            estimated_eta=doc.get("estimated_eta"),
            ordered_items=[OrderedItem.to_entity(x) for x in doc.get("ordered_items", [])],
            total_price=float(total) if total is not None else 0.0,
            status=OrderStatus(doc["status"]),
            created_at=doc["created_at"],
            updated_at=doc["updated_at"],
        )

    def from_entity(self) -> Dict:
        doc = {
            "supplier_id": self.supplier_id,
            "business_id": self.business_id,
            "estimated_eta": self.estimated_eta,
            "ordered_items": [x.from_entity() for x in self.ordered_items],
            "totalPrice": self.total_price,
            "status": self.status.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        if self.id is not None:
            doc["_id"] = self.id
        return doc
