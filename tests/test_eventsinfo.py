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

    def test_EventsInformation_event_range(self):
        zero_to_two = ti.EventsInformation(AdditiveEvents({0: 2, 1: 1, 2: 5, 4: 0}))
        self.assertEqual(zero_to_two.events_range(), (0, 2))

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

    def test_EventsInformation_all_events_include_zeroes_end_zeroes(self):
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

    def test_EventsInformation_total_event_occurrences(self):
        test = ti.EventsInformation(AdditiveEvents({1: 2, 3: 4}))
        self.assertEqual(test.total_occurrences(), 2 + 4)

    def test_AdditiveEvents_mean_normal_case(self):
        test = ti.EventsInformation(AdditiveEvents({-1: 5, 1: 5}))
        self.assertEqual(test.mean(), 0)

    def test_AdditiveEvents_mean_with_non_uniform_table(self):
        test = ti.EventsInformation(AdditiveEvents({1: 2, 2: 5}))
        mean = (2 + 10) / float(2 + 5)
        self.assertEqual(test.mean(), mean)

    def test_AdditiveEvents_mean_with_large_number_table(self):
        test = ti.EventsInformation(AdditiveEvents({1: 2 * 10 ** 1000, 2: 2 * 10 ** 1000}))
        self.assertEqual(test.mean(), 1.5)

    def test_AdditiveEvents_stddev_low_occurrences(self):
        low_freq = ti.EventsInformation(AdditiveEvents({2: 1, -2: 1, 1: 1, -1: 1}))
        self.assertEqual(low_freq.stddev(), round((10 / 4.) ** 0.5, 4))

    def test_AdditiveEvents_stddev_low_occurrences_change_decimal_place_value(self):
        low_freq = ti.EventsInformation(AdditiveEvents({2: 1, -2: 1, 1: 1, -1: 1}))
        self.assertEqual(low_freq.stddev(decimal_place=10), round((10 / 4.) ** 0.5, 10))

    def test_AdditiveEvents_stddev_middle_high_occurrences(self):
        high_freq = ti.EventsInformation(AdditiveEvents({2: 10 ** 50, -2: 10 ** 50, 1: 10 ** 50, -1: 10 ** 50}))
        self.assertEqual(high_freq.stddev(), round((10 / 4.) ** 0.5, 4))

    def test_AdditiveEvents_stddev_middle_high_occurrences_change_decimal_place_value(self):
        high_freq = ti.EventsInformation(AdditiveEvents({2: 10 ** 50, -2: 10 ** 50, 1: 10 ** 50, -1: 10 ** 50}))
        self.assertEqual(high_freq.stddev(decimal_place=10), round(2.5 ** 0.5, 10))

    def test_AdditiveEvents_stddev_very_high_occurrences(self):
        high_freq = ti.EventsInformation(AdditiveEvents({2: 10 ** 500, -2: 10 ** 500, 1: 10 ** 500, -1: 10 ** 500}))
        self.assertEqual(high_freq.stddev(), round((10 / 4.) ** 0.5, 4))

    def test_AdditiveEvents_stddev_very_high_occurrences_change_decimal_place_value(self):
        high_freq = ti.EventsInformation(AdditiveEvents({2: 10 ** 500, -2: 10 ** 500, 1: 10 ** 500, -1: 10 ** 500}))
        self.assertEqual(high_freq.stddev(decimal_place=10), round(2.5 ** 0.5, 10))

    """
    note: format_number is simply a wrapper for NumberFormatter.  for full tests, see test_numberformatter.py
    """
    def test_format_number_works_as_expected(self):
        self.assertEqual(ti.format_number(123456.78), '123,457')
        self.assertEqual(ti.format_number(123456.78, digits_shown=7), '123,456.8')
        self.assertEqual(ti.format_number(123456.78, digits_shown=7, max_comma_exp=4), '1.234568e+5')
        self.assertEqual(ti.format_number(0.0000123), '1.230e-5')
        self.assertEqual(ti.format_number(0.0000123, min_fixed_pt_exp=-6), '0.00001230')
        self.assertEqual(ti.format_number(123456 * 10 ** 1000), '1.235e+1005')

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

    def test_GraphDataGenerator_init_default(self):
        test = ti.GraphDataGenerator()
        self.assertTrue(test.include_zeroes)
        self.assertTrue(test.percent)
        self.assertFalse(test.exact)

    def test_GraphDataGenerator_include_zeroes_getter_setter(self):
        test = ti.GraphDataGenerator(include_zeroes=False)
        self.assertFalse(test.include_zeroes)
        test.include_zeroes = 1
        self.assertTrue(test.include_zeroes)
        test.include_zeroes = ''
        self.assertFalse(test.include_zeroes)

    def test_GraphDataGenerator_percent_getter_setter(self):
        test = ti.GraphDataGenerator(percent=False)
        self.assertFalse(test.percent)
        test.percent = 1
        self.assertTrue(test.percent)
        test.percent = ''
        self.assertFalse(test.percent)

    def test_GraphDataGenerator_exact_getter_setter(self):
        test = ti.GraphDataGenerator(exact=True)
        self.assertTrue(test.exact)
        test.exact = ''
        self.assertFalse(test.exact)
        test.exact = 1
        self.assertTrue(test.exact)

    def test_GraphDataGenerator_get_raw_pts_adds_zeroes(self):
        table = AdditiveEvents({1: 1, 3: 1})
        self.assertEqual(ti.GraphDataGenerator().get_raw_points(table),
                         [(1, 1), (2, 0), (3, 1)])

    def test_GraphDataGenerator_get_raw_points_no_zeroes(self):
        table = AdditiveEvents({1: 1, 3: 1})
        self.assertEqual(ti.GraphDataGenerator(include_zeroes=False).get_raw_points(table),
                         [(1, 1), (3, 1)])

    def test_GraphDataGenerator_get_percent_points_not_exact(self):
        table = AdditiveEvents({1: 3, 3: 4})
        values, pct = zip(*ti.GraphDataGenerator().get_percent_points(table))
        exact_pct = (300./7., 0.0, 400./7.)
        self.assertEqual(values, (1, 2, 3))
        self.assert_list_almost_equal(pct, exact_pct, places=10)
        self.assertNotEqual(pct, exact_pct)

    def test_GraphDataGenerator_get_percent_points_exact(self):
        table = AdditiveEvents({1: 3, 3: 4})
        values, pct = zip(*ti.GraphDataGenerator(exact=True).get_percent_points(table))
        exact_pct = (300./7., 0.0, 400./7.)
        self.assertEqual(values, (1, 2, 3))
        self.assertEqual(pct, exact_pct)

    def test_GraphDataGenerator_get_points_percent(self):
        table = AdditiveEvents({1: 3, 3: 4})
        self.assertEqual(ti.GraphDataGenerator(exact=True, percent=True).get_points(table),
                         [(1, 300./7.), (2, 0), (3, 400./7.)])

    def test_GraphDataGenerator_get_points_not_percent(self):
        table = AdditiveEvents({1: 3, 3: 4})
        self.assertEqual(ti.GraphDataGenerator(exact=True, percent=False).get_points(table),
                         [(1, 3), (2, 0), (3, 4)])

    def test_GraphDataGenerator_get_axes(self):
        table = AdditiveEvents({1: 3, 3: 4})
        grapher = ti.GraphDataGenerator(exact=True, percent=False)
        self.assertEqual(grapher.get_axes(table), [(1, 2, 3), (3, 0, 4)])
        grapher.percent = True
        self.assertEqual(grapher.get_axes(table), [(1, 2, 3), (300./7., 0, 400./7.)])

    def test_graph_pts_axes(self):
        table = AdditiveEvents({1: 1, 2: 1})
        self.assertEqual(ti.graph_pts(table, axes=True), [(1, 2), (50.0, 50.0)])
        self.assertEqual(ti.graph_pts(table, axes=False), [(1, 50.0), (2, 50.0)])

    def test_graph_pts_percent(self):
        table = AdditiveEvents({1: 1, 2: 1})
        self.assertEqual(ti.graph_pts(table, percent=True), [(1, 2), (50.0, 50.0)])
        self.assertEqual(ti.graph_pts(table, percent=False), [(1, 2), (1, 1)])

    def test_graph_pts_include_zeroes(self):
        table = AdditiveEvents({1: 1, 3: 1})
        self.assertEqual(ti.graph_pts(table, include_zeroes=True), [(1, 2, 3), (50.0, 0, 50.0)])
        self.assertEqual(ti.graph_pts(table, include_zeroes=False), [(1, 3), (50.0, 50.0)])

    def test_graph_pts_exact(self):
        table = AdditiveEvents({1: 3, 2: 4})
        exact_pct = (300./7., 400./7.)
        expected_values = (1, 2)

        values, pct = ti.graph_pts(table, exact=True)
        self.assertEqual(expected_values, values)
        self.assertEqual(exact_pct, pct)

        values, pct = ti.graph_pts(table, exact=False)
        self.assertEqual(expected_values, values)
        self.assertNotEqual(exact_pct, pct)
        self.assert_list_almost_equal(exact_pct, pct)

    def test_graph_pts_overflow_for_small_numbers(self):
        table = AdditiveEvents({1: 1, 3: 1})
        self.assertEqual(ti.graph_pts_overflow(table), ([(1, 2, 3), (1, 0, 1)], '1'))

    def test_graph_pts_overflow_for_large_numbers(self):
        table = AdditiveEvents({1: 10 ** 200, 2: 1})
        self.assertEqual(ti.graph_pts_overflow(table),
                         ([(1, 2), (10 ** 200, 1)], '1'))

    def test_graph_pts_overflow_for_very_large_numbers(self):
        table = AdditiveEvents({1: 10 ** 2000, 2: 1})
        self.assertEqual(ti.graph_pts_overflow(table),
                         ([(1, 2), (10 ** 4, 0)], '1.0e+1996'))

    def test_full_table_string_include_zeroes_true(self):
        table = AdditiveEvents({1: 1, 3: 1})
        self.assertEqual(ti.full_table_string(table, include_zeroes=True),
                         '1: 1\n2: 0\n3: 1\n')

    def test_full_table_string_include_zeroes_False(self):
        table = AdditiveEvents({1: 1, 3: 1})
        self.assertEqual(ti.full_table_string(table, include_zeroes=False),
                         '1: 1\n3: 1\n')

    def test_full_table_string_right_justifies_all_values_big_max(self):
        table = AdditiveEvents({1: 10, 10: 200, 1000: 3000})
        self.assertEqual(ti.full_table_string(table, include_zeroes=False),
                         '   1: 10\n  10: 200\n1000: 3,000\n')

    def test_full_table_string_right_justifies_all_values_big_min(self):
        table = AdditiveEvents({-1000: 2, 1: 10, 10: 200, 1000: 3000})
        self.assertEqual(ti.full_table_string(table, include_zeroes=False),
                         '-1000: 2\n    1: 10\n   10: 200\n 1000: 3,000\n')

    def test_full_table_string_edge_case(self):
        table = AdditiveEvents({0: 1})
        self.assertEqual(ti.full_table_string(table), '0: 1\n')

    def test_full_table_string_uses_NumberFormatter_on_occurrences_only(self):
        table = AdditiveEvents({10000: 10**1000})
        self.assertEqual(ti.full_table_string(table), '10000: 1.000e+1000\n')

    def test_format_for_sequence_string_adds_commas(self):
        self.assertEqual(ti.format_for_sequence_str(10), '10')
        self.assertEqual(ti.format_for_sequence_str(1000000), '1,000,000')

    def test_format_for_sequence_string_negative_numbers(self):
        self.assertEqual(ti.format_for_sequence_str(-2), '(-2)')
        self.assertEqual(ti.format_for_sequence_str(-2000), '(-2,000)')

    def test_format_one_sequence_single_number(self):
        self.assertEqual(ti.format_one_sequence([1]), '1')

    def test_format_one_sequence_first_and_last_same_number(self):
        self.assertEqual(ti.format_one_sequence([1, 2, 3, 1]), '1')

    def test_format_one_sequence_first_and_last_different(self):
        self.assertEqual(ti.format_one_sequence([-1, 3, 2]), '(-1)-2')

    def test_is_gap_too_big_size_one_true(self):
        self.assertTrue(ti.is_gap_too_big([[1, 2, 3], [4, 5]], 7, 1))

    def test_is_gap_too_big_size_one_false(self):
        self.assertFalse(ti.is_gap_too_big([[1, 2, 3], [4, 5]], 5, 1))
        self.assertFalse(ti.is_gap_too_big([[1, 2, 3], [4, 5]], 6, 1))

    def test_is_gap_too_big_higher_size_true_false(self):
        self.assertTrue(ti.is_gap_too_big([[1, 2, 3], [4, 5]], 11, 5))
        self.assertTrue(ti.is_gap_too_big([[1, 2, 3], [4, 5]], 15, 5))
        self.assertFalse(ti.is_gap_too_big([[1, 2, 3], [4, 5]], 10, 5))
        self.assertFalse(ti.is_gap_too_big([[1, 2, 3], [4, 5]], 7, 5))

    def test_is_gap_too_big_size_zero_true_false(self):
        self.assertTrue(ti.is_gap_too_big([[1, 2, 3], [4, 5]], 6, 0))
        self.assertTrue(ti.is_gap_too_big([[1, 2, 3], [4, 5]], 15, 0))
        self.assertFalse(ti.is_gap_too_big([[1, 2, 3], [4, 5]], 5, 0))

    def test_split_at_gaps_larger_than_one_empty_list(self):
        self.assertEqual(ti.split_at_gaps_larger_than_one([]), [])

    def test_split_at_gaps_larger_than_one_one_element(self):
        self.assertEqual(ti.split_at_gaps_larger_than_one([1]), [[1]])

    def test_split_at_gaps_larger_than_one_same_element(self):
        self.assertEqual(ti.split_at_gaps_larger_than_one([1, 1, 1, 1]), [[1, 1, 1, 1]])

    def test_split_at_gaps_larger_than_one_not_large_gaps(self):
        self.assertEqual(ti.split_at_gaps_larger_than_one([1, 1, 2, 2, 3]), [[1, 1, 2, 2, 3]])

    def test_split_at_gaps_larger_than_one_all_large_gaps(self):
        self.assertEqual(ti.split_at_gaps_larger_than_one([1, 3, 9]), [[1], [3], [9]])

    def test_split_at_gaps_larger_than_one_mixed_case(self):
        self.assertEqual(ti.split_at_gaps_larger_than_one([1, 1, 2, 5, 6, 9]), [[1, 1, 2], [5, 6], [9]])

    def test_split_at_gaps_larger_than_one_mixed_case_negative_pos_zero(self):
        self.assertEqual(ti.split_at_gaps_larger_than_one([-2, 0, 1, 2, 5, 6, 9]), [[-2], [0, 1, 2], [5, 6], [9]])

    def test_list_to_string_returns_single_number(self):
        self.assertEqual(ti.get_string_for_sequence([1, 1, 1]), '1')

    def test_list_to_string_puts_parentheses_around_negative_numbers(self):
        self.assertEqual(ti.get_string_for_sequence([-1]), '(-1)')

    def test_list_to_string_returns_proper_output_for_a_run_of_numbers(self):
        self.assertEqual(ti.get_string_for_sequence([1, 1, 2, 3, 4, 5]), '1-5')

    def test_list_to_string_returns_values_separated_by_commas(self):
        the_list = [-5, -4, -3, -1, 0, 1, 2, 3, 5]
        self.assertEqual(ti.get_string_for_sequence(the_list), '(-5)-(-3), (-1)-3, 5')

    def test_list_to_string_returns_numbers_with_commas(self):
        the_list = [-1234567, 1234567]
        self.assertEqual(ti.get_string_for_sequence(the_list), '(-1,234,567), 1,234,567')

    def test_stats_not_in_table(self):
        result = ti.stats(AdditiveEvents({1: 1}), [2])
        expected = ('2', '0', '1', 'infinity', '0')
        self.assertEqual(result, expected)

    def test_stats_does_not_repeat_values(self):
        result = ti.stats(AdditiveEvents({1: 1}), [1, 1])
        expected = ('1', '1', '1', '1.000', '100.0')
        self.assertEqual(result, expected)

    def test_stats_includes_values_not_in_table(self):
        result = ti.stats(AdditiveEvents({1: 1, 2: 1}), [0, 1])
        expected = ('0-1', '1', '2', '2.000', '50.00')
        self.assertEqual(result, expected)

    def test_stats_works_for_large_values(self):
        result = ti.stats(AdditiveEvents({1: 10 ** 1000, 2: (10 ** 1002 - 10 ** 1000)}), [1])
        expected = ('1', '1.000e+1000', '1.000e+1002', '100.0', '1.000')
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
