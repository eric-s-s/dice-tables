""" this module contains the class LongIntTable and longintmath that the table
needs to deal with it's BFN"""
# these functions are concerned with float-math for long ints.
from decimal import Decimal as dec

# CONVERSIONS = {'_add_tuple_list': AdditiveEvents._add_tuple_list,
#                '_check_cull_sort': AdditiveEvents._check_cull_sort,
#                '_remove_tuple_list': AdditiveEvents._remove_tuple_list,
#                'add': AdditiveEvents.add,
#                'frequency': AdditiveEvents.frequency,
#                'frequency_all': AdditiveEvents.frequency_all,
#                'frequency_highest': AdditiveEvents.frequency_highest,
#                'frequency_range': AdditiveEvents.frequency_range,
#                'mean': AdditiveEvents.mean,
#                'merge': AdditiveEvents.merge,
#                'remove': AdditiveEvents.remove,
#                'stddev': AdditiveEvents.stddev,
#                'total_frequency': AdditiveEvents.total_frequency,
#                'update_frequency': AdditiveEvents.update_frequency,
#                'update_value_add': AdditiveEvents.update_value_add,
#                'update_value_ow': AdditiveEvents.update_value_ow,
#                'values': AdditiveEvents.event_keys,
#                'values_max': AdditiveEvents.values_max,
#                'values_min': AdditiveEvents.values_min,
#                'values_range': AdditiveEvents.values_range}






def _convert_back(num):
    """helper function.  takes a Decimal and returns float if
    possible, else, long_int"""
    if float(num) == float('inf') or float(num) == float('-inf'):
        return int(num)
    else:
        return float(num)


def long_int_div(numerator, denominator):
    """returns a float division of numbers even if they are over 1e+308"""
    ans = dec(numerator) / dec(denominator)
    return _convert_back(ans)


def long_int_times(number1, number2):
    """returns a float times of numbers even if they are over 1e+308"""
    ans = dec(number1) * dec(number2)
    return _convert_back(ans)


def long_int_pow(number, exponent):
    """returns a float exponent of numbers even if they are over 1e+308"""
    ans = dec(number) ** dec(exponent)
    return _convert_back(ans)


class AdditiveEvents(object):
    """a table of big fucking numbers and some math function for them.
    The table implicitly contains 0 occurrences of all unassigned integers.
    THIS TABLE SHOULD ONLY CONTAIN INT OR LONG.  it will not raise errors if you
    put in other event_keys, but there is not telling what problems will happen."""

    _max_event_to_combination_ratio_for_add_by_list = 1.35
    _max_event_to_gap_between_events_ratio_vs_add_by_list = 3.0
    _max_event_to_gap_between_events_ratio_vs_add_by_tuple = 2.5

    def __init__(self, seed_dictionary):
        """seed_dictionary is a dictionary of ints. frequencies MUST BE POSITIVE.
        {value1: (frequency of value1), value2: (frequency of value 2), ...}"""
        check_dictionary_and_raise_errors(seed_dictionary)
        self._table = seed_dictionary.copy()

    def event_keys(self):
        '''return the all the event_keys, in order, that have non-zero frequency'''
        the_values = []
        for value, freq in self._table.items():
            if freq != 0:
                the_values.append(value)
        the_values.sort()
        return the_values

    def values_min(self):
        '''returns the min value'''
        if self.event_keys() == []:
            return None
        else:
            return self.event_keys()[0]

    def values_max(self):
        '''returns the max value'''
        if self.event_keys() == []:
            return None
        else:
            return self.event_keys()[-1]

    def values_range(self):
        '''returns a tuple of min and max event_keys'''
        return self.values_min(), self.values_max()

    def frequency(self, value):
        '''Returns a tuple of the value and it's frequency.'''
        return value, self._table.get(value, 0)

    def frequency_range(self, start, stopbefore):
        '''Returns a list of tuples (value,frequency).
        Like regular range function, it stops before endvalue.'''
        tuple_list = []
        for value in range(start, stopbefore):
            tuple_list.append(self.frequency(value))
        return tuple_list

    def frequency_all(self):
        '''Returns a list of tuples IN ORDER for all non-zero-frequency
        event_keys in table.'''
        value_list = self.event_keys()
        tuple_list = []
        for value in value_list:
            tuple_list.append(self.frequency(value))
        return tuple_list

    def frequency_highest(self):
        '''Returns a tuple of (one of) the value(s) with the highest frequency,
        and it's frequency'''
        hf_val, hf_freq = None, 0
        for event, frequency in self._table.items():
            if frequency > hf_freq:
                hf_val, hf_freq = event, frequency
        return hf_val, hf_freq

    def total_frequency(self):
        '''returns the sum all the freuencies in a table'''
        all_freq = self._table.event_keys()
        return sum(all_freq)

    def __str__(self):
        return ('table from %s to %s' %
                (self.values_min(), self.values_max()))

    def mean(self):
        '''i mean, don't you just sometimes look at a table of event_keys
        and wonder what the mean is?'''
        numerator = sum([value * freq for value, freq in self._table.items()])
        denominator = self.total_frequency()
        if denominator == 0:
            raise ZeroDivisionError('there are no event_keys in the table')
        return long_int_div(numerator, denominator)

    def stddev(self, decimal_place=4):
        '''returns the standdard deviation of the table, with special measures
        to deal with long ints.'''
        avg = self.mean()
        extra_digits = 5
        power = len(str(self.frequency_highest()[1])) - 1
        if power < 2 * (decimal_place + extra_digits):
            factor = 1
        else:
            factor = 10 ** (power - (decimal_place + extra_digits))
        sqs = 0
        count = 0
        for event, frequency in self._table.items():
            sqs += (frequency // factor) * (avg - event) ** 2
            count += frequency
        new_count = count // factor
        return round((sqs / new_count) ** 0.5, decimal_place)

    def add(self, times, values):
        '''times is positive int or 0. event_keys is a list of tuples(value, frequency)
        value and frequency are ints or longs, NO NEGATIVE FREQUENCIES ALLOWED!
        this function adds your table's event_keys and frequency and the event_keys's.

        here's how it works - original list event A is 3 out of 5.
        event B is 2 out of 5 or {A:3, B:5}. add {A:2, B:1} ( [A,A,B] ) this way.
        A+A = 3*2, A+B = (3*1+5*2) B+B = 5*1.  new dict = {AA:6, AB:8, BB:5}'''
        if times < 0:
            raise ValueError('times must be a positive int')
        to_add = self._check_cull_sort(values)

        def _fastest(tuple_list):
            """returns fastest method"""
            experimentally_determined_ratio = 1.4
            only_the_values = [pair[1] for pair in tuple_list]
            use_tuples = True
            list_ratio = long_int_div(sum(only_the_values), len(only_the_values))
            if list_ratio > experimentally_determined_ratio:
                return tuple_list, use_tuples
            else:
                use_tuples = False
                new_list = []
                for event, freq in tuple_list:
                    new_list = new_list + [event] * freq
                return new_list, use_tuples

        the_list, use_tuples = _fastest(to_add)
        # if a list of ints is faster, will do that
        if use_tuples:
            for _ in range(times):
                self._add_tuple_list(the_list)
        # otherwise adds by tuple
        else:
            for _ in range(times):
                self._add_a_list(the_list)

    @staticmethod
    def _check_cull_sort(tuple_list):
        """prepares a list for add and remove.  removes zero event_keys, raises
        errors where appropriate and returns a sorted list."""
        new_list = []
        for event, freq in tuple_list:
            if freq < 0:
                raise ValueError('frequencies may not be negative')
            if freq != 0:
                new_list.append((event, freq))
        if not new_list:
            raise ValueError('cannot add an empty list')
        return sorted(new_list)

    def _add_a_list(self, lst):
        '''lst is ints. takes the table.  for each int in the list, makes new
        tables with each value changed to value+int. merges those new tables
        and updates the existing table to become the merge.'''
        # so for [1,2,3], this would take {0:1,1:2} and
        # update to {1:1, 2:2} + {2:1, 3:2} + {3:1, 4:2}
        new_dict = {}
        for event, current_frequency in self._table.items():
            for new_event in lst:
                new_dict[event + new_event] = (new_dict.get(event + new_event, 0) + current_frequency)
        self._table = new_dict

    def _add_tuple_list(self, lst):
        '''as add_a_list, but now pass a list of tuples of ints.
        [(2,3), (5,7)] means add 2 three times and add 5 seven times. much more
        efficient if numbers repeat a lot in your list.'''
        new_dict = {}
        for event, current_frequency in self._table.items():
            for new_event, frequency in lst:
                new_dict[event + new_event] = (new_dict.get(event + new_event, 0) +
                                               frequency * current_frequency)
        self._table = new_dict

    def remove(self, times, to_remove):
        """times is positive int or 0. event_keys is a list of tuple(value, frequency)
        value and frequency are long or int. NO NEGATIVE FREQUENCIES ALLOWED!
        this function reverses previous adds.  if you remove something you never
        added, or remove it more times than you added it, THERE IS NO RECORD OF
        WHAT YOU ADDED AND NO ERROR WILL BE RAISED. PLEASE BE CAREFUL."""
        if times < 0:
            raise ValueError('times must be a positive int')
        processed_list = self._check_cull_sort(to_remove)
        for _ in range(times):
            self._remove_tuple_list(processed_list)

    def _remove_tuple_list(self, tuple_list):
        """tuple_list is a sorted list of tuples (value, frequency) with NO ZERO
        frequencies.  does the opposite of _add_tuple_list"""
        to_remove_min = tuple_list[0][0]
        to_remove_max = tuple_list[-1][0]

        new_dict_min = self.values_min() - to_remove_min
        new_dict_max = self.values_max() - to_remove_max
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
        '''looks up a event, and changes its frequency to the new one'''
        self._table[event] = new_freq

    def update_value_ow(self, old_val, new_val):
        '''takes the frequency at old_val and moves it to new_val'''
        freq = self._table[old_val]
        self._table[old_val] = 0
        self._table[new_val] = freq

    def update_value_add(self, old_val, new_val):
        '''takes the frequency at old_vall and moves it to new_val where it adds
        to the frequency already at new_val'''
        freq = self._table[old_val]
        self._table[old_val] = 0
        self._table[new_val] = self._table.get(new_val, 0) + freq


def check_dictionary_and_raise_errors(dictionary):
    must_be_int_or_long = ValueError('all keys and event_keys must be ints')
    cannot_be_empty = ValueError('a table may not be empty. a good alternative is the identity - {0:1}.')
    if not dictionary:
        raise cannot_be_empty

    for key in dictionary.keys():
        if not is_int(key):
            raise must_be_int_or_long

    for value in dictionary.event_keys():
        if not is_int(value):
            raise must_be_int_or_long
        if value < 0:
            raise ValueError('dictionary event_keys may not be negative')

    if sum(dictionary.event_keys()) == 0:
        raise cannot_be_empty


def is_int(number):
    try:
        return isinstance(number, (int, long))
    except NameError:
        return isinstance(number, int)
