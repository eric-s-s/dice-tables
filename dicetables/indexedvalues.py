"""a simulated Counter dict with numpy arrays"""
from operator import add


def make_start_index_and_list(sorted_tuple_list):
    if not sorted_tuple_list:
        return 0, [1]
    start_val = sorted_tuple_list[0][0]
    end_val = sorted_tuple_list[-1][0]
    out_list = [0] * (end_val - start_val + 1)
    for index, value in sorted_tuple_list:
        list_index = index - start_val
        out_list[list_index] = value
    return start_val, out_list


def generate_indexed_values(tuple_list):
    tuple_list.sort()
    start_val, values = make_start_index_and_list(tuple_list)
    return IndexedValues(start_val, values)


def generate_indexed_values_from_dict(input_dict):
    return generate_indexed_values(sorted(input_dict.items()))


class IndexedValues(object):
    def __init__(self, start_val=0, values=None):
        self._start_val = start_val
        if not values:
            self._values = [1]
        else:
            self._values = values[:]

    @property
    def values(self):
        return self._values[:]

    @property
    def start_index(self):
        return self._start_val

    @property
    def range(self):
        return self.start_index, len(self.values) + self.start_index - 1

    def items(self):
        out = []
        for index, value in enumerate(self.values):
            if value:
                out.append((index + self.start_index, value))
        return out

    def get(self, key):
        index = key - self.start_index
        if index < 0 or index >= len(self.values):
            return 0
        else:
            return self.values[index]

    def add(self, other):
        start_index_diff = self.start_index - other.start_index
        if start_index_diff < 0:
            lower = self
            higher = other
        else:
            lower = other
            higher = self
        new_values = combine_values(lower.values, higher.values, abs(start_index_diff))
        return IndexedValues(lower.start_index, new_values)


def equalize_len_lower(lower, total_size):
    zeros = [0] * (total_size - len(lower))
    return lower + zeros


def equalize_len_higher(higher, total_size, start_index_diff):
    left = [0] * start_index_diff
    right = [0] * (total_size - start_index_diff - len(higher))
    return left + higher + right


def combine_values(lower, higher, start_index_diff):
    total_size = max(len(lower), len(higher) + start_index_diff)
    lower = equalize_len_lower(lower, total_size)
    higher = equalize_len_higher(higher, total_size, start_index_diff)
    new = list(map(add, lower, higher))
    return new
