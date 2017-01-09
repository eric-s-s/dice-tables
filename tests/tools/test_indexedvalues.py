# pylint: disable=missing-docstring, invalid-name, too-many-public-methods, line-too-long

"""test indexedlist"""
from __future__ import absolute_import

import unittest

from dicetables.tools import indexedvalues as iv


class TestIndexedValues(unittest.TestCase):

    def assert_indexed_values(self, indexed_values, start_index, values):
        self.assertEqual(indexed_values.start_index, start_index)
        self.assertEqual(indexed_values.raw_values, values)

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

    def test_generated_indexed_values(self):
        test = iv.generate_indexed_values([(1, 1), (2, 2)])
        self.assert_indexed_values(test, 1, [1, 2])

    def test_generated_indexed_values_gap_in_list(self):
        test = iv.generate_indexed_values([(1, 1), (3, 2), (5, 5)])
        self.assert_indexed_values(test, 1, [1, 0, 2, 0, 5])

    def test_generate_indexed_values_from_dict(self):
        test = iv.generate_indexed_values_from_dict({1: 1})
        self.assert_indexed_values(test, 1, [1])

    def test_generate_indexed_values_from_dict_gap_in_values(self):
        test = iv.generate_indexed_values_from_dict({5: 1, 3: 3, 1: 1})
        self.assert_indexed_values(test, 1, [1, 0, 3, 0, 1])

    def test_IndexedValues_init(self):
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

    def test_IndexedValues_get_dict_single_value(self):
        test = iv.IndexedValues(5, [2])
        self.assertEqual(test.get_dict(), {5: 2})

    def test_IndexedValues_get_dict_does_not_include_zeroes(self):
        test = iv.IndexedValues(1, [2, 0, 3])
        self.assertEqual(test.get_dict(), {1: 2, 3: 3})

    def test_indexedValues_get_value_at_key_within_range(self):
        test = iv.IndexedValues(3, [1, 2, 3])
        self.assertEqual(test.get_value_at_key(4), 2)

    def test_indexedValues_get_value_at_key_out_of_range(self):
        test = iv.IndexedValues(3, [1, 2, 3])
        self.assertEqual(test.get_value_at_key(2), 0)
        self.assertEqual(test.get_value_at_key(6), 0)

    def test_IndexedValues_change_list_len_with_zeroes_max_size_offset_zero(self):
        self.assertEqual(iv.change_list_len_with_zeroes([1, 2, 3], 3, 0), [1, 2, 3])

    def test_change_list_len_with_zeroes_other_case_offset_zero(self):
        self.assertEqual(iv.change_list_len_with_zeroes([1, 2, 3], 5, 0), [1, 2, 3, 0, 0])

    def test_change_list_len_with_zeroes_no_adds(self):
        self.assertEqual(iv.change_list_len_with_zeroes([1, 2, 3], 3, 0), [1, 2, 3])

    def test_change_list_len_with_zeroes_offset_and_zeros_is_total_size(self):
        self.assertEqual(iv.change_list_len_with_zeroes([1, 2, 3], 5, 2), [0, 0, 1, 2, 3])

    def test_change_list_len_with_zeroes_offset_and_zeros_lt_total_size(self):
        self.assertEqual(iv.change_list_len_with_zeroes([1, 2, 3], 10, 2), [0, 0, 1, 2, 3, 0, 0, 0, 0, 0])

    def test_equalize_len_demonstration(self):
        lower = [1, 2, 3, 4, 5, 6]
        higher = [1, 2, 3]
        diff_in_start_indices = 2
        total_size = 6
        self.assertEqual(iv.change_list_len_with_zeroes(lower, total_size, 0),
                         [1, 2, 3, 4, 5, 6])
        self.assertEqual(iv.change_list_len_with_zeroes(higher, total_size, diff_in_start_indices),
                         [0, 0, 1, 2, 3, 0])

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
        input_dict = {1: 2, 2: 1}
        """
        [2, 4, 2, 0] +
        [0, 1, 2, 1]
        """
        self.assert_indexed_values(test.combine_with_dictionary(input_dict), 6, [2, 5, 4, 1])

    def test_IndexedValues_combine_with_events_list_gaps_in_list(self):
        test = iv.IndexedValues(5, [1, 2, 1])
        input_dict = {1: 2, 3: 1}
        """
        [2, 4, 2, 0, 0] +
        [0, 0, 1, 2, 1]
        """
        self.assert_indexed_values(test.combine_with_dictionary(input_dict), 6, [2, 4, 3, 2, 1])

    def test_IndexedValues_combine_with_events_list_negative_events(self):
        test = iv.IndexedValues(5, [1, 2, 1])
        input_dict = {-1: 2, 0: 1}
        """
        [2, 4, 2, 0] +
        [0, 1, 2, 1]
        """
        self.assert_indexed_values(test.combine_with_dictionary(input_dict), 4, [2, 5, 4, 1])


if __name__ == '__main__':
    unittest.main()
