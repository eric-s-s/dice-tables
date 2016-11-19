# pylint: disable=missing-docstring, invalid-name, too-many-public-methods
"""tests for the eventsinfo.py module"""

from __future__ import absolute_import

import unittest
from dicetables import AdditiveEvents
import dicetables.eventsinfo as ti


class TestEventsInfo(unittest.TestCase):

    def assert_list_almost_equal(self, first, second, places=None, delta=None):
        for index, element in enumerate(first):
            self.assertAlmostEqual(element, second[index], places=places, delta=delta)

    def test_safe_true_div_returns_zero_when_answer_power_below_neg_300ish(self):
        self.assertEqual(ti.safe_true_div(1e+300, 10 ** 1000), 0)

    def test_safe_true_div_long_long_makes_float(self):
        result = ti.safe_true_div(10 ** 1300, 10 ** 1000)
        self.assertAlmostEqual(result, 10 ** 300, delta=10 ** 290)
        self.assertIsInstance(result, float)

    def test_safe_true_div_long_long_makes_float_with_negative_num(self):
        result = ti.safe_true_div(-10 ** 1300, 10 ** 1000)
        self.assertAlmostEqual(result, -10 ** 300, delta=10 ** 290)
        self.assertIsInstance(result, float)

    def test_safe_true_div_float_float_makes_long(self):
        result = ti.safe_true_div(1e+300, 1e-100)
        self.assertAlmostEqual(result, 10 ** 400, delta=10 ** 390)

    def test_safe_true_div_float_float_makes_long_with_negative_num(self):
        result = ti.safe_true_div(1e+300, -1e-100)
        self.assertAlmostEqual(result, -10 ** 400, delta=10 ** 390)

    def test_safe_true_div_long_long_makes_negative_power_float(self):
        result = ti.safe_true_div(10 ** 1000, 10 ** 1200)
        self.assertAlmostEqual(result, 10 ** -200, delta=10 ** -210)

    def test_EventsInformation_event_keys_removes_zero_occurrences(self):
        test = ti.EventsInformation(AdditiveEvents({0: 1, 1: 0}))
        self.assertEqual(test.events_keys(), [0])

    def test_EventsInformation_event_keys_sorts(self):
        test = ti.EventsInformation(AdditiveEvents({2: 1, 1: 1, 3: 1}))
        self.assertEqual(test.events_keys(), [1, 2, 3])

    def test_EventsInformation_event_keys_one_key(self):
        test = ti.EventsInformation(AdditiveEvents({2: 1}))
        self.assertEqual(test.events_keys(), [2])

    def test_EventsInformation_event_range(self):
        zero_to_two = ti.EventsInformation(AdditiveEvents({0: 2, 1: 1, 2: 5, 4: 0}))
        self.assertEqual(zero_to_two.events_range(), (0, 2))

    def test_EventsInformation_event_range_one_value(self):
        zero_to_two = ti.EventsInformation(AdditiveEvents({0: 2}))
        self.assertEqual(zero_to_two.events_range(), (0, 0))

    def test_EventsInformation_get_event(self):
        zero_three = ti.EventsInformation(AdditiveEvents({0: 3}))
        self.assertEqual(zero_three.get_event(0), (0, 3))

    def test_EventsInformation_get_event_returns_for_empty_event(self):
        zero_three = ti.EventsInformation(AdditiveEvents({0: 3}))
        self.assertEqual(zero_three.get_event(100), (100, 0))

    def test_EventsInformation_get_range_of_events(self):
        test = ti.EventsInformation(AdditiveEvents({1: 1, 2: 2}))
        self.assertEqual(test.get_range_of_events(0, 4),
                         [(0, 0), (1, 1), (2, 2), (3, 0)])

    def test_EventsInformation_all_events(self):
        test = ti.EventsInformation(AdditiveEvents({1: 1, 2: 2}))
        self.assertEqual(test.all_events(),
                         [(1, 1), (2, 2)])

    def test_EventsInformation_all_events_sorts(self):
        test = ti.EventsInformation(AdditiveEvents({2: 1, 1: 2}))
        self.assertEqual(test.all_events(),
                         [(1, 2), (2, 1)])

    def test_EventsInformation_all_events_does_not_return_zero_frequencies(self):
        test = ti.EventsInformation(AdditiveEvents({-1: 2, 0: 0, 1: 2}))
        self.assertEqual(test.all_events(), [(-1, 2), (1, 2)])

    def test_EventsInformation_all_events_include_zeroes_no_zeroes(self):
        test = ti.EventsInformation(AdditiveEvents({1: 1, 2: 2}))
        self.assertEqual(test.all_events_include_zeroes(),
                         [(1, 1), (2, 2)])

    def test_EventsInformation_all_events_include_zeroes_zeroes_out_of_range(self):
        test = ti.EventsInformation(AdditiveEvents({0: 0, 1: 1, 2: 2, 3: 0}))
        self.assertEqual(test.all_events_include_zeroes(),
                         [(1, 1), (2, 2)])

    def test_EventsInformation_all_events_include_zeroes_mid_zeroes(self):
        test = ti.EventsInformation(AdditiveEvents({1: 1, 2: 0, 3: 2}))
        self.assertEqual(test.all_events_include_zeroes(),
                         [(1, 1), (2, 0), (3, 2)])

    def test_EventsInformation_biggest_event_returns_first_biggest_event(self):
        test = ti.EventsInformation(AdditiveEvents({-1: 5, 0: 1, 2: 5}))
        self.assertEqual(test.biggest_event(), (-1, 5), (2, 5))

    def test_EventsInformation_biggest_event_returns_only_biggest_event(self):
        test = ti.EventsInformation(AdditiveEvents({-1: 5, 0: 1, 2: 10}))
        self.assertEqual(test.biggest_event(), (2, 10))

    def test_EventsInformation_biggest_events_all_one_event(self):
        test = ti.EventsInformation(AdditiveEvents({-1: 5}))
        self.assertEqual(test.biggest_events_all(), [(-1, 5)])

    def test_EventsInformation_biggest_events_all_one_biggest_event(self):
        test = ti.EventsInformation(AdditiveEvents({-1: 5, 0: 1, 2: 10}))
        self.assertEqual(test.biggest_events_all(), [(2, 10)])

    def test_EventsInformation_biggest_events_all_multiple_biggest_event_sorted(self):
        test = ti.EventsInformation(AdditiveEvents({-1: 5, 0: 1, 2: 10, -5: 10, 1: 10}))
        self.assertEqual(test.biggest_events_all(), [(-5, 10), (1, 10), (2, 10)])

    def test_EventsInformation_total_event_occurrences(self):
        test = ti.EventsInformation(AdditiveEvents({1: 2, 3: 4}))
        self.assertEqual(test.total_occurrences(), 2 + 4)

    def test_EventsInformation_get_items(self):
        test = ti.EventsInformation(AdditiveEvents({1: 2, 3: 4}))
        self.assertEqual(test.get_items(), {1: 2, 3: 4}.items())

    def test_EventsCalculations_init_defaults_include_zeroes_True(self):
        test = ti.EventsCalculations(AdditiveEvents({-1: 5, 1: 5}))
        self.assertTrue(test._include_zeroes)

    def test_EventsCalculations_init_set_include_zeroes_False(self):
        test = ti.EventsCalculations(AdditiveEvents({-1: 5, 1: 5}), False)
        self.assertFalse(test._include_zeroes)

    def test_EventsCalculations_mean_normal_case(self):
        test = ti.EventsCalculations(AdditiveEvents({-1: 5, 1: 5}))
        self.assertEqual(test.mean(), 0)

    def test_EventsCalculations_mean_with_non_uniform_events(self):
        test = ti.EventsCalculations(AdditiveEvents({1: 2, 2: 5}))
        mean = (2 + 10) / float(2 + 5)
        self.assertEqual(test.mean(), mean)

    def test_EventsCalculations_mean_with_large_number_events(self):
        test = ti.EventsCalculations(AdditiveEvents({1: 2 * 10 ** 1000, 2: 2 * 10 ** 1000}))
        self.assertEqual(test.mean(), 1.5)

    def test_EventsCalculations_stddev_low_occurrences(self):
        low_freq = ti.EventsCalculations(AdditiveEvents({2: 1, -2: 1, 1: 1, -1: 1}))
        self.assertEqual(low_freq.stddev(), round((10 / 4.) ** 0.5, 4))

    def test_EventsCalculations_stddev_low_occurrences_change_decimal_place_value(self):
        low_freq = ti.EventsCalculations(AdditiveEvents({2: 1, -2: 1, 1: 1, -1: 1}))
        self.assertEqual(low_freq.stddev(decimal_place=10), round((10 / 4.) ** 0.5, 10))

    def test_EventsCalculations_stddev_middle_high_occurrences(self):
        high_freq = ti.EventsCalculations(AdditiveEvents({2: 10 ** 50, -2: 10 ** 50, 1: 10 ** 50, -1: 10 ** 50}))
        self.assertEqual(high_freq.stddev(), round((10 / 4.) ** 0.5, 4))

    def test_EventsCalculations_stddev_middle_high_occurrences_change_decimal_place_value(self):
        high_freq = ti.EventsCalculations(AdditiveEvents({2: 10 ** 50, -2: 10 ** 50, 1: 10 ** 50, -1: 10 ** 50}))
        self.assertEqual(high_freq.stddev(decimal_place=10), round(2.5 ** 0.5, 10))

    def test_EventsCalculations_stddev_very_high_occurrences(self):
        high_freq = ti.EventsCalculations(AdditiveEvents({2: 10 ** 500, -2: 10 ** 500, 1: 10 ** 500, -1: 10 ** 500}))
        self.assertEqual(high_freq.stddev(), round((10 / 4.) ** 0.5, 4))

    def test_EventsCalculations_stddev_very_high_occurrences_change_decimal_place_value(self):
        high_freq = ti.EventsCalculations(AdditiveEvents({2: 10 ** 500, -2: 10 ** 500, 1: 10 ** 500, -1: 10 ** 500}))
        self.assertEqual(high_freq.stddev(decimal_place=10), round(2.5 ** 0.5, 10))

    def test_EventsCalculations_full_table_string_include_zeroes_true(self):
        calculator = ti.EventsCalculations(AdditiveEvents({1: 1, 3: 1}), include_zeroes=True)
        self.assertEqual(calculator.full_table_string(),
                         '1: 1\n2: 0\n3: 1\n')

    def test_EventsCalculations_full_table_string_include_zeroes_False(self):
        calculator = ti.EventsCalculations(AdditiveEvents({1: 1, 3: 1}), include_zeroes=False)
        self.assertEqual(calculator.full_table_string(),
                         '1: 1\n3: 1\n')

    def test_EventsCalculations_full_table_string_right_justifies_all_values_big_max(self):
        events = AdditiveEvents({1: 10, 10: 200, 1000: 3000})
        calculator = ti.EventsCalculations(events, include_zeroes=False)
        self.assertEqual(calculator.full_table_string(),
                         '   1: 10\n  10: 200\n1000: 3,000\n')

    def test_EventsCalculations_full_table_string_right_justifies_all_values_big_min(self):
        events = AdditiveEvents({-1000: 2, 1: 10, 10: 200, 1000: 3000})
        calculator = ti.EventsCalculations(events, include_zeroes=False)
        self.assertEqual(calculator.full_table_string(),
                         '-1000: 2\n    1: 10\n   10: 200\n 1000: 3,000\n')

    def test_EventsCalculations_full_table_string_edge_case(self):
        events = AdditiveEvents({0: 1})
        calculator = ti.EventsCalculations(events)
        self.assertEqual(calculator.full_table_string(), '0: 1\n')

    def test_EventsCalculations_full_table_string_uses_NumberFormatter_on_occurrences_only(self):
        events = AdditiveEvents({10000: 10**1000})
        calculator = ti.EventsCalculations(events)
        self.assertEqual(calculator.full_table_string(), '10000: 1.000e+1000\n')

    def test_get_fast_pct_number_zero(self):
        self.assertEqual(ti.get_fast_pct_number(0, 100), 0)

    def test_get_fast_pct_number_small(self):
        self.assertEqual(ti.get_fast_pct_number(10, 100), 10.0)

    def test_get_fast_pct_number_small_denominator_big_numerator(self):
        self.assertEqual(ti.get_fast_pct_number(10, 10**500), 0)

    def test_get_fast_pct_number_big_denominator_big_numerator(self):
        self.assertEqual(ti.get_fast_pct_number(10**499, 10**500), 10.0)

    def test_get_fast_pct_still_pretty_good(self):
        self.assertAlmostEqual(ti.get_fast_pct_number(4, 7), 400./7., places=10)
        self.assertAlmostEqual(ti.get_fast_pct_number(4*10**500, 7*10**500), 400./7., places=10)
        self.assertNotAlmostEqual(ti.get_fast_pct_number(4, 7), 400./7., places=15)
        self.assertNotAlmostEqual(ti.get_fast_pct_number(4*10**500, 7*10**500), 400./7., places=15)

    def test_get_exact_pct_number_zero(self):
        self.assertEqual(ti.get_exact_pct_number(0, 100), 0)

    def test_get_exact_pct_number_small(self):
        self.assertEqual(ti.get_exact_pct_number(10, 100), 10.0)

    def test_get_exact_pct_number_small_denominator_big_numerator(self):
        self.assertEqual(ti.get_exact_pct_number(10, 10**500), 0)

    def test_get_exact_pct_number_big_denominator_big_numerator(self):
        self.assertEqual(ti.get_exact_pct_number(10**499, 10**500), 10.0)

    def test_get_exact_pct_is_exact(self):
        self.assertEqual(ti.get_exact_pct_number(4, 7), 400./7.)
        self.assertEqual(ti.get_exact_pct_number(4*10**500, 7*10**500), 400./7.)

    def test_EventsCalculations_percentage_points(self):
        events = AdditiveEvents({1: 1, 3: 3})
        calculator = ti.EventsCalculations(events)
        self.assertEqual(calculator.percentage_points(), [(1, 25.0), (2, 0.0), (3, 75.0)])

    def test_EventsCalculations_percentage_points_include_zeroes_is_false(self):
        events = AdditiveEvents({1: 1, 3: 3})
        calculator = ti.EventsCalculations(events, False)
        self.assertEqual(calculator.percentage_points(), [(1, 25.0), (3, 75.0)])

    def test_EventsCalculations_percentage_points_is_not_exact(self):
        events = AdditiveEvents({1: 3, 3: 4})
        calculator = ti.EventsCalculations(events, False)
        three_sevenths, four_sevenths = calculator.percentage_points()
        self.assertAlmostEqual(three_sevenths[1], 300./7., places=10)
        self.assertAlmostEqual(four_sevenths[1], 400./7., places=10)

    def test_EventsCalculations_percentage_axes(self):
        events = AdditiveEvents({1: 1, 3: 3})
        calculator = ti.EventsCalculations(events)
        self.assertEqual(calculator.percentage_axes(), [(1, 2, 3), (25.0, 0.0, 75.0)])

    def test_EventsCalculations_percentage_axes_include_zeroes_is_false(self):
        events = AdditiveEvents({1: 1, 3: 3})
        calculator = ti.EventsCalculations(events, False)
        self.assertEqual(calculator.percentage_axes(), [(1, 3), (25.0, 75.0)])

    def test_EventsCalculations_percentage_axes_is_not_exact(self):
        events = AdditiveEvents({1: 3, 3: 4})
        calculator = ti.EventsCalculations(events, False)
        three_sevenths, four_sevenths = calculator.percentage_axes()[1]
        self.assertAlmostEqual(three_sevenths, 300./7., places=10)
        self.assertAlmostEqual(four_sevenths, 400./7., places=10)

    def test_EventsCalculations_percentage_points_exact(self):
        events = AdditiveEvents({1: 1, 3: 3})
        calculator = ti.EventsCalculations(events)
        self.assertEqual(calculator.percentage_points_exact(), [(1, 25.0), (2, 0.0), (3, 75.0)])

    def test_EventsCalculations_percentage_points_exact_include_zeroes_is_false(self):
        events = AdditiveEvents({1: 1, 3: 3})
        calculator = ti.EventsCalculations(events, False)
        self.assertEqual(calculator.percentage_points_exact(), [(1, 25.0), (3, 75.0)])

    def test_EventsCalculations_percentage_points_exact_is_not_exact(self):
        events = AdditiveEvents({1: 3, 3: 4})
        calculator = ti.EventsCalculations(events, False)
        three_sevenths, four_sevenths = calculator.percentage_points_exact()
        self.assertAlmostEqual(three_sevenths[1], 300./7., places=10)
        self.assertAlmostEqual(four_sevenths[1], 400./7., places=10)

    def test_EventsCalculations_percentage_axes_exact(self):
        events = AdditiveEvents({1: 1, 3: 3})
        calculator = ti.EventsCalculations(events)
        self.assertEqual(calculator.percentage_axes_exact(), [(1, 2, 3), (25.0, 0.0, 75.0)])

    def test_EventsCalculations_percentage_axes_exact_include_zeroes_is_false(self):
        events = AdditiveEvents({1: 1, 3: 3})
        calculator = ti.EventsCalculations(events, False)
        self.assertEqual(calculator.percentage_axes_exact(), [(1, 3), (25.0, 75.0)])

    def test_EventsCalculations_percentage_axes_exact_is_exact(self):
        events = AdditiveEvents({1: 3, 3: 4})
        calculator = ti.EventsCalculations(events, False)
        three_sevenths, four_sevenths = calculator.percentage_axes_exact()[1]
        self.assertEqual(three_sevenths, 300./7.)
        self.assertEqual(four_sevenths, 400./7.)

    def test_EventsCalculations_stats_strings_values_not_in_events(self):
        calculator = ti.EventsCalculations(AdditiveEvents({1: 1}))
        expected = ('2', '0', '1', 'Infinity', '0')
        self.assertEqual(calculator.stats_strings([2]), expected)

    def test_EventsCalculations_stats_strings_does_not_repeat_values(self):
        calculator = ti.EventsCalculations(AdditiveEvents({1: 1}))
        expected = ('1', '1', '1', '1.000', '100.0')
        self.assertEqual(calculator.stats_strings([1, 1]), expected)

    def test_EventsCalculations_stats_strings_includes_values_not_in_events(self):
        calculator = ti.EventsCalculations(AdditiveEvents({1: 1, 2: 1}))
        expected = ('0-1', '1', '2', '2.000', '50.00')
        self.assertEqual(calculator.stats_strings([0, 1]), expected)

    def test_EventsCalculations_stats_strings_works_for_large_values(self):
        calculator = ti.EventsCalculations(AdditiveEvents({1: 10 ** 1000, 2: (10 ** 1002 - 10 ** 1000)}))
        expected = ('1', '1.000e+1000', '1.000e+1002', '100.0', '1.000')
        self.assertEqual(calculator.stats_strings([1]), expected)

    """
    note: the following are wrapper functions. These tests simply confirm that the presets work.
    For full test see the following.
        events_range: test_EventsInformation_events_range
        mean: test_EventsCalculations_mean
        stddev: test_EventsCalculations_stddev
        stats: test_EventsCalculations_stats_strings
        full_table_string: test_EventsCalculations_full_table_string
        format_number: test_numberformatter.py
        graph_pts: test_EventsCalculations_percentage, test_EventsInformation_all_events
    """
    def test_events_range(self):
        events = AdditiveEvents({1: 1, 2: 3, 5: 7})
        self.assertEqual(ti.events_range(events), (1, 5))

    def test_mean(self):
        events = AdditiveEvents({1: 1, 2: 3})
        self.assertEqual(ti.mean(events), 1.75)

    def test_stddev(self):
        events = AdditiveEvents({1: 1})
        self.assertEqual(ti.stddev(events), 0.0)

    def test_stddev_decimal_place(self):
        events = AdditiveEvents({1: 1, 2: 2})
        self.assertEqual(ti.stddev(events, decimal_place=2), 0.47)

    def test_percentage_points_zeros_true(self):
        events = AdditiveEvents({1: 1, 3: 1})
        self.assertEqual(ti.percentage_points(events, include_zeroes=True), [(1, 50.0), (2, 0), (3, 50.0)])

    def test_percentage_points_zeros_false(self):
        events = AdditiveEvents({1: 1, 3: 1})
        self.assertEqual(ti.percentage_points(events, include_zeroes=False), [(1, 50.0), (3, 50.0)])

    def test_percentage_axes_zeros_true(self):
        events = AdditiveEvents({1: 1, 3: 1})
        self.assertEqual(ti.percentage_axes(events, include_zeroes=True), [(1, 2, 3), (50.0, 0, 50.0)])

    def test_percentage_axes_zeros_false(self):
        events = AdditiveEvents({1: 1, 3: 1})
        self.assertEqual(ti.percentage_axes(events, include_zeroes=False), [(1, 3), (50.0, 50.0)])

    def test_stats(self):
        events = AdditiveEvents({1: 1})
        self.assertEqual(ti.stats(events, [1]), ('1', '1', '1', '1.000', '100.0'))

    def test_full_table_string_include_zeroes_true(self):
        events = AdditiveEvents({1: 1, 3: 1})
        self.assertEqual(ti.full_table_string(events, True), '1: 1\n2: 0\n3: 1\n')

    def test_full_table_string_include_zeroes_false(self):
        events = AdditiveEvents({1: 1, 3: 1})
        self.assertEqual(ti.full_table_string(events, False), '1: 1\n3: 1\n')

    def test_format_number_works_as_expected(self):
        self.assertEqual(ti.format_number(123456.78), '123,457')
        self.assertEqual(ti.format_number(123456.78, digits_shown=7), '123,456.8')
        self.assertEqual(ti.format_number(123456.78, digits_shown=7, max_comma_exp=4), '1.234568e+5')
        self.assertEqual(ti.format_number(0.0000123), '1.230e-5')
        self.assertEqual(ti.format_number(0.0000123, min_fixed_pt_exp=-6), '0.00001230')
        self.assertEqual(ti.format_number(123456 * 10 ** 1000), '1.235e+1005')

    def test_graph_pts_axes(self):
        events = AdditiveEvents({1: 1, 2: 1})
        self.assertEqual(ti.graph_pts(events, axes=True), [(1, 2), (50.0, 50.0)])
        self.assertEqual(ti.graph_pts(events, axes=False), [(1, 50.0), (2, 50.0)])

    def test_graph_pts_percent(self):
        events = AdditiveEvents({1: 1, 2: 1})
        self.assertEqual(ti.graph_pts(events, percent=True), [(1, 2), (50.0, 50.0)])
        self.assertEqual(ti.graph_pts(events, percent=False), [(1, 2), (1, 1)])

    def test_graph_pts_include_zeroes(self):
        events = AdditiveEvents({1: 1, 3: 1})
        self.assertEqual(ti.graph_pts(events, include_zeroes=True), [(1, 2, 3), (50.0, 0, 50.0)])
        self.assertEqual(ti.graph_pts(events, include_zeroes=False), [(1, 3), (50.0, 50.0)])

    def test_graph_pts_exact(self):
        events = AdditiveEvents({1: 3, 2: 4})
        exact_pct = (300./7., 400./7.)
        expected_values = (1, 2)

        values, pct = ti.graph_pts(events, exact=True)
        self.assertEqual(expected_values, values)
        self.assertEqual(exact_pct, pct)

        values, pct = ti.graph_pts(events, exact=False)
        self.assertEqual(expected_values, values)
        self.assertNotEqual(exact_pct, pct)
        self.assert_list_almost_equal(exact_pct, pct)

    def test_graph_pts_overflow_for_small_numbers(self):
        events = AdditiveEvents({1: 1, 3: 1})
        self.assertEqual(ti.graph_pts_overflow(events), ([(1, 2, 3), (1, 0, 1)], '1'))

    def test_graph_pts_overflow_include_zeroes_false(self):
        events = AdditiveEvents({1: 1, 3: 1})
        self.assertEqual(ti.graph_pts_overflow(events, zeroes=False), ([(1, 3), (1, 1)], '1'))

    def test_graph_pts_overflow_include_axes_false(self):
        events = AdditiveEvents({1: 1, 3: 1})
        self.assertEqual(ti.graph_pts_overflow(events, axes=False), ([(1, 1), (2, 0), (3, 1)], '1'))

    def test_graph_pts_overflow_for_large_numbers(self):
        events = AdditiveEvents({1: 10 ** 200, 2: 1})
        self.assertEqual(ti.graph_pts_overflow(events),
                         ([(1, 2), (10 ** 200, 1)], '1'))

    def test_graph_pts_overflow_for_very_large_numbers(self):
        events = AdditiveEvents({1: 10 ** 2000, 2: 1})
        self.assertEqual(ti.graph_pts_overflow(events),
                         ([(1, 2), (10 ** 4, 0)], '1.0e+1996'))


if __name__ == '__main__':
    unittest.main()
