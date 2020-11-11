from typing import List


def flatten_list(list_to_flatten: List[List]) -> List:
    if not list_to_flatten:\
        return []
    if isinstance(list_to_flatten[0], list):
        return [val for sublist in list_to_flatten for val in sublist]
    return list_to_flatten
