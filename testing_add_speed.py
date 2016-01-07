'''a module solely for finding how add_a_list and add_tuple_list compare.
it's effectively the empirical proof for how LongIntTable.add() chooses
the fastest method with it's _fastest() function. run random_trial or 
n_points_trial for large lists(or be very patient)'''
import longintmath as lim
import time
import pylab
import random   


def random_list(num_vals):
    '''num_vals is how many elements in your list.  generates list start at
    -10 to 10 with a step of 1 - 5'''
    start = random.randrange(-10, 11)
    step = random.randrange(1, 6)
    return range(start, step*num_vals + start, step)

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

def add_dices(table, num_times, lst):
    '''repeat the add_ function num_times times.'''
    for _ in range(num_times):
        table._add_a_list(lst)

def add_weighted_dice(table, num_times, lst):
    '''num_times is an int.  repeat add_tuple_list that many times.'''
    for _ in range(num_times):
        table._add_tuple_list(lst)        

def one_time_trial(t_list, num_adds):
    '''add t_list to identity LongIntTable num_adds times, using _add_a_list and
    _add_tuple_list.  returns the ratio of sum_of_freq/num_of_values, and the
    time for each funtion to do the adding.'''
    t_list.sort()
    lst = []
    for val, freq in t_list:
        lst = lst + [val] * freq
    
    freq_val_ratio = len(lst)/float(len(t_list))

    a = lim.LongIntTable({0:1})    
    start_a = time.clock()
    add_dices(a, num_adds, lst)
    list_time = time.clock() - start_a
    
    b = lim.LongIntTable({0:1})
    start_b = time.clock()
    add_weighted_dice(b, num_adds, t_list)
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
    pylab.figure(figure)
    pylab.plot(ratios, tuples, 'bo-', label='tuple add')
    pylab.plot(ratios, lists, 'r*-', label='list add')
    pylab.ylabel('time')
    pylab.xlabel('num_freq over num_vals')
    pylab.title(title)
    pylab.legend()
    tup_slope, tup_const = pylab.polyfit(ratios, tuples, 1)
    lst_slope, lst_const = pylab.polyfit(ratios, lists, 1)
    pylab.plot(ratios, map(lambda x: tup_slope * x + tup_const, ratios), 'c-')
    pylab.plot(ratios, map(lambda x: lst_slope * x + lst_const, ratios), 'c-')
    
    intersection = (tup_const - lst_const) / (lst_slope - tup_slope)
    return intersection
def random_generator(num_vals):
    '''outputs a random generator of len(lst) = num_vals'''
    start_list = random_list(num_vals)
    gen_str = random.choice(['one_point', 'random_point', 'n_points'])
    if gen_str == 'one_point':
        loc = random.choice(['start', 'mid', 'end'])
        generator = gen_one_point(start_list, loc)
        out_str = '%s\n%s at %s' % (start_list, gen_str, loc)
    elif gen_str == 'random_point':
        generator = gen_random_point(start_list)
        out_str = '%s\n%s' % (start_list, gen_str)
    else:
        num_points = random.randrange(1, 1 + len(start_list)/2)
        generator = gen_n_points(start_list, num_points)
        out_str = '%s\n%s n=%s' % (start_list, gen_str, num_points)
    return generator, out_str
     
def random_trial(num_vals, adds_per_trial):
    '''make a random generator of a random list with num_vals elements. add that
    list num_adds times per trial and plot results and return intesection'''
    generator, title = random_generator(num_vals)
    ratio, tuples, lists = time_trial(generator, adds_per_trial)
    return plot_trial(ratio, tuples, lists, title)

def n_points_trial(num_vals, adds_per_trial, n_points):
    '''make an n_points generator with a random list of num_vals elements. run
    the trial and plot and return intersection.'''
    lst = random_list(num_vals)
    generator = gen_n_points(lst, n_points)
    title = '%s\nn_points n=%s' % (lst, n_points)
    ratio, tuples, lists = time_trial(generator, adds_per_trial)
    return plot_trial(ratio, tuples, lists, title)
    
