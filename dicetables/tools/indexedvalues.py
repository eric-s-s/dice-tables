"""a simulated Counter dict with numpy arrays"""


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
    return generate_indexed_values(list(input_dict.items()))


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
        return [(index + self.start_index, value) for index, value in enumerate(self.raw_values) if value]

    def get_value_at_key(self, key):
        index = key - self.start_index
        if index < 0 or index >= len(self.raw_values):
            return 0
        else:
            return self.raw_values[index]

    def combine_with_dictionary(self, no_zero_values_dict):
        """
        :param no_zero_values_dict: MAY NOT BE EMPTY
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
