""" this module contains the class LongIntTable and longintmath that the table
needs to deal with it's BFN"""
# these functions are concerned with float-math for long ints.
from sys import version_info
from decimal import Decimal
from math import log10

if version_info[0] < 3:
    INT_TYPES = (int, long)
else:
    INT_TYPES = (int, )

CONVERSIONS = {'_add_tuple_list': 'AdditiveEvents._combine_once_by_tuple_list',
               'verify_and_prep_tuple_list': 'AdditiveEvents.verify_and_prep_tuple_list',
               '_remove_tuple_list': 'AdditiveEvents._remove_tuple_list',
               'add': 'AdditiveEvents.combine_with_new_events',
               'frequency': 'AdditiveEvents.get_event',
               'frequency_all': 'AdditiveEvents.get_event_all',
               'frequency_highest': 'AdditiveEvents.get_event_highest',
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
               'values_min': 'AdditiveEvents.min_event_key',
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
def verify_times(times):
    if times < 0 or not isinstance(times, INT_TYPES):
        raise ValueError('times must be a positive int')


def verify_and_prep_tuple_list(tuple_list):
    """prepares a list for AdditiveEvents.combine_with_new_events and AdditiveEvents.remove"""
    check_tuple_list_and_raise_error(tuple_list)
    return sorted([pair for pair in tuple_list if pair[1]])


def check_tuple_list_and_raise_error(tuple_list):
    """dict.items()-like tuple_list"""
    must_be_int_or_long = ValueError('all values must be ints')
    cannot_be_empty = ValueError('events may not be empty. a good alternative is the identity - [(0, 1)].')
    if not tuple_list:
        raise cannot_be_empty
    occurrences_are_all_zero = True
    for event, occurrences in tuple_list:
        if not isinstance(event, INT_TYPES) or not isinstance(occurrences, INT_TYPES):
            raise must_be_int_or_long
        if occurrences_are_all_zero and occurrences:
            occurrences_are_all_zero = False
        if occurrences < 0:
            raise ValueError('events may not occur negative times.')

    if occurrences_are_all_zero:
        raise cannot_be_empty


def check_dictionary_and_raise_errors(dictionary):
    try:
        check_tuple_list_and_raise_error(dictionary.items())
    except ValueError as error:
        new_message = str(error).replace('[(0, 1)]', '{0: 1}')
        raise ValueError(new_message)


def get_fastest_combine_method(verified_and_prepped_tuple_list):
    """see verify_and_prep_tuple_list()"""
    max_occurrences_to_events_ratio_for_add_by_list = 1.35
    max_event_range_to_events_ratio_vs_add_by_list = 2.75
    max_event_range_to_events_ratio_vs_add_by_tuple = 2.4

    occurrences_to_events_ratio = get_occurrences_to_events_ratio(verified_and_prepped_tuple_list)
    event_range_to_events_ratio = get_event_range_to_events_ratio(verified_and_prepped_tuple_list)

    if occurrences_to_events_ratio > max_occurrences_to_events_ratio_for_add_by_list:
        method = 'tuple_list'
        if event_range_to_events_ratio < max_event_range_to_events_ratio_vs_add_by_tuple:
            method = 'tuple_list'  # TODO 'indexed_values'
    else:
        method = 'flattened_list'
        if event_range_to_events_ratio < max_event_range_to_events_ratio_vs_add_by_list:
            method = 'flattened_list'  # TODO 'indexed_values'
    return method


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
    """a table of big fucking numbers and some math function for them.
    The table implicitly contains 0 occurrences of all unassigned integers.
    THIS TABLE SHOULD ONLY CONTAIN INT OR LONG."""

    def __init__(self, seed_dictionary):
        """seed_dictionary is a dictionary of ints. frequencies MUST BE POSITIVE.
        {value1: (get_event of value1), value2: (get_event of value 2), ...}"""
        check_dictionary_and_raise_errors(seed_dictionary)
        self._table = seed_dictionary.copy()

    def event_keys(self):
        """return the all the values, in order, that have non-zero get_event"""
        return sorted([key for key in self._table.keys() if self._table[key]])

    def event_keys_min(self):
        """returns the min value"""
        return self.event_keys()[0]

    def event_keys_max(self):
        """returns the max value"""
        return self.event_keys()[-1]

    def event_keys_range(self):
        """returns a tuple of min and max values"""
        return self.event_keys_min(), self.event_keys_max()

    def get_event(self, value):
        """Returns a tuple of the value and it's get_event."""
        return value, self._table.get(value, 0)

    def get_event_range(self, start, stop_before):
        """Returns a list of tuples (value,get_event).
        Like regular range function, it stops before endvalue."""
        tuple_list = []
        for value in range(start, stop_before):
            tuple_list.append(self.get_event(value))
        return tuple_list

    def get_event_all(self):
        """Returns a list of tuples IN ORDER for all non-zero-get_event
        values in table."""
        value_list = self.event_keys()
        tuple_list = []
        for value in value_list:
            tuple_list.append(self.get_event(value))
        return tuple_list

    def get_event_highest(self):
        """

        :return: (event, occurrences) for first event with highest occurrences
        """
        highest_occurrences = max(self._table.values())
        for event in sorted(self._table.keys()):
            if self._table[event] == highest_occurrences:
                return event, highest_occurrences

    def get_total_event_occurrences(self):
        """returns the sum all the freuencies in a table"""
        all_occurrences = self._table.values()
        return sum(all_occurrences)

    def __str__(self):
        return ('table from %s to %s' %
                (self.event_keys_min(), self.event_keys_max()))

    def mean(self):
        """i mean, don't you just sometimes look at a table of values
        and wonder what the mean is?"""
        numerator = sum([value * freq for value, freq in self._table.items()])
        denominator = self.get_total_event_occurrences()
        if denominator == 0:
            raise ZeroDivisionError('there are no values in the table')
        return long_int_div(numerator, denominator)

    def stddev(self, decimal_place=4):
        """returns the standdard deviation of the table, with special measures
        to deal with long ints."""
        avg = self.mean()
        extra_digits = 5
        largest_exponent = int(log10(self.get_event_highest()[1]))
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

    def combine_with_new_events(self, times, events_as_tuple_list):
        """
        combines the current events with a new set of events "times" times.
        ex: current events are A occurs 3 times, B occurs 2 times {A: 3, B: 2}. if
        combine_with_new_events {A: 2, B:5}: A+A = 3*2, B+A = 2*2, A+B = 5*3, B+B = 5*2
        combined events = {A+A: 6, A+B: 19, B+B: 10}

        :param times: positive int
        :param events_as_tuple_list: [(event, occurrences_of_event), ..]\n
            events may not be empty or zero\n
            all values are ints.\n
            occurrences >= 0.
        :return: None
        """
        verify_times(times)
        prepped_tuple_list = verify_and_prep_tuple_list(events_as_tuple_list)
        method_string = get_fastest_combine_method(prepped_tuple_list)
        if method_string == 'tuple_list':
            self.combine_by_tuple_list(times, prepped_tuple_list, list_is_verified_and_prepped=True)
        if method_string == 'flattened_list':
            self.combine_by_flattened_list(times, prepped_tuple_list, list_is_verified_and_prepped=True)

    def combine_by_flattened_list(self, times, tuple_list_of_events, list_is_verified_and_prepped=False):
        verify_times(times)
        if not list_is_verified_and_prepped:
            tuple_list_of_events = verify_and_prep_tuple_list(tuple_list_of_events)
        flattened_list = self.flatten_tuple_list_of_events(tuple_list_of_events)
        for _ in range(times):
            self._combine_once_by_flattened_list(flattened_list)

    @staticmethod
    def flatten_tuple_list_of_events(tuple_list_of_events):
        flattened_list = []
        for event, freq in tuple_list_of_events:
            flattened_list = flattened_list + [event] * freq
        return flattened_list

    def _combine_once_by_flattened_list(self, flattened_list):
        """the flattened list of [(1, 2), (2, 3)] = [1, 1, 2, 2, 2]"""
        new_dict = {}
        for event, current_frequency in self._table.items():
            for new_event in flattened_list:
                new_dict[event + new_event] = (new_dict.get(event + new_event, 0) + current_frequency)
        self._table = new_dict

    def combine_by_tuple_list(self, times, tuple_list_of_events, list_is_verified_and_prepped=False):
        verify_times(times)
        if not list_is_verified_and_prepped:
            tuple_list_of_events = verify_and_prep_tuple_list(tuple_list_of_events)
        for _ in range(times):
            self._combine_once_by_tuple_list(tuple_list_of_events)

    def _combine_once_by_tuple_list(self, tuple_list):
        new_dict = {}
        for event, current_frequency in self._table.items():
            for new_event, frequency in tuple_list:
                new_dict[event + new_event] = (new_dict.get(event + new_event, 0) +
                                               frequency * current_frequency)
        self._table = new_dict

    def remove(self, times, to_remove):
        """times is positive int or 0. values is a list of tuple(value, get_event)
        value and get_event are long or int. NO NEGATIVE FREQUENCIES ALLOWED!
        this function reverses previous adds.  if you remove something you never
        added, or remove it more times than you added it, THERE IS NO RECORD OF
        WHAT YOU ADDED AND NO ERROR WILL BE RAISED. PLEASE BE CAREFUL."""
        verify_times(times)
        processed_list = verify_and_prep_tuple_list(to_remove)
        for _ in range(times):
            self._remove_tuple_list(processed_list)

    def _remove_tuple_list(self, tuple_list):
        """tuple_list is a sorted list of tuples (value, get_event) with NO ZERO
        frequencies.  does the opposite of _combine_once_by_tuple_list"""
        to_remove_min = tuple_list[0][0]
        to_remove_max = tuple_list[-1][0]

        new_dict_min = self.event_keys_min() - to_remove_min
        new_dict_max = self.event_keys_max() - to_remove_max
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





