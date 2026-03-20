from typing import List, Dict


def get_carousel_data(data_list: List[Dict], keys: Dict) -> List[Dict]:
    return [{k: element[v] for k, v in keys.items()} for element in data_list]
