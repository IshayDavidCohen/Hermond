from typing import List, Dict


def check_dict_validity(validity_map: dict, data: dict) -> bool:
    for k, v in validity_map.items():
        if (not isinstance(data.get(k), v)) or (not data.get(k)):
            return False
    return True
