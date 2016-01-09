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

TUPLES_WITH_ZERO = [(1, 2), (2, 0), (-1, 2)]
TUPLES_WITHOUT_ZERO = [(-1, 2), (1, 2)]
TUPLES_WITH_TWO_HIGHEST = [(1, 2), (2, 1), (-1, 2)]
TUPLES_WITH_ONE_HIGHEST = [(1, 2), (2, 3), (-1, 2)]
class TestLongIntTable(unittest.TestCase):
    def setUp(self):
        self.identity_a = lim.LongIntTable({0:1})
        self.identity_b = lim.LongIntTable({0:1})
        
        self.neg2_to_pos2_freq3_a = lim.LongIntTable(dict([(x, 3) for x in
                                                           range(-2, 3)]))
        self.neg2_to_pos2_freq3_b = lim.LongIntTable(dict([(x, 3) for x in
                                                           range(-2, 3)]))
        self.empty_table = lim.LongIntTable({})
    def tearDown(self):
        del self.identity_a
        del self.identity_b
        
        del self.neg2_to_pos2_freq3_a
        del self.neg2_to_pos2_freq3_b
        del self.empty_table
    def test_values_sorts_and_removes_zeros(self):
        test_table = lim.LongIntTable(dict(TUPLES_WITH_ZERO))
        self.assertEqual(test_table.values(), [-1, 1])
    def test_values_returns_empty_list_for_empty_table(self):
        self.assertEqual(self.empty_table.values(), [])
    def test_values_min_returns_min_value(self):
        self.assertEqual(self.neg2_to_pos2_freq3_a.values_min(), -2)
    def test_values_max_returns_max_value(self):
        self.assertEqual(self.neg2_to_pos2_freq3_a.values_max(), 2)
    def test_values_range_returns_minmax(self):
        self.assertEqual(self.neg2_to_pos2_freq3_a.values_range(), (-2, 2))
    def test_values_min_returns_none_for_empty_table(self):
        self.assertIsNone(self.empty_table.values_min())
    def test_values_max_returns_none_for_empty_table(self):
        self.assertIsNone(self.empty_table.values_max())
    def test_values_range_returns_none_none_for_empty_table(self):
        self.assertEqual(self.empty_table.values_range(), (None, None))
        
    def test_frequency_returns_value_frequency_as_tuple(self):
        self.assertEqual(self.neg2_to_pos2_freq3_a.frequency(0), (0, 3))
    def test_frequency_returns_zero_frequency_for_empty_value(self):
        self.assertEqual(self.neg2_to_pos2_freq3_a.frequency(100), (100, 0))
    def test_frequency_range_returns_correct_tuple_list(self):
        self.assertEqual(self.neg2_to_pos2_freq3_a.frequency_range(-4, 2),
                        [(-4, 0), (-3, 0), (-2, 3), (-1, 3), (0, 3), (1, 3)])
    def test_frequency_all_returns_for_normal_case(self):
        self.assertEqual(self.neg2_to_pos2_freq3_a.frequency_all(), 
                        [(-2, 3), (-1, 3), (0, 3), (1, 3), (2, 3)])
    def test_frequency_all_return_empty_for_empty_table(self):
        self.assertEqual(self.empty_table.frequency_all(), [])
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
        self.assertEqual(self.neg2_to_pos2_freq3_a.total_frequency(), 5*3)
    
    def test_string_returns_min_to_max(self):
        self.assertEqual(str(self.neg2_to_pos2_freq3_a), 'table from -2 to 2')
    def test_string_is_in_order_and_ignores_high_zero_values(self):
        table = lim.LongIntTable(dict(TUPLES_WITH_ZERO))
        self.assertEqual(str(table), 'table from -1 to 1')
    def test_string_of_empty_table(self):
        self.assertEqual(str(self.empty_table), 'table from None to None')
#    def test_frequency(self):
#        '''all the frequency_something functions do what they should'''
#        #confirms frequency function returns appropriate value or zero
#        self.assertEqual(self.table_a.frequency(2), (2, 2))
#        self.assertEqual(self.table_a.frequency(5), (5, 0))
#        self.assertEqual(self.table_a.frequency_range(0, 5),
#                         [(0, 0), (1, 1), (2, 2), (3, 3), (4, 0)])
#        #confirm freq all sorts and removes zero frequency
#        self.assertEqual(self.table_a.frequency_all(), [(1, 1), (2, 2), (3, 3)])
#        self.assertEqual(self.table_b.frequency_all(), [(1, 1), (3, 3)])
#
#        self.assertEqual(self.table_a.frequency_highest(), (3, 3))
#        self.assertEqual(self.table_b.frequency_highest(), (3, 3))
#        self.assertEqual(self.table_c.frequency_highest(), (2, 5))
#        self.assertEqual(self.empty_table_a.frequency_highest(), (None, 0))
#    def test_string(self):
#        '''test the string method'''
#        self.assertEqual(str(self.table_a), 'table from 1 to 3')
#        self.assertEqual(str(self.table_b), 'table from 1 to 3')
#        self.assertEqual(str(self.table_c), 'table from 1 to 3')
#        self.assertEqual(str(self.empty_table_a), 'table from None to None')
#    def test_mean(self):
#        '''test the mean() function'''
#        self.assertEqual(self.table_a.mean(), (1+4+9)/6.)
#        self.assertEqual(self.table_b.mean(), (1+9)/4.)
#        self.assertEqual(self.table_c.mean(), (1+10+9)/(1.+5.+3.))
#        with self.assertRaises(ZeroDivisionError):
#            self.empty_table_a.mean()
#        with self.assertRaises(ZeroDivisionError):
#            self.empty_table_b.mean()
#
#    def test_stddev(self):
#        '''test the stddev() function'''
#        with self.assertRaises(ZeroDivisionError):
#            self.empty_table_a.stddev()
#        #confirms stddev computes correctly for numbers below cutoff for //
#        small_test = lim.LongIntTable(dict((x, 2) for x in range(1, 6)))
#        stddev = ((2*2**2 + 2*1)/5.)**0.5
#        self.assertEqual(small_test.stddev(), round(stddev, 4))
#        small_test = None
#        #confirms stddev computes correctly for numbers above cutoff for //
#        large_test = lim.LongIntTable(dict((x, 10**100) for x in range(1, 6)))
#        self.assertEqual(large_test.stddev(), round(stddev, 4))
#        large_test = None
#        stddev = None
#    def test_merge_update(self):
#        '''test the merge function and the three update functions'''
#
#        answer = [(1, 2), (2, 7), (3, 6)]
#
#        self.table_a.merge(self.table_c.frequency_all())
#        self.assertEqual(answer, self.table_a.frequency_all())
#
#        self.table_a.update_frequency(1, 3)
#        answer[0] = (1, 3)
#        self.assertEqual(answer, self.table_a.frequency_all())
#
#        self.table_a.update_value_ow(1, 3)
#        answer = answer[1:]
#        answer[1] = (3, 3)
#        self.assertEqual(answer, self.table_a.frequency_all())
#
#        self.table_a.update_value_add(3, 2)
#        answer = [(2, 10)]
#        self.assertEqual(answer, self.table_a.frequency_all())
#
#class TestAddRm(unittest.TestCase):
#    '''tests for add and remove of LongIntTable'''
#    def setUp(self):
#        self.basic1 = lim.LongIntTable({0:1})
#        self.basic2 = lim.LongIntTable({0:1})
#        self.table_a = lim.LongIntTable({1:1, 2:2, 3:3})
#        self.table_a1 = lim.LongIntTable({1:1, 2:2, 3:3})
#        self.tuples = [(1, 1), (2, 4)]
#        self.other_tuples = [(1, 1), (3, 1)]
#    def tearDown(self):
#        del self.basic1
#        del self.basic2
#        del self.table_a
#        del self.table_a1
#        del self.tuples
#        del self.other_tuples
#
#    def test_error_raising(self):
#        '''make sure errors are raised and table doesn't mutate'''
#        self.assertRaisesRegexp(ValueError, 'cannot add an empty list',
#                                self.basic1.add, 1, [(1, 0)])
#        self.assertRaisesRegexp(ValueError, 'times must be a positive int',
#                                self.basic1.add, 0, [(1, 1)])
#        self.assertRaisesRegexp(ValueError, 'frequencies may not be negative',
#                                self.basic1.add, 1, [(1, -1)])
#        self.assertEqual(self.basic1.frequency_all(), [(0, 1)])
#    def test_order_zeros(self):
#        '''adding a list in different order or with added zeros deosn't affect
#        the add'''
#        self.table_a.add(1, [(val, 5) for val in range(1, 6)])
#        self.table_a1.add(1, [(val, 5) for val in range(5, 0, -1)])
#        self.assertEqual(self.table_a.frequency_all(),
#                         self.table_a1.frequency_all())
#
#        self.table_a.add(1, [(1, 1), (2, 0), (3, 5)])
#        self.table_a1.add(1, [(3, 5), (1, 1)])
#        self.assertEqual(self.table_a.frequency_all(),
#                         self.table_a1.frequency_all())
#    def test_add(self):
#        '''test the cases for add'''
#        #add works with the identity table
#        self.basic1.add(1, self.tuples)
#        self.basic2.add(1, self.tuples)
#        self.assertEqual(self.basic1.frequency_all(), self.tuples)
#
#        #confirm when _fastest converts to tuples that it works
#        self.basic1.add(1, self.tuples)
#        #[1,1  2,4] becomes [2,1  3,4]+[3,4  4,16]
#        self.assertEqual(self.basic1.frequency_all(), [(2, 1), (3, 8), (4, 16)])
#
#        #confirm when _fastest converts to list that it works
#        self.basic2.add(1, self.other_tuples)
#        #[1,1  2,4] becomes [2,1  3,4]+[4,1  5,4]
#        self.assertEqual(self.basic2.frequency_all(),
#                         [(2, 1), (3, 4), (4, 1), (5, 4)])
#
#        #now adding the other list to each basic should make them equal
#        self.basic1.add(1, self.other_tuples)
#        self.basic2.add(1, self.tuples)
#        self.assertEqual(self.basic1.frequency_all(), self.basic2.frequency_all())
#
#        #adding to an empty table won't change the table
#        empty_table = lim.LongIntTable({})
#        empty_table.add(5, self.tuples)
#        self.assertEqual(empty_table.frequency_all(), [])
#        del empty_table
#
#    def test_remove(self):
#        '''test the remove function'''
#        self.basic1.add(2, self.tuples)
#        self.basic2.add(5, self.tuples)
#        self.basic2.remove(3, self.tuples)
#        self.assertEqual(self.basic1.frequency_all(), self.basic2.frequency_all())
#
#        self.basic1.add(1, self.other_tuples)
#        self.basic1.remove(2, self.tuples)
#        self.assertEqual(self.basic1.frequency_all(), self.other_tuples)
#
#        self.basic2.add(3, self.other_tuples)
#        self.assertRaisesRegexp(ValueError, 'times must be a positive int',
#                                self.basic2.remove, 0, self.tuples)
#        self.assertRaisesRegexp(ValueError, 'frequencies may not be negative',
#                                self.basic2.remove, 1, [(1, -1)])
#        self.basic2.remove(1, self.tuples)
#        self.basic2.remove(1, self.other_tuples)
#        self.basic2.remove(1, self.tuples)
#        self.basic2.remove(1, self.other_tuples)
#        self.assertEqual(self.basic2.frequency_all(), self.other_tuples)
#
#        self.basic1.remove(1, self.other_tuples)
#        self.assertEqual(self.basic1.frequency_all(), [(0, 1)])

if __name__ == '__main__':
    unittest.main()

