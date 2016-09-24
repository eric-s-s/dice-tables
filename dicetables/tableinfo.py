"""functions for getting useful info from tables, ie. plot pts or stats"""
from __future__ import absolute_import
from math import log10
from decimal import Decimal

from dicetables.longintmath import long_int_div as li_div

#tools for string formatting


class NumberFormatter(object):
    def __init__(self, show_digits=4, max_comma_exp=7, min_fixed_pt_exp=-3):
        self._show_digits = None
        self._max_comma_exp = None
        self._min_fixed_pt_exp = None

        self.show_digits = show_digits
        self.max_comma_exp = max_comma_exp
        self.min_fixed_pt_exp = min_fixed_pt_exp

    @property
    def show_digits(self):
        return self._show_digits

    @show_digits.setter
    def show_digits(self, sig_figs):
        self._show_digits = int(max(1, sig_figs))

    @property
    def max_comma_exp(self):
        return self._max_comma_exp

    @max_comma_exp.setter
    def max_comma_exp(self, value):
        overflow_safety = 250
        self._max_comma_exp = int(min(max(0, value), overflow_safety))

    @property
    def min_fixed_pt_exp(self):
        return self._min_fixed_pt_exp

    @min_fixed_pt_exp.setter
    def min_fixed_pt_exp(self, value):
        self._min_fixed_pt_exp = min(0, int(value))

    def get_exponent(self, number):
        if isinstance(number, int):
            return int(log10(number))
        return int('{0:.{1}e}'.format(number, self.show_digits - 1).split('e')[1])

    def format_fixed_point(self, number, exponent):
        return '{0:.{1}f}'.format(number, self.show_digits - 1 - exponent)

    def format_number_using_commas(self, number, exponent):
        if isinstance(number, int):
            return '{:,}'.format(number)
        else:
            return '{:,.{}f}'.format(number, max(0, self.show_digits - 1 - exponent))

    def format_number_exponent(self, number, exponent):
        try:
            answer = '{:.{}e}'.format(number, self.show_digits - 1)
            if -10 < exponent < 10:
                return answer[:-2] + answer[-1:]
            return answer
        except OverflowError:
            return self.format_huge_int(number, exponent)

    def format_huge_int(self, number, exponent):
        extra_digits = 10
        mantissa = number // 10 ** (exponent - self.show_digits - extra_digits)
        mantissa /= 10. ** (self.show_digits + extra_digits)
        mantissa = round(mantissa, self.show_digits - 1)
        if mantissa == 10.0 or mantissa == -10.0:
            mantissa /= 10.0
            exponent += 1
        return '{:.{}f}e+{}'.format(mantissa, self.show_digits - 1, exponent)



    def format_number(self, number):
        if abs(number) == 0:
            return '0'
        exponent = self.get_exponent(number)
        if 0 > exponent >= self.min_fixed_pt_exp:
            return self.format_fixed_point(number, exponent)
        elif 0 <= exponent < self.max_comma_exp:
            return self.format_number_using_commas(number, exponent)
        else:
            return self.format_number_exponent(number, exponent)


def scinote(num, dig_len=4):
    """num is int, float or long.  dig_len is int and < 18 and >= 2.
    returns a string of num in a nicely readable form.  rounds to dig_len.
    note- dig_len over 18 works but has errors in output"""
    max_comma_exp = 7
    min_fixed_pt_exp = -3
    if num == 0:
        string_output = '0.0'
    elif 0 < abs(num) < 1:
        string_output = format_number_lt_one(num, dig_len, min_fixed_pt_exp)
    elif 1 <= abs(num) < 10**max_comma_exp:
        string_output = format_number_gt_one_lt_exponent_cutoff(num, dig_len, max_comma_exp)
    else:
        try:
            string_output = format_as_exponent(num, dig_len)
        except OverflowError:
            string_output = format_huge_int(num, dig_len)
    return string_output


def format_number_lt_one(num, dig_len, min_fixed_pt_exp):
    exponent = int('{0:.{1}e}'.format(num, dig_len - 1).split('e')[1])
    if exponent < min_fixed_pt_exp:
        return format_as_exponent(num, dig_len)

    return '{0:.{1}f}'.format(num, dig_len - 1 - exponent)


def format_number_gt_one_lt_exponent_cutoff(num, dig_len, cutoff_exp):
    if isinstance(num, int):
        return '{:,}'.format(num)
    else:
        exponent = int('{:.{}e}'.format(num, dig_len - 1).split('e')[1])
        output = '{:,.{}f}'.format(num, max(0, dig_len - 1 - exponent))
        # if output in (test_pos, test_neg):
        if exponent >= cutoff_exp:
            return format_as_exponent(num, dig_len)
        else:
            return output


def format_huge_int(num, dig_len):
    number_str = str(abs(num))
    exponent = len(number_str) - 1
    mantissa = float(number_str[0] + '.' + number_str[1:dig_len + 10])
    mantissa = round(mantissa, dig_len - 1)
    if mantissa == 10.0:
        mantissa = 1.0
        exponent += 1
    if num < 0:
        mantissa *= -1
    return '{:.{}f}e+{}'.format(mantissa, dig_len - 1, exponent)


def format_as_exponent(num, dig_len):
    mantissa, exponent = '{:.{}e}'.format(num, dig_len - 1).split('e')
    if len(exponent) == 3 and exponent[1] == '0':
        exponent = exponent[::2]
    return mantissa + 'e' + exponent






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
        return '({:,})'.format(num) if num < 0 else '{:,}'.format(num)
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
    if zeroes and table.values():
        the_pts = table.frequency_range(min_val, max_val + 1)
    else:
        the_pts = table.frequency_all()
    outstr = ''
    max_len = len(str(table.values_max()))
    for value, frequency in the_pts:
        outstr += '{0:>{1}}: {2}\n'.format(value, max_len, scinote(frequency))
    return outstr
def graph_pts(table, percent=True, axes=True, zeroes=True, exact=False):
    '''returns graph pts for a table.
    axes=True returns (x_axis, y_axis). axes=False returns [(x,y), (x,y)...]
    zeroes includes zero freq values from the min_val to max_val of the table
    percent=True converts y values into percent of total y values.
    exact=True/False only works with pct.  exact=False only good to ten decimal
    places, but much much faster.
    percent=False leaves as raw long ints, which will often be too large for
    graphing functions to handle.  for that case, graph_pts_overflow(table) is
    reccommended.'''
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
        if exact:
            for value, freq in the_pts:
                temp.append((value, li_div(100 * freq, total_freq)))
        else:
            factor = 10**50
            for value, freq in the_pts:
                y_val = (freq * factor) // total_freq
                temp.append((value, (y_val*100.)/factor))
        the_pts = temp[:]
    if axes:
        return list(zip(*the_pts))
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
        new_y_axis = tuple([old_val // factor for old_val in old_y_axis])
        return [x_axis, new_y_axis], factor_string
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
import time
if __name__ == '__main__':

    x = NumberFormatter()
    print(x.format_number(99*10**-8))
    def tst(num):
        tster = NumberFormatter()
        return tster.format_number(num)

    def timer(number):
        start = time.clock()
        for _ in range(10000):
            x.format_number(number)
        obj_time = time.clock() - start
        start = time.clock()
        for _ in range(10000):
            tst(number)
        fobj_time = time.clock() - start
        start = time.clock()
        for _ in range(10000):
            scinote(number)
        func_time = time.clock() - start
        print('obj : {}\nfobj: {}\nfunc: {}'.format(obj_time, fobj_time, func_time))

    timer(123*10**290)
