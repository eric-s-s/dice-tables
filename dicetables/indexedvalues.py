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
    def __init__(self, start_index=0, values=None):
        self._start_index = start_index
        if not values:
            self._values = [1]
        else:
            self._values = values[:]

    @property
    def raw_values(self):
        return self._values[:]

    @property
    def start_index(self):
        return self._start_index

    @property
    def index_range(self):
        return self.start_index, len(self.raw_values) + self.start_index - 1

    def get_items(self):
        out = []
        for index, value in enumerate(self.raw_values):
            if value:
                out.append((index + self.start_index, value))
        return out

    def get_value_at_key(self, key):
        index = key - self.start_index
        if index < 0 or index >= len(self.raw_values):
            return 0
        else:
            return self.raw_values[index]

    def combine(self, other):
        start_index_diff = self.start_index - other.start_index
        if start_index_diff < 0:
            lower = self
            higher = other
        else:
            lower = other
            higher = self
        new_values = combine_values(lower.raw_values, higher.raw_values, abs(start_index_diff))
        return IndexedValues(lower.start_index, new_values)

    def combine_with_events_list(self, sorted_tuple_list_of_events):
        base_list = self.raw_values
        current_size = len(base_list)
        current_start_index = self.start_index
        new_start_index = current_start_index + sorted_tuple_list_of_events[0][0]
        new_size = current_size + sorted_tuple_list_of_events[-1][0] - sorted_tuple_list_of_events[0][0]
        big_list = []
        for event, freq in sorted_tuple_list_of_events:
            index_diff = current_start_index + event - new_start_index
            if freq != 1:
                use_list = [value * freq for value in base_list]
            else:
                use_list = base_list[:]
            big_list.append(equalize_len_higher(use_list, new_size, index_diff))
        new_raw_values = list(map(add_many, *big_list))
        return IndexedValues(new_start_index, new_raw_values)


def add_many(*args):
    return sum(args)


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
