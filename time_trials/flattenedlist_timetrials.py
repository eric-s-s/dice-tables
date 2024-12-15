"""
THIS MODULE REQUIRES numpy AND matplotlib TO RUN CORRECTLY

this hastily cobbled together module demonstrates the conditions each of the following methods is fastest
AdditiveEvents.combine_by_dictionary and AdditiveEvents.combine_by_flattened_list
the main determining factor seems to the ratio of (total event occurrences) to (total number of events).
the quick_and_dirty_ui is set up to demonstrate this.

THIS MODULE REQUIRES numpy AND matplotlib TO RUN CORRECTLY
"""

from __future__ import print_function

import time
import random
from os import getcwd
import matplotlib.pyplot as plt
import numpy as np
from dicetables.additiveevents import AdditiveEvents


def gen_one_point(val_list, loc="mid"):
    """a generator for a list of tuples. starts list of tuples (val, 1) for each
    val in list. add one to loc = "start", "mid" or "end" """
    lst = [(val, 1) for val in val_list]
    if loc == "start":
        index = 0
    elif loc == "end":
        index = len(lst) - 1
    else:
        index = len(val_list) // 2
    index_val = lst[index][0]
    while True:
        yield lst
        current_freq = lst[index][1]
        lst[index] = (index_val, current_freq + 1)


def gen_n_points(val_list, num_points):
    """input is a list and the number of points getting added.  start with tuple
    list of (val, 1) for val in list.  adds one to the frequency of number of
    pts."""
    lst = [(val, 1) for val in val_list]
    factor = len(val_list) / float(num_points + 1)
    indexes = [int(factor * multiplier) for multiplier in range(1, num_points + 1)]
    while True:
        yield lst
        for index in indexes:
            val, freq = lst[index]
            lst[index] = (val, freq + 1)


def gen_random_point(val_list):
    """input is a list of vals.  generates list of (val, 1). then each iteration
    add one to a random freq"""
    lst = [(val, 1) for val in val_list]
    length = len(lst)
    while True:
        yield lst
        index = random.randrange(0, length)
        val, freq = lst[index]
        lst[index] = (val, freq + 1)


def one_time_trial(events, num_adds, start_dict_size=1):
    """add t_list to identity AdditiveEvents num_adds times, using combine_once_with_flattened_list and
    combine_once_with_dictionary.  returns the ratio of sum_of_freq/num_of_values, and the
    time for each function to do the adding."""
    events_total_occurrences = sum([pair[1] for pair in events])

    occurrences_to_events_ratio = events_total_occurrences / float(len(events))

    start_dict = dict([(event, 1 + event % 100) for event in range(start_dict_size)])
    to_combine = AdditiveEvents(dict(events))

    id_table_a = AdditiveEvents(start_dict)
    start_a = time.clock()
    id_table_a.combine_by_flattened_list(to_combine, num_adds)
    flattened_list_time = time.clock() - start_a

    id_table_b = AdditiveEvents(start_dict)
    start_b = time.clock()
    id_table_b.combine_by_dictionary(to_combine, num_adds)
    tuple_time = time.clock() - start_b

    return occurrences_to_events_ratio, tuple_time, flattened_list_time


def time_trial(generator, adds_per_trial, start_dict_size=1):
    """run one time trial, then run again while advancing the generator. test
    runs about 1.8 times length from start to equal times. outputs x-axis and
    two y-axes."""
    ratios = []
    tuple_times = []
    list_times = []
    count = 5
    print("please wait for the count-up/down to reach zero")
    while count > 0:
        ratio, tup_time, lst_time = one_time_trial(
            next(generator), adds_per_trial, start_dict_size=start_dict_size
        )
        print(count)
        if tup_time > lst_time:
            count += 1
        else:
            count -= 1.2
        ratios.append(ratio)
        tuple_times.append(tup_time)
        list_times.append(lst_time)
    return ratios, tuple_times, list_times


def plot_trial(ratios, tuples, lists, title="none", figure=1):
    """plot x-axis = ratios.  y-axis = tuples and y-axis = lists. fit curves to
    ax + b and return the intersection of two curves"""
    plt.ion()
    plt.figure(figure)
    plt.plot(ratios, tuples, "bo-", label="tuple add")
    plt.plot(ratios, lists, "r*-", label="list add")
    plt.ylabel("time")
    plt.xlabel("event occurrences over number of events")

    plt.legend()
    intersection, tup_fit, lst_fit = polyfit_and_intersection(ratios, tuples, lists)
    title += "\nintersection = %s" % intersection
    plt.title(title)
    plt.plot(ratios, tup_fit, "c-")
    plt.plot(ratios, lst_fit, "c-")
    plt.pause(0.01)
    return intersection


def polyfit_and_intersection(ratios, tuples, lists):
    """fits tuples and list linearly to ratios. returns the intersection of two
    fits and two lists of y values to plot with ratios"""
    tup_slope, tup_const = np.polyfit(ratios, tuples, 1)
    lst_slope, lst_const = np.polyfit(ratios, lists, 1)
    intersection = (tup_const - lst_const) / (lst_slope - tup_slope)
    tuple_polyfit = [(tup_slope * x + tup_const) for x in ratios]
    lst_polyfit = [(lst_slope * x + lst_const) for x in ratios]
    return intersection, tuple_polyfit, lst_polyfit


def random_list(num_vals):
    """num_vals is how many elements in your list.  generates list start at
    -10 to 10 with a step of 1 - 5"""
    start = random.randrange(-10, 11)
    step = random.randrange(1, 6)
    return range(start, step * num_vals + start, step)


def random_generator(num_vals, n_points_only=False):
    """outputs a random generator of len(lst) = num_vals"""
    start_list = random_list(num_vals)
    if n_points_only:
        gen_str = "n_points"
    else:
        gen_str = random.choice(["one_point", "random_point", "n_points"])
    if gen_str == "one_point":
        loc = random.choice(["start", "mid", "end"])
        generator = gen_one_point(start_list, loc)
        out_str = "%s\n%s at %s" % (start_list, gen_str, loc)
    elif gen_str == "random_point":
        generator = gen_random_point(start_list)
        out_str = "%s\n%s" % (start_list, gen_str)
    else:
        min_pts = len(start_list) // 10
        max_pts = len(start_list) // 5
        if min_pts < 1:
            min_pts = 1
        if max_pts < 2:
            max_pts = 2
        num_points = random.randrange(min_pts, max_pts + 1)
        generator = gen_n_points(start_list, num_points)
        out_str = "%s\n%s n=%s" % (start_list, gen_str, num_points)
    return generator, out_str


def random_trial(num_vals, adds_per_trial, figure=1, n_points_only=False, start_dict_size=1):
    """make a random generator of a random list with num_vals elements. add that
    list num_adds times per trial and plot results and return intesection"""
    generator, title = random_generator(num_vals, n_points_only)
    title += "  adds={}  vals={}  start dictionary size={}".format(
        adds_per_trial, num_vals, start_dict_size
    )
    ratio, tuples, lists = time_trial(generator, adds_per_trial, start_dict_size)
    return plot_trial(ratio, tuples, lists, title, figure)


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
        try:
            answer = raw_input(question + ">>>")
        except NameError:
            answer = input(question + ">>>")
        if answer == "q":
            raise SystemExit
        try:
            output = int(answer)
            return output
        except ValueError:
            print('must be int OR "q" to quit')
            continue


def quick_and_dirty_ui():
    """a UI to demonstrate add speeds"""
    print(get_welcome())
    this_will_take_forever = 2500
    needs_many_points = 50
    max_vals = 300
    min_vals = 3
    min_start_size = 1
    max_start_size = 1000
    figure = 0

    while True:
        figure += 1
        plt.ion()
        num_vals_question = (
            "how many values in your list?" + "\nplease input int between %s and %s\n"
        ) % (min_vals, max_vals)
        num_vals = get_int(num_vals_question)
        if num_vals > max_vals:
            print("num_vals too big. now = %s" % max_vals)
            num_vals = max_vals
        if num_vals < min_vals:
            print("num_vals too small. now = %s" % min_vals)
            num_vals = min_vals

        max_adds = this_will_take_forever // num_vals
        min_adds = 1
        num_adds_question = (
            "please input the number of adds per trial\n"
            + "an int between %s and %s\n" % (min_adds, max_adds)
        )
        num_adds = get_int(num_adds_question)
        if num_adds < min_adds:
            print("num_adds too small. now = %s" % min_adds)
            num_adds = min_adds
        if num_adds > max_adds:
            print("num_adds too big. now = %s" % max_adds)
            num_adds = max_adds

        start_dict_question = (
            "please input the size of the starting dictionary\n"
            + "an int between %s and %s\n" % (min_start_size, max_start_size)
        )
        start_dict_size = get_int(start_dict_question)
        if num_adds < min_start_size:
            print("num_adds too small. now = %s" % min_start_size)
            start_dict_size = min_start_size
        if num_adds > max_adds:
            print("num_adds too big. now = %s" % max_start_size)
            start_dict_size = max_start_size

        n_points_only = num_vals >= needs_many_points

        intersection = random_trial(num_vals, num_adds, figure, n_points_only, start_dict_size)
        print("the graphs intersect at %s" % intersection)
        plt.pause(0.1)


def tst_num_adds(num_vals, start_add, stop_add):
    """shows how the intersection varies with different numbers of adds"""
    start_list = random_list(num_vals)
    num_points = num_vals // 5
    if num_points == 0:
        num_points = 1
    out_lst = []
    x_axis = range(start_add, stop_add + 1)
    for adds in x_axis:
        print("countdown %s" % (x_axis[-1] - adds))
        generator = gen_n_points(start_list, num_points)
        ratios, tuples, lists = time_trial(generator, adds)
        ans = polyfit_and_intersection(ratios, tuples, lists)
        out_lst.append(ans[0])
    plt.figure(1)
    plt.plot(x_axis, out_lst, "bo-", label=str(start_list))
    plt.xlabel("%s to %s" % (start_add, stop_add))
    plt.ylabel("intersections")
    return out_lst


def tst_num_vals(star_vals, stop_vals, num_adds):
    """shows how the intersection varies with different number of values in a
    list"""
    x_axis = range(star_vals, stop_vals + 1)
    out_lst = []
    start_list = []
    for num_vals in x_axis:
        print("countdown %s" % (x_axis[-1] - num_vals))
        num_points = num_vals // 5
        start_list = random_list(num_vals)
        if num_points == 0:
            num_points = 1
        generator = gen_n_points(start_list, num_points)
        ratios, tuples, lists = time_trial(generator, num_adds)
        ans = polyfit_and_intersection(ratios, tuples, lists)
        out_lst.append(ans[0])
    plt.figure(0)
    plt.plot(x_axis, out_lst, "bo-", label=str(start_list))
    plt.xlabel("%s to %s" % (star_vals, stop_vals))
    plt.ylabel("intersections")
    return out_lst


if __name__ == "__main__":
    quick_and_dirty_ui()
