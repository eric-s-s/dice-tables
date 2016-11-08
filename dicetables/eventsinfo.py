"""functions for getting useful info from tables, ie. plot pts or stats"""
from __future__ import absolute_import

from decimal import Decimal
from math import log10

from dicetables.tools.numberforamtter import NumberFormatter


def safe_true_div(numerator, denominator):
    """floating point division for any sized number"""
    ans = Decimal(numerator) / Decimal(denominator)
    return _convert_decimal_to_float_or_int(ans)


def _convert_decimal_to_float_or_int(num):
    answer_as_float = float(num)
    if answer_as_float == float('inf') or answer_as_float == float('-inf'):
        return int(num)
    else:
        return answer_as_float


class EventsInformation(object):
    def __init__(self, events):
        self._dict = events.get_dict()

    def events_keys(self):
        return sorted(self._dict.keys())

    def events_range(self):
        all_keys = self.events_keys()
        return all_keys[0], all_keys[-1]

    def total_occurrences(self):
        return sum(self._dict.values())

    def all_events(self):
        return sorted(self._dict.items())

    def all_events_include_zeroes(self):
        start, stop = self.events_range()
        return self.get_range_of_events(start, stop + 1)

    def biggest_event(self):
        """

        :return: (event, occurrences) for first event with highest occurrences
        """
        highest_occurrences = max(self._dict.values())
        for event in sorted(self._dict.keys()):
            if self._dict[event] == highest_occurrences:
                return event, highest_occurrences

    def get_event(self, event):
        return event, self._dict.get(event, 0)

    def get_range_of_events(self, start, stop_before):
        return [self.get_event(event) for event in range(start, stop_before)]

    def mean(self):
        numerator = sum((value * freq) for value, freq in self._dict.items())
        denominator = self.total_occurrences()
        return safe_true_div(numerator, denominator)

    def stddev(self, decimal_place=4):
        avg = self.mean()
        factor_to_truncate_digits = self._get_truncation_factor(decimal_place)
        truncated_deviations = 0
        for event_value, occurrences in self._dict.items():
            truncated_deviations += (occurrences // factor_to_truncate_digits) * (avg - event_value) ** 2.
        truncated_total_occurrences = self.total_occurrences() // factor_to_truncate_digits
        return round((truncated_deviations / truncated_total_occurrences) ** 0.5, decimal_place)

    def _get_truncation_factor(self, decimal_place):
        extra_digits = 5
        largest_exponent = int(log10(self.biggest_event()[1]))
        required_exp_for_accuracy = 2 * (extra_digits + decimal_place)
        if largest_exponent < required_exp_for_accuracy:
            factor_to_truncate_digits = 1
        else:
            factor_to_truncate_digits = 10 ** (largest_exponent - required_exp_for_accuracy)
        return factor_to_truncate_digits


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

    def _get_raw_points(self, info_getter):
        if self.include_zeroes:
            return info_getter.all_events_include_zeroes()
        else:
            return info_getter.all_events()

    def get_percent_points(self, events_table):
        info_getter = EventsInformation(events_table)
        if self.exact:
            pct_method = get_exact_pct_number
        else:
            pct_method = get_fast_pct_number

        raw_points = self._get_raw_points(info_getter)

        total_values = info_getter.total_occurrences()
        return [(event, pct_method(occurrence, total_values)) for event, occurrence in raw_points]

    def get_points(self, events_table):
        if self.percent:
            return self.get_percent_points(events_table)
        else:
            return self._get_raw_points(EventsInformation(events_table))

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
    if zeroes:
        raw_pts = EventsInformation(table).all_events_include_zeroes()
    else:
        raw_pts = EventsInformation(table).all_events()
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
    biggest_occurrences = EventsInformation(table).biggest_event()[1]
    if biggest_occurrences > overflow_point:
        power = int(log10(biggest_occurrences)) - exponent_adjustment
        factor = 10 ** power
    return factor


def full_table_string(table, include_zeroes=True):
    """

    :param table: any AdditiveEvents or children
    :param include_zeroes: =True, include zero occurrences within table.event_range
    """
    formatter = NumberFormatter()
    info_getter = EventsInformation(table)
    if include_zeroes:
        the_pts = info_getter.all_events_include_zeroes()
    else:
        the_pts = info_getter.all_events()
    out_str = ''
    min_event, max_event = info_getter.events_range()
    value_right_just = max(len(str(min_event)), len(str(max_event)))
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
    info_getter = EventsInformation(table)
    total_combinations = info_getter.total_occurrences()
    query_values_occurrences = get_query_values_occurrences(query_values, info_getter)

    if query_values_occurrences == 0:
        inverse_chance_str = 'infinity'
        pct_str = formatter.format(0)
    else:
        inverse_chance = Decimal(total_combinations) / Decimal(query_values_occurrences)
        pct = Decimal(100.0) / inverse_chance
        inverse_chance_str = formatter.format(inverse_chance)
        pct_str = formatter.format(pct)
    return (get_string_for_sequence(query_values),
            formatter.format(query_values_occurrences),
            formatter.format(total_combinations),
            inverse_chance_str,
            pct_str)


def get_query_values_occurrences(query_values, info_getter):
    combinations_of_values = 0
    no_copies = set(query_values)
    for value in no_copies:
        combinations_of_values += info_getter.get_event(value)[1]
    return combinations_of_values


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
