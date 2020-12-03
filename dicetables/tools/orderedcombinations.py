from itertools import combinations_with_replacement
from math import factorial
from typing import Dict, Tuple

from dicetables.eventsbases.integerevents import IntegerEvents


def count_unique_combination_keys(events: IntegerEvents, pool_size: int) -> int:
    """calculates how large the set of keys will be for `ordered_combinations_of_events(events, pool_size)`."""
    ans = 1
    dict_size = len(events.get_dict())
    for number in range(dict_size, dict_size + pool_size):
        ans *= number
    return ans // factorial(pool_size)


def largest_permitted_pool_size(events, max_number_of_keys):
    pool_size = 0
    num_keys = 0
    while num_keys <= max_number_of_keys:
        pool_size += 1
        num_keys = count_unique_combination_keys(events, pool_size)
    return pool_size - 1


def ordered_combinations_of_events(events: IntegerEvents, times: int) -> Dict[Tuple[int, ...], int]:
    base_dict = events.get_dict()
    ordered_combinations = combinations_with_replacement(sorted(base_dict.keys()), times)
    return {key: get_combination_occurrences(key, base_dict) for key in ordered_combinations}


def get_combination_occurrences(combination, base_dict):
    """simple calculation over tuple of sorted values and possibly repeating value
    to tell number of unique permutations.  so get_count((1, 2, 3)) = 3!.
    get_count((1, 2, 2, 3, 3)) = 5!/(2!*2!)"""
    answer = factorial(len(combination))
    current = combination[0]
    multiplier = base_dict[current]
    count = 0
    for el in combination:
        if el != current:
            count = 0
            multiplier = base_dict[el]
            current = el

        count += 1
        answer //= count
        answer *= multiplier

    return answer
