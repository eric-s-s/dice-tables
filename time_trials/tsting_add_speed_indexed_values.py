"""a module solely for finding how add_a_list and add_tuple_list compare.
it's effectively the empirical proof for how LongIntTable.add() chooses
the fastest method with it's _fastest() function."""
# pylint: disable=protected-access
from __future__ import print_function

from math import log10
import time
import random
from os import getcwd
import matplotlib.pyplot as plt
import numpy as np
import dicetables.longintmath as lim


def generate_tuple_list_with_increasing_number_of_events(first_event, start_length, event_occurrences,
                                                         len_increase_step=1):
    """

    :param first_event:
    :param start_length:
    :param event_occurrences:
    :param len_increase_step: =1
    :return: generator(next)
    """
    tuple_list_of_events = [(first_event, event_occurrences)]
    for add_to_first_event in range(1, start_length):
        tuple_list_of_events.append((first_event + add_to_first_event, event_occurrences))
    while True:
        yield tuple_list_of_events
        highest_event = tuple_list_of_events[-1][0]
        new_tuples = [(highest_event + 1 + step, event_occurrences) for step in range(len_increase_step)]
        tuple_list_of_events += new_tuples


def generate_tuple_list_with_exponentially_increasing_occurrences(first_event, start_length, exponent_increment):
    """

    :param first_event:
    :param start_length:
    :param exponent_increment:
    :return: generator(next)
    """
    tuple_list_of_events = [(event, 1) for event in range(first_event, first_event + start_length)]
    exponent = 0.0
    while True:
        yield tuple_list_of_events
        exponent += exponent_increment
        tuple_list_of_events = [(event, int(10 ** exponent)) for event in range(first_event, first_event + start_length)]


def generate_tuple_list_with_increasing_gaps(first_event, start_length, event_occurrences=1, gaps_per_iteration=1,
                                             randomize=True):
    """

    :param first_event:
    :param start_length:
    :param event_occurrences: =1
    :param gaps_per_iteration: =1
    :param randomize: =True
    :return: generator
    """
    tuple_list_of_events = [(first_event + index, event_occurrences) for index in range(start_length)]
    while sum([event[1] for event in tuple_list_of_events]) > 2 * event_occurrences:
        yield tuple_list_of_events
        for _ in range(gaps_per_iteration):
            if randomize:
                start_search_index = random.randrange(1, start_length - 1)
            else:
                start_search_index = len(tuple_list_of_events) - 2
            only_occurrences = [event[1] for event in tuple_list_of_events]
            while not only_occurrences[start_search_index:-1].count(event_occurrences) and start_search_index:
                start_search_index -= 1
            index_to_make_zero = only_occurrences[start_search_index:].index(event_occurrences) + start_search_index
            event_value = tuple_list_of_events[index_to_make_zero][0]
            tuple_list_of_events[index_to_make_zero] = (event_value, 0)


def get_generator(variable_name, first_event, start_length,
                  exponent_increment=1., event_occurrences=1, len_increase_step=1, gaps_per_iteration=1, randomize=True):
    """

    :param variable_name: 'list_length', 'event_occurrences', 'increasing_gaps'
    :param first_event:
    :param start_length:
    :param exponent_increment: =1.0
    :param event_occurrences: =1
    :param len_increase_step: =1
    :param gaps_per_iteration: =1
    :param randomize: True
    :return:
    """
    if variable_name == 'list_length':
        return generate_tuple_list_with_increasing_number_of_events(first_event, start_length,
                                                                    event_occurrences, len_increase_step)
    if variable_name == 'event_occurrences':
        return generate_tuple_list_with_exponentially_increasing_occurrences(first_event, start_length,
                                                                             exponent_increment)
    if variable_name == 'increasing_gaps':
        return generate_tuple_list_with_increasing_gaps(first_event, start_length,
                                                        event_occurrences, gaps_per_iteration, randomize)


def one_time_trial(combine_times, tuple_list, input_dict_size=1, use_exponential_occurrences=False):
    """

    :param combine_times:
    :param tuple_list:
    :param input_dict_size: =1
    :param use_exponential_occurrences: =True
    :return: (list_len, # occurrences, range/events, start dict size)\n
        , control time, IndexedValues time
    """
    prepped_list = lim.verify_and_prep_tuple_list(tuple_list)
    if prepped_list[0][1] < 10**100:
        print('one_time_trial prepped list {}'.format(prepped_list))
    input_dict = get_input_dict(input_dict_size, use_exponential_occurrences)
    control_method = get_control_method(prepped_list)
    control_events = lim.AdditiveEvents(input_dict)

    if control_method == 'tuple_list':
        control_start = time.clock()
        control_events.combine_by_tuple_list(combine_times, prepped_list)
        control_time = time.clock() - control_start
    else:
        control_start = time.clock()
        control_events.combine_by_flattened_list(combine_times, prepped_list)
        control_time = time.clock() - control_start

    events_for_indexed_values = lim.AdditiveEvents(input_dict)
    indexed_values_start = time.clock()
    events_for_indexed_values.combine_by_indexed_values(combine_times, prepped_list)
    indexed_values_time = time.clock() - indexed_values_start

    list_length = float(len(prepped_list))
    event_occurrences_exponent = log10(prepped_list[0][1])
    events_range_vs_events = (prepped_list[-1][0] - prepped_list[0][0] + 1) / float(list_length)
    start_dict_size = float(input_dict_size)
    y_axis_variables = (list_length, event_occurrences_exponent, events_range_vs_events, start_dict_size)

    return y_axis_variables, control_time, indexed_values_time


def get_input_dict(input_dict_size, use_exponential_occurences):
    if use_exponential_occurences:
        input_dict = dict([(event, 1 + 10 ** (event % 100)) for event in range(input_dict_size)])
    else:
        input_dict = dict([(event, 1 + event % 100) for event in range(input_dict_size)])
    return input_dict


def get_control_method(prepped_list):
    if prepped_list[0][1] == 1:
        return 'flattened_list'
    else:
        return 'tuple_list'


def time_trial_vary_start_dict_first_add(events_tuple_list, input_dict_start_size=1000, input_dict_downward_step=5,
                                         number_of_adds=1, use_exponential_occurrences=False):
    """

    :param events_tuple_list:
    :param input_dict_start_size: =1000
    :param input_dict_downward_step: =5
    :param number_of_adds: =1
    :param use_exponential_occurrences: =False
    :return:
    """
    adds_per_trial = number_of_adds
    variable_name = 'start_dict_size'
    variable_values = []
    control_times = []
    indexed_values_times = []
    print('please wait for the down to reach zero')
    input_dict_size = input_dict_start_size
    while input_dict_size > 0:
        print('adds {}'.format(adds_per_trial))
        y_axis, control_time, indexed_values_time = one_time_trial(
            adds_per_trial,
            events_tuple_list,
            input_dict_size=input_dict_size,
            use_exponential_occurrences=use_exponential_occurrences
        )
        input_dict_size -= input_dict_downward_step

        variable = y_axis[3]
        print('results: variable: {:.2}, control: {:.3e}, indexed vals: {:.3e}'.format(variable,
                                                                                       control_time,
                                                                                       indexed_values_time))
        print('count down: {}\n'.format(input_dict_size))

        variable_values.append(variable)
        control_times.append(control_time)
        indexed_values_times.append(indexed_values_time)

    return variable_values, variable_name, control_times, indexed_values_times


def time_trial(generator, variable_name, adds_per_trial=1, automatic_adds_per_trial=False, input_dict_size=1,
               number_of_data_pts=100):
    """

    :param generator:
    :param variable_name: 'list_length', 'event_occurrences', 'increasing_gaps'
    :param adds_per_trial: =1
    :param automatic_adds_per_trial: =False
    :param input_dict_size: =1
    :param number_of_data_pts: =100
    :return: variable_values, variable_name, control_times, indexed_values_times
    """
    tuple_list_length_times_add_times = 2200
    variable_values = []
    control_times = []
    indexed_values_times = []
    count = number_of_data_pts
    print('please wait for the count-up/down to reach zero')
    while count > 0:

        try:
            tuple_list_for_trial = next(generator)
        except StopIteration:
            break
        if automatic_adds_per_trial:
            adds_per_trial = int(max(1, tuple_list_length_times_add_times / len(tuple_list_for_trial)))

        print('adds {}'.format(adds_per_trial))
        y_axis, control_time, indexed_values_time = one_time_trial(adds_per_trial, tuple_list_for_trial,
                                                                   input_dict_size=input_dict_size)
        if variable_name == 'list_length':
            variable = y_axis[0]
        elif variable_name == 'event_occurrences':
            variable = y_axis[1]
        else:
            variable = y_axis[2]
        print('results: variable: {:.2}, control: {:.3e}, indexed vals: {:.3e}'.format(variable,
                                                                                       control_time,
                                                                                       indexed_values_time))
        print('count down: {}\n'.format(count))
        count -= 1
        variable_values.append(variable)
        control_times.append(control_time)
        indexed_values_times.append(indexed_values_time)

    return variable_values, variable_name, control_times, indexed_values_times


def plot_trial(variable_values, variable_name, control_times, iv_times, title='none', figure=1):
    """

    :param variable_values:
    :param variable_name:'list_length', 'event_occurrences', 'increasing_gaps', 'dict_size'
    :param control_times:
    :param iv_times:
    :param title:
    :param figure:
    :return:
    """
    plt.ion()
    plt.figure(figure)
    plt.plot(variable_values, control_times, 'bo-', label='control')
    plt.plot(variable_values, iv_times, 'r*-', label='IndexedValues')
    plt.ylabel('time')
    x_labels = {'list_length': 'size of tuple list',
                'event_occurrences': '10 ** exponent event occurrences',
                'increasing_gaps': 'ratio of events range to non-zero events',
                'start_dict_size': 'number of events in starting dictionary'}
    plt.xlabel(x_labels[variable_name])

    plt.legend()
    intersection, control_fit, iv_fit = get_poly_fit_and_intersection(variable_values, control_times, iv_times)
    title += '\nintersection = {}'.format(intersection)
    plt.title(title)
    plt.plot(variable_values, control_fit, 'c-')
    plt.plot(variable_values, iv_fit, 'c-')
    plt.pause(0.01)
    return intersection


def get_poly_fit_and_intersection(variable_values, control_times, iv_times):
    control_slope, control_constant = np.polyfit(variable_values, control_times, 1)
    iv_slope, iv_constant = np.polyfit(variable_values, iv_times, 1)
    intersection = (control_constant - iv_constant) / (iv_slope - control_slope)
    control_poly_fit_values = [(control_slope * x + control_constant) for x in variable_values]
    iv_poly_fit_values = [(iv_slope * x + iv_constant) for x in variable_values]
    return intersection, control_poly_fit_values, iv_poly_fit_values


def get_welcome():
    """return welcome_message.txt"""
    try:
        welcome_file_name = getcwd() + '\\' + 'welcome_message.txt'
        welcome_file = open(welcome_file_name, 'r')
        welcome_message = welcome_file.read()
    except IOError:
        welcome_message = 'took a guess where "welcome_' \
                          'message.txt" was, and I was wrong.'
    return welcome_message


def get_int(question):
    """makes sure user input is an int. quit if "q" """
    while True:
        try:
            answer = raw_input(question + '>>>')
        except NameError:
            answer = input(question + '>>>')
        if answer == 'q':
            raise SystemExit
        try:
            output = int(answer)
            return output
        except ValueError:
            print('must be int OR "q" to quit')
            continue


def get_answer(question, min_val, max_val):
    question = '{} between {} and {}'.format(question, min_val, max_val)
    raw_val = get_int(question)
    return min(max_val, (max(min_val, raw_val)))


def do_trials_vary_start_dict(add_list_len=10, occurrences_are_many=False, adds_list=(1, 2, 5)):
    """

    :param add_list_len: =10
    :param occurrences_are_many: =False
    :param adds_list: =(1, 2, 5)
    :return:
    """
    if occurrences_are_many:
        occurrences = 10
    else:
        occurrences = 1
    list_for_vary_start_dict = get_generator('list_length', 0, add_list_len, event_occurrences=occurrences)
    tuple_list_for_time_trial = next(list_for_vary_start_dict)

    for add_variable in adds_list:
        title = 'vary size of start dict. number of adds = {}\n'.format(add_variable)
        title += 'input occurrences = {}.  input list length = {}'.format(occurrences, add_list_len)
        results = time_trial_vary_start_dict_first_add(tuple_list_for_time_trial, input_dict_start_size=3000,
                                                       input_dict_downward_step=50, number_of_adds=add_variable)
        plot_trial(*results, figure=add_variable, title=title)


def do_trials_vary_event_occurrences(add_list_len=10, start_dict_size=1, adds_list=(1, 2, 5)):
    """

    :param add_list_len: =10
    :param start_dict_size: =1
    :param adds_list: =(1, 2, 5)
    :return:
    """
    for add_variable in adds_list:
        event_occurrences_generator = get_generator('event_occurrences', 0, add_list_len, exponent_increment=0.25)
        results = time_trial(event_occurrences_generator, 'event_occurrences', adds_per_trial=add_variable,
                             input_dict_size=start_dict_size, number_of_data_pts=100)
        title = 'increasing event occurrences. number of adds={}\n'.format(add_variable)
        title += 'starting dict size={}. input list length = {}'.format(start_dict_size, add_list_len)
        plot_trial(*results, figure=10 + add_variable, title=title)


def do_trials_vary_list_length(start_dict_size=1, occurrences_are_many=False, adds_list=(1, 2, 5)):
    if occurrences_are_many:
        occurrences = 10
    else:
        occurrences = 1
    for add_variable in adds_list:
        list_length_generator = get_generator('list_length', 0, 2, event_occurrences=occurrences, len_increase_step=2)
        results = time_trial(list_length_generator, 'list_length', adds_per_trial=add_variable,
                             input_dict_size=start_dict_size, number_of_data_pts=100)
        title = 'increasing list length. number of adds={}\n'.format(add_variable)
        title += 'starting dict size={}. input list occurrences = {}'.format(start_dict_size, occurrences)
        plot_trial(*results, figure=20 + add_variable, title=title)


def do_trials_vary_gaps_in_list(add_list_len=100, start_dict_size=1, occurrences_are_many=False, randomize_gaps=True,
                                adds_list=(1, 2, 5)):
    """

    :param add_list_len: =100
    :param start_dict_size: =1
    :param occurrences_are_many: =False
    :param randomize_gaps: =True
    :param adds_list: =(1, 2, 5)
    :return:
    """
    if occurrences_are_many:
        occurrences = 10
    else:
        occurrences = 1
    gaps_per_iteration = max(1, add_list_len // 100)
    for add_variable in adds_list:
        increasing_gaps_generator = get_generator('increasing_gaps', 0, add_list_len, event_occurrences=occurrences,
                                                  gaps_per_iteration=gaps_per_iteration, randomize=randomize_gaps)
        results = time_trial(increasing_gaps_generator, 'increasing_gaps', adds_per_trial=add_variable,
                             input_dict_size=start_dict_size, number_of_data_pts=100)

        title = 'making many gaps in list. number of adds={}\n'.format(add_variable)
        title += 'starting dict size={}. input list length: {}, occurrences: {}'.format(start_dict_size,
                                                                                        add_list_len,
                                                                                        occurrences)
        plot_trial(*results, figure=30 + add_variable, title=title)

# TODO broken
def quick_and_dirty_ui():
    """a UI to demonstrate add speeds"""
    print(get_welcome())

    figure = 0

    while True:
        figure += 1
        plt.ion()
        variable_choice = get_int('enter "1" for varying list_length\nand "2" for varying # of occurrences\n')

        if variable_choice == 1:
            print('chose list length')
            variable = 'list_length'
        else:
            print('chose event occurrences')
            variable = 'event_occurrences'

        start_val = get_answer('pick a starting index for list', -100, 100)
        if variable == 'list_length':
            exp = get_answer('choose number of occurrences based on 10 ** exponent\nenter exponent', 0, 1000)
            occurrences_or_exp_step = 10 ** exp

        else:
            occurrences_or_exp_step = get_answer('choose exponent step for event occurrences', 1, 100)
        start_length = get_answer('choose the initial length of list', 1, 1000)

        intersection = get_and_plot_one_trial(variable, start_val, occurrences_or_exp_step, start_length)

        print('the graphs intersect at %s' % intersection)
        plt.pause(0.1)


if __name__ == '__main__':
    # do_trials_vary_event_occurrences(start_dict_size=1, add_list_len=100)
    do_trials_vary_gaps_in_list(start_dict_size=100, add_list_len=100, randomize_gaps=True, occurrences_are_many=True)
    # do_trials_vary_list_length()
    # do_trials_vary_start_dict()
    plt.waitforbuttonpress()
