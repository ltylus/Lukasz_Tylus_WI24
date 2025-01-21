# from collections import defaultdict as dd
# from itertools import product
from typing import Any, Dict, List, Tuple


def task_1(data_1: Dict[str, int], data_2: Dict[str, int]):
    data_3 = data_1.copy()
    for key, value in data_2.items():
        if key in data_3:
            data_3[key] += value
        else:
            data_3[key] = value
    return data_3


def task_2():
  dict = {}
  i=1
  while i<16:
    dict[i] = i**2
    i+=1
  return dict

from itertools import product

def task_3(data: Dict[Any, List[str]]):
    combinations = list(product(*data.values()))
    return [''.join(combination) for combination in combinations]


def task_4(data: Dict[str, int]):
    sorted_keys = sorted(data, key=data.get, reverse= True)
    return sorted_keys[:3]


def task_5(data: List[Tuple[Any, Any]]) -> Dict[str, List[int]]:
    grouped_dict = {}
    for key, value in data:
        if key not in grouped_dict:
            grouped_dict[key] = []
        grouped_dict[key].append(value)
    return grouped_dict


def task_6(data: List[Any]):
    unique = set()
    result = []
    for i in data:
        if i not in unique:
            result.append(i)
            unique.add(i)
    
    return result


def task_7(words: [List[str]]) -> str:
    if not words:
        return ""
    prefix = words[0]

    for string in words[1:]:
        while not string.startswith(prefix):
            prefix = prefix[:-1]
    return prefix


def task_8(haystack: str, needle: str) -> int:
    if needle == "":
        return 0
    return haystack.find(needle)
