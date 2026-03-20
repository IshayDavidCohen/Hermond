from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class Business:
    id: Optional[str]
    bid: str
    company_name: str
    desc: str
    icon: str
    banner: str
    email: str
    phone: str
    address: str
    shipping_address: str
    categories: List[str]
    my_suppliers: Dict[str, str]
    handshake_requests: Dict[str, str]
    active_orders: List[str]
    order_history: List[str]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def new(cls, *, bid: str, company_name: str, desc: str, icon: str,
            banner: str, email: str, phone: str, address: str, shipping_address: str,
            categories: List[str], now: Optional[datetime] = None) -> "Business":
        now = now or datetime.now()
        return cls(id=None, bid=bid, company_name=company_name,
                   desc=desc, icon=icon, banner=banner, email=email, phone=phone, address=address,
                   shipping_address=shipping_address, categories=categories,
                   my_suppliers={}, handshake_requests={},
                   active_orders=[], order_history=[],
                   created_at=now, updated_at=now,
        )

    @classmethod
    def to_entity(cls, doc: Dict) -> "Business":
        return cls(
            id=str(doc['_id']),
            bid=str(doc['bid']),
            company_name=doc['company_name'],
            desc=doc['desc'],
            icon=doc['icon'],
            banner=doc['banner'],
            email=doc['email'],
            phone=doc['phone'],
            address=doc['address'],
            shipping_address=doc['shipping_address'],
            categories=doc['categories'],
            my_suppliers={k: str(v) for k, v in doc['my_suppliers'].items()},
            handshake_requests={k: str(v) for k, v in doc['handshake_requests'].items()},
            active_orders=[str(order) for order in doc['active_orders']],
            order_history=[str(order) for order in doc['order_history']],
            created_at=doc['created_at'],
            updated_at=doc['updated_at'],
        )

    def from_entity(self) -> Dict:
        doc = {
            "bid": self.bid,
            "company_name": self.company_name,
            "desc": self.desc,
            "icon": self.icon,
            "banner": self.banner,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "shipping_address": self.shipping_address,
            "categories": self.categories,
            "my_suppliers": self.my_suppliers,
            "handshake_requests": self.handshake_requests,
            "active_orders": self.active_orders,
            "order_history": self.order_history,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        if self.id is not None:
            doc["_id"] = self.id
        return doc
