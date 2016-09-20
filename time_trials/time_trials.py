"""a rather messy module that shows time trials.  this is why i don't use Decimal (i am disappoint)
why i don't use Counter (also disappoint. while it is only marginally slower, it doesn't really improve the code).
they are slower, without really conferring any great advantages.  :("""

from __future__ import print_function
from decimal import Decimal
import time
from collections import Counter
import numpy as np
from dicetables.tableinfo import format_huge_int
import dicetables as dt

import numpydict as npd

def time_trial(times, func, *args):
    start = time.clock()
    for _ in range(times):
        func(*args)
    return time.clock() - start

def time_trial_output(times, text, func, *args):
    return 'call using {} {} times: {:.5}'.format(text, times, time_trial(times, func, *args))

def print_time_trial_for_add_list_funcs(arg_list, object_dot_method, label_for_object):
    """arg_list = (text, times, object_to_add)"""
    print(time_trial_output(1, arg_list[0].format(arg_list[1], label_for_object), object_dot_method, *arg_list[1:]))


def format_huge_int_using_decimal(huge_int, dig_len):
    return '{:.{}e}'.format(Decimal(huge_int), dig_len - 1)


def convert_num(number):
    return Decimal(number)

def prep_tuple_list_as_tuple_list(tuple_list):
    return [(convert_num(pair[0]),  convert_num(pair[1])) for pair in tuple_list]

def prep_tuple_list_as_list(tuple_list):
    new_list = []
    for val, freq in tuple_list:
        new_list = new_list + [convert_num(val)] * freq
    return new_list
class NewAddiditiveEventTable(object):
    def __init__(self, seed_dictionary):
        self._dictionary = {}
        for event, val in seed_dictionary.items():
            self._dictionary[convert_num(event)] = convert_num(val)

    def add_list(self, times, lst):
        to_add = prep_tuple_list_as_list(lst)
        for _ in range(times):
            self._add_a_list(to_add)

    def _add_a_list(self, lst):
        """copy of _add_a_list from original."""
        newdic = {}
        for value, current_frequency in self._dictionary.items():
            for val in lst:
                newdic[value+val] = (newdic.get(value+val, 0)+current_frequency)
        self._dictionary = newdic
    def add_tuples(self, times, lst):
        to_add = prep_tuple_list_as_tuple_list(lst)
        for _ in range(times):
            self._add_tuple_list(to_add)
    def _add_tuple_list(self, lst):
        """copy of _add_tuple_list from original"""
        newdic = {}
        for value, current_frequency in self._dictionary.items():
            for val, freq in lst:
                newdic[value + val] = (newdic.get(value + val, 0) +
                                       freq * current_frequency)
        self._dictionary = newdic


    def mean(self):
        numerator = 0
        denominator = 0
        for event, freq in self._dictionary.items():
            denominator += freq
            numerator += freq * event
        return numerator / denominator

    def stddev(self):
        avg = self.mean()
        sqs = 0
        count = 0
        for value, frequency in self._dictionary.items():
            sqs += frequency * (avg - value)**Decimal(2)
            count += frequency

        return round((sqs/count)**Decimal(0.5), 4)

class CounterTable(dt.LongIntTable):
    def __init__(self, seed):
        dt.LongIntTable.__init__(self, seed)
        self._table = Counter(self._table)
    def _add_a_list(self, lst):
        newdic = Counter()
        for event in lst:
            event_dic = Counter({event + value: frequency for value, frequency in self._table.items()})
            newdic.update(event_dic)
        # for value, current_frequency in self._table.items():
        #     for val in lst:
        #         newdic[value + val] += current_frequency
        self._table = newdic
    def _add_tuple_list(self, lst):
        newdic = Counter()
        for value, current_frequency in self._table.items():
            for val, freq in lst:
                newdic[value + val] += freq * current_frequency
        self._table = newdic

def make_list_from_tuples(tuple_list):
    out = []
    for val, freq in tuple_list:
        out = out + freq * [val]
    return out


class NumpyTable(object):
    def __init__(self, seed_dict={0:1}):
        start_val, array = npd.convert_tuple_list_to_array_and_start_value(sorted(seed_dict.items()))
        self.counter = npd.NumpyCounter(start_val, array)

    def add_a_list(self, input_list):
        original = self.counter.start_val
        old_array = self.counter.array[:]
        self.counter.start_val = original + input_list[0]
        for val in input_list[1:]:
            start_val = original + val
            new_array = old_array[:]
            self.counter = self.counter.add(npd.NumpyCounter(start_val, new_array))

    def add(self, times, tuple_list):
        to_add = make_list_from_tuples(tuple_list)
        for _ in range(times):
            self.add_a_list(to_add)

    def add_a_tuple_list(self, tuple_list):
        original = self.counter.start_val
        old_array = self.counter.array[:]
        val_1, freq_1 = tuple_list[0]
        self.counter.start_val = original + val_1
        self.counter.array = old_array * np.array([freq_1], dtype=object)
        for val, freq in tuple_list[1:]:
            start_val = original + val
            new_array = old_array * np.array([freq], dtype=object)
            self.counter = self.counter.add(npd.NumpyCounter(start_val, new_array))

    def add_tuples(self, times, tuple_list):
        for _ in range(times):
            self.add_a_tuple_list(tuple_list)

    def mean(self):
        '''i mean, don't you just sometimes look at a table of values
        and wonder what the mean is?'''
        numerator = sum([value * freq for value, freq in self.counter.items()])
        denominator = sum(self.counter.array)
        if denominator == 0:
            raise ZeroDivisionError('there are no values in the table')
        return dt.long_int_div(numerator, denominator)

    def stddev(self, decimal_place=4):
        '''returns the standdard deviation of the table, with special measures
        to deal with long ints.'''
        avg = self.mean()
        extra_digits = 5
        power = len(str(max(self.counter.array))) - 1
        if power < 2 * (decimal_place + extra_digits):
            factor = 1
        else:
            factor = 10 ** (power - (decimal_place + extra_digits))
        sqs = 0
        count = 0
        for event, frequency in self.counter.items():
            sqs += (frequency // factor) * (avg - event) ** 2
            count += frequency
        new_count = count // factor
        return round((sqs / new_count) ** 0.5, decimal_place)

print()
x = NumpyTable()
x.add(2, [(val, 1) for val in range(1, 7)])
print(x.counter.items())
x.add_a_tuple_list([(val, 1) for val in range(1, 7)])
print(x.counter.items())
print(x.stddev())
y = dt.DiceTable()
y.add_die(3, dt.Die(6))
print(y.stddev())

print()
arg_func_dict = {(123**456, 5): [('scinote: my method, huge int', format_huge_int),
                                 ('scinote: decimal  huge int', format_huge_int_using_decimal)]}

for args, funcs in arg_func_dict.items():
    for elements in funcs:
        print(time_trial_output(10000, *elements, *args))

add_times = 500
my_table = dt.LongIntTable({0: 1})
test_table = NewAddiditiveEventTable({0:1})
c_table = CounterTable({0:1})
np_table = NumpyTable()
add_list_args = ('add list {}*[1,2,3,4,5,6]: {} - ', add_times, [(val, 1) for val in range(1, 7)])
print()
print_time_trial_for_add_list_funcs(add_list_args, my_table.add, 'mine')
print_time_trial_for_add_list_funcs(add_list_args, test_table.add_list, 'new')
print_time_trial_for_add_list_funcs(add_list_args, c_table.add, 'counter')
print_time_trial_for_add_list_funcs(add_list_args, np_table.add, 'numpy')
print(time_trial_output(add_times, 'stddev mine', my_table.stddev))
print(time_trial_output(add_times, 'stddev new', test_table.stddev))
print(time_trial_output(add_times, 'stddev numpy', np_table.stddev))
print('confirmation both tables are same. stddev new: {}, mine: {}, counter: {}, np: {}'
      .format(test_table.stddev(), my_table.stddev(), c_table.stddev(), np_table.stddev()))

print()
my_table = dt.LongIntTable({0: 1})
test_table = NewAddiditiveEventTable({0:1})
c_table = CounterTable({0:1})
np_table = NumpyTable()
add_tuples_args = ('add tuple list {}*[(1,1), (2,2), ... (6,6)]: {} - ', add_times, [(val, val) for val in range(1, 7)])
print_time_trial_for_add_list_funcs(add_tuples_args, my_table.add, 'mine')
print_time_trial_for_add_list_funcs(add_tuples_args, test_table.add_tuples, 'new')
print_time_trial_for_add_list_funcs(add_tuples_args, c_table.add, 'counter')
print_time_trial_for_add_list_funcs(add_tuples_args, np_table.add_tuples, 'numpy')
print('confirmation both tables are same. stddev new: {}, mine: {}, counter: {}, np: {}'
      .format(test_table.stddev(), my_table.stddev(), c_table.stddev(), np_table.stddev()))




