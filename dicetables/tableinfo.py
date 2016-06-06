'''functions for getting useful info from tables, ie. plot pts or stats'''
from __future__ import absolute_import

from dicetables.longintmath import long_int_div as li_div

#tools for string formatting
def scinote(num, dig_len=4):
    '''num is int, float or long.  dig_len is int and < 18 and >= 2.
    returns a string of num in a nicely readable form.  rounds to dig_len.
    note - python has a rounding bug (see tableinfo_test.py), but this
    is a DISPLAY function. also note- dig_len over 18 works but has errors in
    output unless the number is higher than 10**309.'''
    sci_power_cutoff = 7
    if num == 0:
        return '0.0'
    #abs(numbers) less than one use the fixed point or exp to dig_len precision
    elif 0 < abs(num) < 1:
        exp = int('{0:.{1}e}'.format(num, dig_len - 1).split('e')[1])
        use_decimal = -3
        if exp < use_decimal:
            return '{0:.{1}e}'.format(num, dig_len - 1)
        else:
            return '{0:.{1}f}'.format(num, dig_len - 1 - exp)
    #1 <= abs(numbers) < sci_power_cutoff are appropriately rounded and comma-ed
    elif 1 <= abs(num) < 10**sci_power_cutoff:
        left = str(abs(num)).split('.')[0]
        int_digits = len(left)
        if dig_len > int_digits and isinstance(num, float):
            num = float(round(num, dig_len - int_digits))
        else:
            num = int(round(num, 0))
            #edge case workaround-else scinote(9.99e+6, 2) returns '10,000,000'
            if abs(num) == 10**sci_power_cutoff:
                return '{0:.{1}e}'.format(num, dig_len - 1)
        return '{:,}'.format(num)
    else:
        try:
            return '{0:.{1}e}'.format(num, dig_len - 1)
        except OverflowError:
            return _long_note(num, dig_len)

def _long_note(num, dig_len):
    '''converts long ints over +/-1e+308 to sci notation. helper to scinote'''
    num_str = str(abs(num))
    power = len(num_str) - 1
    digits = num_str[0] + '.' + num_str[1:dig_len + 10]
    digits_float = float(digits)
    if num < 0:
        digits_float *= -1
    return '{0:.{1}f}e+{2}'.format(digits_float, dig_len - 1, power)

def list_to_string(lst):
    '''outputs a list of intergers as a nice string.
    [1,2,3,7,9,10] becomes "1-3, 7, 9-10"
    [1,1,2,2,3] becomes "1-3"'''
    lst.sort()
    start_at = current = lst[0]
    tuple_list = []

    for next_one in lst[1:]:
        if current + 1 < next_one:
            tuple_list.append((start_at, current))
            start_at = next_one
        current = next_one
    tuple_list.append((start_at, current))
    def paren_negs(num):
        '''returns str(num) with parentethes around negative numbers'''
        return '({})'.format(num) if num < 0 else str(num)
    out_list = []
    for pair in tuple_list:
        if pair[0] == pair[1]:
            out_list.append(paren_negs(pair[0]))
        else:
            out_list.append('{}-{}'.format(paren_negs(pair[0]),
                                           paren_negs(pair[1])))
    return ', '.join(out_list)



def full_table_string(table, zeroes=True):
    '''returns a string of the entire table with nicely formatted numbers'''
    min_val, max_val = table.values_range()
    if zeroes and min_val:
        the_pts = table.frequency_range(min_val, max_val + 1)
    else:
        the_pts = table.frequency_all()
    outstr = ''
    max_len = len(str(table.values_max()))
    for value, frequency in the_pts:
        outstr += '{0:>{1}}: {2}\n'.format(value, max_len, scinote(frequency))
    return outstr
def graph_pts(table, percent=True, axes=True, zeroes=True):
    '''returns graph pts for a table.
    axes=True returns (x_axis, y_axis). axes=False returns [(x,y), (x,y)...]
    zeroes includes zero freq values from the min_val to max_val of the table
    percent=True converts y values into percent of total y values, percent=False
    leaves as raw long ints, which will often be too large for graphing functions
    to handle.  for that case, graph_pts_overflow(table) is reccommended.'''
    if not table.values():
        raise ValueError('empty table')

    if zeroes:
        the_pts = table.frequency_range(table.values_min(),
                                        table.values_max() + 1)
    else:
        the_pts = table.frequency_all()
    if percent:
        temp = []
        total_freq = table.total_frequency()
        for value, freq in the_pts:
            temp.append((value, li_div(100 * freq, total_freq)))
        the_pts = temp[:]
    if axes:
        x_axis = []
        y_axis = []
        for val, freq in the_pts:
            x_axis.append(val)
            y_axis.append(freq)
        return x_axis, y_axis
    else:
        return the_pts
def graph_pts_overflow(table, axes=True, zeroes=True):
    '''return graph points and the factor they are modified by to control for
    overflow problems by long ints.'''
    raw_pts = graph_pts(table, percent=False, axes=axes, zeroes=zeroes)
    factor = 1
    overflow_point = 10**300

    if table.frequency_highest()[1] > overflow_point:
        power = len(str(table.frequency_highest()[1])) - 5
        factor = 10**power
    factor_string = scinote(factor, 2)
    if axes:
        x_axis, old_y_axis = raw_pts
        new_y_axis = [old_val // factor for old_val in old_y_axis]
        return (x_axis, new_y_axis), factor_string
    else:
        new_pts = [(x_val, y_val // factor) for x_val, y_val in raw_pts]
        return new_pts, factor_string

def ascii_graph_helper(table):
    '''table is a LongIntTable. makes a list of tuples which
    [(value, x's representing value), ...]'''
    output_list = []
    max_frequency = table.frequency_highest()[1]
    max_graph_height = 80
    divisor = 1
    add_s = ''
    if max_frequency > max_graph_height:
        divisor = li_div(max_frequency, max_graph_height)
        add_s = 's'
    val_len = len(str(table.values_max()))
    for value, frequency in table.frequency_all():
        num_of_xs = int(round(li_div(frequency, divisor)))
        output_list.append((value,
                            '{0:>{1}}:{2}'.format(value, val_len, num_of_xs*'x')
                           ))
    output_list.append((None,
                        'each x represents {} occurence{}'.format(
                            scinote(divisor), add_s
                            )
                       ))
    return output_list


def ascii_graph(table):
    '''table is a LongIntTable. returns a graph of x's.'''
    #for output in graph_list(table):
    #    print output[1]
    temp = [pair[1] for pair in  ascii_graph_helper(table)]
    return '\n'.join(temp)


def ascii_graph_truncated(table):
    '''table is a LongIntTable. prints a graph of x's,
    but doesn't print zero-x rolls'''
    excluded = []
    output = []
    for value, string in ascii_graph_helper(table):
        if 'x' in string:
            output.append(string)
        else:
            excluded.append(value)
    if excluded:
        output.append('not included: {}'.format(
            list_to_string(excluded).replace(',', ' and')
            ))
    return '\n'.join(output)



def stats(table, values):
    '''table is a LongIntTable. values is a list. returns tuple of strings
    (string of input values, combinations from input values, total combos,
    1 in how many chance, percent chance)'''
    total_freq = table.total_frequency()
    lst_freq = 0
    no_copies = set(values)
    for value in no_copies:
        lst_freq += table.frequency(value)[1]

    if lst_freq == 0:
        chance = 'infinity'
        pct = scinote(0)
    else:
        chance = scinote(li_div(total_freq, lst_freq))
        pct = scinote(100 * li_div(lst_freq, total_freq))
    return (list_to_string(values),
            scinote(lst_freq),
            scinote(total_freq),
            chance,
            pct)

