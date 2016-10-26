"""a rather messy module that shows time trials.  this is why i don't use Decimal (i am disappoint)
why i don't use Counter (also disappoint. while it is only marginally slower, it doesn't really improve the code).
they are slower, without really conferring any great advantages.  :("""

from __future__ import print_function
from decimal import Decimal
import time
from collections import Counter
import numpy as np
from dicetables.tableinfo import NumberFormatter
import dicetables as dt
import dicetables.baseevents as lim
import numpydict as npd


def time_trial(times, func, *args):
    start = time.clock()
    for _ in range(times):
        func(*args)
    return time.clock() - start


def combine_trial(times, new_events, method, the_object):
    start = time.clock()
    the_object.combine(times, new_events, method)
    result = time.clock() - start
    return result


def print_combine_trial(times, new_events, method, the_object):
    result = combine_trial(times, new_events, method, the_object)
    print('added [{} ... {}]  {} times using {}.  time: {:.3e}'.format(new_events[0],
                                                                       new_events[-1],
                                                                       times,
                                                                       method,
                                                                       result))


def time_trial_output(times, text, func, *args):
    return 'call using {} {} times: {:.5}'.format(text, times, time_trial(times, func, *args))


def print_time_trial_for_add_list_funcs(num_adds, to_add, object_dot_method, label_for_object, method='none'):
    """

    :param num_adds:
    :param to_add:
    :param object_dot_method:
    :param label_for_object:
    :param method: 'none', 'indexed_values', 'all_events', 'flattened_list'
    :return:
    """
    if method == 'none':
        elapsed_time = time_trial(1, object_dot_method, num_adds, to_add)
    else:
        elapsed_time = time_trial(1, object_dot_method, num_adds, to_add, method)
    print('added [{} ... {}]  {} times to {}.  time: {:.3e}'.format(to_add[0],
                                                                    to_add[-1],
                                                                    num_adds,
                                                                    label_for_object,
                                                                    elapsed_time))


def format_huge_int_using_decimal(huge_int, dig_len=4):
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
        """copy of combine_once_with_flattened_list from original."""
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
        """copy of combine_once_with_tuple_list from original"""
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


class CounterTable(lim.AdditiveEvents):
    def __init__(self, seed):
        lim.AdditiveEvents.__init__(self, seed)
        self._table = Counter(self._table)

    def _add_a_list(self, lst):
        newdic = Counter()
        for event in lst:
            event_dic = Counter({event + value: frequency for value, frequency in self._table.items()})
            newdic.update(event_dic)
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
    def __init__(self, seed_dict):
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

    def make_transformation_matrix(self, tuple_list):
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

    def single_transform_add(self, tuple_list):
        trans, start_val = self.make_transformation_matrix(tuple_list)
        new_array = self.counter.array.dot(trans)
        new_start = self.counter.start_val + start_val
        self.counter = npd.NumpyCounter(new_start, new_array)

    def combine_by_matrix_transfor(self, times, tuple_list):
        for _ in range(times):
            self.single_transform_add(tuple_list)

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

    def combine_by_tuple_list(self, times, tuple_list):
        for _ in range(times):
            self.add_a_tuple_list(tuple_list)

    def mean(self):
        """i mean, don't you just sometimes look at a table of values
        and wonder what the mean is?"""
        numerator = sum([value * freq for value, freq in self.counter.items()])
        denominator = sum(self.counter.array)
        if denominator == 0:
            raise ZeroDivisionError('there are no values in the table')
        return dt.safe_true_div(numerator, denominator)

    def stddev(self, decimal_place=4):
        """returns the standdard deviation of the table, with special measures
        to deal with long ints."""
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


def get_int(question):
    """makes sure user input is an int. quit if "q" """
    while True:
        try:
            answer = raw_input(question + '\n>>>')
        except NameError:
            answer = input(question + '\n>>>')
        if answer == 'q':
            raise SystemExit
        try:
            output = int(answer)
            return output
        except ValueError:
            print('must be int OR "q" to quit')
            continue


def get_answer(question, min_val, max_val):
    if max_val > 1000:
        to_format = '{} between {} and {:.2e}'
    else:
        to_format = '{} between {} and {}'
    question = to_format.format(question, min_val, max_val)
    raw_val = get_int(question)
    return min(max_val, (max(min_val, raw_val)))


def super_poopy_ui():

    introduction = """
    this is a hastily cobbled together UI.  If you pick values that are too high, you'll have to restart your kernel.
    This is just to show how different combine methods compare to the two main methods in AdditiveEvents:
    combine_by_flattened_list and combine_by_tuple_list.
    It will compute for each kind compared to the chosen new method and then print the times.
    It will also confirm equality by showing
    "q" will quit at any question prompt.
    """

    print(introduction)
    while True:
        method_choices = {1: 'indexed values',
                          2: 'counter table (currently not working)',
                          3: 'numpy table',
                          4: 'numpy matrix'}
        method_question = '\npick a a table and method\n{}\n'.format(str(method_choices).replace(',', '\n'))
        method_choice = get_answer(method_question, 1, 4)
        method_choice_str = method_choices[method_choice]

        start_dict_size = get_answer('pick a start size for AdditiveEvents', 1, 1000)
        start_dict = dict([(event, 10**(event % 100)) for event in range(start_dict_size)])

        flattened_list_control = lim.AdditiveEvents(start_dict)
        tuple_list_control = lim.AdditiveEvents(start_dict)

        added_events_size = get_answer('how big is the list to add', 2, 1000)
        added_event_occurrences = get_answer('how many occurrences for tuple add', 2, 10**300)
        gaps = get_answer('how many spaces between value', 0, 2)
        flat_events = [(event, 1) for event in range(0, added_events_size, gaps + 1)]
        tuple_events = [(event, added_event_occurrences) for event in range(0, added_events_size, gaps + 1)]

        number_of_adds = get_answer('how many add to do?', 1, 2000)

        print('\n\nRESULTS - VS COMBINE FLATTENED')
        vs_flattened_obj, vs_flattened_method = get_obj_and_method(method_choice, start_dict)
        trial_vs_control(flattened_list_control.combine, 'flattened_list',
                         vs_flattened_method,
                         number_of_adds,
                         flat_events,
                         method_choice_str)
        print()
        confirm_equality(flattened_list_control, vs_flattened_obj, method_choice_str)

        print('\n\nRESULTS - VS COMBINE TUPLE')
        vs_tuple_obj, vs_tuple_method = get_obj_and_method(method_choice, start_dict)
        trial_vs_control(tuple_list_control.combine, 'all_events',
                         vs_tuple_method,
                         number_of_adds,
                         tuple_events,
                         method_choice_str)
        print()
        confirm_equality(tuple_list_control, vs_tuple_obj, method_choice_str)


def get_obj_and_method(number_choice, start_dict):
    indexed_values = lim.AdditiveEvents(start_dict)
    counter = CounterTable(start_dict)
    numpy_table = NumpyTable(start_dict)
    choices = {1: (indexed_values, indexed_values._combine_by_indexed_values),
               2: (counter, counter.combine),
               3: (numpy_table, numpy_table.combine_by_tuple_list),
               4: (numpy_table, numpy_table.combine_by_matrix_transfor)}
    return choices[number_choice]


def trial_vs_control(control_method, control_method_str, trial_method, number_of_adds, events, method_choice_str):
    print_time_trial_for_add_list_funcs(number_of_adds,
                                        events,
                                        control_method,
                                        'control',
                                        control_method_str)
    print_time_trial_for_add_list_funcs(number_of_adds,
                                        events,
                                        trial_method,
                                        method_choice_str)


def confirm_equality(control, other, method_choice_str):
    print('confirmation all tables are same.')
    print('stddev control: {}, stddev {}: {}'
          .format(control.stddev(), method_choice_str, other.stddev()))
    print('mean control: {:.3}, mean {}: {:.3}'
          .format(control.mean(), method_choice_str, other.mean()))


def fastest_vs_tuple_indexed_ui():
    introduction = """
        this is a hastily cobbled together UI.  If you pick values that are too high, you'll have to restart your kernel.
        this shows that fastest is picking the fastest method.
        "q" will quit at any question prompt.
        """

    print(introduction)
    while True:
        print('\n\n')
        start_dict_size = get_answer('pick a start size for AdditiveEvents', 1, 1000)
        start_dict = dict([(event, 2 ** (event % 100)) for event in range(start_dict_size)])

        flattened_list_control = lim.AdditiveEvents(start_dict)
        flattened_list_fastest = lim.AdditiveEvents(start_dict)
        tuple_list_control = lim.AdditiveEvents(start_dict)
        tuple_list_fastest = lim.AdditiveEvents(start_dict)

        added_events_size = get_answer('how long is new events to combine', 2, 1000)
        added_event_occurrences = get_answer('how many occurrences per event', 2, 10 ** 300)
        gaps = get_answer('how many spaces between value', 0, 2)
        flat_events = [(event, 1) for event in range(0, added_events_size, gaps + 1)]
        tuple_events = [(event, added_event_occurrences) for event in range(0, added_events_size, gaps + 1)]

        number_of_adds = get_answer('how many times to combine?', 1, 2000)

        print('\n get_fastest_method')
        print(time_trial_output(1, 'get_fastest', flattened_list_fastest.get_fastest_combine_method, 1, flat_events))
        print('\nFASTEST with one occurrence')
        print_combine_trial(number_of_adds, flat_events, 'fastest', flattened_list_fastest)
        print(flattened_list_fastest.event_range)

        print('\nFLATTENED_LIST with one occurrence')
        print_combine_trial(number_of_adds, flat_events, 'flattened_list', flattened_list_control)
        print(flattened_list_control.event_range)

        print('\n\nFASTEST with many occurrence')
        print_combine_trial(number_of_adds, tuple_events, 'fastest', tuple_list_fastest)
        print(tuple_list_fastest.event_range)

        print('\nTUPLE_LIST with many occurrence')
        print_combine_trial(number_of_adds, tuple_events, 'all_events', tuple_list_control)
        print(tuple_list_control.event_range)


if __name__ == '__main__':
    # super_poopy_ui()
    fastest_vs_tuple_indexed_ui()
    # x = lim.AdditiveEvents({0:1})
    # events = [(event, 1) for event in range(100)]

# # print()
# # x = NumpyTable()
# # x.add(2, [(val, 1) for val in range(1, 7)])
# # print(x.counter.items())
# # x.add_a_tuple_list([(val, 1) for val in range(1, 7)])
# # print(x.counter.items())
# # print(x.stddev())
# # y = dt.DiceTable()
# # y.add_die(3, dt.Die(6))
# # print(y.stddev())
#
# print()
# # formatter = NumberFormatter()
# # str_func = [('format_number: my method, huge int', formatter.format_number),
# #             ('format_number: decimal  huge int', format_huge_int_using_decimal)]
# # the_args = (123**456, )
# #
# #
# # for words, format_func in str_func:
# #     print(time_trial_output(10000, words, format_func, *the_args))
#
# add_times = 1000
# start_dict = dict([(val, 10**val) for val in range(1000)])
# # start_dict = {0: 1}
#
# tuple_list_range = range(1, 7, 1)
#
# flat_list = [(val, 1) for val in tuple_list_range]
#
# many_occurrences = [(val, 5) for val in tuple_list_range]
#
# my_table = lim.AdditiveEvents(start_dict)
# my_table_iv = lim.AdditiveEvents(start_dict)
# dec_table = DecimalEventTable(start_dict)
# c_table = CounterTable(start_dict)
# np_table = NumpyTable(start_dict)
# transform = NumpyTable(start_dict)
#
# # gap ratio maybe 3
# print()
# flat_list_range = flat_list[-1][0] - flat_list[0][0] + 1
# print('range to vals is {}'.format(float(flat_list_range) / len(flat_list)))
# print_time_trial_for_add_list_funcs(add_times, flat_list, my_table.combine, 'mine',
#                                     method='flattened_list')
# print_time_trial_for_add_list_funcs(add_times, flat_list, my_table_iv.combine, 'indexed',
#                                     method='indexed_values')
# # print_time_trial_for_add_list_funcs(add_times, flat_list, dec_table.add_list, 'dec')
# # print_time_trial_for_add_list_funcs(add_times, flat_list, c_table.add, 'counter')
# # print_time_trial_for_add_list_funcs(add_times, flat_list, np_table.add, 'numpy')
# # print_time_trial_for_add_list_funcs(add_times, flat_list, transform.combine_by_matrix_transfor, 'trans')
#
#
# print('confirmation all tables are same.')
# print('stddevs mine: {}, indexed: {}, dec: {}, counter: {}, numpy: {}, tansform: {}'
#       .format(my_table.stddev(), my_table_iv.stddev(), dec_table.stddev(), c_table.stddev(), np_table.stddev(),
#               transform.stddev()))
# print('means mine: {:.3}, indexed: {:.3}, dec: {:.3}, counter: {:.3}, numpy: {:.3}, tansform: {:.3}'
#       .format(my_table.mean(), my_table_iv.mean(), dec_table.mean(), c_table.mean(), np_table.mean(),
#               transform.mean()))
#
# print()
# my_table = lim.AdditiveEvents(start_dict)
# my_table_iv = lim.AdditiveEvents(start_dict)
# dec_table = DecimalEventTable(start_dict)
# c_table = CounterTable(start_dict)
# np_table = NumpyTable(start_dict)
# # gap ratio maybe 2.5
#
# many_occurrences_range = many_occurrences[-1][0] - many_occurrences[0][0] + 1
# print('range to vals is {}'.format(float(many_occurrences_range) / len(many_occurrences)))
# print_time_trial_for_add_list_funcs(add_times, many_occurrences, my_table.combine, 'mine',
#                                     method='all_events')
# print_time_trial_for_add_list_funcs(add_times, many_occurrences, my_table_iv.combine, 'indexed',
#                                     method='indexed_values')
# # print_time_trial_for_add_list_funcs(add_times, many_occurrences, dec_table.add_tuples, 'dec')
# # print_time_trial_for_add_list_funcs(add_times, many_occurrences, c_table.add, 'counter')
# # print_time_trial_for_add_list_funcs(add_times, many_occurrences, np_table.add_tuples, 'numpy')
# print('confirmation all tables are same.')
# print('stddevs mine: {}, indexed: {}, dec: {}, counter: {}, numpy: {}'
#       .format(my_table.stddev(), my_table_iv.stddev(), dec_table.stddev(), c_table.stddev(), np_table.stddev()))
# print('means mine: {:.3}, indexed: {:.3}, dec: {:.3}, counter: {:.3}, numpy: {:.3}'
#       .format(my_table.mean(), my_table_iv.mean(), dec_table.mean(), c_table.mean(), np_table.mean()))
