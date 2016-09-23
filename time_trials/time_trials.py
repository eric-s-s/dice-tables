"""a rather messy module that shows time trials.  this is why i don't use Decimal (i am disappoint)
why i don't use Counter (also disappoint. while it is only marginally slower, it doesn't really improve the code).
they are slower, without really conferring any great advantages.  :("""

from __future__ import print_function
from decimal import Decimal
import time
from collections import Counter
from operator import mul
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
class DecimalEventTable(object):
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

    def make_trans(self, tuple_list):
        start_val = min(tuple_list)[0]
        dlist_end = max(tuple_list)[0]
        dlist_size = dlist_end - start_val
        row = self.counter.array.size
        col = row + dlist_size
        trans = np.zeros((row, col), dtype=object)
        for row in range(trans.shape[0]):
            for index, val in tuple_list:
                index -= start_val
                trans[row][row + index] = val
        return trans, start_val

    def trans_add(self, tuple_list):
        trans, start_val = self.make_trans(tuple_list)
        new_array = self.counter.array.dot(trans)
        new_start = self.counter.start_val + start_val
        self.counter = npd.NumpyCounter(new_start, new_array)

    def do_trans(self,times,  tuple_list):
        for _ in range(times):
            self.trans_add(tuple_list)


    def add_a_tuple_list(self, tuple_list):
        original = self.counter.start_val
        old_array = self.counter.array[:]
        val_1, freq_1 = tuple_list[0]
        self.counter.start_val = original + val_1
        self.counter.array = old_array * freq_1
        for val, freq in tuple_list[1:]:
            start_val = original + val
            new_array = old_array * freq
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

class ListTable(object):
    def __init__(self, seed_dict={0:1}):
        start_val, array = npd.convert_tuple_list_to_array_and_start_value(sorted(seed_dict.items()))
        self.counter = npd.MyCounter(start_val, array.tolist())

    def add_a_list(self, input_list):
        original = self.counter.start_val
        old_array = self.counter.array[:]
        self.counter.start_val = original + input_list[0]
        for val in input_list[1:]:
            start_val = original + val
            new_array = old_array[:]
            self.counter = self.counter.add(npd.MyCounter(start_val, new_array))

    def add(self, times, tuple_list):
        to_add = make_list_from_tuples(tuple_list)
        for _ in range(times):
            self.add_a_list(to_add)

    def add_a_tuple_list(self, tuple_list):
        original = self.counter.start_val
        old_array = self.counter.array[:]
        val_1, freq_1 = tuple_list[0]
        self.counter.start_val = original + val_1
        self.counter.array = [freq_1 * num for num in old_array]
        for val, freq in tuple_list[1:]:
            start_val = original + val
            new_array = [freq * num for num in old_array]
            self.counter = self.counter.add(npd.MyCounter(start_val, new_array))

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


class WrapListTable(dt.LongIntTable):
    def __init__(self, seed={0: 1}):
        dt.LongIntTable.__init__(self, seed)

    def generate_my_counter(self):
        start_val, array = npd.make_start_val_and_list(self._table)
        return npd.MyCounter(start_val, array)

    def add_list_to_my_counter(self, input_list, input_counter):
        new_counter = npd.MyCounter(input_counter.start_val + input_list[0], input_counter.array[:])
        for val in input_list[1:]:
            start_val = input_counter.start_val + val
            new_array = input_counter.array[:]
            new_counter = new_counter.add(npd.MyCounter(start_val, new_array))
        return new_counter

    def add_list_to_my_counter_lots(self, times, input_list, start_counter):
        for _ in range(times):
            start_counter = self.add_list_to_my_counter(input_list, start_counter)
        return start_counter

    def alt_add_list(self, times, tuple_list):
        input_list = make_list_from_tuples(tuple_list)
        start_counter = self.generate_my_counter()
        out_counter = self.add_list_to_my_counter_lots(times, input_list, start_counter)
        self._table = dict(out_counter.items())





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
str_func = [('scinote: my method, huge int', format_huge_int),
            ('scinote: decimal  huge int', format_huge_int_using_decimal)]
the_args = (123**456, 5)


for words, func in str_func:
    print(time_trial_output(10000, words, func, *the_args))

add_times = 200
my_table = dt.LongIntTable({0: 1})
dec_table = DecimalEventTable({0:1})
c_table = CounterTable({0:1})
np_table = NumpyTable()
l_table = ListTable()
wl_table = WrapListTable()
transform = NumpyTable()
line_302_list = [(val, 1) for val in range(-3, 3, 1)]
# line_302_list = [(1, 1), (7, 1)]


add_list_args = ('add list {}*[1,2,3,4,5,6]: {} - ', add_times, line_302_list)
print()
print_time_trial_for_add_list_funcs(add_list_args, my_table.add, 'mine')
# print_time_trial_for_add_list_funcs(add_list_args, dec_table.add_list, 'dec')
print_time_trial_for_add_list_funcs(add_list_args, c_table.add, 'counter')
print_time_trial_for_add_list_funcs(add_list_args, np_table.add, 'numpy')
print_time_trial_for_add_list_funcs(add_list_args, l_table.add, 'lists')
print_time_trial_for_add_list_funcs(add_list_args, wl_table.alt_add_list, 'wlist')
print_time_trial_for_add_list_funcs(add_list_args, transform.do_trans, 'trans')
print(time_trial_output(add_times, 'stddev mine', my_table.stddev))
print(time_trial_output(add_times, 'stddev dec', dec_table.stddev))
print(time_trial_output(add_times, 'stddev numpy', np_table.stddev))
print(time_trial_output(add_times, 'stddev list', l_table.stddev))

print('confirmation both tables are same. stddev wlst: {}, mine: {}, counter: {}, trans: {}, list: {}'
      .format(wl_table.stddev(), my_table.stddev(), c_table.stddev(), transform.stddev(), l_table.stddev()))
print('means wlst: {:.3}, mine: {:.3}, counter: {:.3}, trans: {:.3}, list: {:.3}'
      .format(wl_table.mean(), my_table.mean(), c_table.mean(), transform.mean(), l_table.mean()))

print()
my_table = dt.LongIntTable({0: 1})
dec_table = DecimalEventTable({0:1})
c_table = CounterTable({0:1})
np_table = NumpyTable()
l_table = ListTable()


# line_291_list = [(1, 1), (100, 10)]
line_291_list = [(val, val) for val in range(3, 10, 2)]
add_tuples_args = ('add tuple list {}*[(1,1), (2,2), ... (6,6)]: {} - ', add_times, line_291_list)
print_time_trial_for_add_list_funcs(add_tuples_args, my_table.add, 'mine')
# print_time_trial_for_add_list_funcs(add_tuples_args, dec_table.add_tuples, 'dec')
print_time_trial_for_add_list_funcs(add_tuples_args, c_table.add, 'counter')
print_time_trial_for_add_list_funcs(add_tuples_args, np_table.add_tuples, 'numpy')
print_time_trial_for_add_list_funcs(add_tuples_args, l_table.add_tuples, 'lists')
print('confirmation both tables are same. stddev dec: {}, mine: {}, counter: {}, np: {}, list: {}'
      .format(dec_table.stddev(), my_table.stddev(), c_table.stddev(), np_table.stddev(), l_table.stddev()))
print('means dec: {:.3}, mine: {:.3}, counter: {:.3}, np: {:.3}, list: {:.3}'
      .format(dec_table.mean(), my_table.mean(), c_table.mean(), np_table.mean(), l_table.mean()))




