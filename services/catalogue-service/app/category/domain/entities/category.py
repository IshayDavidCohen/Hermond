from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional


@dataclass
class Category:
    oid: str
    title: str
    icon: str
    image: str
    users: Dict[str, str]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def new(cls, *, oid: str, title: str, icon: str, image: str,
            users: Dict[str, str], now: Optional[datetime] = None) -> "Category":
        now = now or datetime.now()
        return cls(oid=oid, title=title,
                   icon=icon, image=image,
                   users=users,
                   created_at=now, updated_at=now,
        )

    @classmethod
    def to_entity(cls, doc: Dict) -> "Category":
        return cls(
            oid=str(doc['_id']),
            title=doc['title'],
            icon=doc['icon'],
            image=doc['image'],
            users={k: str(v) for k, v in doc['users'].items()},
            created_at=doc['created_at'],
            updated_at=doc['updated_at'],
        )

    def from_entity(self) -> Dict:
        return {
            '_id': self.oid,
            'title': self.title,
            'icon': self.icon,
            'image': self.image,
            'users': self.users,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }
