"""a class that combines a dictionary with valid IntegerEvents"""
from tools.indexedvalues import generate_indexed_values_from_dict


class DictCombiner(object):
    def __init__(self, dictionary):
        self._dict = dictionary

    def get_dict(self):
        return self._dict.copy()

    def combine_by_flattened_list(self, times, integer_events):
        events_dict = DictCombiner(self.get_dict())
        flattened_list = flatten_events_tuples(integer_events.all_events)
        for _ in range(times):
            events_dict = events_dict.combine_once_with_flattened_list(flattened_list)
        return events_dict

    def combine_once_with_flattened_list(self, flattened_list):
        new_dict = {}
        for event, current_frequency in self._dict.items():
            for new_event in flattened_list:
                new_dict[event + new_event] = (new_dict.get(event + new_event, 0) + current_frequency)
        return DictCombiner(new_dict)

    def combine_by_tuple_list(self, times, integer_events):
        events_tuples = integer_events.all_events
        new_events = DictCombiner(self.get_dict())
        for _ in range(times):
            new_events = new_events.combine_once_with_tuple_list(events_tuples)
        return new_events

    def combine_once_with_tuple_list(self, tuple_list):
        new_dict = {}
        for event, current_frequency in self._dict.items():
            for new_event, frequency in tuple_list:
                new_dict[event + new_event] = (new_dict.get(event + new_event, 0) + frequency * current_frequency)
        return DictCombiner(new_dict)

    def combine_by_indexed_values(self, times, integer_events):
        events_tuples = integer_events.all_events
        indexed_values_to_update = generate_indexed_values_from_dict(self._dict)
        for _ in range(times):
            indexed_values_to_update = indexed_values_to_update.combine_with_events_list(events_tuples)
        return DictCombiner(dict(indexed_values_to_update.get_items()))

    def combine_by_fastest(self, times, integer_events):
        method_dict = {'tuple_list': self.combine_by_tuple_list,
                       'flattened_list': self.combine_by_flattened_list,
                       'indexed_values': self.combine_by_indexed_values}
        method = self.get_fastest_combine_method(times, integer_events)

        return method_dict[method](times, integer_events)

    def get_fastest_combine_method(self, times, integer_events):
        events_tuples = integer_events.all_events
        first_comparison = self._compare_tuple_list_with_flattened_list(events_tuples)
        second_comparison = self._compare_with_indexed_values(first_comparison, times, events_tuples)
        return second_comparison

    @staticmethod
    def _compare_tuple_list_with_flattened_list(events_tuples):
        max_occurrences_to_events_ratio_for_flattened_list = 1.3
        safe_limit_flattened_list_len = 10 ** 4
        total_occurrences = sum([pair[1] for pair in events_tuples])

        if total_occurrences >= safe_limit_flattened_list_len:
            return 'tuple_list'

        occurrences_to_events_ratio = float(total_occurrences) / len(events_tuples)
        if occurrences_to_events_ratio > max_occurrences_to_events_ratio_for_flattened_list:
            return 'tuple_list'
        return 'flattened_list'

    def _compare_with_indexed_values(self, first_method, times, events_tuples):
        size_of_events_tuples = len(events_tuples)
        cutoff_size = get_current_size_cutoff(first_method, times, size_of_events_tuples)
        size_of_main_events = len(self._dict.keys())
        if size_of_main_events < cutoff_size:
            return first_method
        else:
            return 'indexed_values'

    def remove_by_tuple_list(self, times, integer_events):
        events_tuples = integer_events.all_events
        new_events = DictCombiner(self.get_dict())
        for _ in range(times):
            new_events = new_events.remove_once_by_tuple_list(events_tuples)
        return new_events

    def remove_once_by_tuple_list(self, events_tuples):
        min_event_being_removed = events_tuples[0][0]
        max_event_being_removed = events_tuples[-1][0]

        current_min_event = min(self._dict.keys())
        current_max_event = max(self._dict.keys())
        new_dict_min = current_min_event - min_event_being_removed
        new_dict_max = current_max_event - max_event_being_removed
        new_dict = {}
        for target_event in range(new_dict_min, new_dict_max + 1):
            try:
                freq_at_new_event = self._dict[target_event + min_event_being_removed]
                for event_being_removed, event_weight in events_tuples[1:]:
                    removal_value_offset = event_being_removed - min_event_being_removed
                    freq_at_new_event -= new_dict.get(target_event - removal_value_offset, 0) * event_weight
                new_dict[target_event] = freq_at_new_event // events_tuples[0][1]
            except KeyError:
                continue
        return DictCombiner(new_dict)


def flatten_events_tuples(events_tuples):
    flattened_list = []
    for event, freq in events_tuples:
        flattened_list = flattened_list + [event] * freq
    return flattened_list


def get_current_size_cutoff(first_method, combine_times, size_of_events_tuples):
    """
    keys_are_new_event_size = {size_of_events_tuples: {combine_times: (choices_for_current_size_cutoff), ...}, ...}

    :first_method: 'flattened_list', 'tuple_list'
    """
    keys_are_new_event_size = {
        2: {10: (250, 500), 50: (100, 200), 500: (1, 1)},
        3: {4: (500, 500), 10: (50, 100), 20: (10, 50), 50: (1, 10), 100: (1, 1)},
        4: {2: (500, 100), 4: (50, 100), 20: (1, 50), 50: (1, 1)},
        6: {2: (500, 500), 4: (10, 50), 20: (1, 1)},
        8: {1: (500, 1000), 2: (200, 200), 5: (50, 50), 10: (1, 1)},
        20: {1: (50, 100), 3: (1, 50), 4: (1, 1)},
        50: {1: (50, 100), 3: (1, 1)}
    }
    closest_new_size = get_best_key(size_of_events_tuples, keys_are_new_event_size)
    keys_are_times = keys_are_new_event_size[closest_new_size]
    closest_times = get_best_key(combine_times, keys_are_times)
    choices_for_current_size_cutoff = keys_are_times[closest_times]
    index_to_choose = {'flattened_list': 0, 'tuple_list': 1}[first_method]
    current_size_cutoff = choices_for_current_size_cutoff[index_to_choose]
    return current_size_cutoff


def get_best_key(value, dictionary):
    sorted_keys = sorted(dictionary.keys())
    best_key = sorted_keys[0]
    for test in sorted_keys:
        if value < test:
            break
        best_key = test
    return best_key
