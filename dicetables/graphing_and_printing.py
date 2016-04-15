'''printing and graphing functions for use with LongIntTable class.
main functions are - grapher(), truncate_grapher(), fancy_grapher()
print_table() and stats()'''

from longintmath import long_int_div as li_div
import pylab


#helper function. used everywhere to make numbers look purty.
def scinote(num, dig_len=4):
    '''num is int, float or long.  dig_len is 18>int >=2 returns a nice formatted
    string for any number.  rounds to dig_len. (dig_len over 18 makes errors in
    output unless the number is higher than 10**309. this is for readability.
    for high precision, use the "decimal" module.)'''
    sci_power_cutoff = 7
    if num == 0:
        return '0.0'
    #abs(numbers) less than one use the general format to dig_len precision
    elif 0 < abs(num) < 1:
        str_format = '{:.%sg}' % (dig_len)
        return str_format.format(num)
    #1 <= abs(numbers) < sci_power_cutoff are appropriately rounded and comma-ed
    elif 1 <= abs(num) < 10**sci_power_cutoff:
        left = str(abs(num)).split('.')[0]
        int_digits = len(left)
        if dig_len > int_digits and isinstance(num, float):
            num = float(round(num, dig_len - int_digits))
        else:
            num = int(round(num, 0))
        return '{:,}'.format(num)
    else:
        try:
            str_format = '{:0%s.%se}' % (dig_len-1, dig_len-1)
            return str_format.format(num)
        except OverflowError:
            return long_note(num, dig_len)

def long_note(num, dig_len):
    '''converts long ints over +/-1e+308 to sci notation. helper to scinote'''
    num_str = str(abs(num))
    power = len(num_str) - 1
    digits = num_str[0] + '.' + num_str[1:dig_len + 2]
    #this rounds the final digit
    digits_float = float(digits)
    rounded_digits = str(round(digits_float, dig_len-1)).ljust(dig_len + 1, '0')
    if num < 0:
        rounded_digits = '-' + rounded_digits
    return '%se+%s' % (rounded_digits, power)


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
        divisor = li_div(max_frequency, max_graph_height)
        divstring = scinote(divisor)

    for value, frequency in table.frequency_all():
        num_of_xs = int(round(li_div(frequency, divisor)))
        output_list.append((value,
                            justify_right(value, max_value) +':'+num_of_xs*'x'))

    output_list.append((None, 'each x represents '+divstring+' occurences'))
    return output_list
def print_table_string(table):
    '''returns a string of the table printout'''
    max_value = table.values_max()
    outstr = ''
    for value, frequency in table.frequency_all():
        outstr = outstr + justify_right(value, max_value) +': '+scinote(frequency) + '\n'
    return outstr
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

def fancy_grapher(table, figure=1, style='bo', legend=False):
    '''table is a LongIntTable. makes a pylab plot of a table.
    You can set other figures and styles'''
    x_axis = []
    y_axis = []
    factor = 1
    too_big_for_pylab = 10**300
    pylab.figure(figure)
    pylab.ylabel('number of occurences')
    pylab.ion()
    #A work-around for the limitations of pylab.
    #It can't handle really fucking big ints and can't use my workarounds
    if table.total_frequency() > too_big_for_pylab:
        power = len(str(table.frequency_highest()[1])) - 5
        factor = 10**power
        pylab.ylabel('number of occurences times 10^'+str(power))

    for value, frequency in table.frequency_all():
        x_axis.append(value)
        y_axis.append(frequency/factor)

    pylab.xlabel('values')
    pylab.title('all the combinations for '+str(table))
    line, = pylab.plot(x_axis, y_axis, style, label=str(table))
    if legend:
        pylab.legend(loc='best')
    line.set_ydata(y_axis)
    pylab.show()

def fancy_grapher_pct(table, figure=1, style='bo', legend=False):
    '''table is a LongIntTable. makes a pylab plot of a table.
    You can set other figures and styles'''
    x_axis = []
    y_axis = []
    pylab.figure(figure)
    pylab.ylabel('pct of the total occurences')
    pylab.ion()
    factor = li_div(table.total_frequency(), 100)

    for value, frequency in table.frequency_all():
        x_axis.append(value)
        y_axis.append(li_div(frequency, factor))

    pylab.xlabel('values')
    pylab.title('all the combinations for '+str(table))
    line, = pylab.plot(x_axis, y_axis, style, label=str(table))
    if legend:
        pylab.legend(loc='best')
    line.set_ydata(y_axis)
    pylab.show()

def stats(table, values):
    '''table is a LongIntTable. values is a list. prints stats information
    for the values in the list.'''
    all_combos = table.total_frequency()
    lst_frequency = 0
    no_copies = []
    for number in values:
        if number not in no_copies:
            no_copies.append(number)
    for value in no_copies:
        lst_frequency += table.frequency(value)[1]

    if lst_frequency == 0:
        #print 'no results'
        #return None
        return 'no results'
    chance = li_div(all_combos, lst_frequency)
    pct = 100 * li_div(lst_frequency, all_combos)

    values_str = list_to_string(no_copies)
    #add extra space to str(table) \n parts so it prints purty after 'for '
    added_width = 4
    #print

    out_str = ('%s occurred %s times \nout of a total of %s possible combinations' %
               (values_str, scinote(lst_frequency), scinote(all_combos)))
    out_str = out_str + '\nfor %s,' % (str(table).replace('\n', '\n' + added_width*' '))
    out_str = out_str + ('\nthe chance of %s is \n1 in %s or \n%s percent' %
                         (values_str, scinote(chance), scinote(pct)))
    #print
    return out_str
