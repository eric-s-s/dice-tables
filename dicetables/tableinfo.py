"""functions for getting useful info from tables, ie. plot pts or stats"""
from __future__ import absolute_import
from sys import version_info
from math import log10
from decimal import Decimal

from dicetables.longintmath import safe_true_div


def is_int(number):
    if version_info[0] < 3:
        int_types = (int, long)
    else:
        int_types = (int,)
    return isinstance(number, int_types)


class NumberFormatter(object):
    def __init__(self, shown_digits=4, max_comma_exp=6, min_fixed_pt_exp=-3):
        self._shown_digits = None
        self._max_comma_exp = None
        self._min_fixed_pt_exp = None

        self.shown_digits = shown_digits
        self.max_comma_exp = max_comma_exp
        self.min_fixed_pt_exp = min_fixed_pt_exp

    @property
    def shown_digits(self):
        return self._shown_digits

    @shown_digits.setter
    def shown_digits(self, sig_figs):
        self._shown_digits = int(max(1, sig_figs))

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
        if is_int(number):
            return int(log10(abs(number)))
        return int('{:.{}e}'.format(number, self.shown_digits - 1).split('e')[1])

    def format_as_fixed_point(self, number, exponent):
        return '{:.{}f}'.format(number, self.shown_digits - 1 - exponent)

    def format_using_commas(self, number, exponent):
        if is_int(number):
            return '{:,}'.format(number)
        else:
            return '{:,.{}f}'.format(number, max(0, self.shown_digits - 1 - exponent))

    def format_as_exponent(self, number, exponent):
        try:
            answer = '{:.{}e}'.format(number, self.shown_digits - 1)
            if -10 < exponent < 10:
                return remove_extra_zero_from_exponent(answer)
            return answer
        except OverflowError:
            return self.format_huge_int(number, exponent)

    def format_huge_int(self, number, exponent):
        extra_digits = 10
        mantissa = number // 10 ** (exponent - self.shown_digits - extra_digits)
        mantissa /= 10. ** (self.shown_digits + extra_digits)
        mantissa = round(mantissa, self.shown_digits - 1)
        if mantissa == 10.0 or mantissa == -10.0:
            mantissa /= 10.0
            exponent += 1
        return '{:.{}f}e+{}'.format(mantissa, self.shown_digits - 1, exponent)

    def format(self, number):
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
    if answer[-2] == '0':
        return answer[:-2] + answer[-1:]
    return answer


def scinote(num, dig_len=4, max_comma_exp=6, min_fixed_pt_exp=-3):
    """num is int, float or long.  dig_len is int and < 18 and >= 2.
    returns a string of num in a nicely readable form.  rounds to dig_len.
    note- dig_len over 18 works but has errors in output"""
    formatter = NumberFormatter(dig_len, max_comma_exp, min_fixed_pt_exp)
    return formatter.format(num)


def get_raw_graph_points(table, include_zeroes=True):
    if include_zeroes:
        min_val, max_val = table.event_range
        the_pts = table.get_range_of_events(min_val, max_val + 1)
    else:
        the_pts = table.all_events
    return the_pts


# def full_table_string(table, include_zeroes=True):
#     """
#
#     :param table: AdditiveEvents or child.  is never empty
#     :param include_zeroes: =True, include zero occurrences within table.event_range
#     :return:
#     """
#     formatter = NumberFormatter()
#     the_pts = get_raw_graph_points(table, include_zeroes)
#     out_str = ''
#     value_right_just = len(str(table.event_range[1]))
#     for value, frequency in the_pts:
#         out_str += '{:>{}}: {}\n'.format(value, value_right_just, formatter.format(frequency))
#     return out_str


def full_table_string(table, include_zeroes=True):
    """

    :param table: AdditiveEvents or child.  is never empty
    :param include_zeroes: =True, include zero occurrences within table.event_range
    :return:
    """
    formatter = NumberFormatter()
    graph_data = GraphDataGenerator(include_zeroes=include_zeroes)
    the_pts = graph_data.get_raw_points(table)
    out_str = ''
    value_right_just = len(str(table.event_range[1]))
    for value, frequency in the_pts:
        out_str += '{:>{}}: {}\n'.format(value, value_right_just, formatter.format(frequency))
    return out_str

#  TODO delete
# from dicetables import AdditiveEvents


class GraphDataGenerator(object):
    def __init__(self, percent=True, include_zeroes=True, exact=False):
        self._percent = None
        self._include_zeroes = None
        self._exact = None

        self.percent = percent
        self.include_zeroes = include_zeroes
        self.exact = exact

    @property
    def percent(self):
        return self._percent

    @percent.setter
    def percent(self, boolean):
        self._percent = bool(boolean)

    @property
    def include_zeroes(self):
        return self._include_zeroes

    @include_zeroes.setter
    def include_zeroes(self, boolean):
        self._include_zeroes = bool(boolean)

    @property
    def exact(self):
        return self._exact

    @exact.setter
    def exact(self, boolean):
        self._exact = bool(boolean)

    def get_raw_points(self, events_table):
        if self.include_zeroes:
            start, end = events_table.event_range
            return events_table.get_range_of_events(start, end + 1)
        else:
            return events_table.all_events

    def get_percent_points(self, events_table):
        if self.exact:
            method = get_exact_pct_number
        else:
            method = get_fast_pct_number
        raw_points = self.get_raw_points(events_table)
        total_values = events_table.total_occurrences
        return [(event, method(occurrence, total_values)) for event, occurrence in raw_points]

    def get_points(self, events_table):
        if self.percent:
            return self.get_percent_points(events_table)
        else:
            return self.get_raw_points(events_table)

    def get_axes(self, events_table):
        return list(zip(*self.get_points(events_table)))


def get_fast_pct_number(number, total_values):
    factor = 10 ** 50
    will_not_overflow = (number * factor) // total_values
    return will_not_overflow * 100. / float(factor)


def get_exact_pct_number(number, total_values):
    return safe_true_div(100 * number, total_values)


def graph_pts(table, percent=True, axes=True, include_zeroes=True, exact=False):
    """

    :param table: AdditiveEvents or child. is never empty
    :param percent: y-values are percentages=True
    :param axes: True: [(x-axis), (y-axis)], False:[(xy-point), (xy-point), ...]
    :param include_zeroes: =True, include zero occurrences within table.event_range
    :param exact: =False, points only good to ten decimal places.
    :return:
    """
    data_generator = GraphDataGenerator(percent, include_zeroes, exact)
    if axes:
        return data_generator.get_axes(table)
    else:
        return data_generator.get_points(table)


def graph_pts_overflow(table, axes=True, zeroes=True):
    """return graph points and the factor they are modified by to control for
    overflow problems by long ints."""
    raw_pts = GraphDataGenerator(include_zeroes=zeroes).get_raw_points(table)

    factor = 1
    overflow_point = 10 ** 300
    exponent_adjustment = 4

    if table.biggest_event[1] > overflow_point:
        power = int(log10(table.biggest_event[1])) - exponent_adjustment
        factor = 10 ** power
    factor_string = scinote(factor, 2)
    new_points = [(x_val, y_val // factor) for x_val, y_val in raw_pts]
    if axes:
        new_points = list(zip(*new_points))
    return new_points, factor_string


def ascii_graph_helper(table):
    """table is a AdditiveEvents. makes a list of tuples which
    [(value, x's representing value), ...]"""
    output_list = []
    max_frequency = table.biggest_event[1]
    max_graph_height = 80
    divisor = 1
    add_s = ''
    if max_frequency > max_graph_height:
        divisor = safe_true_div(max_frequency, max_graph_height)
        add_s = 's'
    val_len = len(str(table.event_range[1]))
    for value, frequency in table.all_events:
        num_of_xs = int(round(safe_true_div(frequency, divisor)))
        output_list.append((value,
                            '{0:>{1}}:{2}'.format(value, val_len, num_of_xs * 'x')
                            ))
    output_list.append((None, 'each x represents {} occurrence{}'.format(scinote(divisor), add_s)))
    return output_list


def ascii_graph(table):
    """table is a AdditiveEvents. returns a graph of x's."""
    temp = [pair[1] for pair in ascii_graph_helper(table)]
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
    total_combinations = table.total_occurrences
    combinations_of_values = 0
    no_copies = set(values)
    for value in no_copies:
        combinations_of_values += table.get_event(value)[1]

    if combinations_of_values == 0:
        inverse_chance_str = 'infinity'
        pct_str = formatter.format(0)
    else:
        inverse_chance = Decimal(total_combinations) / Decimal(combinations_of_values)
        pct = Decimal(100.0) / inverse_chance
        inverse_chance_str = formatter.format(inverse_chance)
        pct_str = formatter.format(pct)
    return (get_string_for_sequence(values),
            formatter.format(combinations_of_values),
            formatter.format(total_combinations),
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
