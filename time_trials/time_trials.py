"""a rather messy module that shows time trials.  this is why i don't use Decimal (i am disappoint)
why i don't use Counter (also disappoint. while it is only marginally slower, it doesn't really improve the code).
they are slower, without really conferring any great advantages.  :("""

from __future__ import print_function
from decimal import Decimal
import time
from collections import Counter
import numpy as np
from tools.dictcombiner import DictCombiner
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
    method_dict = {'fastest': the_object.combine,
                   'tuple_list': the_object.combine_by_tuple_list,
                   'indexed_values': the_object.combine_by_indexed_values,
                   'flattened_list': the_object.combine_by_flattened_list}
    method_dict[method](times, new_events)
    result = time.clock() - start
    return result


def print_combine_trial(times, new_events, method, the_object):
    result = combine_trial(times, new_events, method, the_object)
    start, stop = new_events.event_range
    first = new_events.get_event(start)
    last = new_events.get_event(stop)
    print('added [{} ... {}]  {} times using {}.  time: {:.3e}'.format(first,
                                                                       last,
                                                                       times,
                                                                       method,
                                                                       result))


def time_trial_output(times, text, func, *args):
    return 'call using {} {} times: {:.5}'.format(text, times, time_trial(times, func, *args))


# for demonstration that NumberFormatter.format() works better
def format_huge_int_using_decimal(huge_int, dig_len=4):
    return '{:.{}e}'.format(Decimal(huge_int), dig_len - 1)


# here for notes only if need be can experiment in DictCombiner
class CounterTable(lim.AdditiveEvents):
    def __init__(self, seed):
        lim.AdditiveEvents.__init__(self, seed)
        self._table = Counter(self._table)

    def _add_a_list(self, lst):
        new_dic = Counter()
        for event in lst:
            event_dic = Counter({event + value: frequency for value, frequency in self._table.items()})
            new_dic.update(event_dic)
        self._table = new_dic

    def _add_tuple_list(self, lst):
        new_dic = Counter()
        for value, current_frequency in self._table.items():
            for val, freq in lst:
                new_dic[value + val] += freq * current_frequency
        self._table = new_dic


def make_list_from_tuples(tuple_list):
    out = []
    for val, freq in tuple_list:
        out = out + freq * [val]
    return out


# here for notes only!  can now use DictCombiner and add there!
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

    def make_transformation_matrix(self, events_tuples):
        increase_in_start_val = min(events_tuples)[0]
        events_tuples_size = max(events_tuples)[0] - increase_in_start_val
        row = self.counter.array.size
        col = row + events_tuples_size
        trans = np.zeros((row, col), dtype=object)
        for row in range(trans.shape[0]):
            for index, val in events_tuples:
                index -= increase_in_start_val
                trans[row][row + index] = val
        return trans, increase_in_start_val

    def single_transform_add(self, tuple_list):
        trans, start_val = self.make_transformation_matrix(tuple_list)
        new_array = self.counter.array.dot(trans)
        new_start = self.counter.start_val + start_val
        self.counter = npd.NumpyCounter(new_start, new_array)

    def combine_by_matrix_transform(self, times, tuple_list):
        for _ in range(times):
            self.single_transform_add(tuple_list)


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


def fastest_vs_tuple_indexed_ui():
    introduction = """
        this is a hastily cobbled together UI.  If you pick values that are too high,
        you'll have to restart your kernel.
        this shows that fastest is picking the fastest method.
        "q" will quit at any question prompt.
        """

    print(introduction)
    while True:
        print('\n\n')
        start_dict_size = get_answer('pick a start size for AdditiveEvents', 1, 1000)
        start_dict = dict([(event, 2 ** (event % 100)) for event in range(start_dict_size)])

        show_fastest_method_speed = DictCombiner(start_dict)
        flattened_list_control = lim.AdditiveEvents(start_dict)
        flattened_list_fastest = lim.AdditiveEvents(start_dict)
        tuple_list_control = lim.AdditiveEvents(start_dict)
        tuple_list_fastest = lim.AdditiveEvents(start_dict)

        added_events_size = get_answer('how long is new events to combine', 2, 1000)
        added_event_occurrences = get_answer('how many occurrences per event', 2, 10 ** 300)
        gaps = get_answer('how many spaces between value', 0, 2)
        flat_events = dt.AdditiveEvents(dict.fromkeys(range(0, added_events_size, gaps + 1), 1))
        tuple_events = dt.AdditiveEvents(dict.fromkeys(range(0, added_events_size, gaps + 1), added_event_occurrences))

        number_of_adds = get_answer('how many times to combine?', 1, 2000)

        print('\n get_fastest_method')
        print(time_trial_output(1, 'get_fastest', show_fastest_method_speed.get_fastest_combine_method, 1, flat_events))
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
        print_combine_trial(number_of_adds, tuple_events, 'tuple_list', tuple_list_control)
        print(tuple_list_control.event_range)


if __name__ == '__main__':
    fastest_vs_tuple_indexed_ui()
