from __future__ import absolute_import

import unittest

import dicetables.tools.listtostring as l2s


class TestListToString(unittest.TestCase):
    def test_format_for_sequence_string_adds_commas(self):
        self.assertEqual(l2s.format_for_sequence_str(10), '10')
        self.assertEqual(l2s.format_for_sequence_str(1000000), '1,000,000')

    def test_format_for_sequence_string_negative_numbers(self):
        self.assertEqual(l2s.format_for_sequence_str(-2), '(-2)')
        self.assertEqual(l2s.format_for_sequence_str(-2000), '(-2,000)')

    def test_format_one_sequence_single_number(self):
        self.assertEqual(l2s.format_one_sequence([1]), '1')

    def test_format_one_sequence_first_and_last_same_number(self):
        self.assertEqual(l2s.format_one_sequence([1, 2, 3, 1]), '1')

    def test_format_one_sequence_first_and_last_different(self):
        self.assertEqual(l2s.format_one_sequence([-1, 3, 2]), '(-1)-2')

    def test_gap_is_larger_than_one_true(self):
        self.assertTrue(l2s.gap_is_larger_than_one([[1, 2, 3], [4, 5]], 7))

    def test_gap_is_larger_than_one_false(self):
        self.assertFalse(l2s.gap_is_larger_than_one([[1, 2, 3], [4, 5]], 5))
        self.assertFalse(l2s.gap_is_larger_than_one([[1, 2, 3], [4, 5]], 6))

    def test_split_at_gaps_larger_than_one_empty_list(self):
        self.assertEqual(l2s.split_at_gaps_larger_than_one([]), [])

    def test_split_at_gaps_larger_than_one_one_element(self):
        self.assertEqual(l2s.split_at_gaps_larger_than_one([1]), [[1]])

    def test_split_at_gaps_larger_than_one_same_element(self):
        self.assertEqual(l2s.split_at_gaps_larger_than_one([1, 1, 1, 1]), [[1, 1, 1, 1]])

    def test_split_at_gaps_larger_than_one_not_large_gaps(self):
        self.assertEqual(l2s.split_at_gaps_larger_than_one([1, 1, 2, 2, 3]), [[1, 1, 2, 2, 3]])

    def test_split_at_gaps_larger_than_one_all_large_gaps(self):
        self.assertEqual(l2s.split_at_gaps_larger_than_one([1, 3, 9]), [[1], [3], [9]])

    def test_split_at_gaps_larger_than_one_mixed_case(self):
        self.assertEqual(l2s.split_at_gaps_larger_than_one([1, 1, 2, 5, 6, 9]), [[1, 1, 2], [5, 6], [9]])

    def test_split_at_gaps_larger_than_one_mixed_case_negative_pos_zero(self):
        self.assertEqual(l2s.split_at_gaps_larger_than_one([-2, 0, 1, 2, 5, 6, 9]), [[-2], [0, 1, 2], [5, 6], [9]])

    def test_get_string_from_list_returns_single_number(self):
        self.assertEqual(l2s.get_string_from_list_of_ints([1, 1, 1]), '1')

    def test_get_string_from_list_puts_parentheses_around_negative_numbers(self):
        self.assertEqual(l2s.get_string_from_list_of_ints([-1]), '(-1)')

    def test_get_string_from_list_returns_proper_output_for_a_run_of_numbers(self):
        self.assertEqual(l2s.get_string_from_list_of_ints([1, 1, 2, 3, 4, 5]), '1-5')

    def test_get_string_from_list_returns_values_separated_by_commas(self):
        the_list = [-5, -4, -3, -1, 0, 1, 2, 3, 5]
        self.assertEqual(l2s.get_string_from_list_of_ints(the_list), '(-5)-(-3), (-1)-3, 5')

    def test_get_string_from_list_returns_numbers_with_commas(self):
        the_list = [-1234567, 1234567]
        self.assertEqual(l2s.get_string_from_list_of_ints(the_list), '(-1,234,567), 1,234,567')

    def test_get_string_from_list_returns_number_out_of_order(self):
        the_list = [5, 3, 7, 1, 3, 6, 8, 9, 10, 2]
        self.assertEqual(l2s.get_string_from_list_of_ints(the_list), '1-3, 5-10')


if __name__ == '__main__':
    unittest.main()
