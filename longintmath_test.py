# pylint: disable=missing-docstring, invalid-name, too-many-public-methods
'''tests for the longintmath.py module'''
import unittest
import longintmath as lim


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
#todo get rid of these constants
TUPLES_WITH_ZERO = [(1, 2), (2, 0), (-1, 2)]
TUPLES_WITHOUT_ZERO = [(-1, 2), (1, 2)]
TUPLES_WITH_TWO_HIGHEST = [(1, 2), (2, 1), (-1, 2)]
TUPLES_WITH_ONE_HIGHEST = [(1, 2), (2, 3), (-1, 2)]
TUPLES_FOR_STDDEV_SMALL = [(2, 1), (-2, 1), (1, 1), (-1, 1)]
TUPLES_FOR_STDDEV_LARGE = [(2, 10**1000), (-2, 10**1000),
                           (1, 10**1000), (-1, 10**1000)]
class TestLongIntTable(unittest.TestCase):
    def setUp(self):
        self.identity_a = lim.LongIntTable({0:1})
        self.identity_b = lim.LongIntTable({0:1})

        self.neg2_to_pos2_freq3 = lim.LongIntTable(dict([(x, 3) for x in
                                                         range(-2, 3)]))
        self.empty_table = lim.LongIntTable({1:0, 2:0})
    def tearDown(self):
        del self.identity_a
        del self.identity_b

        del self.neg2_to_pos2_freq3
        del self.empty_table
#todo explicit dictionary in test so not looking up stuff
    def test_values_sorts_and_removes_zeros(self):
        test_table = lim.LongIntTable(dict(TUPLES_WITH_ZERO))
        self.assertEqual(test_table.values(), [-1, 1])
#todo code empty table explicityly
    def test_values_returns_empty_list_for_empty_table(self):
        self.assertEqual(self.empty_table.values(), [])

    def test_values_min_returns_min_value(self):
        self.assertEqual(self.neg2_to_pos2_freq3.values_min(), -2)
    def test_values_max_returns_max_value(self):
        self.assertEqual(self.neg2_to_pos2_freq3.values_max(), 2)
    def test_values_range_returns_minmax(self):
        self.assertEqual(self.neg2_to_pos2_freq3.values_range(), (-2, 2))

    def test_values_min_returns_none_for_empty_table(self):
        self.assertIsNone(self.empty_table.values_min())
    def test_values_max_returns_none_for_empty_table(self):
        self.assertIsNone(self.empty_table.values_max())
    def test_values_range_returns_none_none_for_empty_table(self):
        self.assertEqual(self.empty_table.values_range(), (None, None))


    def test_frequency_returns_value_frequency_as_tuple(self):
        self.assertEqual(self.neg2_to_pos2_freq3.frequency(0), (0, 3))
    def test_frequency_returns_zero_frequency_for_empty_value(self):
        self.assertEqual(self.neg2_to_pos2_freq3.frequency(100), (100, 0))

    def test_frequency_range_returns_correct_tuple_list(self):
        self.assertEqual(self.neg2_to_pos2_freq3.frequency_range(-4, 2),
                         [(-4, 0), (-3, 0), (-2, 3), (-1, 3), (0, 3), (1, 3)])

    def test_frequency_all_returns_for_normal_case(self):
        self.assertEqual(self.neg2_to_pos2_freq3.frequency_all(),
                         [(-2, 3), (-1, 3), (0, 3), (1, 3), (2, 3)])
    def test_frequency_all_return_empty_for_empty_table(self):
        self.assertEqual(self.empty_table.frequency_all(), [])
#todo explicit tuple lists in tests
    def test_frequency_all_sorts_and_does_not_return_zero_frequencies(self):
        table = lim.LongIntTable(dict(TUPLES_WITH_ZERO))
        self.assertEqual(table.frequency_all(), [(-1, 2), (1, 2)])

    def test_frequency_highest_returns_either_tuple_with_highest(self):
        table = lim.LongIntTable(dict(TUPLES_WITH_TWO_HIGHEST))
        self.assertIn(table.frequency_highest(), TUPLES_WITHOUT_ZERO)
    def test_frequency_highest_returns_only_the_highest(self):
        table = lim.LongIntTable(dict(TUPLES_WITH_ONE_HIGHEST))
        self.assertEqual(table.frequency_highest(), (2, 3))
    def test_frequency_highest_handles_empty_table(self):
        self.assertEqual(self.empty_table.frequency_highest(), (None, 0))

    def test_total_frequency_is_zero_for_empty_table(self):
        self.assertEqual(self.empty_table.total_frequency(), 0)
    def test_total_frequency_returns_correct_value_table(self):
        self.assertEqual(self.neg2_to_pos2_freq3.total_frequency(), 5*3)


    def test_string_returns_min_to_max(self):
        self.assertEqual(str(self.neg2_to_pos2_freq3), 'table from -2 to 2')
    def test_string_is_in_order_and_ignores_high_zero_values(self):
        table = lim.LongIntTable(dict(TUPLES_WITH_ZERO))
        self.assertEqual(str(table), 'table from -1 to 1')
    def test_string_of_empty_table(self):
        self.assertEqual(str(self.empty_table), 'table from None to None')


    def test_mean_normal_case(self):
        self.assertEqual(self.neg2_to_pos2_freq3.mean(), 0)
    def test_mean_empty_list_raises_zero_division_error(self):
        self.assertRaises(ZeroDivisionError, self.empty_table.mean)
    def test_mean_with_non_uniform_table(self):
        table = lim.LongIntTable(dict(TUPLES_WITH_ONE_HIGHEST))
        mean = (-1 * 2 + 1 * 2 + 2 * 3) / float(2 + 2 + 3)
        self.assertEqual(table.mean(), mean)
    def test_mean_with_large_number_table(self):
        table = lim.LongIntTable(dict(TUPLES_FOR_STDDEV_SMALL))
        self.assertEqual(table.mean(), 0)


    def test_stddev_for_table_with_highest_frequency_below_cutoff(self):
        low_freq = lim.LongIntTable(dict(TUPLES_FOR_STDDEV_SMALL))
        self.assertEqual(low_freq.stddev(), round(2.5**0.5, 4))
    def test_stddev_for_below_cutoff_table_with_more_decimals(self):
        low_freq = lim.LongIntTable(dict(TUPLES_FOR_STDDEV_SMALL))
        self.assertEqual(low_freq.stddev(decimal_place=10), round(2.5**0.5, 10))

    def test_stddev_for_table_with_highest_frequency_above_cutoff(self):
        low_freq = lim.LongIntTable(dict(TUPLES_FOR_STDDEV_LARGE))
        self.assertEqual(low_freq.stddev(), round(2.5**0.5, 4))
    def test_stddev_for_above_cutoff_table_with_more_decimals(self):
        low_freq = lim.LongIntTable(dict(TUPLES_FOR_STDDEV_LARGE))
        self.assertEqual(low_freq.stddev(decimal_place=10), round(2.5**0.5, 10))


    def test_merge_adds_old_vals_and_makes_new_vals(self):
        table = lim.LongIntTable(dict((x, 1) for x in range(1, 4)))
        table.merge([(x, 1) for x in range(-1, 3)])
        self.assertEqual(table.frequency_all(),
                         [(-1, 1), (0, 1), (1, 2), (2, 2), (3, 1)])

    def test_update_frequency(self):
        self.neg2_to_pos2_freq3.update_frequency(2, 5)
        self.assertEqual(self.neg2_to_pos2_freq3.frequency(2)[1], 5)
    def test_update_value_ow(self):
        self.neg2_to_pos2_freq3.update_value_ow(2, 5)
        self.assertEqual(self.neg2_to_pos2_freq3.frequency(2)[1], 0)
        self.assertEqual(self.neg2_to_pos2_freq3.frequency(5)[1], 3)
    def test_update_value_add(self):
        self.neg2_to_pos2_freq3.update_value_add(2, 1)
        self.assertEqual(self.neg2_to_pos2_freq3.frequency(2)[1], 0)
        self.assertEqual(self.neg2_to_pos2_freq3.frequency(1)[1], 6)

    def test_add_error_raising_and_errors_do_not_mutate_table(self):
        self.assertRaisesRegexp(ValueError, 'cannot add an empty list',
                                self.identity_a.add, 1, [(1, 0)])
        self.assertRaisesRegexp(ValueError, 'times must be a positive int',
                                self.identity_a.add, -1, [(1, 1)])
        self.assertRaisesRegexp(ValueError, 'frequencies may not be negative',
                                self.identity_a.add, 1, [(1, -1)])
        self.assertEqual(self.identity_a.frequency_all(), [(0, 1)])
#the next two tests test that add works for the two cases for _fastest()
#_fastest() is found in the the add() method
#for details of adding ints vs tuples, see testing_add_speed.py
    def test_add_works_with_low_total_frequency_to_number_of_vals(self):
        low_ratio_tuples = [(1, 1), (2, 1)]
        self.identity_a.add(1, low_ratio_tuples)
        self.assertEqual(self.identity_a.frequency_all(), low_ratio_tuples)
    def test_add_works_with_high_total_frequency_to_number_of_vals(self):
        high_ratio_tuples = [(1, 10**1000), (2, 10**1000)]
        self.identity_a.add(1, high_ratio_tuples)
        self.assertEqual(self.identity_a.frequency_all(), high_ratio_tuples)

    def test_one_multiple_add_is_multiple_single_adds(self):
        self.identity_a.add(1, TUPLES_WITHOUT_ZERO)
        self.identity_a.add(1, TUPLES_WITHOUT_ZERO)
        self.identity_b.add(2, TUPLES_WITHOUT_ZERO)
        self.assertEqual(self.identity_a.frequency_all(),
                         self.identity_b.frequency_all())
    def test_add_adds_correctly(self):
        tuple_list = [(1, 2), (2, 2)]
        self.identity_a.add(2, tuple_list)
        self.assertEqual(self.identity_a.frequency_all(),
                         [(2, 4), (3, 8), (4, 4)])
    def test_add_works_with_long_large_number_list(self):
        tuple_list = [(x, 10**1000) for x in range(-1000, 1000)]
        self.identity_a.add(1, tuple_list)
        self.assertEqual(self.identity_a.frequency_all(), tuple_list)
    def test_remove_removes_correctly(self):
        self.identity_a.add(5, TUPLES_WITHOUT_ZERO)
        self.identity_b.add(10, TUPLES_WITHOUT_ZERO)
        self.identity_b.remove(5, TUPLES_WITHOUT_ZERO)
        self.assertEqual(self.identity_a.frequency_all(),
                         self.identity_b.frequency_all())
    def test_remove_works_for_large_numbers(self):
        self.identity_a.add(1, TUPLES_FOR_STDDEV_LARGE)
        self.identity_b.add(2, TUPLES_FOR_STDDEV_LARGE)
        self.identity_b.remove(1, TUPLES_FOR_STDDEV_LARGE)
        self.assertEqual(self.identity_a.frequency_all(),
                         self.identity_b.frequency_all())

    def test_add_adds_same_regardless_of_order(self):
        self.identity_a.add(1, TUPLES_WITH_TWO_HIGHEST)
        self.identity_a.add(2, TUPLES_WITH_ONE_HIGHEST)
        self.identity_b.add(2, TUPLES_WITH_ONE_HIGHEST)
        self.identity_b.add(1, TUPLES_WITH_TWO_HIGHEST)
        self.assertEqual(self.identity_a.frequency_all(),
                         self.identity_b.frequency_all())

    def test_remove_removes_same_regardless_of_order(self):
        self.identity_a.add(5, TUPLES_WITH_TWO_HIGHEST)
        self.identity_a.add(5, TUPLES_WITH_ONE_HIGHEST)
        self.identity_b.add(1, TUPLES_WITH_ONE_HIGHEST)
        self.identity_b.add(1, TUPLES_WITH_TWO_HIGHEST)
        self.identity_a.remove(3, TUPLES_WITH_TWO_HIGHEST)
        self.identity_a.remove(3, TUPLES_WITH_ONE_HIGHEST)
        self.identity_a.remove(1, TUPLES_WITH_ONE_HIGHEST)
        self.identity_a.remove(1, TUPLES_WITH_TWO_HIGHEST)
        self.assertEqual(self.identity_a.frequency_all(),
                         self.identity_b.frequency_all())


if __name__ == '__main__':
    unittest.main()

