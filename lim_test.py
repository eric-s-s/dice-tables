'''tests for the longintmath.py module'''
import unittest
import longintmath as lim

class TestLIMFunc(unittest.TestCase):
    '''tests for the long_int_(mathfunction) functions'''
    def setUp(self):
        self.long_big = 10**1000
        self.float_big = 1.0e+300
        self.float_sm = 1.0e-100

    def tearDown(self):
        del self.long_big
        del self.float_big
        del self.float_sm

    def error_tester(self, result, expected):
        '''use the inverse error to avoid trouble with overflow errors.'''
        allowed_error = 1e-8
        if result - expected == 0:
            inv_error = float('inf')
        else:
            inv_error = abs(expected // (result - expected))
        self.assertGreater(inv_error, 1/allowed_error)

    def test_li_div(self):
        '''test long_int_div'''
        self.assertEqual(lim.long_int_div(self.float_big, self.long_big), 0)
        self.assertEqual(lim.long_int_div(self.float_sm, self.float_big), 0)

        result1 = lim.long_int_div(self.float_big, self.float_sm)
        self.error_tester(result1, 10**400)

        result2 = lim.long_int_div(self.long_big, -self.float_big)
        self.error_tester(result2, -10**700)

        result3 = lim.long_int_div(2, self.float_big)
        self.error_tester(result3, 2e-300)

        result4 = lim.long_int_div(-self.float_big, 5)
        self.error_tester(result4, -2e+299)

    def test_li_times(self):
        '''test long_int_times'''
        result1 = lim.long_int_times(self.long_big, self.float_big)
        self.error_tester(result1, 10**1300)

        result2 = lim.long_int_times(-4 * self.float_sm, self.float_sm)
        self.error_tester(result2, -4e-200)
    def test_li_pow(self):
        '''test long_int_pow'''
        result1 = lim.long_int_pow(self.long_big, 2.5)
        self.error_tester(result1, 10**2500)


class TestLITable(unittest.TestCase):
    '''tests for all functions on a LongIntTable that aren't add and remove'''
    def setUp(self):
        self.table_a = lim.LongIntTable({3:3, 1:1, 2:2})
        self.table_a1 = lim.LongIntTable({3:3, 1:1, 2:2})

        self.table_b = lim.LongIntTable({1:1, 2:0, 3:3})
        self.table_b1 = lim.LongIntTable({1:1, 2:0, 3:3})

        self.table_c = lim.LongIntTable({1:1, 2:5, 3:3})

        self.empty_table_a = lim.LongIntTable({})
        self.empty_table_b = lim.LongIntTable({1:0, 2:0})

    def tearDown(self):
        del self.table_a
        del self.table_a1

        del self.table_b
        del self.table_b1

        del self.table_c

        del self.empty_table_a
        del self.empty_table_b

    def test_values(self):
        '''all the values_something functions do what they should'''
        self.assertEqual(self.table_a.values(), [1, 2, 3])
        self.assertEqual(self.table_b.values(), [1, 3])
        self.assertEqual(self.empty_table_b.values(), [])

        self.assertIsNone(self.empty_table_a.values_min())
        self.assertIsNone(self.empty_table_a.values_max())
        self.assertEqual(self.table_a.values_min(), 1)
        self.assertEqual(self.table_a.values_max(), 3)

        self.assertEqual(self.table_a.values_range(), (1, 3))
        self.assertEqual(self.empty_table_b.values_range(), (None, None))

    def test_frequency(self):
        '''all the frequency_something functions do what they should'''
        #confirms frequency function returns appropriate value or zero
        self.assertEqual(self.table_a.frequency(2), (2, 2))
        self.assertEqual(self.table_a.frequency(5), (5, 0))
        self.assertEqual(self.table_a.frequency_range(0, 5),
                         [(0, 0), (1, 1), (2, 2), (3, 3), (4, 0)])
        #confirm freq all sorts and removes zero frequency
        self.assertEqual(self.table_a.frequency_all(), [(1, 1), (2, 2), (3, 3)])
        self.assertEqual(self.table_b.frequency_all(), [(1, 1), (3, 3)])

        self.assertEqual(self.table_a.frequency_highest(), (3, 3))
        self.assertEqual(self.table_b.frequency_highest(), (3, 3))
        self.assertEqual(self.table_c.frequency_highest(), (2, 5))
        self.assertEqual(self.empty_table_a.frequency_highest(), (None, 0))
    def test_string(self):
        '''test the string method'''
        self.assertEqual(str(self.table_a), 'table from 1 to 3')
        self.assertEqual(str(self.table_b), 'table from 1 to 3')
        self.assertEqual(str(self.table_c), 'table from 1 to 3')
        self.assertEqual(str(self.empty_table_a), 'table from None to None')
    def test_mean(self):
        '''test the mean() function'''
        self.assertEqual(self.table_a.mean(), (1+4+9)/6.)
        self.assertEqual(self.table_b.mean(), (1+9)/4.)
        self.assertEqual(self.table_c.mean(), (1+10+9)/(1.+5.+3.))
        with self.assertRaises(ZeroDivisionError):
            self.empty_table_a.mean()
        with self.assertRaises(ZeroDivisionError):
            self.empty_table_b.mean()

    def test_stddev(self):
        '''test the stddev() function'''
        with self.assertRaises(ZeroDivisionError):
            self.empty_table_a.stddev()
        #confirms stddev computes correctly for numbers below cutoff for //
        small_test = lim.LongIntTable(dict((x, 2) for x in range(1, 6)))
        stddev = ((2*2**2 + 2*1)/5.)**0.5
        self.assertEqual(small_test.stddev(), round(stddev, 4))
        small_test = None
        #confirms stddev computes correctly for numbers above cutoff for //
        large_test = lim.LongIntTable(dict((x, 10**100) for x in range(1, 6)))
        self.assertEqual(large_test.stddev(), round(stddev, 4))
        large_test = None
        stddev = None
    def test_merge_update(self):
        '''test the merge function and the three update functions'''

        answer = [(1, 2), (2, 7), (3, 6)]

        self.table_a.merge(self.table_c.frequency_all())
        self.assertEqual(answer, self.table_a.frequency_all())

        self.table_a.update_frequency(1, 3)
        answer[0] = (1, 3)
        self.assertEqual(answer, self.table_a.frequency_all())

        self.table_a.update_value_ow(1, 3)
        answer = answer[1:]
        answer[1] = (3, 3)
        self.assertEqual(answer, self.table_a.frequency_all())

        self.table_a.update_value_add(3, 2)
        answer = [(2, 10)]
        self.assertEqual(answer, self.table_a.frequency_all())

class TestAddRm(unittest.TestCase):
    '''tests for add and remove of LongIntTable'''
    def setUp(self):
        self.basic1 = lim.LongIntTable({0:1})
        self.basic2 = lim.LongIntTable({0:1})
        self.table_a = lim.LongIntTable({1:1, 2:2, 3:3})
        self.table_a1 = lim.LongIntTable({1:1, 2:2, 3:3})
        self.tuples = [(1, 1), (2, 4)]
        self.other_tuples = [(1, 1), (3, 1)]
    def tearDown(self):
        del self.basic1
        del self.basic2
        del self.table_a
        del self.table_a1
        del self.tuples
        del self.other_tuples

    def test_error_raising(self):
        '''make sure errors are raised and table doesn't mutate'''
        self.assertRaisesRegexp(ValueError, 'cannot add an empty list',
                                self.basic1.add, 1, [(1, 0)])
        self.assertRaisesRegexp(ValueError, 'times must be a positive int',
                                self.basic1.add, 0, [(1, 1)])
        self.assertRaisesRegexp(ValueError, 'frequencies may not be negative',
                                self.basic1.add, 1, [(1, -1)])
        self.assertEqual(self.basic1.frequency_all(), [(0, 1)])
    def test_order_zeros(self):
        '''adding a list in different order or with added zeros deosn't affect
        the add'''
        self.table_a.add(1, [(val, 5) for val in range(1, 6)])
        self.table_a1.add(1, [(val, 5) for val in range(5, 0, -1)])
        self.assertEqual(self.table_a.frequency_all(),
                         self.table_a1.frequency_all())

        self.table_a.add(1, [(1, 1), (2, 0), (3, 5)])
        self.table_a1.add(1, [(3, 5), (1, 1)])
        self.assertEqual(self.table_a.frequency_all(),
                         self.table_a1.frequency_all())
    def test_add(self):
        '''test the cases for add'''
        #add works with the identity table
        self.basic1.add(1, self.tuples)
        self.basic2.add(1, self.tuples)
        self.assertEqual(self.basic1.frequency_all(), self.tuples)

        #confirm when _fastest converts to tuples that it works
        self.basic1.add(1, self.tuples)
        #[1,1  2,4] becomes [2,1  3,4]+[3,4  4,16]
        self.assertEqual(self.basic1.frequency_all(), [(2, 1), (3, 8), (4, 16)])

        #confirm when _fastest converts to list that it works
        self.basic2.add(1, self.other_tuples)
        #[1,1  2,4] becomes [2,1  3,4]+[4,1  5,4]
        self.assertEqual(self.basic2.frequency_all(),
                         [(2, 1), (3, 4), (4, 1), (5, 4)])

        #now adding the other list to each basic should make them equal
        self.basic1.add(1, self.other_tuples)
        self.basic2.add(1, self.tuples)
        self.assertEqual(self.basic1.frequency_all(), self.basic2.frequency_all())

        #adding to an empty table won't change the table
        empty_table = lim.LongIntTable({})
        empty_table.add(5, self.tuples)
        self.assertEqual(empty_table.frequency_all(), [])
        del empty_table

    def test_remove(self):
        '''test the remove function'''
        self.basic1.add(2, self.tuples)
        self.basic2.add(5, self.tuples)
        self.basic2.remove(3, self.tuples)
        self.assertEqual(self.basic1.frequency_all(), self.basic2.frequency_all())

        self.basic1.add(1, self.other_tuples)
        self.basic1.remove(2, self.tuples)
        self.assertEqual(self.basic1.frequency_all(), self.other_tuples)

        self.basic2.add(3, self.other_tuples)
        self.assertRaisesRegexp(ValueError, 'times must be a positive int',
                                self.basic2.remove, 0, self.tuples)
        self.assertRaisesRegexp(ValueError, 'frequencies may not be negative',
                                self.basic2.remove, 1, [(1, -1)])
        self.basic2.remove(1, self.tuples)
        self.basic2.remove(1, self.other_tuples)
        self.basic2.remove(1, self.tuples)
        self.basic2.remove(1, self.other_tuples)
        self.assertEqual(self.basic2.frequency_all(), self.other_tuples)

        self.basic1.remove(1, self.other_tuples)
        self.assertEqual(self.basic1.frequency_all(), [(0, 1)])

SUITE = unittest.TestLoader().loadTestsFromTestCase(TestLIMFunc)
SUITE_A = unittest.TestLoader().loadTestsFromTestCase(TestLITable)
SUITE_B = unittest.TestLoader().loadTestsFromTestCase(TestAddRm)
SUITE.addTest(SUITE_A)
SUITE.addTest(SUITE_B)
unittest.TextTestRunner(verbosity=4).run(SUITE)
