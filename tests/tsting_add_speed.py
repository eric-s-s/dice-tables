'''a module solely for finding how add_a_list and add_tuple_list compare.
it's effectively the empirical proof for how LongIntTable.add() chooses
the fastest method with it's _fastest() function.'''
import dicetables.longintmath as lim
import time
import matplotlib.pyplot as plt
import numpy as np
import random

def gen_one_point(val_list, loc='mid'):
    '''a generator for a list of tuples. starts list of tuples (val, 1) for each
    val in list. add one to loc = "start", "mid" or "end"'''
    lst = [(val, 1) for val in val_list]
    if loc == 'start':
        index = 0
    elif loc == 'end':
        index = len(lst) - 1
    else:
        index = len(val_list) // 2
    index_val = lst[index][0]
    while True:
        yield lst
        current_freq = lst[index][1]
        lst[index] = (index_val, current_freq + 1)

def gen_n_points(val_list, num_points):
    '''input is a list and the number of points getting added.  start with tuple
    list of (val, 1) for val in list.  adds one to the frequency of number of
    pts.'''
    lst = [(val, 1) for val in val_list]
    factor = len(val_list) / float(num_points + 1)
    indexes = [int(factor * multiplier) for multiplier in range(1, num_points + 1)]
    while True:
        yield lst
        for index in indexes:
            val, freq = lst[index]
            lst[index] = (val, freq + 1)

def gen_random_point(val_list):
    '''input is a list of vals.  generates list of (val, 1). then each iteration
    add one to a random freq'''
    lst = [(val, 1) for val in val_list]
    length = len(lst)
    while True:
        yield lst
        index = random.randrange(0, length)
        val, freq = lst[index]
        lst[index] = (val, freq + 1)

def add_int_lists(table, num_times, lst):
    '''repeat the add_a_list function num_times times.'''
    for _ in range(num_times):
        table._add_a_list(lst)

def add_tuple_lists(table, num_times, lst):
    '''num_times is an int.  repeat add_tuple_list that many times.'''
    for _ in range(num_times):
        table._add_tuple_list(lst)

def one_time_trial(tuple_list, num_adds):
    '''add t_list to identity LongIntTable num_adds times, using _add_a_list and
    _add_tuple_list.  returns the ratio of sum_of_freq/num_of_values, and the
    time for each funtion to do the adding.'''
    tuple_list.sort()
    lst = []
    for val, freq in tuple_list:
        lst = lst + [val] * freq

    freq_val_ratio = len(lst)/float(len(tuple_list))

    id_table_a = lim.LongIntTable({0:1})
    start_a = time.clock()
    add_int_lists(id_table_a, num_adds, lst)
    list_time = time.clock() - start_a

    id_table_b = lim.LongIntTable({0:1})
    start_b = time.clock()
    add_tuple_lists(id_table_b, num_adds, tuple_list)
    tuple_time = time.clock() - start_b

    return freq_val_ratio, tuple_time, list_time

def time_trial(generator, adds_per_trial):
    '''run one time trial, then run again while advancing the generator. test
    runs about 1.8 times length from start to equal times. outputs x-axis and
    two y-axes.'''
    ratios = []
    tuple_times = []
    list_times = []
    count = 1
    print 'please wait for the count-up/down to reach zero'
    while count > 0:
        ratio, tup_time, lst_time = one_time_trial(generator.next(),
                                                   adds_per_trial)
        print count
        if tup_time > lst_time:
            count += 1
        else:
            count -= 1.2
        ratios.append(ratio)
        tuple_times.append(tup_time)
        list_times.append(lst_time)
    return ratios, tuple_times, list_times

def plot_trial(ratios, tuples, lists, title='none', figure=1):
    '''plot x-axis = ratios.  y-axis = tuples and y-axis = lists. fit curves to
    ax + b and return the intesection of two curves'''
    plt.figure(figure)
    plt.plot(ratios, tuples, 'bo-', label='tuple add')
    plt.plot(ratios, lists, 'r*-', label='list add')
    plt.ylabel('time')
    plt.xlabel('num_freq over num_vals')

    plt.legend()
    intersection, tup_fit, lst_fit = polyfit_and_intersection(ratios,
                                                              tuples, lists)
    title = title + '\nintersection = %s' % (intersection)
    plt.title(title)
    plt.plot(ratios, tup_fit, 'c-')
    plt.plot(ratios, lst_fit, 'c-')
    return intersection

def polyfit_and_intersection(ratios, tuples, lists):
    '''fits tuples and list linearly to ratios. returns the intersection of two
    fits and two lists of y values to plot with ratios'''
    tup_slope, tup_const = np.polyfit(ratios, tuples, 1)
    lst_slope, lst_const = np.polyfit(ratios, lists, 1)
    intersection = (tup_const - lst_const) / (lst_slope - tup_slope)
    tuple_polyfit = [(tup_slope * x + tup_const) for x in ratios]
    lst_polyfit = [(lst_slope * x + lst_const) for x in ratios]
    return intersection, tuple_polyfit, lst_polyfit

def random_list(num_vals):
    '''num_vals is how many elements in your list.  generates list start at
    -10 to 10 with a step of 1 - 5'''
    start = random.randrange(-10, 11)
    step = random.randrange(1, 6)
    return range(start, step*num_vals + start, step)

def random_generator(num_vals, n_points_only=False):
    '''outputs a random generator of len(lst) = num_vals'''
    start_list = random_list(num_vals)
    if n_points_only:
        gen_str = 'n_points'
    else:
        gen_str = random.choice(['one_point', 'random_point', 'n_points'])
    if gen_str == 'one_point':
        loc = random.choice(['start', 'mid', 'end'])
        generator = gen_one_point(start_list, loc)
        out_str = '%s\n%s at %s' % (start_list, gen_str, loc)
    elif gen_str == 'random_point':
        generator = gen_random_point(start_list)
        out_str = '%s\n%s' % (start_list, gen_str)
    else:
        min_pts = len(start_list) // 10
        max_pts = len(start_list) // 5
        if min_pts < 1:
            min_pts = 1
        if max_pts < 2:
            max_pts = 2
        num_points = random.randrange(min_pts, max_pts + 1)
        generator = gen_n_points(start_list, num_points)
        out_str = '%s\n%s n=%s' % (start_list, gen_str, num_points)
    return generator, out_str

def random_trial(num_vals, adds_per_trial, figure=1, n_points_only=False):
    '''make a random generator of a random list with num_vals elements. add that
    list num_adds times per trial and plot results and return intesection'''
    generator, title = random_generator(num_vals, n_points_only)
    title = title + '  adds=%s  vals=%s' % (adds_per_trial, num_vals)
    ratio, tuples, lists = time_trial(generator, adds_per_trial)
    return plot_trial(ratio, tuples, lists, title, figure)

from os import getcwd

def get_welcome():
    '''return welcom_message.txt'''
    try:
        welcome_file_name = getcwd() + '\\' + 'welcome_message.txt'
        welcome_file = open(welcome_file_name, 'r')
        welcome_message = welcome_file.read()
    except IOError:
        welcome_message = 'took a guess where "welcome_' \
                          'message.txt" was, and I was wrong.'
    return welcome_message
def get_int(question):
    '''makes sure user input is an int. quit if "q"'''
    while True:
        answer = raw_input(question + '>>>')
        if answer == 'q':
            raise SystemExit
        try:
            output = int(answer)
            return output
        except ValueError:
            print 'must be int OR "q" to quit'
            continue

def quick_and_dirty_ui():
    '''a UI to demonstrate add speeds'''
    print get_welcome()
    this_will_take_forever = 2500
    too_short_for_accuracy = 1200
    needs_many_points = 50
    max_vals = 300
    min_vals = 3
    figure = 0

    while True:
        figure += 1
        plt.ion()
        num_vals_question = (('how many values in your list?'+
                              '\nplease input int between %s and %s\n') %
                             (min_vals, max_vals))
        num_vals = get_int(num_vals_question)
        if num_vals > max_vals:
            print 'num_vals too big. now = %s' % (max_vals)
            num_vals = max_vals
        if num_vals < min_vals:
            print 'num_vals too small. now = %s' % (min_vals)
            num_vals = min_vals

        max_adds = this_will_take_forever // num_vals
        min_adds = 1 + too_short_for_accuracy // num_vals
        num_adds_question = ('please input the number of adds per trial\n' +
                             'an int between %s and %s\n' % (min_adds, max_adds))
        num_adds = get_int(num_adds_question)
        if num_adds < min_adds:
            print 'num_adds too small. now = %s' % (min_adds)
            num_adds = min_adds
        if num_adds > max_adds:
            print 'num_adds too big. now = %s' % (max_adds)
            num_adds = max_adds

        if num_vals >= needs_many_points:
            n_points_only = True
        else:
            n_points_only = False
        intersection = random_trial(num_vals, num_adds, figure, n_points_only)
        print 'the graphs intersect at %s' % (intersection)
        plt.pause(0.1)

def tst_num_adds(num_vals, start_add, stop_add):
    '''shows how the intersecion varies with different numbers of adds'''
    start_list = random_list(num_vals)
    num_points = num_vals // 5
    if num_points == 0:
        num_points = 1
    out_lst = []
    x_axis = range(start_add, stop_add + 1)
    for adds in x_axis:
        print 'countdown %s' % (x_axis[-1] - adds)
        generator = gen_n_points(start_list, num_points)
        ratios, tuples, lists = time_trial(generator, adds)
        ans = polyfit_and_intersection(ratios, tuples, lists)
        out_lst.append(ans[0])
    plt.figure(1)
    plt.plot(x_axis, out_lst, 'bo-', label=str(start_list))
    plt.xlabel('%s to %s' % (start_add, stop_add))
    plt.ylabel('intersections')
    return out_lst

def tst_num_vals(star_vals, stop_vals, num_adds):
    '''shows how the intesection varies with different number of values in a
    list'''
    x_axis = range(star_vals, stop_vals + 1)
    out_lst = []
    for num_vals in x_axis:
        print 'countdown %s' % (x_axis[-1] - num_vals)
        num_points = num_vals // 5
        start_list = random_list(num_vals)
        if num_points == 0:
            num_points = 1
        generator = gen_n_points(start_list, num_points)
        ratios, tuples, lists = time_trial(generator, num_adds)
        ans = polyfit_and_intersection(ratios, tuples, lists)
        out_lst.append(ans[0])
        plt.figure(2)
    plt.plot(x_axis, out_lst, 'bo-', label=str(start_list))
    plt.xlabel('%s to %s' % (star_vals, stop_vals))
    plt.ylabel('intersections')
    return out_lst

if __name__ == '__main__':
    quick_and_dirty_ui()
