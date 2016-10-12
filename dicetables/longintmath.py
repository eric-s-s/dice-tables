""" this module contains the class LongIntTable and longintmath that the table
needs to deal with it's BFN"""
# these functions are concerned with float-math for long ints.
from sys import version_info
from decimal import Decimal
from math import log10

from dicetables.indexedvalues import generate_indexed_values


CONVERSIONS = {'add': 'AdditiveEvents.combine_with_new_events',
               'frequency': 'AdditiveEvents.get_event',
               'frequency_all': 'AdditiveEvents.get_event_all',
               'frequency_highest': 'AdditiveEvents.get_biggest_event',
               'frequency_range': 'AdditiveEvents.get_event_range',
               'mean': 'AdditiveEvents.mean',
               'merge': 'AdditiveEvents.merge',
               'remove': 'AdditiveEvents.remove',
               'stddev': 'AdditiveEvents.stddev',
               'total_frequency': 'AdditiveEvents.get_total_event_occurrences',
               'update_frequency': 'AdditiveEvents.update_frequency',
               'update_value_add': 'AdditiveEvents.update_value_add',
               'update_value_ow': 'AdditiveEvents.update_value_ow',
               'values': 'AdditiveEvents.event_keys',
               'values_max': 'AdditiveEvents.event_keys_max',
               'values_min': 'AdditiveEvents.event_keys_min',
               'values_range': 'AdditiveEvents.event_keys_range'}


def _convert_back(num):
    """helper function.  takes a Decimal and returns float if
    possible, else, long_int"""
    answer_as_float = float(num)
    if answer_as_float == float('inf') or answer_as_float == float('-inf'):
        return int(num)
    else:
        return answer_as_float


def long_int_div(numerator, denominator):
    """returns a float division of numbers even if they are over 1e+308"""
    ans = Decimal(numerator) / Decimal(denominator)
    return _convert_back(ans)


def long_int_times(number1, number2):
    """returns a float times of numbers even if they are over 1e+308"""
    ans = Decimal(number1) * Decimal(number2)
    return _convert_back(ans)


def long_int_pow(number, exponent):
    """returns a float exponent of numbers even if they are over 1e+308"""
    ans = Decimal(number) ** Decimal(exponent)
    return _convert_back(ans)


# tools for AdditiveEvents
class InvalidEventsError(ValueError):
    def __init__(self, message='', *args, **kwargs):
        ValueError.__init__(self, message, *args, **kwargs)
        

class EventsVerifier(object):
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

        :raises: InvalidEventsError
        """
        if times < 0 or not self.is_int(times):
            raise InvalidEventsError('events may only be combined (int >= 0) times')

    def verify_events_tuple(self, event_tuple):
        """

        :raises: InvalidEventsError
        """
        identity_str = '[(0, 1)]'
        self._verify_events(event_tuple, identity_str)

    def verify_events_dictionary(self, dictionary):
        """

        :raises: InvalidEventsError
        """
        identity_str = '{0: 1}'
        self._verify_events(dictionary.items(), identity_str)

    def _verify_events(self, events_as_tuple_list, identity_str):
        cannot_be_empty = self.empty_message.format(identity_str)

        if not events_as_tuple_list:
            raise InvalidEventsError(cannot_be_empty)

        events, occurrences = zip(*events_as_tuple_list)
        if not self.is_all_ints(events) or not self.is_all_ints(occurrences):
            raise InvalidEventsError(self.types_message)
        if any(occurrence < 0 for occurrence in occurrences):
            raise InvalidEventsError('events may not occur negative times.')
        if all(occurrence == 0 for occurrence in occurrences):
            raise InvalidEventsError(cannot_be_empty)

    def is_all_ints(self, iterable):
        return all(self.is_int(value) for value in iterable)


def get_occurrences_to_events_ratio(verified_and_prepped_tuple_list):
    """see get_fastest_combine_method()"""
    only_the_occurrences = [pair[1] for pair in verified_and_prepped_tuple_list]
    occurrences_to_events_ratio = long_int_div(sum(only_the_occurrences), len(only_the_occurrences))
    return occurrences_to_events_ratio


def get_event_range_to_events_ratio(verified_and_prepped_tuple_list):
    """see get_fastest_combine_method()"""
    event_range = verified_and_prepped_tuple_list[-1][0] - verified_and_prepped_tuple_list[0][0] + 1
    events = len(verified_and_prepped_tuple_list)
    return long_int_div(event_range, events)


class AdditiveEvents(object):
    """manages (event, number of occurrences) for events that can be added to, like dice rolls."""

    def __init__(self, seed_dictionary):
        """

        :param seed_dictionary: {event: occurrences}\n
            event = int. occurrences = int >=0
            total occurrences > 0
        :raises: InvalidEventsError
        """
        self._verifier = EventsVerifier()
        self._verifier.verify_events_dictionary(seed_dictionary)
        self._table = seed_dictionary.copy()

    def event_keys(self):
        """return the all the values, in order, that have non-zero get_event"""
        return sorted([key for key in self._table.keys() if self._table[key]])

    def event_keys_min(self):
        return self.event_keys()[0]

    def event_keys_max(self):
        return self.event_keys()[-1]

    def event_keys_range(self):
        return self.event_keys_min(), self.event_keys_max()

    def get_event(self, event):
        """:return: (event, occurrences)"""
        return event, self._table.get(event, 0)

    def get_event_range(self, start, stop_before):
        """:return: dict.items()-like tuple_list [(event, occurrences), ..]"""
        tuple_list = []
        for value in range(start, stop_before):
            tuple_list.append(self.get_event(value))
        return tuple_list

    def get_event_all(self):
        """

        :return: dict.items()-like tuple_list [(event, occurrences), ..]\n
            sorted and only non-zero events.
        """
        value_list = self.event_keys()
        tuple_list = []
        for value in value_list:
            tuple_list.append(self.get_event(value))
        return tuple_list

    def get_biggest_event(self):
        """

        :return: (event, occurrences) for first event with highest occurrences
        """
        highest_occurrences = max(self._table.values())
        for event in sorted(self._table.keys()):
            if self._table[event] == highest_occurrences:
                return event, highest_occurrences

    def get_total_event_occurrences(self):
        all_occurrences = self._table.values()
        return sum(all_occurrences)

    def __str__(self):
        return 'table from {} to {}'.format(*self.event_keys_range())

    def mean(self):
        numerator = sum([value * freq for value, freq in self._table.items()])
        denominator = self.get_total_event_occurrences()
        return long_int_div(numerator, denominator)

    def stddev(self, decimal_place=4):
        avg = self.mean()
        extra_digits = 5
        largest_exponent = int(log10(self.get_biggest_event()[1]))
        required_exp_for_accuracy = 2 * (extra_digits + decimal_place)
        if largest_exponent < required_exp_for_accuracy:
            factor_to_truncate_digits = 1
        else:
            factor_to_truncate_digits = 10 ** (largest_exponent - required_exp_for_accuracy)
        truncated_deviations = 0
        total_occurrences = self.get_total_event_occurrences()
        for event_value, occurrences in self._table.items():
            truncated_deviations += (occurrences // factor_to_truncate_digits) * (avg - event_value) ** 2.
        truncated_total_occurrences = total_occurrences // factor_to_truncate_digits
        return round((truncated_deviations / truncated_total_occurrences) ** 0.5, decimal_place)
    
    def combine_with_new_events(self, times, events_tuple, method='fastest'):
        """
        combines the current events with a new set of events "times" times.
        ex: current events are A occurs 3 times, B occurs 2 times {A: 3, B: 2}. if
        combine_with_new_events {A: 2, B:5}: A+A = 3*2, B+A = 2*2, A+B = 5*3, B+B = 5*2
        combined events = {A+A: 6, A+B: 19, B+B: 10}

        :param times: positive int
        :param events_tuple: [(event, occurrences_of_event), ..]\n
            events may not be empty or zero\n
            all values are ints.\n
            occurrences >= 0.
        :param method: 'fastest', 'tuple_list', 'flattened_list', 'indexed_values'\n
            WARNING: len(flattened_list) = total occurrences. can throw MemoryError and OverflowError
            if too many occurrences
        :raises: InvalidEventsError
        :return: None
        """
        self.verify_inputs_for_combine_and_remove(times, events_tuple)
        prepped_events = self.prep_tuple_list(events_tuple)
        method_dict = {'tuple_list': self._combine_by_tuple_list,
                       'flattened_list': self._combine_by_flattened_list,
                       'indexed_values': self._combine_by_indexed_values}
        if method == 'fastest':
            method = self.get_fastest_combine_method(times, prepped_events)

        method_dict[method](times, prepped_events)

    def _combine_by_flattened_list(self, times, events):
        flattened_list = self._flatten_events_tuple(events)
        for _ in range(times):
            self._combine_once_by_flattened_list(flattened_list)

    @staticmethod
    def _flatten_events_tuple(events_tuple):
        flattened_list = []
        for event, freq in events_tuple:
            flattened_list = flattened_list + [event] * freq
        return flattened_list

    def _combine_once_by_flattened_list(self, flattened_list):
        """the flattened list of [(1, 2), (2, 3)] = [1, 1, 2, 2, 2]"""
        new_dict = {}
        for event, current_frequency in self._table.items():
            for new_event in flattened_list:
                new_dict[event + new_event] = (new_dict.get(event + new_event, 0) + current_frequency)
        self._table = new_dict

    def _combine_by_tuple_list(self, times, events):
        for _ in range(times):
            self._combine_once_by_tuple_list(events)

    def _combine_once_by_tuple_list(self, tuple_list):
        new_dict = {}
        for event, current_frequency in self._table.items():
            for new_event, frequency in tuple_list:
                new_dict[event + new_event] = (new_dict.get(event + new_event, 0) +
                                               frequency * current_frequency)
        self._table = new_dict

    def _combine_by_indexed_values(self, times, events):
        indexed_values_to_update = generate_indexed_values(self.get_event_all())
        for _ in range(times):
            indexed_values_to_update = indexed_values_to_update.combine_with_events_list(events)
        self._table = dict(indexed_values_to_update.get_items())

    def verify_inputs_for_combine_and_remove(self, times, events):
        """

        :param times: int >= 0
        :param events: [(event, occurrences) ..]\n
            all values ints. must have total occurrences>0 and each occurrences>=0
        :raises: InvalidEventsError
        """
        self._verifier.verify_times(times)
        self._verifier.verify_events_tuple(events)

    @staticmethod
    def prep_tuple_list(events_tuple):
        return sorted([pair for pair in events_tuple if pair[1]])

    def get_fastest_combine_method(self, times, verified_and_prepped_tuple_list):
        max_occurrences_to_events_ratio_for_add_by_list = 1.3
        max_event_range_to_events_ratio_vs_add_by_list = 2.75
        max_event_range_to_events_ratio_vs_add_by_tuple = 2.4

        table_size = max(self.event_keys()) - min(self.event_keys()) + 1

        occurrences_to_events_ratio = get_occurrences_to_events_ratio(verified_and_prepped_tuple_list)

        if occurrences_to_events_ratio > max_occurrences_to_events_ratio_for_add_by_list:
            method = 'tuple_list'
            # if event_range_to_events_ratio < max_event_range_to_events_ratio_vs_add_by_tuple:
            #     method = 'indexed_values'  # TODO 'indexed_values'
        else:
            method = 'flattened_list'
            # if event_range_to_events_ratio < max_event_range_to_events_ratio_vs_add_by_list:
            #     method = 'indexed_values'  # TODO 'indexed_values'
        return method

    def remove(self, times, to_remove):
        """IF YOU REMOVE WHAT YOU HAVEN'T ADDED, NO ERROR WILL BE RAISED BUT YOU WILL HAVE BUGS.
        There is no record of what you added to an AdditiveEvents.  Please use with caution.

        :param times: int > 0
        :param to_remove: [(event, occurrences) ..]\n
            event: int, occurrences: int>=0 total occurrences >0"""
        self.verify_inputs_for_combine_and_remove(times, to_remove)
        processed_list = self.prep_tuple_list(to_remove)
        for _ in range(times):
            self._remove_tuple_list(processed_list)

    def _remove_tuple_list(self, tuple_list):
        to_remove_min = tuple_list[0][0]
        to_remove_max = tuple_list[-1][0]

        new_dict_min = min(self.event_keys()) - to_remove_min
        new_dict_max = max(self.event_keys()) - to_remove_max
        new_dict = {}
        for target_event in range(new_dict_min, new_dict_max + 1):
            try:
                freq_at_new_event = self._table[target_event + to_remove_min]
                for to_remove_event, event_weight in tuple_list[1:]:
                    the_diff = to_remove_event - to_remove_min
                    freq_at_new_event -= new_dict.get(target_event - the_diff, 0) * event_weight
                new_dict[target_event] = freq_at_new_event // tuple_list[0][1]
            except KeyError:
                continue
        self._table = new_dict

    def merge(self, other):
        """other is list of int tuples [(event, freq)].  adds all those event,
        freq to self"""
        for event, freq in other:
            self._table[event] = self._table.get(event, 0) + freq

    def update_frequency(self, event, new_freq):
        """looks up a event, and changes its get_event to the new one"""
        self._table[event] = new_freq

    def update_value_ow(self, old_val, new_val):
        """takes the get_event at old_val and moves it to new_val"""
        freq = self._table[old_val]
        self._table[old_val] = 0
        self._table[new_val] = freq

    def update_value_add(self, old_val, new_val):
        """takes the get_event at old_vall and moves it to new_val where it adds
        to the get_event already at new_val"""
        freq = self._table[old_val]
        self._table[old_val] = 0
        self._table[new_val] = self._table.get(new_val, 0) + freq
