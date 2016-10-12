"""test indexedlist"""
import unittest
import dicetables.indexedvalues as iv


class TestIndexedValues(unittest.TestCase):

    def assert_indexed_values(self, indexed_values, start_index, values):
        self.assertEqual(indexed_values.start_index, start_index)
        self.assertEqual(indexed_values.raw_values, values)

    def assert_combine(self, start_index_values_1, start_index_values_2, expected_items):
        first = iv.IndexedValues(*start_index_values_1)
        second = iv.IndexedValues(*start_index_values_2)
        return self.assertEqual(first.combine(second).get_items(), expected_items)

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

    def test_IndexedValues_init_is_mutated_list_safe(self):
        the_list_to_mutate = [1, 2, 3]
        test = iv.IndexedValues(0, the_list_to_mutate)
        the_list_to_mutate[0] = 5
        self.assertEqual(test.raw_values, [1, 2, 3])

    def test_IndexedValues_start_index(self):
        test = iv.IndexedValues(3, [1])
        self.assertEqual(test.start_index, 3)

    def test_IndexedValues_values(self):
        test = iv.IndexedValues(3, [1, 2])
        self.assertEqual(test.raw_values, [1, 2])

    def test_indexedValues_range(self):
        test = iv.IndexedValues(3, [1, 2, 3])
        self.assertEqual(test.index_range, (3, 5))

    def test_IndexedValues_items(self):
        test = iv.IndexedValues(1, [1, 0, 3])
        self.assertEqual(test.get_items(), [(1, 1), (3, 3)])

    def test_indexedValues_get_within_range(self):
        test = iv.IndexedValues(3, [1, 2, 3])
        self.assertEqual(test.get_value_at_key(4), 2)

    def test_indexedValues_get_out_of_range(self):
        test = iv.IndexedValues(3, [1, 2, 3])
        self.assertEqual(test.get_value_at_key(2), 0)
        self.assertEqual(test.get_value_at_key(6), 0)

    def test_IndexedValues_change_list_len_with_zeroes_max_size_offset_zero(self):
        self.assertEqual(iv.change_list_len_with_zeroes([1, 2, 3], 3, 0), [1, 2, 3])

    def test_IndexedValues_change_list_len_with_zeroes_other_case_offset_zero(self):
        self.assertEqual(iv.change_list_len_with_zeroes([1, 2, 3], 5, 0), [1, 2, 3, 0, 0])

    def test_IndexedValues_change_list_len_with_zeroes_no_adds(self):
        self.assertEqual(iv.change_list_len_with_zeroes([1, 2, 3], 3, 0), [1, 2, 3])

    def test_IndexedValues_change_list_len_with_zeroes_offset_and_zeros_is_total_size(self):
        self.assertEqual(iv.change_list_len_with_zeroes([1, 2, 3], 5, 2), [0, 0, 1, 2, 3])

    def test_IndexedValues_change_list_len_with_zeroes_offset_and_zeros_lt_total_size(self):
        self.assertEqual(iv.change_list_len_with_zeroes([1, 2, 3], 10, 2), [0, 0, 1, 2, 3, 0, 0, 0, 0, 0])

    def test_IndexedValues_equalize_len_demonstration(self):
        lower = [1, 2, 3, 4, 5, 6]
        higher = [1, 2, 3]
        diff_in_start_indices = 2
        total_size = 6
        self.assertEqual(iv.change_list_len_with_zeroes(lower, total_size, 0),
                         [1, 2, 3, 4, 5, 6])
        self.assertEqual(iv.change_list_len_with_zeroes(higher, total_size, diff_in_start_indices),
                         [0, 0, 1, 2, 3, 0])

    def test_IndexedValues_combine_values_demonstration_continued(self):
        lower = [1, 2, 3, 4, 5, 6]
        higher = [1, 2, 3]
        start_index_diff = 2
        total_size = 6
        self.assertEqual(iv.change_list_len_with_zeroes(lower, total_size, 0),
                         [1, 2, 3, 4, 5, 6])
        self.assertEqual(iv.change_list_len_with_zeroes(higher, total_size, start_index_diff),
                         [0, 0, 1, 2, 3, 0])
        self.assertEqual(iv.combine_values(lower, higher, start_index_diff),
                         [1, 2, 4, 6, 8, 6])

    def test_combine_values_offset_is_zero(self):
        lower = [1, 2]
        higher = [1, 2, 3]
        self.assertEqual(iv.combine_values(lower, higher, 0), [2, 4, 3])

    def test_combine_values_offset_is_non_zero(self):
        lower = [1, 2, 3]
        higher = [1, 2, 3, 4]
        self.assertEqual(iv.combine_values(lower, higher, 2), [1, 2, 4, 2, 3, 4])

    def test_IndexedValues_combine_return_new_IndexedValues(self):
        first = iv.IndexedValues()
        second = iv.IndexedValues()
        third = first.combine(second)
        self.assertNotEqual(first, second)
        self.assertNotEqual(third, second)
        self.assertNotEqual(first, third)
        first._values[0] = 5
        second._values[0] = 6
        self.assertEqual(third.raw_values, [2])
        self.assertIsInstance(third, iv.IndexedValues)

    def test_IndexedValues_combine_out_of_range_of_each_other(self):
        self.assert_combine((3, [1, 2, 3]),
                            (7, [4, 5]),
                            [(3, 1), (4, 2), (5, 3), (7, 4), (8, 5)])

    def test_IndexedValues_combine_same_sized_obj_in_range_of_each_other(self):
        self.assert_combine((3, [1, 2]),
                            (4, [4, 5]),
                            [(3, 1), (4, 6), (5, 5)])

    def test_IndexedValues_combine_first_larger_than_second(self):
        self.assert_combine((3, [1, 2, 3, 4, 5]),
                            (4, [1, 2, 3]),
                            [(3, 1), (4, 3), (5, 5), (6, 7), (7, 5)])

    def test_IndexedValues_combine_commutative(self):
        first = iv.IndexedValues(1, [2, 3, 4])
        second = iv.IndexedValues(2, [3, 4, 5, 6])
        self.assertEqual(first.combine(second).get_items(), second.combine(first).get_items())

    def test_add_many_empty(self):
        self.assertEqual(iv.add_many(), 0)

    def test_add_many_non_empty(self):
        self.assertEqual(iv.add_many(-1, 0, 1, 2, 3), 5)

    def test_get_events_list_normal_case(self):
        occurrences = 3
        new_size = 6
        offset = 2
        event_list = iv.get_events_list([1, 2, 3], occurrences, new_size, offset)
        self.assertEqual(event_list, [0, 0, 3, 6, 9, 0])

    def test_get_events_list_empty(self):
        occurrences = 3
        new_size = 6
        offset = 2
        event_list = iv.get_events_list([], occurrences, new_size, offset)
        self.assertEqual(event_list, [0, 0, 0, 0, 0, 0])

    def test_get_events_list_occurrences_are_one(self):
        occurrences = 1
        new_size = 6
        offset = 2
        event_list = iv.get_events_list([1, 2, 3], occurrences, new_size, offset)
        self.assertEqual(event_list, [0, 0, 1, 2, 3, 0])

    def test_IndexedValues_combine_with_events_list_normal_case(self):
        test = iv.IndexedValues(5, [1, 2, 1])
        events = [(1, 2), (2, 1)]
        """
        [2, 4, 2, 0] +
        [0, 1, 2, 1]
        """
        self.assert_indexed_values(test.combine_with_events_list(events), 6, [2, 5, 4, 1])

    def test_IndexedValues_combine_with_events_list_gaps_in_list(self):
        test = iv.IndexedValues(5, [1, 2, 1])
        events = [(1, 2), (3, 1)]
        """
        [2, 4, 2, 0, 0] +
        [0, 0, 1, 2, 1]
        """
        self.assert_indexed_values(test.combine_with_events_list(events), 6, [2, 4, 3, 2, 1])

    def test_IndexedValues_combine_with_events_list_negative_events(self):
        test = iv.IndexedValues(5, [1, 2, 1])
        events = [(-1, 2), (0, 1)]
        """
        [2, 4, 2, 0] +
        [0, 1, 2, 1]
        """
        self.assert_indexed_values(test.combine_with_events_list(events), 4, [2, 5, 4, 1])


if __name__ == '__main__':
    unittest.main()
