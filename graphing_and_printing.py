'''printing and graphing functions for use with LongIntTable class.
main functions are - grapher(), truncate_grapher(), fancy_grapher()
print_table() and stats()'''


import pylab


#helper function. used everywhere to make numbers look purty.
def scinote(num):
    '''checks a positive int or float.  outputs a string of the number.
    float(string) will give you the number.
    if number lower than scinonote_cutoff, no change.
    if number already in scientific notation, just prints first 4 digits
    else prints first four digits in scientific notation.'''
    scinote_cutoff = 10**6
    if num < scinote_cutoff:
        return str(num)
    elif 'e' in str(num):
        left, right = str(num).split('e')
        return left[0:5]+'e'+right
    else:
        string = str(int(num))
        power = str(len(string)-1)
        digits = string[0]+'.'+string[1:4]
        return digits+'e+'+power

#helper function for truncate_grapher() and stats()
def list_to_string(lst):
    '''outputs a list of intergers as a nice string.
    [1,2,3,7,9,10] becomes "1-3, 7, 9-10"
    [1,1,2,2,3] becomes "1-3"'''
    lst.sort()
    start_index = 0
    tuple_list = []
    for index in range(len(lst)-1):
        if lst[index+1]-lst[index] > 1:
            tuple_list.append((lst[start_index], lst[index]))
            start_index = index+1
    tuple_list.append((lst[start_index], lst[-1]))
    out_list = []
    for pair in tuple_list:
        if pair[0] == pair[1]:
            out_list.append(str(pair[0]))
        else:
            out_list.append(str(pair[0])+'-'+str(pair[1]))
    return ', '.join(out_list)

#helper function. currently used in print_table(), grapher()
#and truncate_grapher()
def justify_right(value, max_value):
    '''takes a value, and the largest value from a LongIntTable.
    outputs a string of the roll with enough added spaces so that
    "roll:" and "max_roll:" will be the same number of characters.'''
    max_len = len(str(max_value))
    out_val = str(value)
    spaces = (max_len - len(out_val))*' '
    return spaces + out_val

#helper function that's really only useful for grapher and truncate_grapher
def graph_list(table):
    '''table is a LongIntTable. makes a list of tuples which
    [(value, x's representing value), ...]
    it's a helper function for grapher and truncate_grapher'''
    output_list = []

    max_frequency = table.frequency_highest()[1]
    max_value = table.values_max()
    max_graph_height = 80

    divisor = 1
    divstring = '1'
    #this sets the divisor so that max height of graph is MAX_GRAPH_HEIGHT x's
    if max_frequency > max_graph_height:
        divisor = table.divide(max_frequency, max_graph_height)
        divstring = scinote(divisor)

    for value, frequency in table.frequency_all():
        num_of_xs = int(round(table.divide(frequency, divisor)))
        output_list.append((value,
                            justify_right(value, max_value) +':'+num_of_xs*'x'))

    output_list.append((None, 'each x represents '+divstring+' occurences'))
    return output_list

def print_table(table):
    '''table is a LongIntTable. Prints all the values and their frequencies.'''
    max_value = table.values_max()
    for value, frequency in table.frequency_all():
        print justify_right(value, max_value) +':'+scinote(frequency)
    print table

def grapher(table):
    '''table is a LongIntTable. prints a graph of x's.'''
    for output in graph_list(table):
        print output[1]
    print table

def truncate_grapher(table):
    '''table is a LongIntTable. prints a graph of x's,
    but doesn't print zero-x rolls'''
    excluded = []
    for output in graph_list(table):
        if 'x' in output[1]:
            print output[1]
        else:
            excluded.append(output[0])
    if excluded != []:
        print 'not included:', list_to_string(excluded).replace(',', ' and')
    print table

def fancy_grapher(table, figure=1, style='bo'):
    '''table is a LongIntTable. makes a pylab plot of a table.
    You can set other figures and styles'''
    x_axis = []
    y_axis = []
    factor = 1

    pylab.figure(figure)
    pylab.ylabel('number of occurences')
    #A work-around for the limitations of pylab.
    #It can't handle really fucking big ints and can't use my workarounds
    if table.check_overflow():
        power = len(str(table.frequency_highest()[1])) - 5
        factor = 10**power
        pylab.ylabel('number of occurences times 10^'+str(power))

    for value, frequency in table.frequency_all():
        x_axis.append(value)
        y_axis.append(frequency/factor)

    pylab.xlabel('values')
    pylab.title('all the combinations for '+str(table))
    pylab.plot(x_axis, y_axis, style)
    pylab.draw()


def stats(table, values):
    '''table is a LongIntTable. values is a list. prints stats information
    for the values in the list.'''
    all_combos = table.total_frequency()
    lst_frequency = 0
    for value in values:
        lst_frequency += table.frequency(value)[1]

    if lst_frequency == 0:
        print 'no results'
        return None
    chance = table.divide(all_combos, lst_frequency, 4)
    pct = 100 * table.divide(lst_frequency, all_combos, 3)

    lst_frequency_str = scinote(lst_frequency)
    chance_str = scinote(chance)
    all_combos_str = scinote(all_combos)
    values_str = list_to_string(values)
    print
    print ('%s occurred %s times out of a total of %s possible combinations' %
           (values_str, lst_frequency_str, all_combos_str))
    print 'for %s,' % (table)
    print ('the chance of %s is 1 in %s or %s percent' %
           (values_str, chance_str, pct))
    print


#TODO delete.  for eval.
def stddevtst(table):
    '''for evaluating stddev'''
    avg = table.mean()
    sqs = 0
    count = 0
    for roll, freq in table.frequency_all():
        sqs += freq*(((avg - roll)**2))
        count += freq
    return round((sqs/count)**0.5, 4)

def stddeverr(table):
    '''compares stddevtst to the table method and sees pct diff'''
    accurate = stddevtst(table)
    approx = table.stddev()
    return 100*(accurate - approx)/accurate

from dice_classes import add_dice
def showit2(table):
    '''the final function for stddev checking.  adds a die and prints pctdiff'''
    for _ in range(100):
        add_dice(table)
        print str(stddeverr(table))
def highest(table):
    '''quick! gimme the highest val, nicely displayed'''
    return scinote(table.frequency_highest()[1])
#TODO ends

