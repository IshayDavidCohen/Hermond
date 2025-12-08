from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List


@dataclass
class Supplier:
    id: str
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
    def from_document(cls, doc: Dict) -> "Supplier":
        # Convert MongoDB document to Supplier dataclass instance
        return cls(
            id=str(doc['_id']),
            business_id=str(doc['bid']),
            company_name=doc['companyName'],
            desc=doc['desc'],
            icon=doc['icon'],
            banner=doc['banner'],
            email=doc['email'],
            phone=doc['phone'],
            address=doc['address'],
            shipping_address=doc['shippingAddress'],
            categories=doc['categories'],
            approved_businesses={k: str(v) for k, v in doc['approvedBusinesses'].items()},
            handshake_requests={k: str(v) for k, v in doc['handshakeRequests'].items()},
            items=[str(item) for item in doc['items']],
            active_orders=[str(order) for order in doc['activeOrders']],
            order_history=[str(order) for order in doc['orderHistory']],
            created_at=doc['createdAt'],
            updated_at=doc['updatedAt']
        )

    def to_document(self) -> Dict:
        # Convert Supplier dataclass instance to MongoDB document
        return {
            '_id': self.id,
            'bid': self.business_id,
            'companyName': self.company_name,
            'desc': self.desc,
            'icon': self.icon,
            'banner': self.banner,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'shippingAddress': self.shipping_address,
            'categories': self.categories,
            'approvedBusinesses': {k: v for k, v in self.approved_businesses.items()},
            'handshakeRequests': {k: v for k, v in self.handshake_requests.items()},
            'items': [item for item in self.items],
            'activeOrders': [order for order in self.active_orders],
            'orderHistory': [order for order in self.order_history],
            'createdAt': self.created_at,
            'updatedAt': self.updated_at
        }
