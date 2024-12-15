# pylint: disable=missing-docstring, invalid-name, too-many-public-methods


import unittest

import dicetables.eventsinfo as ti
from dicetables import AdditiveEvents


class TestEventsInfo(unittest.TestCase):
    def test_safe_true_div_returns_zero_when_answer_power_below_neg_300ish(self):
        self.assertEqual(ti.safe_true_div(1e300, 10**1000), 0)

    def test_safe_true_div_long_long_makes_float(self):
        result = ti.safe_true_div(10**1300, 10**1000)
        self.assertAlmostEqual(result, 10**300, delta=10**290)
        self.assertIsInstance(result, float)

    def test_safe_true_div_long_long_makes_float_with_negative_num(self):
        result = ti.safe_true_div(-(10**1300), 10**1000)
        self.assertAlmostEqual(result, -(10**300), delta=10**290)
        self.assertIsInstance(result, float)

    def test_safe_true_div_float_float_makes_long(self):
        result = ti.safe_true_div(1e300, 1e-100)
        self.assertAlmostEqual(result, 10**400, delta=10**390)

    def test_safe_true_div_float_float_makes_long_with_negative_num(self):
        result = ti.safe_true_div(1e300, -1e-100)
        self.assertAlmostEqual(result, -(10**400), delta=10**390)

    def test_safe_true_div_long_long_makes_negative_power_float(self):
        result = ti.safe_true_div(10**1000, 10**1200)
        self.assertAlmostEqual(result, 10**-200, delta=10**-210)

    def test_EventsInformation_get_items(self):
        test = ti.EventsInformation(AdditiveEvents({1: 2, 3: 4}))
        self.assertEqual(test.get_items(), {1: 2, 3: 4}.items())

    def test_EventsInformation_event_keys_removes_zero_occurrences(self):
        test = ti.EventsInformation(AdditiveEvents({0: 1, 1: 0}))
        self.assertEqual(test.events_keys(), [0])

    def test_EventsInformation_events_keys_sorts(self):
        test = ti.EventsInformation(AdditiveEvents({2: 1, 1: 1, 3: 1}))
        self.assertEqual(test.events_keys(), [1, 2, 3])

    def test_EventsInformation_events_keys_one_key(self):
        test = ti.EventsInformation(AdditiveEvents({2: 1}))
        self.assertEqual(test.events_keys(), [2])

    def test_EventsInformation_events_range(self):
        zero_to_two = ti.EventsInformation(AdditiveEvents({0: 2, 1: 1, 2: 5, 4: 0}))
        self.assertEqual(zero_to_two.events_range(), (0, 2))

    def test_EventsInformation_events_range_one_value(self):
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
        self.assertEqual(test.get_range_of_events(0, 4), [(0, 0), (1, 1), (2, 2), (3, 0)])

    def test_EventsInformation_all_events(self):
        test = ti.EventsInformation(AdditiveEvents({1: 1, 2: 2}))
        self.assertEqual(test.all_events(), [(1, 1), (2, 2)])

    def test_EventsInformation_all_events_sorts(self):
        test = ti.EventsInformation(AdditiveEvents({2: 1, 1: 2}))
        self.assertEqual(test.all_events(), [(1, 2), (2, 1)])

    def test_EventsInformation_all_events_does_not_return_zero_frequencies(self):
        test = ti.EventsInformation(AdditiveEvents({-1: 2, 0: 0, 1: 2}))
        self.assertEqual(test.all_events(), [(-1, 2), (1, 2)])

    def test_EventsInformation_all_events_include_zeroes_no_zeroes(self):
        test = ti.EventsInformation(AdditiveEvents({1: 1, 2: 2}))
        self.assertEqual(test.all_events_include_zeroes(), [(1, 1), (2, 2)])

    def test_EventsInformation_all_events_include_zeroes_zeroes_out_of_range(self):
        test = ti.EventsInformation(AdditiveEvents({0: 0, 1: 1, 2: 2, 3: 0}))
        self.assertEqual(test.all_events_include_zeroes(), [(1, 1), (2, 2)])

    def test_EventsInformation_all_events_include_zeroes_mid_zeroes(self):
        test = ti.EventsInformation(AdditiveEvents({1: 1, 2: 0, 3: 2}))
        self.assertEqual(test.all_events_include_zeroes(), [(1, 1), (2, 0), (3, 2)])

    def test_EventsInformation_biggest_event_returns_first_biggest_event(self):
        test = ti.EventsInformation(AdditiveEvents({-1: 5, 0: 1, 2: 5}))
        self.assertEqual(test.biggest_event(), (-1, 5))

    def test_EventsInformation_biggest_event_returns_only_biggest_event(self):
        test = ti.EventsInformation(AdditiveEvents({-1: 5, 0: 1, 2: 10}))
        self.assertEqual(test.biggest_event(), (2, 10))

    def test_EventsInformation_biggest_events_all_one_event(self):
        test = ti.EventsInformation(AdditiveEvents({-1: 5}))
        self.assertEqual(test.biggest_events_all(), [(-1, 5)])

    def test_EventsInformation_biggest_events_all_one_biggest_event(self):
        test = ti.EventsInformation(AdditiveEvents({-1: 5, 0: 1, 2: 10}))
        self.assertEqual(test.biggest_events_all(), [(2, 10)])

    def test_EventsInformation_biggest_events_all_multiple_biggest_events_sorted(self):
        test = ti.EventsInformation(AdditiveEvents({-1: 5, 0: 1, 2: 10, -5: 10, 1: 10}))
        self.assertEqual(test.biggest_events_all(), [(-5, 10), (1, 10), (2, 10)])

    def test_EventsInformation_total_event_occurrences(self):
        test = ti.EventsInformation(AdditiveEvents({1: 2, 3: 4}))
        self.assertEqual(test.total_occurrences(), 2 + 4)

    def test_EventsInformation_total_event_occurrences_one_event(self):
        test = ti.EventsInformation(AdditiveEvents({1: 2}))
        self.assertEqual(test.total_occurrences(), 2)

    def test_EventsCalculations_init_defaults_include_zeroes_True(self):
        test = ti.EventsCalculations(AdditiveEvents({-1: 5, 1: 5}))
        self.assertTrue(test.include_zeroes)

    def test_EventsCalculations_init_set_include_zeroes_False(self):
        test = ti.EventsCalculations(AdditiveEvents({-1: 5, 1: 5}), False)
        self.assertFalse(test.include_zeroes)

    def test_EventsCalculations_mean_normal_case(self):
        test = ti.EventsCalculations(AdditiveEvents({-1: 5, 1: 5}))
        self.assertEqual(test.mean(), 0)

    def test_EventsCalculations_mean_with_non_uniform_events(self):
        test = ti.EventsCalculations(AdditiveEvents({1: 2, 2: 5}))
        mean = (2 + 10) / float(2 + 5)
        self.assertEqual(test.mean(), mean)

    def test_EventsCalculations_mean_with_large_number_events(self):
        test = ti.EventsCalculations(AdditiveEvents({1: 2 * 10**1000, 2: 2 * 10**1000}))
        self.assertEqual(test.mean(), 1.5)

    def test_EventsCalculations_stddev_low_occurrences(self):
        low_freq = ti.EventsCalculations(AdditiveEvents({2: 1, -2: 1, 1: 1, -1: 1}))
        self.assertEqual(low_freq.stddev(), round((10 / 4.0) ** 0.5, 4))

    def test_EventsCalculations_stddev_low_occurrences_change_decimal_place_value(self):
        low_freq = ti.EventsCalculations(AdditiveEvents({2: 1, -2: 1, 1: 1, -1: 1}))
        self.assertEqual(low_freq.stddev(decimal_place=10), round((10 / 4.0) ** 0.5, 10))

    def test_EventsCalculations_stddev_middle_high_occurrences(self):
        high_freq = ti.EventsCalculations(
            AdditiveEvents({2: 10**50, -2: 10**50, 1: 10**50, -1: 10**50})
        )
        self.assertEqual(high_freq.stddev(), round((10 / 4.0) ** 0.5, 4))

    def test_EventsCalculations_stddev_middle_high_occurrences_change_decimal_place_value(self):
        high_freq = ti.EventsCalculations(
            AdditiveEvents({2: 10**50, -2: 10**50, 1: 10**50, -1: 10**50})
        )
        self.assertEqual(high_freq.stddev(decimal_place=10), round(2.5**0.5, 10))

    def test_EventsCalculations_stddev_very_high_occurrences(self):
        high_freq = ti.EventsCalculations(
            AdditiveEvents({2: 10**500, -2: 10**500, 1: 10**500, -1: 10**500})
        )
        self.assertEqual(high_freq.stddev(), round((10 / 4.0) ** 0.5, 4))

    def test_EventsCalculations_stddev_very_high_occurrences_change_decimal_place_value(self):
        high_freq = ti.EventsCalculations(
            AdditiveEvents({2: 10**500, -2: 10**500, 1: 10**500, -1: 10**500})
        )
        self.assertEqual(high_freq.stddev(decimal_place=10), round(2.5**0.5, 10))

    def test_EventsCalculations_full_table_string_include_zeroes_true(self):
        calculator = ti.EventsCalculations(AdditiveEvents({1: 1, 3: 1}), include_zeroes=True)
        self.assertEqual(calculator.full_table_string(), "1: 1\n2: 0\n3: 1\n")

    def test_EventsCalculations_full_table_string_include_zeroes_False(self):
        calculator = ti.EventsCalculations(AdditiveEvents({1: 1, 3: 1}), include_zeroes=False)
        self.assertEqual(calculator.full_table_string(), "1: 1\n3: 1\n")

    def test_EventsCalculations_full_table_string_right_justifies_to_pos_number_is_max_len(self):
        events = AdditiveEvents({1: 10, 10: 200, 1000: 3000})
        calculator = ti.EventsCalculations(events, include_zeroes=False)
        self.assertEqual(calculator.full_table_string(), "   1: 10\n  10: 200\n1000: 3,000\n")

    def test_EventsCalculations_full_table_string_right_justifies_to_neg_number_is_max_len(self):
        events = AdditiveEvents({-1000: 2, 1: 10, 10: 200, 1000: 3000})
        calculator = ti.EventsCalculations(events, include_zeroes=False)
        self.assertEqual(
            calculator.full_table_string(), "-1000: 2\n    1: 10\n   10: 200\n 1000: 3,000\n"
        )

    def test_EventsCalculations_full_table_string_edge_case(self):
        events = AdditiveEvents({0: 1})
        calculator = ti.EventsCalculations(events)
        self.assertEqual(calculator.full_table_string(), "0: 1\n")

    def test_EventsCalculations_full_table_string_uses_NumberFormatter_on_occurrences_only(self):
        events = AdditiveEvents({10000: 10**1000})
        calculator = ti.EventsCalculations(events)
        self.assertEqual(calculator.full_table_string(), "10000: 1.000e+1000\n")

    def test_EventsCalculations_full_table_string_shown_digits_lt_one(self):
        events = AdditiveEvents({10000: 10**1000})
        calculator = ti.EventsCalculations(events)
        self.assertEqual(calculator.full_table_string(shown_digits=-5), "10000: 1e+1000\n")

    def test_EventsCalculations_full_table_string_shown_digits_lt_four(self):
        events = AdditiveEvents({10000: 10**1000})
        calculator = ti.EventsCalculations(events)
        self.assertEqual(calculator.full_table_string(shown_digits=2), "10000: 1.0e+1000\n")

    def test_EventsCalculations_full_table_string_show_digits_gt_four(self):
        events = AdditiveEvents({10000: 10**1000})
        calculator = ti.EventsCalculations(events)
        self.assertEqual(calculator.full_table_string(shown_digits=6), "10000: 1.00000e+1000\n")

    def test_EventsCalculations_full_table_string_max_power_for_commaed(self):
        events = AdditiveEvents({1: 9, 2: 99999, 3: 100000, 4: 999999})
        calculator = ti.EventsCalculations(events)
        expected = "1: 9\n2: 99,999\n3: 1.000e+5\n4: 1.000e+6\n"
        self.assertEqual(calculator.full_table_string(max_power_for_commaed=4), expected)

    def test_EventsCalculations_full_table_string_max_power_for_commaed_zero(self):
        events = AdditiveEvents({1: 1, 2: 10, 3: 100})
        calculator = ti.EventsCalculations(events)
        expected = "1: 1\n2: 1.000e+1\n3: 1.000e+2\n"
        self.assertEqual(calculator.full_table_string(max_power_for_commaed=0), expected)

    def test_EventsCalculations_full_table_string_max_power_for_commaed_neg_one(self):
        events = AdditiveEvents({1: 1, 2: 10, 3: 100})
        calculator = ti.EventsCalculations(events)
        expected = "1: 1.000e+0\n2: 1.000e+1\n3: 1.000e+2\n"
        self.assertEqual(calculator.full_table_string(max_power_for_commaed=-1), expected)

    def test_EventsCalculations_full_table_string_max_power_for_commaed_neg_many(self):
        events = AdditiveEvents({1: 1, 2: 10, 3: 100})
        calculator = ti.EventsCalculations(events)
        expected = "1: 1.000e+0\n2: 1.000e+1\n3: 1.000e+2\n"
        self.assertEqual(calculator.full_table_string(max_power_for_commaed=-10), expected)

    def test_EventsCalculations_full_table_string_max_power_for_commaed_high(self):
        events = AdditiveEvents({1: 10**10, 2: 10**11})
        calculator = ti.EventsCalculations(events)
        expected = "1: 10,000,000,000\n2: 1.000e+11\n"
        self.assertEqual(calculator.full_table_string(max_power_for_commaed=10), expected)

    def test_get_fast_pct_number_zero(self):
        self.assertEqual(ti.get_fast_pct_number(0, 100), 0)

    def test_get_fast_pct_number_small(self):
        self.assertEqual(ti.get_fast_pct_number(10, 100), 10.0)

    def test_get_fast_pct_number_small_denominator_big_numerator(self):
        self.assertEqual(ti.get_fast_pct_number(10, 10**500), 0)

    def test_get_fast_pct_number_big_denominator_big_numerator(self):
        self.assertEqual(ti.get_fast_pct_number(10**499, 10**500), 10.0)

    def test_get_fast_pct_still_pretty_good(self):
        self.assertAlmostEqual(ti.get_fast_pct_number(4, 7), 400.0 / 7.0, places=10)
        self.assertAlmostEqual(
            ti.get_fast_pct_number(4 * 10**500, 7 * 10**500), 400.0 / 7.0, places=10
        )
        self.assertNotAlmostEqual(ti.get_fast_pct_number(4, 7), 400.0 / 7.0, places=15)
        self.assertNotAlmostEqual(
            ti.get_fast_pct_number(4 * 10**500, 7 * 10**500), 400.0 / 7.0, places=15
        )

    def test_get_exact_pct_number_zero(self):
        self.assertEqual(ti.get_exact_pct_number(0, 100), 0)

    def test_get_exact_pct_number_small(self):
        self.assertEqual(ti.get_exact_pct_number(10, 100), 10.0)

    def test_get_exact_pct_number_small_denominator_big_numerator(self):
        self.assertEqual(ti.get_exact_pct_number(10, 10**500), 0)

    def test_get_exact_pct_number_big_denominator_big_numerator(self):
        self.assertEqual(ti.get_exact_pct_number(10**499, 10**500), 10.0)

    def test_get_exact_pct_is_exact(self):
        self.assertEqual(ti.get_exact_pct_number(4, 7), 400.0 / 7.0)
        self.assertEqual(ti.get_exact_pct_number(4 * 10**500, 7 * 10**500), 400.0 / 7.0)

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
        self.assertAlmostEqual(three_sevenths[1], 300.0 / 7.0, places=10)
        self.assertAlmostEqual(four_sevenths[1], 400.0 / 7.0, places=10)

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
        self.assertAlmostEqual(three_sevenths, 300.0 / 7.0, places=10)
        self.assertAlmostEqual(four_sevenths, 400.0 / 7.0, places=10)

    def test_EventsCalculations_percentage_points_exact(self):
        events = AdditiveEvents({1: 1, 3: 3})
        calculator = ti.EventsCalculations(events)
        self.assertEqual(calculator.percentage_points_exact(), [(1, 25.0), (2, 0.0), (3, 75.0)])

    def test_EventsCalculations_percentage_points_exact_include_zeroes_is_false(self):
        events = AdditiveEvents({1: 1, 3: 3})
        calculator = ti.EventsCalculations(events, False)
        self.assertEqual(calculator.percentage_points_exact(), [(1, 25.0), (3, 75.0)])

    def test_EventsCalculations_percentage_points_exact_is_exact(self):
        events = AdditiveEvents({1: 3, 3: 4})
        calculator = ti.EventsCalculations(events, False)
        three_sevenths, four_sevenths = calculator.percentage_points_exact()
        self.assertAlmostEqual(three_sevenths[1], 300.0 / 7.0, places=10)
        self.assertAlmostEqual(four_sevenths[1], 400.0 / 7.0, places=10)

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
        self.assertEqual(three_sevenths, 300.0 / 7.0)
        self.assertEqual(four_sevenths, 400.0 / 7.0)

    def test_EventsCalculations_log10_points_include_zeroes_is_false(self):
        events = AdditiveEvents({1: 10, 3: 100})
        calculator = ti.EventsCalculations(events, False)
        self.assertEqual(calculator.log10_points(), [(1, 1.0), (3, 2.0)])

    def test_EventsCalculations_log10_points_include_zeroes_is_true(self):
        events = AdditiveEvents({1: 10, 3: 100})
        calculator = ti.EventsCalculations(events)
        self.assertEqual(calculator.log10_points(), [(1, 1.0), (2, -100.0), (3, 2.0)])

    def test_EventsCalculations_log10_points_set_log10_of_zero_value(self):
        events = AdditiveEvents({1: 10, 3: 100})
        calculator = ti.EventsCalculations(events)
        self.assertEqual(calculator.log10_points(-3.0), [(1, 1.0), (2, -3.0), (3, 2.0)])

    def test_EventsCalculations_log10_axes_include_zeroes_is_false(self):
        events = AdditiveEvents({1: 10, 3: 100})
        calculator = ti.EventsCalculations(events, False)
        self.assertEqual(calculator.log10_axes(), [(1, 3), (1.0, 2.0)])

    def test_EventsCalculations_log10_axes_include_zeroes_is_true(self):
        events = AdditiveEvents({1: 10, 3: 100})
        calculator = ti.EventsCalculations(events)
        self.assertEqual(calculator.log10_axes(), [(1, 2, 3), (1.0, -100.0, 2.0)])

    def test_EventsCalculations_log10_axes_set_log10_of_zero_value(self):
        events = AdditiveEvents({1: 10, 3: 100})
        calculator = ti.EventsCalculations(events)
        self.assertEqual(calculator.log10_axes(-3.0), [(1, 2, 3), (1.0, -3.0, 2.0)])

    def test_EventsCalculations_stats_strings_values_not_in_events(self):
        calculator = ti.EventsCalculations(AdditiveEvents({1: 1}))
        expected = ("2", "0", "1", "Infinity", "0")
        self.assertEqual(calculator.stats_strings([2]), expected)

    def test_EventsCalculations_stats_strings_does_not_repeat_values(self):
        calculator = ti.EventsCalculations(AdditiveEvents({1: 1}))
        expected = ("1", "1", "1", "1.000", "100.0")
        self.assertEqual(calculator.stats_strings([1, 1]), expected)

    def test_EventsCalculations_stats_strings_includes_values_not_in_events(self):
        calculator = ti.EventsCalculations(AdditiveEvents({1: 1, 2: 1}))
        expected = ("0-1", "1", "2", "2.000", "50.00")
        self.assertEqual(calculator.stats_strings([0, 1]), expected)

    def test_EventsCalculations_stats_strings_works_for_large_values(self):
        calculator = ti.EventsCalculations(AdditiveEvents({1: 10**1000, 2: (10**1002 - 10**1000)}))
        expected = ("1", "1.000e+1000", "1.000e+1002", "100.0", "1.000")
        self.assertEqual(calculator.stats_strings([1]), expected)

    def test_EventsCalculations_stats_strings_pct_less_than_zero(self):
        calculator = ti.EventsCalculations(AdditiveEvents({1: 1, 2: 9999}))
        expected = ("1", "1", "10,000", "10,000", "0.01000")
        self.assertEqual(calculator.stats_strings([1]), expected)

    def test_EventsCalculations_stats_strings_pct_much_less_than_zero(self):
        calculator = ti.EventsCalculations(AdditiveEvents({1: 1, 2: 10**2000}))
        expected = ("1", "1", "1.000e+2000", "1.000e+2000", "1.000e-1998")
        self.assertEqual(calculator.stats_strings([1]), expected)

    def test_EventsCalculations_stats_strings_digit_value_below_min(self):
        calculator = ti.EventsCalculations(AdditiveEvents({1: 1, 2: 10**2000}))
        expected = ("1", "1", "1e+2000", "1e+2000", "1e-1998")
        self.assertEqual(calculator.stats_strings([1], shown_digits=-5), expected)

    def test_EventsCalculations_stats_strings_digit_value_below_four(self):
        calculator = ti.EventsCalculations(AdditiveEvents({1: 1, 2: 10**2000}))
        expected = ("1", "1", "1.00e+2000", "1.00e+2000", "1.00e-1998")
        self.assertEqual(calculator.stats_strings([1], shown_digits=3), expected)

    def test_EventsCalculations_stats_strings_digit_value_above_four(self):
        calculator = ti.EventsCalculations(AdditiveEvents({1: 1, 2: 10**2000}))
        expected = ("1", "1", "1.00000e+2000", "1.00000e+2000", "1.00000e-1998")
        self.assertEqual(calculator.stats_strings([1], shown_digits=6), expected)

    def test_EventsCalculations_stats_strings_max_power_for_commaed(self):
        calculator = ti.EventsCalculations(AdditiveEvents({1: 1, 2: 10**9}))
        expected = ("1", "1", "1,000,000,001", "1,000,000,001", "1.000e-7")
        self.assertEqual(calculator.stats_strings([1], max_power_for_commaed=9), expected)

    def test_EventsCalculations_stats_strings_max_power_for_commaed_rounding(self):
        calculator = ti.EventsCalculations(AdditiveEvents({1: 2, 2: 199986}))
        expected = ("1", "2", "2.000e+5", "99,994", "0.001000")
        self.assertEqual(calculator.stats_strings([1], max_power_for_commaed=4), expected)

        # once the first four digits round up (shown_digits defaults to 4), it switches to scientific notation.
        calculator = ti.EventsCalculations(AdditiveEvents({1: 2, 2: 199989}))
        expected = ("1", "2", "2.000e+5", "1.000e+5", "0.001000")
        self.assertEqual(calculator.stats_strings([1], max_power_for_commaed=4), expected)

    def test_EventsCalculations_stats_strings_max_power_for_commaed_at_zero(self):
        calculator = ti.EventsCalculations(AdditiveEvents({1: 1, 2: 1}))
        expected = (
            "1",
            "1",
            "2",
            "2.000",
            "5.000e+1",
        )  # The '2' is from an int. The '2.000' is from a float.
        self.assertEqual(calculator.stats_strings([1], max_power_for_commaed=0), expected)

    def test_EventsCalculations_stats_strings_max_power_for_commaed_at_neg_one(self):
        calculator = ti.EventsCalculations(AdditiveEvents({1: 1, 2: 1}))
        expected = ("1", "1.000e+0", "2.000e+0", "2.000e+0", "5.000e+1")
        self.assertEqual(calculator.stats_strings([1], max_power_for_commaed=-1), expected)

    def test_EventsCalculations_stats_strings_max_power_for_commaed_at_high_neg(self):
        calculator = ti.EventsCalculations(AdditiveEvents({1: 1, 2: 1}))
        expected = ("1", "1.000e+0", "2.000e+0", "2.000e+0", "5.000e+1")
        self.assertEqual(calculator.stats_strings([1], max_power_for_commaed=-100), expected)

    def test_EventsCalculations_stats_strings_min_power_for_fixed_pt(self):
        calculator = ti.EventsCalculations(AdditiveEvents({1: 1, 2: 10**6}))
        expected = ("1", "1", "1,000,001", "1,000,001", "0.0001000")
        self.assertEqual(calculator.stats_strings([1], min_power_for_fixed_pt=-4), expected)

        calculator = ti.EventsCalculations(AdditiveEvents({1: 1, 2: 10**7}))
        expected = ("1", "1", "1.000e+7", "1.000e+7", "1.000e-5")
        self.assertEqual(calculator.stats_strings([1], min_power_for_fixed_pt=-4), expected)

    def test_EventsCalculations_stats_strings_min_power_for_fixed_pt_rounding(self):
        calculator = ti.EventsCalculations(AdditiveEvents({1: 999, 2: 99999999}))
        expected = ("1", "999", "1.000e+8", "100,101", "0.0009990")
        self.assertEqual(calculator.stats_strings([1], min_power_for_fixed_pt=-4), expected)

        calculator = ti.EventsCalculations(AdditiveEvents({1: 999, 2: 99999999}))
        expected = ("1", "999", "1.0e+8", "100,101", "0.0010")
        self.assertEqual(
            calculator.stats_strings([1], min_power_for_fixed_pt=-4, shown_digits=2), expected
        )

    def test_EventsCalculations_stats_strings_min_power_for_fixed_pt_at_zero(self):
        calculator = ti.EventsCalculations(AdditiveEvents({1: 1, 2: 499}))
        expected = ("1", "1", "500", "500.0", "2.000e-1")
        self.assertEqual(calculator.stats_strings([1], min_power_for_fixed_pt=0), expected)

    def test_EventsCalculations_stats_strings_min_power_for_fixed_pt_positive_number(self):
        calculator = ti.EventsCalculations(AdditiveEvents({1: 1, 2: 499}))
        expected = ("1", "1", "500", "500.0", "2.000e-1")
        self.assertEqual(calculator.stats_strings([1], min_power_for_fixed_pt=10), expected)

    def test_EventsCalculations_stats_strings_named_tuple_values(self):
        calculator = ti.EventsCalculations(AdditiveEvents({1: 2, 2: 10**2000}))
        test_result = calculator.stats_strings([1])
        query_values = "1"
        query_occurrences = "2"
        total_occurrences = "1.000e+2000"
        one_in_chance = "5.000e+1999"
        pct_chance = "2.000e-1998"

        self.assertIsInstance(test_result, ti.StatsStrings)

        self.assertEqual(test_result.query_values, query_values)
        self.assertEqual(test_result.query_occurrences, query_occurrences)
        self.assertEqual(test_result.total_occurrences, total_occurrences)
        self.assertEqual(test_result.one_in_chance, one_in_chance)
        self.assertEqual(test_result.pct_chance, pct_chance)

        self.assertEqual(test_result[0], query_values)
        self.assertEqual(test_result[1], query_occurrences)
        self.assertEqual(test_result[2], total_occurrences)
        self.assertEqual(test_result[3], one_in_chance)
        self.assertEqual(test_result[4], pct_chance)

    """
    note: the following are wrapper functions. These tests simply confirm that the presets work.
    For full test see above and (for format_number) test_numberformatter.py
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
        self.assertEqual(
            ti.percentage_points(events, include_zeroes=True), [(1, 50.0), (2, 0), (3, 50.0)]
        )

    def test_percentage_points_zeros_false(self):
        events = AdditiveEvents({1: 1, 3: 1})
        self.assertEqual(ti.percentage_points(events, include_zeroes=False), [(1, 50.0), (3, 50.0)])

    def test_percentage_axes_zeros_true(self):
        events = AdditiveEvents({1: 1, 3: 1})
        self.assertEqual(
            ti.percentage_axes(events, include_zeroes=True), [(1, 2, 3), (50.0, 0, 50.0)]
        )

    def test_percentage_axes_zeros_false(self):
        events = AdditiveEvents({1: 1, 3: 1})
        self.assertEqual(ti.percentage_axes(events, include_zeroes=False), [(1, 3), (50.0, 50.0)])

    def test_stats(self):
        events = AdditiveEvents({1: 1})
        self.assertEqual(ti.stats(events, [1]), ("1", "1", "1", "1.000", "100.0"))

    def test_stats_can_access_shown_digits(self):
        events = AdditiveEvents({1: 1})
        self.assertEqual(ti.stats(events, [1], shown_digits=5), ("1", "1", "1", "1.0000", "100.00"))

    def test_stats_can_access_min_power_for_fixed_pt(self):
        events = AdditiveEvents({1: 1, 2: 499})
        expected = ("1", "1", "500", "500.0", "2.000e-1")
        self.assertEqual(ti.stats(events, [1], min_power_for_fixed_pt=0), expected)

    def test_stats_can_access_max_power_for_commaed(self):
        events = AdditiveEvents({1: 1, 2: 1})
        expected = ("1", "1", "2", "2.000", "5.000e+1")
        self.assertEqual(ti.stats(events, [1], max_power_for_commaed=0), expected)

    def test_full_table_string_include_zeroes_true(self):
        events = AdditiveEvents({1: 1, 3: 1})
        self.assertEqual(ti.full_table_string(events, True), "1: 1\n2: 0\n3: 1\n")

    def test_full_table_string_include_zeroes_false(self):
        events = AdditiveEvents({1: 1, 3: 1})
        self.assertEqual(ti.full_table_string(events, False), "1: 1\n3: 1\n")

    def test_full_table_string_can_access_shown_digits(self):
        events = AdditiveEvents({1: 10**100})
        self.assertEqual(ti.full_table_string(events, False, shown_digits=5), "1: 1.0000e+100\n")

    def test_full_table_string_can_access_max_power_for_commaed(self):
        events = AdditiveEvents({1: 10})
        self.assertEqual(
            ti.full_table_string(events, False, max_power_for_commaed=0), "1: 1.000e+1\n"
        )


if __name__ == "__main__":
    unittest.main()
