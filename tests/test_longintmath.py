# pylint: disable=missing-docstring, invalid-name, too-many-public-methods
'''tests for the longintmath.py module'''
from __future__ import absolute_import

import unittest
import dicetables.longintmath as lim


FLOAT_BIG = 1e+300
FLOAT_SMALL = 1e+100
LONG_BIG = 10**1000


class TestLongIntMathFunctionsDivTimesPow(unittest.TestCase):

    def test_long_int_div_returns_zero_when_answer_power_below_neg_300ish(self):
        self.assertEqual(lim.long_int_div(FLOAT_BIG, LONG_BIG), 0)

    def test_long_int_div_long_long_makes_float(self):
        result = lim.long_int_div(10**300 * LONG_BIG, LONG_BIG)
        self.assertAlmostEqual(result, 10**300, delta=10**290)
        self.assertIsInstance(result, float)

    def test_long_int_div_long_long_makes_float_with_negative_num(self):
        result = lim.long_int_div(-10**300 * LONG_BIG, LONG_BIG)
        self.assertAlmostEqual(result, -10**300, delta=10**290)
        self.assertIsInstance(result, float)

    def test_long_int_div_float_float_makes_long(self):
        result = lim.long_int_div(FLOAT_BIG, 1 / FLOAT_SMALL)
        self.assertAlmostEqual(result, 10**400, delta=10**390)

    def test_long_int_div_float_float_makes_long_with_negative_num(self):
        result = lim.long_int_div(FLOAT_BIG, -1 / FLOAT_SMALL)
        self.assertAlmostEqual(result, -10**400, delta=10**390)

    def test_long_int_div_long_long_makes_negative_power_float(self):
        result = lim.long_int_div(LONG_BIG, LONG_BIG * 10**200)
        self.assertAlmostEqual(result, 10**-200, delta=10**-210)

    def test_long_int_times_makes_large_value(self):
        result = lim.long_int_times(LONG_BIG, FLOAT_BIG)
        self.assertAlmostEqual(result, 10**1300, delta=10**1290)

    def test_long_int_times_makes_between_one_and_zero(self):
        result = lim.long_int_times(FLOAT_SMALL, 1 / FLOAT_BIG)
        self.assertAlmostEqual(result, 10**-200, delta=10**-210)

    def test_long_int_times_makes_negative_number(self):
        result = lim.long_int_times(FLOAT_SMALL, -FLOAT_BIG)
        self.assertAlmostEqual(result, -10**400, delta=10**390)

    def test_long_int_pow_makes_one(self):
        result = lim.long_int_pow(LONG_BIG, 0)
        self.assertEqual(result, 1)

    def test_long_int_pow_makes_zero(self):
        result = lim.long_int_pow(LONG_BIG, -1)
        self.assertEqual(result, 0)

    def test_long_pow_makes_between_one_and_zero(self):
        result = lim.long_int_pow(FLOAT_SMALL, -2)
        self.assertAlmostEqual(result, 1e-200, delta=10**-210)

    def test_long_pow_with_float_power(self):
        result = lim.long_int_pow(LONG_BIG, 2.5)
        self.assertAlmostEqual(result, 10**2500, delta=10**2490)


class TestLongIntTable(unittest.TestCase):
    def setUp(self):
        self.identity_a = lim.AdditiveEvents({0:1})
        self.identity_b = lim.AdditiveEvents({0:1})

    def tearDown(self):
        del self.identity_a
        del self.identity_b

    def assert_my_regex(self, error_type, regex, func, *args):
        with self.assertRaises(error_type) as cm:
            func(*args)
        error_msg = str(cm.exception)
        self.assertEqual(error_msg, regex)

    def test_assert_my_regex(self):
        self.assert_my_regex(ValueError, "invalid literal for int() with base 10: 'a'", int, 'a')

    def test_verify_times_pass(self):
        self.assertIsNone(lim.verify_times(10))

    def test_verify_times_not_int(self):
        self.assert_my_regex(ValueError, 'times must be a positive int', lim.verify_times, 1.0)

    def test_verify_times_negative(self):
        self.assert_my_regex(ValueError, 'times must be a positive int', lim.verify_times, -1)

    def test_check_tuple_list_and_raise_error_pass(self):
        self.assertIsNone(lim.check_tuple_list_and_raise_error([(1, 1), (-1, 2)]))

    def test_check_tuple_list_and_raise_error_empty(self):
        self.assert_my_regex(ValueError, 'events may not be empty. a good alternative is the identity - [(0, 1)].',
                             lim.check_tuple_list_and_raise_error, [])

    def test_check_tuple_list_and_raise_error_zero_occurrences(self):
        self.assert_my_regex(ValueError, 'events may not be empty. a good alternative is the identity - [(0, 1)].',
                             lim.check_tuple_list_and_raise_error, [(1, 0), (2, 0)])

    def test_check_tuple_list_and_raise_error_negative_occurrences(self):
        self.assert_my_regex(ValueError, 'events may not occur negative times.',
                             lim.check_tuple_list_and_raise_error, [(1, 0), (2, -1)])

    def test_check_tuple_list_and_raise_error_non_int_occurrences(self):
        self.assert_my_regex(ValueError, 'all values must be ints',
                             lim.check_tuple_list_and_raise_error, [(1, 1.0)])

    def test_check_tuple_list_and_raise_error_non_int_event(self):
        self.assert_my_regex(ValueError, 'all values must be ints',
                             lim.check_tuple_list_and_raise_error, [(1.0, 1)])

    def test_check_dictionary_and_raise_errors_catches_error_and_formats(self):
        self.assert_my_regex(ValueError, 'events may not be empty. a good alternative is the identity - {0: 1}.',
                             lim.check_dictionary_and_raise_errors, {1: 0})
        self.assert_my_regex(ValueError, 'all values must be ints',
                             lim.check_dictionary_and_raise_errors, {1: 1.0})

    def test_verify_and_prep_tuple_list_raises_error(self):
        self.assert_my_regex(ValueError, 'all values must be ints',
                             lim.verify_and_prep_tuple_list, [(1.0, 1)])
        self.assert_my_regex(ValueError, 'events may not be empty. a good alternative is the identity - [(0, 1)].',
                             lim.verify_and_prep_tuple_list, [(1, 0), (2, 0)])

    def test_verify_and_prep_tuple_list_sorts(self):
        self.assertEqual(lim.verify_and_prep_tuple_list([(3, 4), (1, 2)]), [(1, 2), (3, 4)])

    def test_verify_and_prep_tuple_list_removes_zero_occurrences(self):
        self.assertEqual(lim.verify_and_prep_tuple_list([(-1, 0), (0, 1), (1, 0), (2, 1), (3, 0)]),
                         [(0, 1), (2, 1)])

    def test_get_occurrences_to_events_ratio(self):
        self.assertEqual(lim.get_occurrences_to_events_ratio([(1, 2), (3, 4)]), 6.0 / 2.0)

    def test_get_event_range_to_events_ratio(self):
        self.assertEqual(lim.get_event_range_to_events_ratio([(1, 2), (3, 4)]), 3.0/2.0)

    def test_init_empty_table_raises_error(self):
        error_msg = 'events may not be empty. a good alternative is the identity - {0: 1}.'
        self.assert_my_regex(ValueError, error_msg, lim.AdditiveEvents, {})

    def test_init_zero_values_dict_raises_error(self):
        error_msg = 'events may not be empty. a good alternative is the identity - {0: 1}.'
        self.assert_my_regex(ValueError, error_msg, lim.AdditiveEvents, {1: 0, 2: 0})

    def test_values_sorts_and_removes_zeros(self):
        test_table = lim.AdditiveEvents({0:1, 1:0})
        self.assertEqual(test_table.event_keys(), [0])

    @unittest.skip("line 96 fixme")
    def test_values_returns_empty_list_for_empty_table(self):
        empty = lim.AdditiveEvents({})
        self.assertEqual(empty.event_keys(), [])

    def test_values_min_returns_min_value(self):
        min_val_neg_one = lim.AdditiveEvents({1:1, -1:1})
        self.assertEqual(min_val_neg_one.event_keys_min(), -1)

    def test_values_max_returns_max_value(self):
        max_val_neg_one = lim.AdditiveEvents({-1:1, -2:1})
        self.assertEqual(max_val_neg_one.event_keys_max(), -1)

    def test_values_range_returns_minmax(self):
        zero_to_two = lim.AdditiveEvents({0:2, 1:1, 2:5, 4:0})
        self.assertEqual(zero_to_two.event_keys_range(), (0, 2))

    @unittest.skip("line 113 fixme")
    def test_values_min_returns_none_for_empty_table(self):
        empty = lim.AdditiveEvents({})
        self.assertIsNone(empty.event_keys_min())

    @unittest.skip("line 117 fixme")
    def test_values_max_returns_none_for_empty_table(self):
        empty = lim.AdditiveEvents({})
        self.assertIsNone(empty.event_keys_max())

    @unittest.skip("line 122 fixme")
    def test_values_range_returns_none_none_for_empty_table(self):
        empty = lim.AdditiveEvents({})
        self.assertEqual(empty.event_keys_range(), (None, None))

    def test_frequency_returns_value_frequency_as_tuple(self):
        zero_three = lim.AdditiveEvents({0:3})
        self.assertEqual(zero_three.get_event(0), (0, 3))

    def test_frequency_returns_zero_frequency_for_empty_value(self):
        zero_three = lim.AdditiveEvents({0:3})
        self.assertEqual(zero_three.get_event(100), (100, 0))

    def test_frequency_range_returns_correct_tuple_list(self):
        table = lim.AdditiveEvents({1:1, 2:2})
        self.assertEqual(table.get_event_range(0, 4),
                         [(0, 0), (1, 1), (2, 2), (3, 0)])

    def test_frequency_all_returns_for_normal_case(self):
        table = lim.AdditiveEvents({1:1, 2:2})
        self.assertEqual(table.get_event_all(),
                         [(1, 1), (2, 2)])

    @unittest.skip("line 140 fixme")
    def test_frequency_all_return_empty_for_empty_table(self):
        empty = lim.AdditiveEvents({})
        self.assertEqual(empty.get_event_all(), [])

    def test_frequency_all_sorts_and_does_not_return_zero_frequencies(self):
        table = lim.AdditiveEvents({1:2, 2:0, -1:2})
        self.assertEqual(table.get_event_all(), [(-1, 2), (1, 2)])

    def test_frequency_highest_returns_either_tuple_with_highest(self):
        table = lim.AdditiveEvents({-1:5, 0:1, 2:5})
        self.assertIn(table.get_event_highest(), [(-1, 5), (2, 5)])

    def test_frequency_highest_returns_only_the_highest(self):
        table = lim.AdditiveEvents({-1:5, 0:1, 2:3})
        self.assertEqual(table.get_event_highest(), (-1, 5))

    @unittest.skip("line 157 fixme")
    def test_frequency_highest_handles_empty_table(self):
        empty = lim.AdditiveEvents({})
        self.assertEqual(empty.get_event_highest(), (None, 0))

    @unittest.skip("line 162 fixme")
    def test_total_frequency_is_zero_for_empty_table(self):
        empty = lim.AdditiveEvents({})
        self.assertEqual(empty.get_total_event_occurrences(), 0)

    def test_total_frequency_returns_correct_value_table(self):
        table = lim.AdditiveEvents({1:2, 3:4})
        self.assertEqual(table.get_total_event_occurrences(), 2 + 4)

    def test_string_returns_min_to_max(self):
        table = lim.AdditiveEvents({-1:1, 2:1, 5:1})
        self.assertEqual(str(table), 'table from -1 to 5')

    def test_string_is_in_order_and_ignores_high_zero_values(self):
        table = lim.AdditiveEvents({2:0, 1:1, -1:1, -2:0})
        self.assertEqual(str(table), 'table from -1 to 1')

    @unittest.skip("line 179 fixme")
    def test_string_of_empty_table(self):
        empty = lim.AdditiveEvents({})
        self.assertEqual(str(empty), 'table from None to None')

    def test_mean_normal_case(self):
        table = lim.AdditiveEvents({-1:5, 1:5})
        self.assertEqual(table.mean(), 0)

    @unittest.skip("line 188 fixme")
    def test_mean_empty_list_raises_zero_division_error(self):
        empty = lim.AdditiveEvents({})
        with self.assertRaises(ZeroDivisionError) as cm:
            empty.mean()
        self.assertEqual(cm.exception.args[0], 'there are no values in the table')

    def test_mean_with_non_uniform_table(self):
        table = lim.AdditiveEvents({1:2, 2:5})
        mean = (2 + 10) / float(2 + 5)
        self.assertEqual(table.mean(), mean)

    def test_mean_with_large_number_table(self):
        table = lim.AdditiveEvents({1: 2 * 10 ** 1000, 2: 2 * 10 ** 1000})
        self.assertEqual(table.mean(), 1.5)

    def test_stddev_for_table_with_highest_frequency_below_cutoff(self):
        low_freq = lim.AdditiveEvents({2:1, -2:1, 1:1, -1:1})
        self.assertEqual(low_freq.stddev(), round((10/4.)**0.5, 4))

    def test_stddev_for_below_cutoff_table_with_more_decimals(self):
        low_freq = lim.AdditiveEvents({2:1, -2:1, 1:1, -1:1})
        self.assertEqual(low_freq.stddev(decimal_place=10), round((10/4.)**0.5, 10))

    def test_stddev_for_table_with_highest_frequency_above_cutoff(self):
        high_freq = lim.AdditiveEvents({2: 10 ** 50, -2: 10 ** 50, 1: 10 ** 50, -1: 10 ** 50})
        self.assertEqual(high_freq.stddev(), round((10/4.)**0.5, 4))

    def test_stddev_for_above_cutoff_table_with_more_decimals(self):
        high_freq = lim.AdditiveEvents({2: 10 ** 50, -2: 10 ** 50, 1: 10 ** 50, -1: 10 ** 50})
        self.assertEqual(high_freq.stddev(decimal_place=10), round(2.5**0.5, 10))

    def test_merge_adds_old_vals_and_makes_new_vals(self):
        table = lim.AdditiveEvents({1:1, 2:1, 3:1})
        table.merge({-1:1, 0:1, 1:1, 2:1}.items())
        self.assertEqual(table.get_event_all(),
                         [(-1, 1), (0, 1), (1, 2), (2, 2), (3, 1)])

    def test_update_frequency(self):
        table = lim.AdditiveEvents({1:1, 2:2})
        table.update_frequency(2, 5)
        self.assertEqual(table.get_event(2)[1], 5)

    def test_update_frequency_when_update_value_not_in_table(self):
        table = lim.AdditiveEvents({1:1})
        table.update_frequency(2, 5)
        self.assertEqual(table.get_event(2)[1], 5)

    def test_update_value_ow(self):
        table = lim.AdditiveEvents({1:100, 2:2})
        table.update_value_ow(1, 2)
        self.assertEqual(table.get_event_all(), [(2, 100)])

    def test_update_value_add(self):
        table = lim.AdditiveEvents({1:100, 2:2})
        table.update_value_add(1, 2)
        self.assertEqual(table.get_event_all(), [(2, 102)])

    def test_add_empty_list_error(self):
        identity = lim.AdditiveEvents({0:1})
        self.assert_my_regex(ValueError, 'events may not be empty. a good alternative is the identity - [(0, 1)].',
                             identity.combine_with_new_events, 1, [(1, 0)])

    def test_add_negative_times_error(self):
        identity = lim.AdditiveEvents({0:1})
        self.assert_my_regex(ValueError, 'times must be a positive int',
                             identity.combine_with_new_events, -1, [(1, 1)])

    def test_add_negative_frequencies_error(self):
        identity = lim.AdditiveEvents({0:1})
        self.assert_my_regex(ValueError, 'events may not occur negative times.',
                             identity.combine_with_new_events, 1, [(1, -1)])

    def test_add_errors_do_not_mutate_table(self):
        identity = lim.AdditiveEvents({0:1})
        try:
            identity.combine_with_new_events(1, [(1, 0)])
        except ValueError:
            pass
        try:
            identity.combine_with_new_events(-1, [(1, 1)])
        except ValueError:
            pass
        try:
            identity.combine_with_new_events(1, [(1, -1)])
        except ValueError:
            pass
        self.assertEqual(identity.get_event_all(), [(0, 1)])

#the next two tests test that add works for the two cases for get_fastest_combine_method()
#get_fastest_combine_method() is found in the the add() method
#for details of adding ints vs tuples, see testing_add_speed.py

    def test_add_works_with_low_total_frequency_to_number_of_vals(self):
        low_ratio_tuples = [(1, 1), (2, 1)]
        self.identity_a.combine_with_new_events(1, low_ratio_tuples)
        self.assertEqual(self.identity_a.get_event_all(), low_ratio_tuples)

    def test_add_works_with_high_total_frequency_to_number_of_vals(self):
        high_ratio_tuples = [(1, 10**1000), (2, 10**1000)]
        self.identity_a.combine_with_new_events(1, high_ratio_tuples)
        self.assertEqual(self.identity_a.get_event_all(), high_ratio_tuples)

    def test_one_multiple_add_is_multiple_single_adds(self):
        tuples = [(1, 2), (3, 4)]
        self.identity_a.combine_with_new_events(1, tuples)
        self.identity_a.combine_with_new_events(1, tuples)
        self.identity_b.combine_with_new_events(2, tuples)
        self.assertEqual(self.identity_a.get_event_all(),
                         self.identity_b.get_event_all())

    def test_add_adds_correctly(self):
        tuple_list = [(2, 2), (1, 2)]
        self.identity_a.combine_with_new_events(2, tuple_list)
        self.assertEqual(self.identity_a.get_event_all(),
                         [(2, 4), (3, 8), (4, 4)])

    def test_add_works_with_long_large_number_list(self):
        tuple_list = [(x, 10**1000) for x in range(-1000, 1000)]
        self.identity_a.combine_with_new_events(1, tuple_list)
        self.assertEqual(self.identity_a.get_event_all(), tuple_list)

    def test_remove_removes_correctly(self):
        arbitrary_tuples = [(-5, 2), (0, 5), (3, 10)]
        self.identity_a.combine_with_new_events(5, arbitrary_tuples)
        self.identity_b.combine_with_new_events(10, arbitrary_tuples)
        self.identity_b.remove(5, arbitrary_tuples)
        self.assertEqual(self.identity_a.get_event_all(),
                         self.identity_b.get_event_all())

    def test_remove_works_for_large_numbers(self):
        arbitrary_tuples_large = [(-5, 10**500), (0, 5*10**700), (3, 2**1000)]

        self.identity_a.combine_with_new_events(1, arbitrary_tuples_large)
        self.identity_b.combine_with_new_events(2, arbitrary_tuples_large)
        self.identity_b.remove(1, arbitrary_tuples_large)
        self.assertEqual(self.identity_a.get_event_all(),
                         self.identity_b.get_event_all())

    def test_add_adds_same_regardless_of_order(self):
        arbitrary_a = [(1, 2), (3, 10**456)]
        arbitrary_b = [(0, 5), (-1, 2)]
        self.identity_a.combine_with_new_events(1, arbitrary_a)
        self.identity_a.combine_with_new_events(2, arbitrary_b)
        self.identity_b.combine_with_new_events(2, arbitrary_b)
        self.identity_b.combine_with_new_events(1, arbitrary_a)
        self.assertEqual(self.identity_a.get_event_all(),
                         self.identity_b.get_event_all())

    def test_remove_removes_same_regardless_of_order(self):
        arbitrary_a = [(-1, 2), (3, 5)]
        arbitrary_b = [(100, 4), (0, 9)]
        self.identity_a.combine_with_new_events(5, arbitrary_a)
        self.identity_a.combine_with_new_events(5, arbitrary_b)
        self.identity_b.combine_with_new_events(1, arbitrary_b)
        self.identity_b.combine_with_new_events(1, arbitrary_a)
        self.identity_a.remove(3, arbitrary_a)
        self.identity_a.remove(3, arbitrary_b)
        self.identity_a.remove(1, arbitrary_b)
        self.identity_a.remove(1, arbitrary_a)
        self.assertEqual(self.identity_a.get_event_all(),
                         self.identity_b.get_event_all())


if __name__ == '__main__':
    unittest.main()

