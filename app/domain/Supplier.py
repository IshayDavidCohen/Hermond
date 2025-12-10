from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class Supplier:
    id: Optional[str]
    business_id: str
    company_name: str
    desc: str
    icon: str
    banner: str
    email: str
    phone: str
    address: str
    shipping_address: str
    categories: List[str]
    approved_businesses: Dict[str, str]
    handshake_requests: Dict[str, str]
    items: List[str]
    active_orders: List[str]
    order_history: List[str]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def new(cls, *, business_id: str, company_name: str, desc: str, icon: str,
            banner: str, email: str, phone: str, address: str, shipping_address: str,
            categories: List[str], now: Optional[datetime] = None) -> "Supplier":
        now = now or datetime.now()
        # Create a new Supplier instance with default values for certain fields
        return cls(id=None, business_id=business_id, company_name=company_name,
                   desc=desc, icon=icon, banner=banner, email=email, phone=phone, address=address,
                   shipping_address=shipping_address, categories=categories, approved_businesses={},
                   handshake_requests={}, items=[], active_orders=[], order_history=[],
                   created_at=now, updated_at=now,
        )

    @classmethod
    def to_entity(cls, doc: Dict) -> "Supplier":
        # Convert MongoDB document to Supplier dataclass instance
        return cls(
            id=str(doc['_id']),
            business_id=str(doc['bid']),
            company_name=doc['company_name'],
            desc=doc['desc'],
            icon=doc['icon'],
            banner=doc['banner'],
            email=doc['email'],
            phone=doc['phone'],
            address=doc['address'],
            shipping_address=doc['shipping_address'],
            categories=doc['categories'],
            approved_businesses={k: str(v) for k, v in doc['approved_businesses'].items()},
            handshake_requests={k: str(v) for k, v in doc['handshake_requests'].items()},
            items=[str(item) for item in doc['items']],
            active_orders=[str(order) for order in doc['active_orders']],
            order_history=[str(order) for order in doc['order_history']],
            created_at=doc['created_at'],
            updated_at=doc['updated_at']
        )

    def from_entity(self) -> Dict:
        # Convert Supplier dataclass instance to MongoDB document
        doc = {
            '_id': self.id,
            'bid': self.business_id,
            'company_name': self.company_name,
            'desc': self.desc,
            'icon': self.icon,
            'banner': self.banner,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'shipping_address': self.shipping_address,
            'categories': self.categories,
            'approved_businesses': {k: v for k, v in self.approved_businesses.items()},
            'handshake_requests': {k: v for k, v in self.handshake_requests.items()},
            'items': [item for item in self.items],
            'active_orders': [order for order in self.active_orders],
            'order_history': [order for order in self.order_history],
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        if self.id is not None:
            doc['_id'] = self.id
        return doc

