"""
For getting and computing details for any IntegerEvents, including:

- points/axes for graphing, both raw and pct
    - pct can be computed quickly up to 10 decimal places or more exactly and slowly using Decimal
    - can include all the zero values between the lowest and highest non-zero events in an IntegerEvents
- stddev and mean
- string of all numbers in events in human readable form
- strings for the percent chance of any subset of events within an events

Can be accessed through objects or wrapper functions.
"""

from collections import namedtuple
from decimal import Decimal
from math import log10
from typing import List, Tuple

from dicetables.eventsbases.integerevents import IntegerEvents
from dicetables.tools.listtostring import get_string_from_list_of_ints
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
    def __init__(self, events: IntegerEvents):
        self._dict = events.get_dict()

    def get_items(self):
        """

        :return: dict.items(): a list in py2 and an iterator in py3.
        """
        return self._dict.items()

    def events_keys(self) -> List[int]:
        return sorted(self._dict.keys())

    def events_range(self) -> Tuple[int, int]:
        all_keys = self.events_keys()
        return all_keys[0], all_keys[-1]

    def total_occurrences(self) -> int:
        return sum(self._dict.values())

    def all_events(self):
        return sorted(self._dict.items())

    def all_events_include_zeroes(self):
        start, stop = self.events_range()
        return self.get_range_of_events(start, stop + 1)

    def biggest_event(self) -> Tuple[int, int]:
        """

        :return: (event, occurrences) for first event with highest occurrences
        """
        highest_occurrences = max(self._dict.values())
        for event, occurrences in sorted(self._dict.items()):  # pragma: no branch
            if occurrences == highest_occurrences:
                return event, highest_occurrences

    def biggest_events_all(self) -> List[Tuple[int, int]]:
        """

        :return: the list of all events that have biggest occurrence
        """
        highest_occurrences = max(self._dict.values())
        output = []
        for event, occurrences in self._dict.items():
            if occurrences == highest_occurrences:
                output.append((event, occurrences))
        return sorted(output)

    def get_event(self, event: int) -> Tuple[int, int]:
        return event, self._dict.get(event, 0)

    def get_range_of_events(self, start: int, stop_before: int) -> List[Tuple[int, int]]:
        return [self.get_event(event) for event in range(start, stop_before)]


class EventsCalculations(object):

    def __init__(self, events: IntegerEvents, include_zeroes: bool = True):
        self._info = EventsInformation(events)
        self._include_zeroes = include_zeroes

    @property
    def include_zeroes(self) -> int:
        return self._include_zeroes

    @property
    def info(self) -> EventsInformation:
        return self._info

    def mean(self) -> float:
        numerator = sum((value * freq) for value, freq in self._info.get_items())
        denominator = self._info.total_occurrences()
        return safe_true_div(numerator, denominator)

    def stddev(self, decimal_place=4) -> float:
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

    def percentage_points(self) -> List[Tuple[int, float]]:
        """
        Very fast, but only good to ten decimal places.
        """
        return self._percentage_points_by_method('fast')

    def percentage_points_exact(self) -> List[Tuple[int, float]]:
        return self._percentage_points_by_method('exact')

    def percentage_axes(self):
        """
        Very fast, but only good to ten decimal places.
        """
        return list(zip(*self.percentage_points()))

    def percentage_axes_exact(self):
        return list(zip(*self.percentage_points_exact()))

    def log10_points(self, log10_of_zero_value=-100.0) -> List[Tuple[int, float]]:
        """
        returns log10 of the occurrences.

        :param log10_of_zero_value: any zero-occurrence must have a preset value.
        """
        return [(event, log10(occurrence) if occurrence != 0 else log10_of_zero_value)
                for event, occurrence in self._get_data_set()]

    def log10_axes(self, log10_of_zero_value=-100.0):
        """
        returns log10 of the occurrences.

        :param log10_of_zero_value: any zero-occurrence must have a preset value.
        """
        return list(zip(*self.log10_points(log10_of_zero_value)))

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

    def full_table_string(self, shown_digits=4, max_power_for_commaed=6):
        """

        :param shown_digits: How many digits in each scientific notation string.
        :param max_power_for_commaed: The largest power to be represented in comma notation.
            if set to -1, all numbers are in scientific notation.
        """
        shown_digits = max(shown_digits, 1)
        formatter = NumberFormatter(shown_digits=shown_digits, max_comma_exp=max_power_for_commaed)
        right_just = self._get_right_just()
        out_str = ''
        for value, frequency in self._get_data_set():
            out_str += '{:>{}}: {}\n'.format(value, right_just, formatter.format(frequency))
        return out_str

    def _get_right_just(self):
        min_event, max_event = self._info.events_range()
        value_right_just = max(len(str(min_event)), len(str(max_event)))
        return value_right_just

    def stats_strings(self, query_list, shown_digits=4, max_power_for_commaed=6, min_power_for_fixed_pt=-3):
        """
        Calculates the pct chance and one-in chance of any list of numbers,
        including numbers not in the Events.

        :param query_list: A list of ints. Calculates the chance of the list getting rolled.
        :param shown_digits: How many digits in each scientific notation number str.
        :param max_power_for_commaed: The largest power to be represented in comma notation.
            if set to -1, all numbers >= 1 are in scientific notation.
        :param min_power_for_fixed_pt: The smallest power to be represented in fixed point notation.
            If set to zero, all values < 1 represented in scientific notation.
        :return: (query values, query occurrences, total occurrences, inverse chance, pct chance)
        """
        shown_digits = max(shown_digits, 1)
        formatter = NumberFormatter(shown_digits=shown_digits, max_comma_exp=max_power_for_commaed,
                                    min_fixed_pt_exp=min_power_for_fixed_pt)

        total_occurrences = self._info.total_occurrences()
        query_values_occurrences = self._get_query_values_occurrences(query_list)

        inverse_chance_str, pct_str = _calculate_chance_and_pct(query_values_occurrences, total_occurrences)

        return StatsStrings(get_string_from_list_of_ints(query_list),
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


StatsStrings = namedtuple('StatsStrings',
                          ['query_values', 'query_occurrences', 'total_occurrences', 'one_in_chance', 'pct_chance'])


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


# wrappers functions

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


def stats(events, query_values, shown_digits=4, max_power_for_commaed=6, min_power_for_fixed_pt=-3):
    return EventsCalculations(events).stats_strings(query_values,
                                                    shown_digits=shown_digits,
                                                    max_power_for_commaed=max_power_for_commaed,
                                                    min_power_for_fixed_pt=min_power_for_fixed_pt)


def full_table_string(events, include_zeroes=True, shown_digits=4, max_power_for_commaed=6):
    return EventsCalculations(events, include_zeroes).full_table_string(shown_digits=shown_digits,
                                                                        max_power_for_commaed=max_power_for_commaed)
