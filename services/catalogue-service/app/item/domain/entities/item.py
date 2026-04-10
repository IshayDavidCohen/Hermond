from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional


@dataclass
class Item:
    id: Optional[str]
    supplier_id: str
    name: str
    category: str
    image: str
    desc: str
    base_price: float
    unit: str
    currency: str
    custom_prices: Dict[str, float]
    stock_quantity: int
    out_of_stock: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def new(cls, *, supplier_id: str, name: str, category: str, image: str,
            desc: str, base_price: float, unit: str, currency: str,
            stock_quantity: int = 0, out_of_stock: bool = False,
            now: Optional[datetime] = None) -> "Item":
        now = now or datetime.now()
        # Auto-set out of stock if created with 0 quantity
        if stock_quantity <= 0:
            out_of_stock = True
        return cls(
            id=None, supplier_id=supplier_id, name=name,
            category=category, image=image, desc=desc,
            base_price=base_price, unit=unit, currency=currency,
            custom_prices={},
            stock_quantity=max(0, stock_quantity),
            out_of_stock=out_of_stock,
            created_at=now, updated_at=now,
        )

    @classmethod
    def to_entity(cls, doc: Dict) -> "Item":
        return cls(
            id=str(doc['_id']),
            supplier_id=str(doc['supplier_id']),
            name=doc['name'],
            category=doc['category'],
            image=doc['image'],
            desc=doc['desc'],
            base_price=doc['base_price'],
            unit=doc['unit'],
            currency=doc['currency'],
            custom_prices={k: v for k, v in doc['custom_prices'].items()},
            stock_quantity=doc.get('stock_quantity', 0),
            out_of_stock=doc.get('out_of_stock', False),
            created_at=doc['created_at'],
            updated_at=doc['updated_at'],
        )

    def from_entity(self) -> Dict:
        doc = {
            'supplier_id': self.supplier_id,
            'name': self.name,
            'category': self.category,
            'image': self.image,
            'desc': self.desc,
            'base_price': self.base_price,
            'unit': self.unit,
            'currency': self.currency,
            'custom_prices': self.custom_prices,
            'stock_quantity': self.stock_quantity,
            'out_of_stock': self.out_of_stock,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }
        if self.id is not None:
            doc['_id'] = self.id
        return doc