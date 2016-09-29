"""test indexedlist"""
import unittest
import dicetables.indexedvalues as iv


class TestIndexedValues(unittest.TestCase):

    def assert_indexed_values(self, indexed_values, start_index, values):
        self.assertEqual(indexed_values.start_index, start_index)
        self.assertEqual(indexed_values.event_keys, values)

    def assert_add(self, start_index_values_1, start_index_values_2, expected_items):
        first = iv.IndexedValues(*start_index_values_1)
        second = iv.IndexedValues(*start_index_values_2)
        return self.assertEqual(first.add(second).items(), expected_items)

    def test_make_start_index_and_list_empty(self):
        start_index, lst = iv.make_start_index_and_list([])
        self.assertEqual(start_index, 0)
        self.assertEqual(lst, [1])

    def test_make_start_index_and_list_start_zero(self):
        start_index, lst = iv.make_start_index_and_list(sorted({0: 1, 1: 1}.items()))
        self.assertEqual(start_index, 0)
        self.assertEqual(lst, [1, 1])

    def test_make_start_index_and_list_start_other(self):
        start_index, lst = iv.make_start_index_and_list(sorted({-2: 1, -1: 1}.items()))
        self.assertEqual(start_index, -2)
        self.assertEqual(lst, [1, 1])

    def test_make_start_index_and_list_gap_in_values(self):
        start_index, lst = iv.make_start_index_and_list(sorted({-2: 1, 1: 1}.items()))
        self.assertEqual(start_index, -2)
        self.assertEqual(lst, [1, 0, 0, 1])

    def test_generated_indexed_values_empty(self):
        test = iv.generate_indexed_values([])
        self.assert_indexed_values(test, 0, [1])

    def test_generate_indexed_values_unsorted_tuples(self):
        test = iv.generate_indexed_values([(2, 1), (1, 2)])
        self.assert_indexed_values(test, 1, [2, 1])

    def test_generated_indexed_values_sorted_tuples(self):
        test = iv.generate_indexed_values([(1, 1), (2, 2)])
        self.assert_indexed_values(test, 1, [1, 2])

    def test_generate_indexed_values_from_dict_empty(self):
        test = iv.generate_indexed_values_from_dict({})
        self.assert_indexed_values(test, 0, [1])

    def test_generate_indexed_values_from_dict(self):
        test = iv.generate_indexed_values_from_dict({1: 1})
        self.assert_indexed_values(test, 1, [1])

    def test_IndexedValues_init_empty(self):
        test = iv.IndexedValues()
        self.assert_indexed_values(test, 0, [1])

    def test_IndexedValues_init_non_empty(self):
        test = iv.IndexedValues(1, [1, 3])
        self.assert_indexed_values(test, 1, [1, 3])

    def test_IndexedValues_start_index(self):
        test = iv.IndexedValues(3, [1])
        self.assertEqual(test.start_index, 3)

    def test_IndexedValues_values(self):
        test = iv.IndexedValues(3, [1, 2])
        self.assertEqual(test.values, [1, 2])

    def test_indexedValues_range(self):
        test = iv.IndexedValues(3, [1, 2, 3])
        self.assertEqual(test.range, (3, 5))

    def test_IndexedValues_items(self):
        test = iv.IndexedValues(1, [1, 0, 3])
        self.assertEqual(test.items(), [(1, 1), (3, 3)])

    def test_indexedValues_get_within_range(self):
        test = iv.IndexedValues(3, [1, 2, 3])
        self.assertEqual(test.get(4), 2)

    def test_indexedValues_get_out_of_range(self):
        test = iv.IndexedValues(3, [1, 2, 3])
        self.assertEqual(test.get(2), 0)
        self.assertEqual(test.get(6), 0)

    def test_IndexedValues_equalize_len_lower_max_size(self):
        self.assertEqual(iv.equalize_len_lower([1, 2, 3], 3), [1, 2, 3])

    def test_IndexedValues_equalize_len_lower_other_case(self):
        self.assertEqual(iv.equalize_len_lower([1, 2, 3], 5), [1, 2, 3, 0, 0])

    def test_IndexedValues_equalize_len_higher_no_adds(self):
        self.assertEqual(iv.equalize_len_higher([1, 2, 3], 3, 0), [1, 2, 3])

    def test_IndexedValues_equalize_len_higher_higher_and_zeros_is_total_size(self):
        self.assertEqual(iv.equalize_len_higher([1, 2, 3], 5, 2), [0, 0, 1, 2, 3])

    def test_IndexedValues_equalize_len_higher_higher_and_zeros_lt_total_size(self):
        self.assertEqual(iv.equalize_len_higher([1, 2, 3], 10, 2), [0, 0, 1, 2, 3, 0, 0, 0, 0, 0])

    def test_IndexedValues_equalize_len_demonstration(self):
        lower = [1, 2, 3, 4, 5, 6]
        higher = [1, 2, 3]
        start_index_diff = 2
        total_size = 6
        self.assertEqual(iv.equalize_len_lower(lower, total_size),
                         [1, 2, 3, 4, 5, 6])
        self.assertEqual(iv.equalize_len_higher(higher, total_size, start_index_diff),
                         [0, 0, 1, 2, 3, 0])

    def test_IndexedValues_combine_values_demonstration_continued(self):
        lower = [1, 2, 3, 4, 5, 6]
        higher = [1, 2, 3]
        start_index_diff = 2
        total_size = 6
        self.assertEqual(iv.equalize_len_lower(lower, total_size),
                         [1, 2, 3, 4, 5, 6])
        self.assertEqual(iv.equalize_len_higher(higher, total_size, start_index_diff),
                         [0, 0, 1, 2, 3, 0])
        self.assertEqual(iv.combine_values(lower, higher, start_index_diff),
                         [1, 2, 4, 6, 8, 6])

    def test_combine_values_diff_is_zero(self):
        lower = [1, 2]
        higher = [1, 2, 3]
        self.assertEqual(iv.combine_values(lower, higher, 0), [2, 4, 3])

    def test_combine_values_diff_is_non_zero(self):
        lower = [1, 2, 3]
        higher = [1, 2, 3, 4]
        self.assertEqual(iv.combine_values(lower, higher, 2), [1, 2, 4, 2, 3, 4])

    def test_IndexedValues_add_return_new_IndexedValues(self):
        first = iv.IndexedValues()
        second = iv.IndexedValues()
        third = first.add(second)
        self.assertNotEqual(first, second)
        self.assertNotEqual(third, second)
        self.assertNotEqual(first, third)
        first._values[0] = 5
        second._values[0] = 6
        self.assertEqual(third.event_keys, [2])
        self.assertIsInstance(third, iv.IndexedValues)

    def test_IndexedValues_add_out_of_range_of_each_other(self):
        self.assert_add((3, [1, 2, 3]),
                        (7, [4, 5]),
                        [(3, 1), (4, 2), (5, 3), (7, 4), (8, 5)])

    def test_IndexedValues_add_same_sized_obj_in_range_of_each_other(self):
        self.assert_add((3, [1, 2]),
                        (4, [4, 5]),
                        [(3, 1), (4, 6), (5, 5)])

    def test_IndexedValues_add_first_larger_than_second(self):
        self.assert_add((3, [1, 2, 3, 4, 5]),
                        (4, [1, 2, 3]),
                        [(3, 1), (4, 3), (5, 5), (6, 7), (7, 5)])

    def test_IndexedValues_add_commutative(self):
        first = iv.IndexedValues(1, [2, 3, 4])
        second = iv.IndexedValues(2, [3, 4, 5, 6])
        self.assertEqual(first.add(second).items(), second.add(first).items())


if __name__ == '__main__':
    unittest.main()
