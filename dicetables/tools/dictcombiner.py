"""
DictCombiner combines dictionary of {event value: occurrences} and returns a DictCombiner.  Retrieve the result with
the "get_dict()" method.

THIS IS A SPECIFIC TOOL. IT HAS SEVERAL IMPORTANT CONSTRAINTS. USE WITH CAUTION.

if you mutate the __init__ dictionary elsewhere, IT WILL AFFECT IT HERE. (but it will
not mutate any dictionaries passed to it.)
    this class is for speed, so there is minimal copying. it is specifically
    designed to be instantiated once, used and then immediately discarded.

:__init__ dictionary: {int: int>0, ...}
:variable - times: int >=0
:variable - dictionary: {int: int>0, ...}
"""
from dicetables.tools.indexedvalues import generate_indexed_values_from_dict


class DictCombiner(object):
    def __init__(self, dictionary: dict):
        """
        :dictionary: {int: int>0, ...}
        """
        self._dict = dictionary

    def get_dict(self) -> dict:
        return self._dict.copy()

    def combine_by_flattened_list(self, dictionary: dict, times: int) -> dict:
        """
        :dictionary: {int: int>0, ...}
        """
        new_combiner = DictCombiner(self.get_dict())
        flattened_list = flatten_events_tuples(dictionary)
        for _ in range(times):
            new_combiner = new_combiner.combine_once_with_flattened_list(flattened_list)
        return new_combiner.get_dict()

    def combine_once_with_flattened_list(self, flattened_list) -> 'DictCombiner':
        new_dict = {}
        for event, current_frequency in self._dict.items():
            for new_event in flattened_list:
                new_dict[event + new_event] = (new_dict.get(event + new_event, 0) + current_frequency)
        return DictCombiner(new_dict)

    def combine_by_dictionary(self, dictionary: dict, times: int) -> dict:
        """
        :dictionary: {int: int>0, ...}
        """
        new_combiner = DictCombiner(self.get_dict())
        for _ in range(times):
            new_combiner = new_combiner.combine_once_with_dictionary(dictionary)
        return new_combiner.get_dict()

    def combine_once_with_dictionary(self, dictionary):
        new_dict = {}
        for event, current_frequency in self._dict.items():
            for new_event, frequency in dictionary.items():
                new_dict[event + new_event] = (new_dict.get(event + new_event, 0) + frequency * current_frequency)
        return DictCombiner(new_dict)

    def combine_by_indexed_values(self, dictionary: dict, times: int) -> dict:
        """
        :dictionary: {int: int>0, ...}
        """
        new_indexed_values = generate_indexed_values_from_dict(self._dict)
        for _ in range(times):
            new_indexed_values = new_indexed_values.combine_with_dictionary(dictionary)
        return new_indexed_values.get_dict()

    def combine_by_fastest(self, dictionary: dict, times: int) -> dict:
        """
        :dictionary: {int: int>0, ...}
        """
        method_dict = {'dictionary': self.combine_by_dictionary,
                       'flattened_list': self.combine_by_flattened_list,
                       'indexed_values': self.combine_by_indexed_values}
        method = self.get_fastest_combine_method(dictionary, times)

        return method_dict[method](dictionary, times)

    def get_fastest_combine_method(self, dictionary, times):
        """
        :dictionary: {int: int>0, ...}
        """
        first_comparison = self._compare_tuple_list_with_flattened_list(dictionary)
        second_comparison = self._compare_with_indexed_values(first_comparison, times, dictionary)
        return second_comparison

    @staticmethod
    def _compare_tuple_list_with_flattened_list(dictionary):
        max_occurrences_to_events_ratio_for_flattened_list = 1.3
        safe_limit_flattened_list_len = 10 ** 4
        total_occurrences = sum(dictionary.values())

        if total_occurrences >= safe_limit_flattened_list_len:
            return 'dictionary'

        occurrences_to_events_ratio = float(total_occurrences) / len(dictionary)
        if occurrences_to_events_ratio > max_occurrences_to_events_ratio_for_flattened_list:
            return 'dictionary'
        return 'flattened_list'

    def _compare_with_indexed_values(self, first_method, times, dictionary):
        size_of_dict_to_combine = len(dictionary)
        min_size_for_indexed_values = get_indexed_values_min(first_method, size_of_dict_to_combine, times)
        size_of_main_dict = len(self._dict)
        if size_of_main_dict < min_size_for_indexed_values:
            return first_method
        else:
            return 'indexed_values'

    def remove_by_tuple_list(self, dictionary, times):
        """
        :dictionary: {int: int>0, ...}
        """
        events_tuples = sorted(dictionary.items())
        new_events = DictCombiner(self.get_dict())
        for _ in range(times):
            new_events = new_events.remove_once_by_tuple_list(events_tuples)
        return new_events.get_dict()

    def remove_once_by_tuple_list(self, events_tuples):
        new_dict_max, new_dict_min = self.get_new_dict_range(events_tuples)
        new_dict = {}
        for target_event in range(new_dict_min, new_dict_max + 1):

            freq_at_new_event = self.get_target_event_freq(target_event, events_tuples, new_dict)
            if freq_at_new_event:
                new_dict[target_event] = freq_at_new_event

        return DictCombiner(new_dict)

    def get_new_dict_range(self, events_tuples):
        min_event_being_removed = events_tuples[0][0]
        max_event_being_removed = events_tuples[-1][0]
        current_min_event = min(self._dict.keys())
        current_max_event = max(self._dict.keys())

        new_dict_min = current_min_event - min_event_being_removed
        new_dict_max = current_max_event - max_event_being_removed
        return new_dict_max, new_dict_min

    def get_target_event_freq(self, target_event, events_tuples, new_dict):
        min_event_being_removed = events_tuples[0][0]
        try:
            old_freq = self._dict[target_event + min_event_being_removed]
        except KeyError:
            return 0
        freq_at_new_event = old_freq
        for event_being_removed, event_weight in events_tuples[1:]:
            removal_value_offset = event_being_removed - min_event_being_removed
            freq_at_new_event -= new_dict.get(target_event - removal_value_offset, 0) * event_weight
        freq_at_new_event = freq_at_new_event // events_tuples[0][1]
        return freq_at_new_event


def flatten_events_tuples(dictionary):
    flattened_list = []
    for event, freq in dictionary.items():
        flattened_list += [event] * freq
    return flattened_list


def get_indexed_values_min(first_method, size_of_dict_to_combine, combine_times):
    """
    {'first method': {size of input dict: {combine times: size of Dictcombiner.get_dict(), ...}, ...}, ... }

    :first_method: 'flattened_list', 'dictionary'
    """
    choices = {
        'flattened_list':
            {
                2: {10: 200, 20: 100, 100: 50, 500: 1},
                4: {2: 100, 5: 50, 10: 10, 20: 1},
                6: {1: 100, 4: 50, 10: 1},
                8: {1: 100, 3: 50, 5: 10, 10: 1},
                20: {1: 50, 3: 10, 4: 1},
                50: {1: 50, 3: 1},
                100: {1: 100, 2: 1}
            },
        'dictionary':
            {
                2: {10: 100, 50: 50, 100: 1},
                4: {2: 100, 10: 50, 50: 1},
                6: {2: 50, 10: 10, 20: 1},
                8: {1: 100, 3: 50, 10: 1},
                10: {1: 100, 3: 50, 5: 1},
                20: {1: 50, 3: 10, 4: 1},
                50: {1: 50, 2: 10, 3: 1},
                100: {1: 100, 2: 1}
            }
    }
    keys_are_input_dict_size = choices[first_method]

    closest_dict_size = get_best_key(size_of_dict_to_combine, keys_are_input_dict_size)
    keys_are_times = keys_are_input_dict_size[closest_dict_size]
    closest_times = get_best_key(combine_times, keys_are_times)
    min_size_for_indexed_values = keys_are_times[closest_times]
    return min_size_for_indexed_values


def get_best_key(value, dictionary):
    sorted_keys = sorted(dictionary.keys())
    best_key = sorted_keys[0]
    for test in sorted_keys:
        if value < test:
            break
        best_key = test
    return best_key
