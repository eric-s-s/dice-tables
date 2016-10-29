"""functions for getting useful info from tables, ie. plot pts or stats"""
from __future__ import absolute_import

from decimal import Decimal
from math import log10

from dicetables.baseevents import safe_true_div
from tools.numberforamtter import NumberFormatter


def format_number(number, digits_shown=4, max_comma_exp=6, min_fixed_pt_exp=-3):
    """

    :param number: any numerical type
    :param digits_shown: 1 < int <=18
    :param max_comma_exp: int >= -1
    :param min_fixed_pt_exp: int <= 0
    :return: str
    """
    formatter = NumberFormatter(digits_shown, max_comma_exp, min_fixed_pt_exp)
    return formatter.format(number)


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
            pct_method = get_exact_pct_number
        else:
            pct_method = get_fast_pct_number
        raw_points = self.get_raw_points(events_table)
        total_values = events_table.total_occurrences
        return [(event, pct_method(occurrence, total_values)) for event, occurrence in raw_points]

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

    :param table: any AdditiveEvents or children
    :param percent: =True: y-values are percentages
    :param axes: True: [(x-axis), (y-axis)], False:[(xy-point), (xy-point), ...]
    :param include_zeroes: =True: include zero occurrences within table.event_range
    :param exact:  =False: percentages only good to ten decimal places.
    """
    data_generator = GraphDataGenerator(percent, include_zeroes, exact)
    if axes:
        return data_generator.get_axes(table)
    else:
        return data_generator.get_points(table)


def graph_pts_overflow(table, axes=True, zeroes=True):
    """

    :param table: any AdditiveEvents or children
    :param axes: =True: [(x-axis), (y-axis)], False:[(xy-point), (xy-point), ...]
    :param zeroes: =True: include zero occurrences within table.event_range
    :return: ([graphing data], 'factor all y-data  was divided by')
    """
    raw_pts = GraphDataGenerator(include_zeroes=zeroes).get_raw_points(table)
    formatter = NumberFormatter(shown_digits=2)

    factor = get_overflow_factor(table)
    factor_string = formatter.format(factor)
    new_points = [(x_val, y_val // factor) for x_val, y_val in raw_pts]
    if axes:
        new_points = list(zip(*new_points))
    return new_points, factor_string


def get_overflow_factor(table):
    factor = 1
    overflow_point = 10 ** 300
    exponent_adjustment = 4
    if table.biggest_event[1] > overflow_point:
        power = int(log10(table.biggest_event[1])) - exponent_adjustment
        factor = 10 ** power
    return factor


def full_table_string(table, include_zeroes=True):
    """

    :param table: any AdditiveEvents or children
    :param include_zeroes: =True, include zero occurrences within table.event_range
    """
    formatter = NumberFormatter()
    graph_data = GraphDataGenerator(include_zeroes=include_zeroes)
    the_pts = graph_data.get_raw_points(table)
    out_str = ''
    value_right_just = len(str(table.event_range[1]))
    for value, frequency in the_pts:
        out_str += '{:>{}}: {}\n'.format(value, value_right_just, formatter.format(frequency))
    return out_str


def stats(table, query_values):
    """

    :param table: any AdditiveEvents or children
    :param query_values: list(int)
    :rtype: tuple[str]
    :return: ("query_values", "query_values combinations", "total combinations", "inverse chance", "pct chance")
    """
    formatter = NumberFormatter()
    total_combinations = table.total_occurrences
    combinations_of_values = 0
    no_copies = set(query_values)
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
    return (get_string_for_sequence(query_values),
            formatter.format(combinations_of_values),
            formatter.format(total_combinations),
            inverse_chance_str,
            pct_str)


def get_string_for_sequence(input_list):
    input_list.sort()
    list_of_sequences = split_at_gaps_larger_than_one(input_list)
    list_of_sequence_strings = format_sequences(list_of_sequences)
    return ', '.join(list_of_sequence_strings)


def split_at_gaps_larger_than_one(sorted_list):
    max_gap_size = 1
    list_of_sequences = []
    for value in sorted_list:
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
