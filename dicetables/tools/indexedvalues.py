"""
tool for combining dictionaries.
IndexedValues is a list with a start index.  It is for simulating dictionaries of {int: int>0}
"""


def generate_indexed_values(sorted_tuple_list):
    """

    :param sorted_tuple_list: may not be empty.\n
        [(int, int>0), ...]
    """
    start_val, values = make_start_index_and_list(sorted_tuple_list)
    return IndexedValues(start_val, values)


def generate_indexed_values_from_dict(input_dict) -> 'IndexedValues':
    """

    :param input_dict: may not be empty.\n
        {int: int>0, ...}
    """
    return generate_indexed_values(sorted(input_dict.items()))


def make_start_index_and_list(sorted_tuple_list):
    start_val = sorted_tuple_list[0][0]
    end_val = sorted_tuple_list[-1][0]
    out_list = [0] * (end_val - start_val + 1)
    for index, value in sorted_tuple_list:
        list_index = index - start_val
        out_list[list_index] = value
    return start_val, out_list


class IndexedValues(object):
    def __init__(self, start_index, sorted_values):
        """

        :param start_index: int
        :param sorted_values: may not be empty\n
            [int>=0, ...] \n
            values[0] != 0\n
            values[-1] != 0
        """
        self._start_index = start_index
        self._values = sorted_values[:]

    @property
    def raw_values(self):
        return self._values[:]

    @property
    def start_index(self):
        return self._start_index

    @property
    def index_range(self):
        return self.start_index, len(self.raw_values) + self.start_index - 1

    def get_dict(self):
        return {index + self.start_index: value for index, value in enumerate(self.raw_values) if value}

    def get_value_at_key(self, key):
        index = key - self.start_index
        if index < 0 or index >= len(self.raw_values):
            return 0
        else:
            return self.raw_values[index]

    def combine_with_dictionary(self, no_zero_values_dict):
        """
        :param no_zero_values_dict: may not be empty\n
            {int: int>0, ...}
        """
        base_list = self.raw_values

        first_event = min(no_zero_values_dict.keys())
        last_event = max(no_zero_values_dict.keys())

        new_start_index = self.start_index + first_event
        new_size = len(base_list) + last_event - first_event

        container_for_lists_to_combine = []

        for event, occurrences in no_zero_values_dict.items():
            index_offset = event - first_event
            new_group_of_events = get_events_list(base_list, occurrences, new_size, index_offset)
            container_for_lists_to_combine.append(new_group_of_events)
        new_raw_values = list(map(add_many, *container_for_lists_to_combine))
        return IndexedValues(new_start_index, new_raw_values)


def add_many(*args):
    return sum(args)


def get_events_list(base_list, occurrences, new_size, index_offset):
    if occurrences != 1:
        adjusted_events = [value * occurrences for value in base_list]
    else:
        adjusted_events = base_list[:]
    return change_list_len_with_zeroes(adjusted_events, new_size, index_offset)


def change_list_len_with_zeroes(input_list, new_size, index_offset):
    left = [0] * index_offset
    right = [0] * (new_size - index_offset - len(input_list))
    return left + input_list + right
