"""a module solely for finding how add_a_list and add_tuple_list compare.
it's effectively the empirical proof for how LongIntTable.add() chooses
the fastest method with it's get_fastest_method() function."""

from __future__ import print_function

from math import log10
import time
import random
from os import getcwd
from itertools import cycle
import matplotlib.pyplot as plt
import numpy as np
from dicetables.additiveevents import AdditiveEvents

WELCOME_TXT = "hi"


def input_py_2_and_3(question):
    try:
        return raw_input(question)
    except NameError:
        return input(question)


def generate_tuple_list_with_increasing_number_of_events(
    first_event, start_length, event_occurrences, len_increase_step=1
):
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
        new_tuples = [
            (highest_event + 1 + step, event_occurrences) for step in range(len_increase_step)
        ]
        tuple_list_of_events += new_tuples


def generate_tuple_list_with_increasing_occurrences(
    first_event, start_length, increment, exponential_increase=True
):
    """

    :param first_event:
    :param start_length:
    :param increment:
    :param exponential_increase: =True
    :return: generator(next)
    """
    tuple_list_of_events = [(event, 1) for event in range(first_event, first_event + start_length)]
    growth = 0.0
    while True:
        yield tuple_list_of_events
        growth += increment
        if exponential_increase:
            tuple_list_of_events = [
                (event, int(2**growth)) for event in range(first_event, first_event + start_length)
            ]
        else:
            tuple_list_of_events = [
                (event, int(growth)) for event in range(first_event, first_event + start_length)
            ]


def generate_tuple_list_with_increasing_gaps(
    first_event, start_length, event_occurrences=1, gaps_per_iteration=1, randomize=True
):
    """

    :param first_event:
    :param start_length:
    :param event_occurrences: =1
    :param gaps_per_iteration: =1
    :param randomize: =True
    :return: generator
    """
    tuple_list_of_events = [
        (first_event + index, event_occurrences) for index in range(start_length)
    ]
    while sum([event[1] for event in tuple_list_of_events]) > 2 * event_occurrences:
        yield tuple_list_of_events
        for _ in range(gaps_per_iteration):
            if randomize:
                start_search_index = random.randrange(1, start_length - 1)
            else:
                start_search_index = len(tuple_list_of_events) - 2
            only_occurrences = [event[1] for event in tuple_list_of_events]
            while (
                not only_occurrences[start_search_index:-1].count(event_occurrences)
                and start_search_index
            ):
                start_search_index -= 1
            index_to_make_zero = (
                only_occurrences[start_search_index:].index(event_occurrences) + start_search_index
            )
            event_value = tuple_list_of_events[index_to_make_zero][0]
            tuple_list_of_events[index_to_make_zero] = (event_value, 0)


def get_generator(
    variable_name,
    first_event,
    start_length,
    growth_increment=1.0,
    event_occurrences=1,
    len_increase_step=1,
    gaps_per_iteration=1,
    randomize=True,
    exponential_increase=True,
):
    """

    :param variable_name: 'list_length', 'event_occurrences', 'increasing_gaps'
    :param first_event:
    :param start_length:
    :param growth_increment: =1.0
    :param event_occurrences: =1
    :param len_increase_step: =1
    :param gaps_per_iteration: =1
    :param randomize: True
    :param exponential_increase: =True
    :return:
    """
    if variable_name == "list_length":
        return generate_tuple_list_with_increasing_number_of_events(
            first_event, start_length, event_occurrences, len_increase_step
        )
    if variable_name == "event_occurrences":
        return generate_tuple_list_with_increasing_occurrences(
            first_event, start_length, growth_increment, exponential_increase
        )
    if variable_name == "increasing_gaps":
        return generate_tuple_list_with_increasing_gaps(
            first_event, start_length, event_occurrences, gaps_per_iteration, randomize
        )


def one_time_trial(
    combine_times, events_tuples, input_dict_size=1, use_exponential_occurrences=True
):
    """

    :param combine_times:
    :param events_tuples:
    :param input_dict_size: =1
    :param use_exponential_occurrences: =True
    :return: (list_len, # occurrences, log10(# occurrences), range/events, start dict size)\n
        , control time, IndexedValues time
    """

    if events_tuples[0][1] < 10**100:
        print("one_time_trial prepped list [{} .. {}]".format(events_tuples[0], events_tuples[-1]))
    input_dict = get_input_dict(input_dict_size, use_exponential_occurrences)

    events_tuples = [pair for pair in events_tuples if pair[1]]

    control_time, indexed_values_time = get_control_and_indexed_values_times(
        combine_times, events_tuples, input_dict
    )

    list_length = float(len(events_tuples))
    event_occurrences = float(events_tuples[0][1])
    event_occurrences_exponent = log10(events_tuples[0][1])
    events_range_vs_events = (max(events_tuples)[0] - min(events_tuples)[0] + 1) / float(
        list_length
    )
    start_dict_size = float(input_dict_size)
    y_axis_variables = (
        list_length,
        event_occurrences,
        event_occurrences_exponent,
        events_range_vs_events,
        start_dict_size,
    )

    return y_axis_variables, control_time, indexed_values_time


def get_input_dict(input_dict_size, use_exponential_occurrences):
    if use_exponential_occurrences:
        input_dict = dict([(event, 1 + 2 ** (event % 1000)) for event in range(input_dict_size)])
    else:
        input_dict = dict([(event, 1 + event % 1000) for event in range(input_dict_size)])
    return input_dict


def get_control_and_indexed_values_times(combine_times, events_tuples, input_dict):
    control_events_action = get_control_action(input_dict, events_tuples)

    events_for_indexed_values = AdditiveEvents(input_dict)
    events_to_add = AdditiveEvents(dict(events_tuples))
    indexed_values_start = time.clock()
    events_for_indexed_values.combine_by_indexed_values(events_to_add, combine_times)
    indexed_values_time = time.clock() - indexed_values_start
    control_start = time.clock()
    control_events_action(events_to_add, combine_times)
    control_time = time.clock() - control_start
    return control_time, indexed_values_time


def get_control_action(input_dict, events_tuples):
    control_events = AdditiveEvents(input_dict)
    control_method_str = get_control_method_str(events_tuples)
    control_method_dict = {
        "tuple_list": control_events.combine_by_dictionary,
        "flattened_list": control_events.combine_by_flattened_list,
    }
    control_events_action = control_method_dict[control_method_str]
    return control_events_action


def get_control_method_str(prepped_list):
    if prepped_list[0][1] == 1:
        return "flattened_list"
    else:
        return "tuple_list"


def time_trial_vary_start_dict(
    events_tuple_list,
    input_dict_start_size=1000,
    input_dict_downward_step=5,
    number_of_adds=1,
    use_exponential_occurrences=True,
):
    """

    :param events_tuple_list:
    :param input_dict_start_size: =1000
    :param input_dict_downward_step: =5
    :param number_of_adds: =1
    :param use_exponential_occurrences: =False
    :return:
    """
    adds_per_trial = number_of_adds
    variable_name = "start_dict_size"
    variable_values = []
    control_times = []
    indexed_values_times = []
    print("please wait for the down to reach zero")
    input_dict_size = input_dict_start_size
    while input_dict_size > 0:
        print("adds {}".format(adds_per_trial))
        y_axis, control_time, indexed_values_time = one_time_trial(
            adds_per_trial,
            events_tuple_list,
            input_dict_size=input_dict_size,
            use_exponential_occurrences=use_exponential_occurrences,
        )
        input_dict_size -= input_dict_downward_step

        variable = y_axis[4]
        print(
            "results: variable: {:.2}, control: {:.3e}, IndexedValues: {:.3e}".format(
                variable, control_time, indexed_values_time
            )
        )
        print("count down: {}\n".format(input_dict_size))

        variable_values.append(variable)
        control_times.append(control_time)
        indexed_values_times.append(indexed_values_time)

    return variable_values, variable_name, control_times, indexed_values_times


def time_trial(
    generator,
    variable_name,
    adds_per_trial=1,
    automatic_adds_per_trial=False,
    input_dict_size=1,
    number_of_data_pts=100,
):
    """

    :param generator:
    :param variable_name: 'list_length', 'event_occurrences_linear', 'event_occurrences', 'increasing_gaps'
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
    print("please wait for the count-up/down to reach zero")
    while count > 0:
        try:
            tuple_list_for_trial = next(generator)
        except StopIteration:
            break
        if automatic_adds_per_trial:
            adds_per_trial = int(
                max(1, tuple_list_length_times_add_times / len(tuple_list_for_trial))
            )

        print("adds {}".format(adds_per_trial))
        y_axis, control_time, indexed_values_time = one_time_trial(
            adds_per_trial, tuple_list_for_trial, input_dict_size=input_dict_size
        )
        variable_order = [
            "list_length",
            "event_occurrences_linear",
            "event_occurrences",
            "increasing_gaps",
        ]
        index = variable_order.index(variable_name)
        variable = y_axis[index]

        print(
            "results: variable: {:.2}, control: {:.3e}, IndexedValues: {:.3e}".format(
                variable, control_time, indexed_values_time
            )
        )
        print("count down: {}\n".format(count))
        count -= 1
        variable_values.append(variable)
        control_times.append(control_time)
        indexed_values_times.append(indexed_values_time)

    return variable_values, variable_name, control_times, indexed_values_times


def plot_trial_with_ratio(
    variable_values,
    variable_name,
    control_times,
    iv_times,
    title="none",
    figure=1,
    style="bo-",
    label="",
    base_line=False,
):
    """

    :param variable_values:
    :param variable_name: 'list_length', 'event_occurrences', 'event_occurrences_linear', 'increasing_gaps', 'dict_size'
    :param control_times:
    :param iv_times:
    :param title:
    :param figure:
    :param style: ='bo-'
    :param label: =''
    :param base_line: =False
    :return:
    """
    plt.ion()

    # use_figure = plt.figure(figure)
    # use_figure.clf()
    speed_ratios = []
    equality_line = [1.0] * len(control_times)
    for index, numerator in enumerate(control_times):
        speed_ratios.append(numerator / iv_times[index])
    plt.plot(variable_values, speed_ratios, style, label=label)
    if base_line:
        plt.plot(variable_values, equality_line, "g-", label="equal speed")
    plt.ylabel("speed of indexed values over speed of control")
    x_labels = {
        "list_length": "size of tuple list",
        "event_occurrences": "10 ** exponent event occurrences",
        "event_occurrences_linear": "event occurrences",
        "increasing_gaps": "ratio of events range to non-zero events",
        "start_dict_size": "number of events in starting dictionary",
    }
    plt.xlabel(x_labels[variable_name])

    plt.legend()
    plt.title(title)
    plt.pause(0.01)


def plot_trial_two_lines(
    variable_values, variable_name, control_times, iv_times, title="none", figure=1
):
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

    use_figure = plt.figure(figure)
    use_figure.clf()
    plt.plot(variable_values, control_times, "bo-", label="control")
    plt.plot(variable_values, iv_times, "r*-", label="IndexedValues")
    plt.ylabel("time")
    x_labels = {
        "list_length": "size of tuple list",
        "event_occurrences": "10 ** exponent event occurrences",
        "increasing_gaps": "ratio of events range to non-zero events",
        "start_dict_size": "number of events in starting dictionary",
    }
    plt.xlabel(x_labels[variable_name])

    plt.legend()
    intersection, control_fit, iv_fit = get_poly_fit_and_intersection(
        variable_values, control_times, iv_times
    )
    title += "\nintersection = {}".format(intersection)
    plt.title(title)
    plt.plot(variable_values, control_fit, "c-")
    plt.plot(variable_values, iv_fit, "c-")
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
        welcome_file_name = getcwd() + "\\" + "welcome_message.txt"
        welcome_file = open(welcome_file_name, "r")
        welcome_message = welcome_file.read()
    except IOError:
        welcome_message = 'took a guess where "welcome_' 'message.txt" was, and I was wrong.'
    return welcome_message


def get_int(question):
    """makes sure user input is an int. quit if "q" """
    while True:
        answer = input_py_2_and_3(question + "\n>>> ")
        if answer == "q":
            raise SystemExit
        try:
            output = int(answer)
            return output
        except ValueError:
            print('must be int OR "q" to quit')
            continue


def get_answer(question, min_val, max_val):
    question = "{} between {} and {}".format(question, min_val, max_val)
    raw_val = get_int(question)
    return min(max_val, (max(min_val, raw_val)))


def get_plot_style_generator():
    pt_style = cycle(["o", "<", ">", "v", "s", "p", "*", "+", "x", "D", "d"])
    colors = cycle(["b", "y", "r", "c", "m", "k", "g"])
    while True:
        yield "{}{}-".format(next(colors), next(pt_style))


def do_trials_vary_start_dict(
    add_list_len=10,
    occurrences_are_many=False,
    use_exponential_occurrences=True,
    adds_list=(1, 2, 5),
):
    """

    :param add_list_len: =10
    :param occurrences_are_many: =False
    :param use_exponential_occurrences: =False
    :param adds_list: =(1, 2, 5)
    :return:
    """
    style_generator = get_plot_style_generator()
    if occurrences_are_many:
        occurrences = 10
    else:
        occurrences = 1
    list_for_vary_start_dict = get_generator(
        "list_length", 0, add_list_len, event_occurrences=occurrences
    )
    tuple_list_for_time_trial = next(list_for_vary_start_dict)

    for add_variable in adds_list:
        title = "vary size of start dict. number of adds = {}\n".format(add_variable)
        title += "input occurrences = {}.  input list length = {}".format(occurrences, add_list_len)
        results = time_trial_vary_start_dict(
            tuple_list_for_time_trial,
            input_dict_start_size=1000,
            input_dict_downward_step=10,
            number_of_adds=add_variable,
            use_exponential_occurrences=use_exponential_occurrences,
        )
        do_base_line = False
        if add_variable == adds_list[-1]:
            do_base_line = True
        plot_trial_with_ratio(
            *results,
            figure=1,
            title=title,
            label="add: {}".format(add_variable),
            style=next(style_generator),
            base_line=do_base_line,
        )


def do_trials_vary_event_occurrences(
    add_list_len=10, start_dict_size=1, adds_list=(1, 2, 5), exponential_growth=True
):
    """

    :param add_list_len: =10
    :param start_dict_size: =1
    :param adds_list: =(1, 2, 5)
    :param exponential_growth: =True
    :return:
    """
    style_generator = get_plot_style_generator()
    for add_variable in adds_list:
        if exponential_growth:
            increment = 0.2
            time_trial_variable = "event_occurrences"
        else:
            increment = 1
            time_trial_variable = "event_occurrences_linear"
        event_occurrences_generator = get_generator(
            "event_occurrences",
            0,
            add_list_len,
            growth_increment=increment,
            exponential_increase=exponential_growth,
        )
        results = time_trial(
            event_occurrences_generator,
            time_trial_variable,
            adds_per_trial=add_variable,
            input_dict_size=start_dict_size,
            number_of_data_pts=100,
        )
        title = "increasing event occurrences.\n"
        title += "starting dict size={}. input list length = {}".format(
            start_dict_size, add_list_len
        )
        do_base_line = False
        if add_variable == adds_list[-1]:
            do_base_line = True
        plot_trial_with_ratio(
            *results,
            figure=1,
            title=title,
            label="add: {}".format(add_variable),
            style=next(style_generator),
            base_line=do_base_line,
        )


def do_trials_vary_list_length(start_dict_size=1, occurrences_are_many=False, adds_list=(1, 2, 5)):
    """

    :param start_dict_size: =1
    :param occurrences_are_many: =False
    :param adds_list: =(1, 2, 4)
    :return:
    """
    style_generator = get_plot_style_generator()
    if occurrences_are_many:
        occurrences = 10
    else:
        occurrences = 1
    for add_variable in adds_list:
        list_length_generator = get_generator(
            "list_length", 0, 2, event_occurrences=occurrences, len_increase_step=1
        )
        results = time_trial(
            list_length_generator,
            "list_length",
            adds_per_trial=add_variable,
            input_dict_size=start_dict_size,
            number_of_data_pts=100,
        )
        title = "increasing list length.\n"
        title += "starting dict size={}. input list occurrences = {}".format(
            start_dict_size, occurrences
        )
        do_base_line = False
        if add_variable == adds_list[-1]:
            do_base_line = True
        plot_trial_with_ratio(
            *results,
            figure=1,
            title=title,
            label="add: {}".format(add_variable),
            style=next(style_generator),
            base_line=do_base_line,
        )


def do_trials_vary_gaps_in_list(
    add_list_len=100,
    start_dict_size=1,
    occurrences_are_many=False,
    randomize_gaps=True,
    adds_list=(1, 2, 5),
):
    """

    :param add_list_len: =100
    :param start_dict_size: =1
    :param occurrences_are_many: =False
    :param randomize_gaps: =True
    :param adds_list: =(1, 2, 5)
    :return:
    """
    style_generator = get_plot_style_generator()
    if occurrences_are_many:
        occurrences = 10
    else:
        occurrences = 1
    gaps_per_iteration = max(1, add_list_len // 100)
    for add_variable in adds_list:
        increasing_gaps_generator = get_generator(
            "increasing_gaps",
            0,
            add_list_len,
            event_occurrences=occurrences,
            gaps_per_iteration=gaps_per_iteration,
            randomize=randomize_gaps,
        )
        results = time_trial(
            increasing_gaps_generator,
            "increasing_gaps",
            adds_per_trial=add_variable,
            input_dict_size=start_dict_size,
            number_of_data_pts=100,
        )

        title = "making many gaps in list.\n"
        title += "starting dict size={}. input list length: {}, occurrences: {}".format(
            start_dict_size, add_list_len, occurrences
        )
        do_base_line = False
        if add_variable == adds_list[-1]:
            do_base_line = True
        plot_trial_with_ratio(
            *results,
            figure=1,
            title=title,
            label="add: {}".format(add_variable),
            style=next(style_generator),
            base_line=do_base_line,
        )


def graphing_ui():
    """a UI to demonstrate add speeds"""
    print(WELCOME_TXT)

    """
    'list_length', 'event_occurrences', 'increasing_gaps', 'dict_size'
    """
    plt_figure = 1
    while True:
        plt.figure(plt_figure)
        plt_figure += 1
        plt.ion()
        variable_choice = get_answer(
            'enter "1" for varying input events\' length\n'
            + 'enter "2" for varying input events\' # of occurrences\n'
            + 'enter "3" for varying input events\' gaps in values\n'
            + 'enter "4" for varying the size of the start dictionary',
            1,
            4,
        )

        variable_dict = {
            1: "list_length",
            2: "event_occurrences",
            3: "increasing_gaps",
            4: "dict_size",
        }
        action_dict = {
            1: do_trials_vary_list_length,
            2: do_trials_vary_event_occurrences,
            3: do_trials_vary_gaps_in_list,
            4: do_trials_vary_start_dict,
        }
        variable = variable_dict[variable_choice]
        action = action_dict[variable_choice]
        print("chose {}".format(variable))
        input_variables = get_kwargs(variable)
        action(**input_variables)

        plt.pause(0.1)


def get_kwargs(request):
    default_adds_list = [1, 2, 3, 4, 5]

    keys = ["start_dict_size", "add_list_len", "occurrences_are_many", "exponential_growth"]
    questions = [
        "what size for starting dictionary?",
        "how large a list to add?",
        "should the list have many occurrences? 1=True, 0=False",
        "should the occurrences increase exponentially? 1=True, 0=False",
    ]
    min_max = [(1, 2000), (2, 500), (0, 1), (0, 1), (0, 1)]
    if request == "dict_size":
        min_max[1] = (2, 100)

    request_and_indices = {
        "list_length": (0, 2),
        "event_occurrences": (0, 1, 3),
        "increasing_gaps": (0, 1, 2),
        "dict_size": (1, 2),
    }
    output_kwargs = {}
    for index in request_and_indices[request]:
        output_kwargs[keys[index]] = get_answer(questions[index], *min_max[index])
        if min_max[index] == (0, 1):
            output_kwargs[keys[index]] = bool(output_kwargs[keys[index]])
    if request != "list_length":
        adds_list = get_adds_list(output_kwargs)
        output_kwargs["adds_list"] = adds_list
    else:
        output_kwargs["adds_list"] = default_adds_list
    return output_kwargs


def get_adds_list(dictionary):
    start_size = dictionary.get("start_dict_size", 1000)
    add_list_size = dictionary["add_list_len"]
    complete_add_list = [1, 2, 3, 4, 5, 10, 50, 100, 500]
    max_adds = 5
    if start_size <= 100:
        max_list_size_for_add = [(3, 500), (6, 100), (9, 50), (20, 10), (10000, 5)]
        for pair in max_list_size_for_add:
            if add_list_size <= pair[0]:
                max_adds = pair[1]
                break

    else:
        max_list_size_for_add = [(4, 50), (9, 10), (10000, 5)]
        for pair in max_list_size_for_add:
            if add_list_size <= pair[0]:
                max_adds = pair[1]
                break
    adds_list_end = complete_add_list.index(max_adds)
    return complete_add_list[: adds_list_end + 1]


def get_tuple_list(size, many_occurrences=False, step=1):
    if many_occurrences:
        occur = 10
    else:
        occur = 1
    return [(event, occur) for event in range(0, size, step)]


def get_indexed_advantage_ratio(start_dict_size, adds, tuple_list_sizes, many_occurrences):
    events_tuples = get_tuple_list(tuple_list_sizes, many_occurrences)
    input_dict = get_input_dict(start_dict_size, True)

    control_time, indexed_values_time = get_control_and_indexed_values_times(
        adds, events_tuples, input_dict
    )

    return control_time / indexed_values_time


def get_data_list(many_occurrences):
    titles = ("ADDS", "DICT SIZE", "LIST SIZE", "OCCUR MANY", "RESULT")
    adds = [1, 2, 3, 4, 5, 10, 20, 50, 100, 500, 1000, 2000]
    start_dict_sizes = [1, 10, 50, 100, 200, 500, 1000, 2000, 5000]
    tuple_list_sizes = [2, 3, 4, 6, 8, 10, 20, 50, 100]
    all_data = [titles]
    for add_time in adds:
        print(add_time)
        for start_size in start_dict_sizes:
            for tuple_size in tuple_list_sizes:
                if add_time * tuple_size <= 4000:
                    datum = get_indexed_advantage_ratio(
                        start_size, add_time, tuple_size, many_occurrences
                    )
                    data_line = (
                        float(add_time),
                        float(start_size),
                        float(tuple_size),
                        float(many_occurrences),
                        datum,
                    )
                    all_data.append(data_line)

    return all_data


def data_grouper(data_list, index_priority=(0, 1, 2, 3, 4)):
    new_list = []
    for data in data_list:
        new_data = []
        for index in index_priority:
            new_data.append(data[index])
        new_list.append(tuple(new_data))
    new_labels = new_list[0]
    the_rest = sorted(new_list[1:])
    return [new_labels] + the_rest


def get_result_str(data_list):
    labels = data_list[0]
    result_index = labels.index("RESULT")
    bool_index = labels.index("OCCUR MANY")
    star_the_result = 1.0

    number_of_labels = len(labels)
    middle_just = "10"
    template = "\n" + ("{:^" + middle_just + "}|") * number_of_labels
    template.rstrip("|")

    table_descriptor = template.format(*labels)
    line_len = len(table_descriptor)
    table_descriptor = add_sep_line(table_descriptor, line_len, "*")
    table_descriptor = "\n" + line_len * "=" + table_descriptor

    first_element = -1
    second_element = -1

    output_str = ""
    for line in data_list[1:]:
        new_first_element = int(line[0])
        new_second_element = int(line[1])
        if new_first_element != first_element:
            output_str += table_descriptor
        if new_second_element != second_element:
            output_str = add_sep_line(output_str, line_len, "-")
        first_element = new_first_element
        second_element = new_second_element
        line_strings = []
        for index, element in enumerate(line):
            if index == result_index:
                to_add = "{:.3f}".format(element)
            elif index == bool_index:
                to_add = str(bool(element))
            else:
                to_add = str(int(element))
            line_strings.append(to_add)
        output_str += template.format(*line_strings)

        result = float(line[result_index])
        if result > star_the_result:
            output_str += "  ***  "

    return output_str


def add_sep_line(input_str, line_length, separator):
    return input_str + "\n" + line_length * separator


def save_data_pts(data_flat, data_bumpy):
    flat_save = np.array(data_flat)
    np.save("save_flat_data", flat_save)

    bumpy_save = np.array(data_bumpy)
    np.save("save_bumpy_data", bumpy_save)


def load_data_pts(full_file_name):
    np_array = np.load(full_file_name)
    output = []
    for data_tuple in np_array.tolist():
        try:
            output.append(tuple([float(number) for number in data_tuple]))
        except ValueError:
            output.append(tuple(data_tuple))
    return output


def get_saved_data():
    data_points_flat = load_data_pts("save_flat_data.npy")
    data_points_bumpy = load_data_pts("save_bumpy_data.npy")
    return data_points_flat, data_points_bumpy


def data_points_ui():
    try:
        get_new_data = input_py_2_and_3(
            'generate new data pts (will take some minutes)? type "y" for yes.\n>>> '
        )
        if get_new_data == "y":
            raise IOError
        data_points_flat, data_points_bumpy = get_saved_data()
    except IOError:
        print("generating data points.  this will take a few minutes")
        data_points_flat = get_data_list(False)
        data_points_bumpy = get_data_list(True)
        save_data_pts(data_points_flat, data_points_bumpy)
    labels_dict = dict(enumerate(data_points_flat[0]))
    intro = """
    here are the values whose order you may change
    {}
    at the prompt put in a new 5-digit string showing how you want the data ordered
    so "01234" will order the data by ('ADDS', 'DICT SIZE', 'LIST SIZE', 'OCCUR MANY', 'RESULT')
       "21034" will order the data by ('LIST SIZE', 'DICT SIZE', 'ADDS', 'OCCUR MANY', 'RESULT')

    when prompted, enter the base name for the file.
    "test" would create 3 files.
    "test_flat.txt", "test_many.txt", "test_combined.txt".  they will be text files showing the data
    grouped accordingly.  flat show adding events that occurred once and many shows events that occurred 10 times.

    the result column shows how many times faster the index_values method is and so any time
    indexed values is faster, it is starred.

    """
    print(intro.format(str(labels_dict).replace(",", "\n")))
    while True:
        print(str(labels_dict).replace(",", "\n"))
        new_order = input_py_2_and_3('new order or "q" quits >>> ')
        if new_order == "q":
            break
        change_list = []
        for digit in new_order:
            change_list.append(int(digit))
        result_to_print_flat = data_grouper(data_points_flat, change_list)
        result_to_print_bumpy = data_grouper(data_points_bumpy, change_list)
        flat = get_result_str(result_to_print_flat)
        many = get_result_str(result_to_print_bumpy)
        name = input_py_2_and_3("file base name >>> ")
        with open(name + "_flat.txt", "w") as file:
            file.write(flat)
        with open(name + "_many.txt", "w") as file:
            file.write(many)
        with open(name + "_combined.txt", "w") as file:
            file.write(get_side_by_side_data(flat, many))


def get_side_by_side_data(left_answer, right_answer):
    left_lines = left_answer.split("\n")
    right_lines = right_answer.split("\n")

    left_just_line_len = 64

    joined_lines = []
    for index, line in enumerate(left_lines):
        new_line = "{:<{}}{}".format(line, left_just_line_len, right_lines[index])
        joined_lines.append(new_line)

    joined_answer = "\n".join(joined_lines)

    return joined_answer


if __name__ == "__main__":
    graphing_ui()

    # data_points_ui()
