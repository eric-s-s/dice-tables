""" this module contains the class LongIntTable and longintmath that the table
needs to deal with it's BFN"""
from decimal import Decimal
from math import log10
from sys import version_info

from tools.indexedvalues import generate_indexed_values

CONVERSIONS = {'add': 'AdditiveEvents.combines',
               'frequency': 'AdditiveEvents.get_event',
               'frequency_all': 'AdditiveEvents.all_events',
               'frequency_highest': 'AdditiveEvents.biggest_event',
               'frequency_range': 'AdditiveEvents.get_range_of_events',
               'mean': 'AdditiveEvents.mean',
               'merge': 'AdditiveEvents.merge',
               'remove': 'AdditiveEvents.remove',
               'stddev': 'AdditiveEvents.stddev',
               'total_frequency': 'AdditiveEvents.total_occurrences',
               'update_frequency': 'AdditiveEvents.update_frequency',
               'update_value_add': 'AdditiveEvents.update_value_add',
               'update_value_ow': 'AdditiveEvents.update_value_ow',
               'values': 'AdditiveEvents.event_keys',
               'values_max': 'AdditiveEvents.event_range[0]',
               'values_min': 'AdditiveEvents.event_range[1]',
               'values_range': 'AdditiveEvents.event_range'}


def _convert_decimal_to_float_or_int(num):
    answer_as_float = float(num)
    if answer_as_float == float('inf') or answer_as_float == float('-inf'):
        return int(num)
    else:
        return answer_as_float


def safe_true_div(numerator, denominator):
    """floating point division for any sized number"""
    ans = Decimal(numerator) / Decimal(denominator)
    return _convert_decimal_to_float_or_int(ans)


class InvalidEventsError(ValueError):
    def __init__(self, message='', *args, **kwargs):
        super(InvalidEventsError, self).__init__(message, *args, **kwargs)
        

class InputVerifier(object):
    def __init__(self):
        if version_info[0] < 3:
            self._int_tuple = (int, long)
            type_str = 'ints or longs'
        else:
            self._int_tuple = (int, )
            type_str = 'ints'
        self.types_message = 'all values must be {}'.format(type_str)
        self.empty_message = 'events may not be empty. a good alternative is the identity - {}.'
            
    def is_int(self, number):
        return isinstance(number, self._int_tuple)
            
    def verify_times(self, times):
        """
        :raises: TypeError, ValueError
        """
        if not self.is_int(times):
            raise TypeError('AdditiveEvents.combine/remove: times variable must be int')
        if times < 0:
            raise ValueError('AdditiveEvents.combine/remove times must be >=0')

    def verify_events_tuple(self, event_tuple):
        """

        :param event_tuple: [(event, occurrences),  ... ]
        :raises: InvalidEventsError with 3 specific error messages
        """
        identity_str = '[(0, 1)]'
        self._verify_events(event_tuple, identity_str)

    def verify_events_dictionary(self, dictionary):
        """

        :param dictionary: {event: occurrences, ...}
        :raises: InvalidEventsError with 3 specific error messages
        """
        identity_str = '{0: 1}'
        self._verify_events(dictionary.items(), identity_str)

    def _verify_events(self, events_as_tuple_list, error_form_completion_str):
        cannot_be_empty = self.empty_message.format(error_form_completion_str)
        no_negative_occurrences = 'events may not occur negative times.'
        bad_types = self.types_message

        if not events_as_tuple_list:
            raise InvalidEventsError(cannot_be_empty)

        events, occurrences = zip(*events_as_tuple_list)
        if not self.is_all_ints(events) or not self.is_all_ints(occurrences):
            raise InvalidEventsError(bad_types)
        if any(occurrence < 0 for occurrence in occurrences):
            raise InvalidEventsError(no_negative_occurrences)
        if all(occurrence == 0 for occurrence in occurrences):
            raise InvalidEventsError(cannot_be_empty)

    def is_all_ints(self, iterable):
        return all(self.is_int(value) for value in iterable)


class IntegerEvents(object):
    def __init__(self):
        self.verifier = InputVerifier()
        self.verifier.verify_events_tuple(self.all_events)

    @property
    def all_events(self):
        message = 'all_events must return a tuple list of [(event, occurrences),  ...] event=int, occurrence=int>=0.'
        raise NotImplementedError(message)


class AdditiveEvents(IntegerEvents):
    """manages (event, number of occurrences) for events that can be added to, like dice rolls."""

    def __init__(self, seed_dictionary):
        """

        :param seed_dictionary: {event: occurrences}\n
            event = int. occurrences = int >=0
            total occurrences > 0
        :raises: InvalidEventsError
        """
        # self._verifier = InputVerifier()
        # self._verifier.verify_events_dictionary(seed_dictionary)
        self._table = seed_dictionary.copy()
        self.dict_combiner = DictCombiner(self._table)
        super(AdditiveEvents, self).__init__()

    @property
    def event_keys(self):
        """return the all the values, in order, that have non-zero occurrences"""
        return sorted([key for key in self._table.keys() if self._table[key]])

    @property
    def event_range(self):
        all_events = self.event_keys
        return all_events[0], all_events[-1]

    @property
    def all_events(self):
        """

        :return: dict.items()-like all_events [(event, occurrences), ..]\n
            sorted and only non-zero events.
        """
        return [(key, self._table[key]) for key in self.event_keys]

    @property
    def biggest_event(self):
        """

        :return: (event, occurrences) for first event with highest occurrences
        """
        highest_occurrences = max(self._table.values())
        for event in sorted(self._table.keys()):
            if self._table[event] == highest_occurrences:
                return event, highest_occurrences

    @property
    def total_occurrences(self):
        all_occurrences = self._table.values()
        return sum(all_occurrences)

    def get_dict(self):
        return self._table.copy()

    def get_event(self, event):
        """:return: (event, occurrences)"""
        return event, self._table.get(event, 0)

    def get_range_of_events(self, start, stop_before):
        """:return: dict.items()-like all_events [(event, occurrences), ..]"""
        tuple_list = []
        for value in range(start, stop_before):
            tuple_list.append(self.get_event(value))
        return tuple_list

    def __str__(self):
        min_event, max_event = self.event_range
        return 'table from {} to {}'.format(min_event, max_event)

    def mean(self):
        numerator = sum([value * freq for value, freq in self._table.items()])
        denominator = self.total_occurrences
        return safe_true_div(numerator, denominator)

    def stddev(self, decimal_place=4):
        avg = self.mean()
        extra_digits = 5
        largest_exponent = int(log10(self.biggest_event[1]))
        required_exp_for_accuracy = 2 * (extra_digits + decimal_place)
        if largest_exponent < required_exp_for_accuracy:
            factor_to_truncate_digits = 1
        else:
            factor_to_truncate_digits = 10 ** (largest_exponent - required_exp_for_accuracy)
        truncated_deviations = 0
        total_occurrences = self.total_occurrences
        for event_value, occurrences in self._table.items():
            truncated_deviations += (occurrences // factor_to_truncate_digits) * (avg - event_value) ** 2.
        truncated_total_occurrences = total_occurrences // factor_to_truncate_digits
        return round((truncated_deviations / truncated_total_occurrences) ** 0.5, decimal_place)
    
    def _combine(self, times, other_integer_events):
        """
        combines the current events with a new set of events "times" times.
        ex: current events are A occurs 3 times, B occurs 2 times {A: 3, B: 2}. if
        combine_with_new_events {A: 2, B:5}: A+A = 3*2, B+A = 2*2, A+B = 5*3, B+B = 5*2
        combined events = {A+A: 6, A+B: 19, B+B: 10}

        :param times: >=0
        :type times: int
        :param other_integer_events: [(event, occurrences_of_event), ..]\n
            events may not be empty or zero\n
            all values are ints.\n
            occurrences >= 0.
        :raises: InvalidEventsError, TypeError, ValueError
        :return: None
        """
        prepped_tuples = prepare_events(other_integer_events.all_events)
        method_dict = {'tuple_list': self._combine_by_tuple_list,
                       'flattened_list': self._combine_by_flattened_list,
                       'indexed_values': self._combine_by_indexed_values}
        method = self.get_fastest_combine_method(times, prepped_tuples)

        return method_dict[method](times, prepped_tuples)

    def combine(self, times, other_integer_events):
        dictionary = self._combine(times, other_integer_events)
        return AdditiveEvents(dictionary)

    def combine_by_flattened_list(self, times, events):
        prepped_tuples = prepare_events(events.all_events)
        return AdditiveEvents(self._combine_by_flattened_list(times, prepped_tuples))

    def combine_by_tuple_list(self, times, events):
        prepped_tuples = prepare_events(events.all_events)
        return AdditiveEvents(self._combine_by_tuple_list(times, prepped_tuples))

    def combine_by_indexed_values(self, times, events):
        prepped_tuples = prepare_events(events.all_events)
        return AdditiveEvents(self._combine_by_indexed_values(times, prepped_tuples))

    def _combine_by_flattened_list(self, times, tuple_list):
        flattened_list = flatten_events_tuple(tuple_list)
        return self.dict_combiner.combine_dict_with_flattened_list(flattened_list, times).get_dict()

    def _combine_by_tuple_list(self, times, tuple_list):
        new_events = self.get_dict()
        for _ in range(times):
            new_events = self._combine_once_by_tuple_list(new_events, tuple_list)
        return new_events

    @staticmethod
    def _combine_once_by_tuple_list(all_events, tuple_list):
        new_dict = {}
        for event, current_frequency in all_events.items():
            for new_event, frequency in tuple_list:
                new_dict[event + new_event] = (new_dict.get(event + new_event, 0) +
                                               frequency * current_frequency)
        return new_dict

    def _combine_by_indexed_values(self, times, tuple_list):
        indexed_values_to_update = generate_indexed_values(self.all_events)
        for _ in range(times):
            indexed_values_to_update = indexed_values_to_update.combine_with_events_list(tuple_list)
        return dict(indexed_values_to_update.get_items())

    def raise_error_for_bad_input(self, times, events):
        """

        :raises: InvalidEventsError, TypeError, ValueError
        """
        self.verifier.verify_times(times)
        self.verifier.verify_events_tuple(events)

    def get_fastest_combine_method(self, times, prepped_events):
        first_comparison = self._compare_tuple_list_with_flattened_list(prepped_events)
        second_comparison = self._compare_with_indexed_values(first_comparison, times, prepped_events)
        return second_comparison

    @staticmethod
    def _compare_tuple_list_with_flattened_list(prepped_events):
        max_occurrences_to_events_ratio_for_add_by_list = 1.3
        safe_limit_flattened_list_len = 10 ** 4
        total_occurrences = sum([pair[1] for pair in prepped_events])

        if total_occurrences >= safe_limit_flattened_list_len:
            return 'tuple_list'

        occurrences_to_events_ratio = float(total_occurrences) / len(prepped_events)
        if occurrences_to_events_ratio > max_occurrences_to_events_ratio_for_add_by_list:
            return 'tuple_list'
        return 'flattened_list'

    def _compare_with_indexed_values(self, first_method, times, prepped_events):
        new_events_size = len(prepped_events)
        current_size_cutoff = get_current_size_cutoff(first_method, times, new_events_size)
        current_events_size = len(self.event_keys)
        if current_events_size < current_size_cutoff:
            return first_method
        else:
            return 'indexed_values'

    def _remove(self, times, to_remove):
        """IF YOU REMOVE WHAT YOU HAVEN'T ADDED, NO ERROR WILL BE RAISED BUT YOU WILL HAVE BUGS.
        There is no record of what you added to an AdditiveEvents.  Please use with caution.

        :param times: int > 0
        :param to_remove: [(event, occurrences) ..]\n
            event: int, occurrences: int>=0 total occurrences >0"""
        processed_list = prepare_events(to_remove.all_events)
        new_dict = self.get_dict()
        for _ in range(times):
            new_dict = self._remove_tuple_list(new_dict, processed_list)
        return new_dict

    def remove(self, times, to_remove):
        return AdditiveEvents(self._remove(times, to_remove))

    @staticmethod
    def _remove_tuple_list(dict_of_original, events_to_remove):
        min_event_being_removed = events_to_remove[0][0]
        max_event_being_removed = events_to_remove[-1][0]

        current_min_event = min(dict_of_original.keys())
        current_max_event = max(dict_of_original.keys())
        new_dict_min = current_min_event - min_event_being_removed
        new_dict_max = current_max_event - max_event_being_removed
        new_dict = {}
        for target_event in range(new_dict_min, new_dict_max + 1):
            try:
                freq_at_new_event = dict_of_original[target_event + min_event_being_removed]
                for event_being_removed, event_weight in events_to_remove[1:]:
                    removal_value_offset = event_being_removed - min_event_being_removed
                    freq_at_new_event -= new_dict.get(target_event - removal_value_offset, 0) * event_weight
                new_dict[target_event] = freq_at_new_event // events_to_remove[0][1]
            except KeyError:
                continue
        return new_dict


class DictCombiner(object):
    def __init__(self, dictionary):
        self._dict = dictionary

    def get_dict(self):
        return self._dict.copy()

    def combine_dict_with_flattened_list(self, events_tuple, times):
        events_dict = DictCombiner(self.get_dict())
        for _ in range(times):
            events_dict = events_dict.combine_once_dict_and_flattened_list(events_tuple)
        return events_dict

    def combine_once_dict_and_flattened_list(self, flattened_list):
        new_dict = {}
        for event, current_frequency in self._dict.items():
            for new_event in flattened_list:
                new_dict[event + new_event] = (new_dict.get(event + new_event, 0) + current_frequency)
        return DictCombiner(new_dict)


def prepare_events(events_tuple):
    return sorted([pair for pair in events_tuple if pair[1]])


def flatten_events_tuple(events_tuple):
    flattened_list = []
    for event, freq in events_tuple:
        flattened_list = flattened_list + [event] * freq
    return flattened_list


def get_current_size_cutoff(first_method, times, new_events_size):
    """
    data_dict = {new_event_size: {times: (current_events_size_choices), ...}, ...}

    :param first_method: 'flattened_list', 'tuple_list'
    :param times:
    :param new_events_size:
    :return: current events cutoff size
    """
    keys_are_new_event_size = {
        2: {10: (250, 500), 50: (100, 200), 500: (1, 1)},
        3: {4: (500, 500), 10: (50, 100), 20: (10, 50), 50: (1, 10), 100: (1, 1)},
        4: {2: (500, 100), 4: (50, 100), 20: (1, 50), 50: (1, 1)},
        6: {2: (500, 500), 4: (10, 50), 20: (1, 1)},
        8: {1: (500, 1000), 2: {200, 200}, 5: (50, 50), 10: (1, 1)},
        20: {1: (50, 100), 3: (1, 50), 4: (1, 1)},
        50: {1: (50, 100), 3: (1, 1)}
    }
    closest_new_size = get_best_key(new_events_size, keys_are_new_event_size)
    keys_are_times = keys_are_new_event_size[closest_new_size]
    closest_times = get_best_key(times, keys_are_times)
    current_size_choices = keys_are_times[closest_times]
    current_size_index = {'flattened_list': 0, 'tuple_list': 1}[first_method]
    current_size_cutoff = current_size_choices[current_size_index]
    return current_size_cutoff


def get_best_key(value, dictionary):
    sorted_keys = sorted(dictionary.keys())
    best_key = sorted_keys[0]
    for test in sorted_keys:
        if value < test:
            break
        best_key = test
    return best_key
