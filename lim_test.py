import unittest
import longintmath as lim
from decimal import Decimal as dc


class TestLIMFunc(unittest.TestCase):
    def setUp(self):
        self.long_big = 10**1000
        self.float_big = 1.0e+200
        self.float_sm = 1.0e-100
    def tearDown(self):
        self.long_big = None
        self.float_big = None
        self.float_sm = None
    def test_conv_bak(self):
        self.assertEqual(lim._convert_back(dc(self.long_big)), self.long_big)
        self.assertEqual(lim._convert_back(dc(-self.long_big)),-self.long_big)
        self.assertEqual(lim._convert_back(dc(self.float_big)), self.float_big)
        self.assertEqual(lim._convert_back(dc(self.float_sm)), self.float_sm)
    def test_li_div(self):
        self.assertEqual(lim.long_int_div(self.float_big, self.long_big), 0)
        self.assertAlmostEqual(lim.long_int_div(self.float_big, self.float_sm), 1e+300)
        self.assertEqual(lim.long_int_div(self.long_big, -self.float_big), -10**800)
        self.assertEqual(lim.long_int_div(self.float_sm, self.float_big), 0)
        #self.assertEqual(lim.long_int_div(self.float_big, self.long_big), 0)
        #self.assertEqual(lim.long_int_div(self.float_big, self.long_big), 0)
        #self.assertEqual(lim.long_int_div(self.float_big, self.long_big), 0)
        
class TestLITable(unittest.TestCase):
    def setUp(self):
        self.table_a = lim.LongIntTable({3:3, 1:1, 2:2})
        self.table_b = lim.LongIntTable({1:1, 2:0, 3:3})
        self.table_c = lim.LongIntTable({1:1, 2:5, 3:3})
        self.empty_table_a = lim.LongIntTable({})
        self.empty_table_b = lim.LongIntTable({1:0, 2:0})
        
    def test_values(self):
        self.assertEqual(self.table_a.values(), [1,2, 3])
        self.assertEqual(self.table_b.values(), [1, 3])
        self.assertEqual(self.empty_table_b.values(), [])
        
        self.assertIsNone(self.empty_table_a.values_min())
        self.assertIsNone(self.empty_table_a.values_max())
        self.assertEqual(self.table_a.values_min(), 1)
        self.assertEqual(self.table_a.values_max(), 3)
        
        self.assertEqual(self.table_a.values_range(), (1,3))
        self.assertEqual(self.empty_table_b.values_range(), (None, None))
    
    def test_frequency(self):
        #confirms frequency function returns appropriate value or zero    
        self.assertEqual(self.table_a.frequency(2), (2,2))
        self.assertEqual(self.table_a.frequency(5), (5,0))
        self.assertEqual(self.table_a.frequency_range(0,5), 
                        [(0,0), (1,1), (2,2), (3,3,), (4,0)])
        #confirm freq all sorts and removes zero frequency               
        self.assertEqual(self.table_a.frequency_all(), [(1,1,), (2,2), (3,3)])
        self.assertEqual(self.table_b.frequency_all(), [(1,1,), (3,3)])

        self.assertEqual(self.table_a.frequency_highest(), (3,3))
        self.assertEqual(self.table_b.frequency_highest(), (3,3))
        self.assertEqual(self.table_c.frequency_highest(), (2,5))
        self.assertEqual(self.empty_table_a.frequency_highest(), (None, 0))
    def test_string(self):    
        self.assertEqual(str(self.table_a), 'table from 1 to 3')
        self.assertEqual(str(self.table_b), 'table from 1 to 3')
        self.assertEqual(str(self.table_c), 'table from 1 to 3')
        self.assertEqual(str(self.empty_table_a), 'table from None to None')
    def test_mean(self):
        self.assertEqual(self.table_a.mean(), (1+4+9)/6.)
        self.assertEqual(self.table_b.mean(), (1+9)/4.)
        self.assertEqual(self.table_c.mean(), (1+10+9)/(1.+5.+3.))
        with self.assertRaises(ZeroDivisionError):
            self.empty_table_a.mean()
        with self.assertRaises(ZeroDivisionError):
            self.empty_table_b.mean()
            
    def test_stddev(self):
        with self.assertRaises(ZeroDivisionError):
            self.empty_table_a.stddev()
        #confirms stddev computes correctly for numbers below cutoff for //
        small_test = lim.LongIntTable(dict((x,2) for x in range(1,6)))
        stddev = ((2*2**2 + 2*1)/5.)**0.5
        self.assertEqual(small_test.stddev(), round(stddev, 4))
        small_test = None
        #confirms stddev computes correctly for numbers above cutoff for //       
        large_test = lim.LongIntTable(dict((x,10**100) for x in range(1,6)))
        self.assertEqual(large_test.stddev(), round(stddev, 4))
        large_test = None 
        stddev = None

    def test_add(self):
        basic1 = lim.LongIntTable({0:1})
        basic2 = lim.LongIntTable({0:1})
        the_list = [1,2,2,2,2]
        the_tuples = [(1,1), (2, 4)]
        other_tuples = [(1,1), (3,1)]
        #confirm _add_tuple_list and _add_a_list do the same thing and that
        #they do the correct thing for the special case
        basic1._add_tuple_list(the_tuples)
        basic2._add_a_list(the_list)
        self.assertEqual(basic1.frequency_all(), basic2.frequency_all())
        self.assertEqual(basic1.frequency_all(), the_tuples)
        #confirm errors in _check_cull_sort and that it works properly
        self.assertRaisesRegexp(ValueError, 'frequencies may not be negative',
                                basic1._check_cull_sort, [(1,-1)])
        self.assertRaisesRegexp(ValueError, 'cannot add an empty list',
                                basic1._check_cull_sort, [(1,0)])
        self.assertEqual(basic1._check_cull_sort([(3,1), (2, 5), (1, 0)]),
                        [(2, 5), (3,1)])
        #confirm errors raised and that basic1 doesn't mutate
        self.assertRaisesRegexp(ValueError, 'times must be a positive int',
                                basic1.add,0, [(1,1)])
        self.assertRaisesRegexp(ValueError, 'frequencies may not be negative',
                                basic1.add, 1, [(1,-1)])
        self.assertEqual(basic1.frequency_all(), the_tuples)
        
        #confirm when _fastest converts to tuples that it works
        basic1.add(1, the_tuples)
        #[1,1  2,4] becomes [2,1  3,4]+[3,4  4,16]
        self.assertEqual(basic1.frequency_all(), [(2,1), (3, 8), (4,16)])
        
        #confirm when _fastest converts to list that it works
        basic2.add(1, other_tuples)
        #[1,1  2,4] becomes [2,1  3,4]+[4,1  5,4]
        self.assertEqual(basic2.frequency_all(), [(2,1), (3, 4), (4,1), (5,4)])        

        #now adding the other list to each basic should make them equal
        basic1.add(1, other_tuples)
        basic2.add(1, the_tuples)
        self.assertEqual(basic1.frequency_all(), basic2.frequency_all())
        
        #finally adding to an empty table won't change the table
        self.empty_table_b.add(5, the_tuples)
        self.assertEqual(self.empty_table_b.frequency_all(), [])
        
    #def test_remove(self):
        

suite = unittest.TestLoader().loadTestsFromTestCase(TestLIMFunc)
suite_a = unittest.TestLoader().loadTestsFromTestCase(TestLITable)
suite.addTest(suite_a)
unittest.TextTestRunner(verbosity=4).run(suite)
      