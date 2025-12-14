from bson import ObjectId
from bson.errors import InvalidId

def check_dict_validity(validity_map: dict, data: dict) -> bool:
    for k, v in validity_map.items():
        if (not isinstance(data.get(k), v)) or (not data.get(k)):
            return False
    return True

def to_oid(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except (InvalidId, TypeError):
        raise ValueError(f"Invalid ObjectId: {id_str}")