"""functions for getting useful info from tables, ie. plot pts or stats"""
from __future__ import absolute_import

from decimal import Decimal
from math import log10

from dicetables.tools.numberforamtter import NumberFormatter
from dicetables.tools.listtostring import get_string_from_list_of_ints


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

    def get_items(self):
        return self._dict.items()

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
        for event, occurrences in sorted(self._dict.items()):
            if occurrences == highest_occurrences:
                return event, highest_occurrences

    def biggest_events_all(self):
        highest_occurrences = max(self._dict.values())
        output = []
        for event, occurrences in sorted(self._dict.items()):
            if occurrences == highest_occurrences:
                output.append((event, occurrences))
        return sorted(output)

    def get_event(self, event):
        return event, self._dict.get(event, 0)

    def get_range_of_events(self, start, stop_before):
        return [self.get_event(event) for event in range(start, stop_before)]


class EventsCalculations(object):

    def __init__(self, events, include_zeroes=True):
        self._info = EventsInformation(events)
        self._include_zeroes = include_zeroes

    @property
    def include_zeroes(self):
        return self._include_zeroes

    @property
    def info(self):
        return self._info

    def mean(self):
        numerator = sum((value * freq) for value, freq in self._info.get_items())
        denominator = self._info.total_occurrences()
        return safe_true_div(numerator, denominator)

    def stddev(self, decimal_place=4):
        avg = self.mean()
        factor_to_truncate_digits = self._get_truncation_factor(decimal_place)
        truncated_deviations = 0
        for event_value, occurrences in self._info.get_items():
            truncated_deviations += (occurrences // factor_to_truncate_digits) * (avg - event_value) ** 2.
        truncated_total_occurrences = self._info.total_occurrences() // factor_to_truncate_digits
        return round((truncated_deviations / truncated_total_occurrences) ** 0.5, decimal_place)

    def _get_truncation_factor(self, decimal_place):
        extra_digits = 5
        largest_exponent = int(log10(self._info.biggest_event()[1]))
        required_exp_for_accuracy = 2 * (extra_digits + decimal_place)
        if largest_exponent < required_exp_for_accuracy:
            factor_to_truncate_digits = 1
        else:
            factor_to_truncate_digits = 10 ** (largest_exponent - required_exp_for_accuracy)
        return factor_to_truncate_digits

    def percentage_points(self):
        return self._percentage_points_by_method('fast')

    def percentage_points_exact(self):
        return self._percentage_points_by_method('exact')

    def percentage_axes(self):
        return list(zip(*self.percentage_points()))

    def percentage_axes_exact(self):
        return list(zip(*self.percentage_points_exact()))

    def _percentage_points_by_method(self, method_str):
        methods = {'fast': get_fast_pct_number, 'exact': get_exact_pct_number}
        pct_method = methods[method_str]
        total_values = self._info.total_occurrences()
        return [(event, pct_method(occurrence, total_values)) for event, occurrence in self._get_data_set()]

    def _get_data_set(self):
        if self._include_zeroes:
            return self._info.all_events_include_zeroes()
        else:
            return self._info.all_events()

    def full_table_string(self):
        formatter = NumberFormatter()
        right_just = self._get_right_just()
        out_str = ''
        for value, frequency in self._get_data_set():
            out_str += '{:>{}}: {}\n'.format(value, right_just, formatter.format(frequency))
        return out_str

    def _get_right_just(self):
        min_event, max_event = self._info.events_range()
        value_right_just = max(len(str(min_event)), len(str(max_event)))
        return value_right_just

    def stats_strings(self, query_values):
        """

        :return: (query values, query occurrences, total occurrences, inverse chance, pct chance)
        """
        formatter = NumberFormatter()

        total_occurrences = self._info.total_occurrences()
        query_values_occurrences = self._get_query_values_occurrences(query_values)

        inverse_chance_str, pct_str = _calculate_chance_and_pct(query_values_occurrences, total_occurrences)

        return (get_string_from_list_of_ints(query_values),
                formatter.format(query_values_occurrences),
                formatter.format(total_occurrences),
                formatter.format(inverse_chance_str),
                formatter.format(pct_str))

    def _get_query_values_occurrences(self, query_values):
        combinations_of_values = 0
        no_copies = set(query_values)
        for value in no_copies:
            combinations_of_values += self._info.get_event(value)[1]
        return combinations_of_values


def _calculate_chance_and_pct(query_values_occurrences, total_combinations):
    if not query_values_occurrences:
        return Decimal('inf'), Decimal('0')
    inverse_chance = Decimal(total_combinations) / Decimal(query_values_occurrences)
    pct = Decimal(100.0) / inverse_chance
    return inverse_chance, pct


def get_fast_pct_number(number, total_values):
    factor = 10 ** 50
    will_not_overflow = (number * factor) // total_values
    return will_not_overflow * 100. / float(factor)


def get_exact_pct_number(number, total_values):
    return safe_true_div(100 * number, total_values)


# wrappers functions and deprecated functions

def events_range(events):
    return EventsInformation(events).events_range()


def mean(events):
    return EventsCalculations(events).mean()


def stddev(events, decimal_place=4):
    return EventsCalculations(events).stddev(decimal_place=decimal_place)


def percentage_points(events, include_zeroes=True):
    return EventsCalculations(events, include_zeroes).percentage_points()


def percentage_axes(events, include_zeroes=True):
    return EventsCalculations(events, include_zeroes).percentage_axes()


def stats(events, query_values):
    return EventsCalculations(events).stats_strings(query_values)


def full_table_string(events, include_zeroes=True):
    return EventsCalculations(events, include_zeroes).full_table_string()


def format_number(number, digits_shown=4, max_comma_exp=6, min_fixed_pt_exp=-3):
    formatter = NumberFormatter(digits_shown, max_comma_exp, min_fixed_pt_exp)
    return formatter.format(number)


def graph_pts(events, percent=True, axes=True, include_zeroes=True, exact=False):
    """

    :param events: any AdditiveEvents or children
    :param percent: =True: y-values are pct of total occurrences,\n
        False: y-values are occurrences
    :param axes: =True: [(x-axis), (y-axis)], False:[(xy-point), (xy-point), ...]
    :param include_zeroes: =True: include zero occurrences within the event range
    :param exact: =False: get results quickly, but only good to about 10 decimal places,\n
        =True: get result slowly, but calculated to many decimal places
    """
    if percent:
        points = _get_pct_pts(events, include_zeroes, exact)
    else:
        points = _get_non_pct_pts(events, include_zeroes)

    if axes:
        return list(zip(*points))
    else:
        return points


def _get_non_pct_pts(events, include_zeroes):
    if include_zeroes:
        points = EventsInformation(events).all_events_include_zeroes()
    else:
        points = EventsInformation(events).all_events()
    return points


def _get_pct_pts(events, include_zeroes, exact):
    calculator = EventsCalculations(events, include_zeroes)
    if exact:
        return calculator.percentage_points_exact()
    else:
        return calculator.percentage_points()


def graph_pts_overflow(events, axes=True, zeroes=True):
    """

    :param events: any AdditiveEvents or children
    :param axes: =True: [(x-axis), (y-axis)], False:[(xy-point), (xy-point), ...]
    :param zeroes: =True: include zero occurrences within the event range
    :return: ([graphing data], 'factor all y-data  was divided by')
    """
    if zeroes:
        raw_pts = EventsInformation(events).all_events_include_zeroes()
    else:
        raw_pts = EventsInformation(events).all_events()
    formatter = NumberFormatter(shown_digits=2)

    factor = get_overflow_factor(events)
    factor_string = formatter.format(factor)
    new_points = [(x_val, y_val // factor) for x_val, y_val in raw_pts]
    if axes:
        new_points = list(zip(*new_points))
    return new_points, factor_string


def get_overflow_factor(events):
    factor = 1
    overflow_point = 10 ** 300
    exponent_adjustment = 4
    biggest_occurrences = EventsInformation(events).biggest_event()[1]
    if biggest_occurrences > overflow_point:
        power = int(log10(biggest_occurrences)) - exponent_adjustment
        factor = 10 ** power
    return factor
