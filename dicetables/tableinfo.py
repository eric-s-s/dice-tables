"""functions for getting useful info from tables, ie. plot pts or stats"""
from __future__ import absolute_import
from sys import version_info
from math import log10
from decimal import Decimal

from dicetables.longintmath import long_int_div as li_div


if version_info[0] < 3:
    INT_TYPES = (int, long)
else:
    INT_TYPES = (int, )
#tools for string formatting


class NumberFormatter(object):
    def __init__(self, show_digits=4, max_comma_exp=6, min_fixed_pt_exp=-3):
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
        self._max_comma_exp = int(max(-1, value))

    @property
    def min_fixed_pt_exp(self):
        return self._min_fixed_pt_exp

    @min_fixed_pt_exp.setter
    def min_fixed_pt_exp(self, value):
        self._min_fixed_pt_exp = min(0, int(value))

    def get_exponent(self, number):
        if isinstance(number, INT_TYPES):
            return int(log10(abs(number)))
        return int('{:.{}e}'.format(number, self.show_digits - 1).split('e')[1])

    def format_as_fixed_point(self, number, exponent):
        return '{:.{}f}'.format(number, self.show_digits - 1 - exponent)

    def format_using_commas(self, number, exponent):
        if isinstance(number, INT_TYPES):
            return '{:,}'.format(number)
        else:
            return '{:,.{}f}'.format(number, max(0, self.show_digits - 1 - exponent))

    def format_as_exponent(self, number, exponent):
        try:
            answer = '{:.{}e}'.format(number, self.show_digits - 1)
            if -10 < exponent < 10:
                return remove_extra_zero_from_exponent(answer)
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
            return self.format_as_fixed_point(number, exponent)
        elif 0 <= exponent <= self.max_comma_exp:
            return self.format_using_commas(number, exponent)
        else:
            return self.format_as_exponent(number, exponent)


def remove_extra_zero_from_exponent(answer):
    return answer[:-2] + answer[-1:]


def scinote(num, dig_len=4, max_comma_exp=6, min_fixed_pt_exp=-3):
    """num is int, float or long.  dig_len is int and < 18 and >= 2.
    returns a string of num in a nicely readable form.  rounds to dig_len.
    note- dig_len over 18 works but has errors in output"""
    formatter = NumberFormatter(dig_len, max_comma_exp, min_fixed_pt_exp)
    return formatter.format_number(num)


def get_pts_list(table, include_zeroes=True):
    if include_zeroes and table.event_keys():
        min_val, max_val = table.event_keys_range()
        the_pts = table.get_event_range(min_val, max_val + 1)
    else:
        the_pts = table.get_event_all()
    return the_pts


def full_table_string(table, include_zeroes=True):
    formatter = NumberFormatter()
    the_pts = get_pts_list(table, include_zeroes)
    out_str = ''
    value_right_just = len(str(table.event_keys_max()))
    for value, frequency in the_pts:
        out_str += '{:>{}}: {}\n'.format(value, value_right_just, formatter.format_number(frequency))
    return out_str


def graph_pts(table, percent=True, axes=True, include_zeroes=True, exact=False):
    """returns graph pts for a table.
    axes=True returns (x_axis, y_axis). axes=False returns [(x,y), (x,y)...]
    zeroes includes zero freq values from the min_val to max_val of the table
    percent=True converts y values into percent of total y values.
    exact=True/False only works with pct.  exact=False only good to ten decimal
    places, but much much faster.
    percent=False leaves as raw long ints, which will often be too large for
    graphing functions to handle.  for that case, graph_pts_overflow(table) is
    reccommended."""
    if not table.event_keys():
        raise ValueError('empty table')

    the_pts = get_pts_list(table, include_zeroes)
    if percent:
        if exact:
            the_pts = get_pct_exactly(the_pts)
        else:
            the_pts = get_pct_quickly(the_pts)
    if axes:
        return list(zip(*the_pts))
    else:
        return the_pts


def get_pct_quickly(the_pts):
    total_y_value = sum([pair[1] for pair in the_pts])
    output = []
    factor = 10 ** 50
    for value, freq in the_pts:
        y_val = (freq * factor) // total_y_value
        output.append((value, (y_val * 100.) / factor))
    return output


def get_pct_exactly(the_pts):
    total_y_value = sum([pair[1] for pair in the_pts])
    output = []
    for value, freq in the_pts:
        output.append((value, li_div(100 * freq, total_y_value)))
    return output


def graph_pts_overflow(table, axes=True, zeroes=True):
    """return graph points and the factor they are modified by to control for
    overflow problems by long ints."""
    raw_pts = graph_pts(table, percent=False, axes=axes, include_zeroes=zeroes)
    factor = 1
    overflow_point = 10**300
    exponent_adjustment = 4

    if table.get_biggest_event()[1] > overflow_point:
        power = int(log10(table.get_biggest_event()[1])) - exponent_adjustment
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
    """table is a AdditiveEvents. makes a list of tuples which
    [(value, x's representing value), ...]"""
    output_list = []
    max_frequency = table.get_biggest_event()[1]
    max_graph_height = 80
    divisor = 1
    add_s = ''
    if max_frequency > max_graph_height:
        divisor = li_div(max_frequency, max_graph_height)
        add_s = 's'
    val_len = len(str(table.event_keys_max()))
    for value, frequency in table.get_event_all():
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
    """table is a AdditiveEvents. returns a graph of x's."""
    #for output in graph_list(table):
    #    print output[1]
    temp = [pair[1] for pair in  ascii_graph_helper(table)]
    return '\n'.join(temp)


def ascii_graph_truncated(table):
    """table is a AdditiveEvents. prints a graph of x's,
    but doesn't print zero-x rolls"""
    excluded = []
    output = []
    for value, string in ascii_graph_helper(table):
        if 'x' in string:
            output.append(string)
        else:
            excluded.append(value)
    if excluded:
        output.append('not included: {}'.format(
            get_string_for_sequence(excluded).replace(',', ' and')
            ))
    return '\n'.join(output)


def stats(table, values):
    """

    :param table: AdditiveEvents/DiceTable
    :param values: list of ints
    :return: tuple of strings (str of values, values combinations, total combinations, inverse chance, pct chance)
    """
    formatter = NumberFormatter()
    total_combinations = table.get_total_event_occurrences()
    combinations_of_values = 0
    no_copies = set(values)
    for value in no_copies:
        combinations_of_values += table.get_event(value)[1]

    if combinations_of_values == 0:
        inverse_chance_str = 'infinity'
        pct_str = formatter.format_number(0)
    else:
        inverse_chance = Decimal(total_combinations) / Decimal(combinations_of_values)
        pct = Decimal(100.0) / inverse_chance
        inverse_chance_str = formatter.format_number(inverse_chance)
        pct_str = formatter.format_number(pct)
    return (get_string_for_sequence(values),
            formatter.format_number(combinations_of_values),
            formatter.format_number(total_combinations),
            inverse_chance_str,
            pct_str)


def get_string_for_sequence(input_list):
    input_list.sort()
    list_of_sequences = split_at_gaps_larger_than_one(input_list)
    list_of_sequence_strings = format_sequences(list_of_sequences)
    return ', '.join(list_of_sequence_strings)


def split_at_gaps_larger_than_one(input_list):
    max_gap_size = 1
    list_of_sequences = []
    for value in input_list:
        if not list_of_sequences or is_gap_too_big(list_of_sequences, value, max_gap_size):
            list_of_sequences.append([value])
        else:
            last_group = list_of_sequences[-1]
            last_group.append(value)
    return list_of_sequences


def is_gap_too_big(list_of_sequences, value, max_gap_size):
    last_value_of_list = list_of_sequences[-1][-1]
    return value - last_value_of_list > max_gap_size


def format_sequences(list_of_sequences):
    string_list = []
    for sequence in list_of_sequences:
        string_list.append(format_one_sequence(sequence))
    return string_list


def format_one_sequence(sequence):
    first = sequence[0]
    last = sequence[-1]
    if first == last:
        return format_for_sequence_str(first)
    else:
        return '{}-{}'.format(format_for_sequence_str(first), format_for_sequence_str(last))


def format_for_sequence_str(num):
    return '({:,})'.format(num) if num < 0 else '{:,}'.format(num)
# import time
# if __name__ == '__main__':
#
#     x = NumberFormatter()
#     print(x.format_number(99*10**-8))
#     def tst(num):
#         tster = NumberFormatter()
#         return tster.format_number(num)
#
#     def timer(number):
#         start = time.clock()
#         for _ in range(10000):
#             x.format_number(number)
#         obj_time = time.clock() - start
#         start = time.clock()
#         for _ in range(10000):
#             tst(number)
#         fobj_time = time.clock() - start
#         start = time.clock()
#         for _ in range(10000):
#             scinote(number)
#         func_time = time.clock() - start
#         print('obj : {}\nfobj: {}\nfunc: {}'.format(obj_time, fobj_time, func_time))
#
#     timer(123*10**-290)
#
#     import dicetables.dicestats as dt
#     tabel = dt.DiceTable()
#     tabel.add_die(500, dt.Die(6))
#
#     start = time.clock()
#     for _ in range(100):
#         full_table_string(tabel)
#     orig_time = time.clock() - start
#
#     start = time.clock()
#     for _ in range(100):
#         full_table_string_2(tabel)
#     new_time = time.clock() - start
#
#     print('orig: {}\nnew : {}'.format(orig_time, new_time))
#
#     start = time.clock()
#     for _ in range(100):
#         get_pts_list(tabel, True)
#     pts_time = time.clock() - start
#     print(pts_time)
#
#     this_pts_list = get_pts_list(tabel, True)
#
#     start = time.clock()
#     for _ in range(100):
#         outstr = ''
#         for value, frequency in this_pts_list:
#             outstr += '{0:>{1}}: {2}\n'.format(value, 5, x.format_number(frequency))
#             # outstr += '{0:>{1}}: '.format(value, max_len) + formatter.format_number(frequency) + '\n'
#
#     format_time = time.clock() - start
#     print(format_time)



