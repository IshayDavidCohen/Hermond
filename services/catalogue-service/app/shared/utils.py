from typing import Optional
from bson import ObjectId
from bson.errors import InvalidId


def to_oid(id_str: str) -> Optional[ObjectId]:
    try:
        return ObjectId(id_str)
    except (InvalidId, TypeError):
        return None
