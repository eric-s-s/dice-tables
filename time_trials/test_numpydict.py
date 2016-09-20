"""test for numpydict"""

import unittest
import numpy as np

import numpydict as npd

def make_obj_array(input_list):
    return np.array(input_list, dtype=object)


class TestNumpyDict(unittest.TestCase):
    def setUp(self):
        self.empty = npd.NumpyCounter()

    def tearDown(self):
        del self.empty

    def assert_array_equal(self, array_1, array_2):
        self.assertEqual(array_1.tolist(), array_2.tolist())
        self.assertEqual(array_1.dtype, array_2.dtype)

    def check_counter(self, numpy_counter, start_val, array_list):
        self.assertEqual(numpy_counter.start_val, start_val)
        self.assert_array_equal(numpy_counter.array,
                                make_obj_array(array_list))

    def test_convert_tuple_list_to_array_and_start_value_start_zero(self):
        start_val, array = npd.convert_tuple_list_to_array_and_start_value([(0, 1), (1, 1)])
        self.assertEqual(start_val, 0)
        self.assert_array_equal(array, make_obj_array([1, 1]))

    def test_convert_tuple_list_to_array_and_start_value_start_other(self):
        start_val, array = npd.convert_tuple_list_to_array_and_start_value([(-2, 1), (-1, 1)])
        self.assertEqual(start_val, -2)
        self.assert_array_equal(array, make_obj_array([1, 1]))

    def test_convert_tuple_list_to_array_and_start_value_gap_in_values(self):
        start_val, array = npd.convert_tuple_list_to_array_and_start_value([(-2, 1), (1, 1)])
        self.assertEqual(start_val, -2)
        self.assert_array_equal(array, make_obj_array([1, 0, 0, 1]))

    def test_numpy_dict_init_empty(self):
        test = npd.NumpyCounter()
        self.check_counter(test, 0, [1])

    def test_NumpyCounter_init_non_empty(self):
        test = npd.NumpyCounter(1, make_obj_array([1, 3]))
        self.check_counter(test, 1, [1, 3])

    def test_NumpyCounter_items(self):
        test = npd.NumpyCounter(1, make_obj_array([1, 0, 3]))
        self.assertEqual(test.items(), [(1, 1), (3, 3)])



    def test_combine_arrays_diff_is_zero(self):
        lower = make_obj_array([1, 2])
        higher = make_obj_array([1, 2, 3])
        self.assert_array_equal(npd.combine_arrays(lower, higher, 0),
                                make_obj_array([2, 4, 3]))

    def test_combine_arrays_diff_is_non_zero(self):
        lower = make_obj_array([1, 2, 3])
        higher = make_obj_array([1, 2, 3])
        self.assert_array_equal(npd.combine_arrays(lower, higher, 2),
                                make_obj_array([1, 2, 4, 2, 3]))
        
    def test_NumpyCounter_add_same_sized_obj(self):
        first = npd.NumpyCounter(3, make_obj_array([1, 2]))
        second = npd.NumpyCounter(7, make_obj_array([4, 5]))
        new = first.add(second)
        self.assertEqual(new.items(),
                         [(3, 1), (4, 2), (7, 4), (8, 5)])

    def test_NumpyCounter_add_is_commutative(self):
        first = npd.NumpyCounter(3, make_obj_array([1, 2]))
        second = npd.NumpyCounter(7, make_obj_array([4, 5]))
        new_1 = first.add(second)
        new_2 = second.add(first)
        self.assertEqual(new_1.items(), new_2.items())

    def test_NumpyCounter_add_first_larger_than_second(self):
        first = npd.NumpyCounter(3, make_obj_array([1, 2, 3, 4, 5]))
        second = npd.NumpyCounter(4, make_obj_array([1, 2, 3]))
        self.assertEqual(first.add(second).items(),
                         sorted({3: 1, 4: 3, 5: 5, 6: 7, 7: 5}.items()))






if __name__ == '__main__':
    unittest.main()
