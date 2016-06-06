# pylint: disable=missing-docstring, invalid-name, too-many-public-methods
'''tests for the tableinfo.py module'''

from __future__ import absolute_import


import unittest
from dicetables import LongIntTable
import dicetables.tableinfo as ti

class TestTableInfo(unittest.TestCase):
    def test_scinote_returns_exp_for_val_le_ten_to_neg_four(self):
        self.assertEqual(ti.scinote(10**-4), '1.000e-04')
    def test_scinote_returns_fixed_pt_for_val_gt_ten_to_neg_four(self):
        self.assertEqual(ti.scinote(10**-3), '0.001000')
    def test_scinote_edge_case_at_ten_to_neg_four(self):
        self.assertEqual(ti.scinote(9.99952*10**-4), '0.001000')
        self.assertEqual(ti.scinote(9.99949*10**-4), '9.999e-04')
    def test_scinote_returns_zero(self):
        self.assertEqual(ti.scinote(2*10**-500), '0.0')
    def test_scinote_returns_commaed_int_at_less_than_ten_million(self):
        self.assertEqual(ti.scinote(2300001), '2,300,001')
    def test_scinote_return_commaed_int_for_float_longer_than_dig_len(self):
        self.assertEqual(ti.scinote(1.234567e+6, 4), '1,234,567')
    def test_scinote_rounds_commaed_int_for_float_larger_than_dig_len(self):
        self.assertEqual(ti.scinote(1.2345675e+6, 4), '1,234,568')
    def test_scinote_as_above_with_negative_number(self):
        self.assertEqual(ti.scinote(-1.2345675e+6, 4), '-1,234,568')
    def test_scinote_rounds_commaed_float_for_dig_len_larger_than_tens_place(self):
        self.assertEqual(ti.scinote(123456.789, 8), '123,456.79')
    def test_scinote_doesnt_add_digits_when_dig_len_larger_than_int(self):
        self.assertEqual(ti.scinote(1234, 6), '1,234')
    def test_scinote_edge_case_at_10_to_7th_1(self):
        self.assertEqual(ti.scinote(9.999999999e+6, 10), '9,999,999.999')
    def test_scinote_edge_case_at_10_to_7th_2(self):
        self.assertEqual(ti.scinote(9.999999999e+6, 3), '1.00e+07')
    def test_scinote_edge_case_at_10_to_7th_3(self):
        self.assertEqual(ti.scinote(10000000), '1.000e+07')
    def test_scinote_edge_case_at_10_to_7th_negative_number_1(self):
        self.assertEqual(ti.scinote(-9.999999999e+6, 10), '-9,999,999.999')
    def test_scinote_edge_case_at_10_to_7th_negative_number_2(self):
        self.assertEqual(ti.scinote(-9.999999999e+6, 3), '-1.00e+07')
    def test_scinote_edge_case_at_10_to_7th_negative_number_3(self):
        self.assertEqual(ti.scinote(-10000000), '-1.000e+07')
    def test_scinote_returns_exponent_form_for_number_over_10_to_7th(self):
        self.assertEqual(ti.scinote(1.2345678e+7, 6), '1.23457e+07')
    def test_scinote_fills_zeros_to_dig_len_over_10_to_7th(self):
        self.assertEqual(ti.scinote(1.2e+7, 6), '1.20000e+07')
    def test_scinote_large_number(self):
        self.assertEqual(ti.scinote(5*10**1000, 4), '5.000e+1000')
    def test_scinote_large_number_negative(self):
        self.assertEqual(ti.scinote(-56*10**1000, 4), '-5.600e+1001')
    def test_scinote_large_number_rounds_like_it_should(self):
        self.assertEqual(ti.scinote(555551*10**1000, 4), '5.556e+1005')
    def test_scinote_annoying_edge_case_due_to_python_rounding_errors(self):
        #the issue is python rounds the binary approximation of the float
        #so it's not rounding 5.5550000000000 it's rounding a slightly
        #smaller binary number.
        self.assertEqual(ti.scinote(5555*10**1000, 3), '5.55e+1003')
        self.assertEqual(ti.scinote(-5555*10**1000, 3), '-5.55e+1003')

    def test_list_to_string_returns_single_number(self):
        self.assertEqual(ti.list_to_string([1, 1, 1]), '1')
    def test_list_to_string_puts_parentheses_around_negative_numbers(self):
        self.assertEqual(ti.list_to_string([-1]), '(-1)')
    def test_list_to_string_returns_proper_output_for_a_run_of_numbers(self):
        self.assertEqual(ti.list_to_string([1, 1, 2, 3, 4, 5]), '1-5')
    def test_list_to_string_returns_values_separated_by_commas(self):
        the_list = [-5, -4, -3, -1, 0, 1, 2, 3, 5]
        self.assertEqual(ti.list_to_string(the_list), '(-5)-(-3), (-1)-3, 5')

    def test_full_table_string_returns_empty_str_for_empty_table(self):
        self.assertEqual(ti.full_table_string(LongIntTable({})), '')
    def test_full_table_string_right_justifies_all_values_also_no_zeroes(self):
        table = LongIntTable({1:10, 10:200, 1000:3000})
        self.assertEqual(ti.full_table_string(table, zeroes=False),
                         '   1: 10\n  10: 200\n1000: 3,000\n')
    def test_full_table_string_includes_zeroes_as_requested(self):
        table = LongIntTable({1:1, 3:1})
        self.assertEqual(ti.full_table_string(table, zeroes=True),
                         '1: 1\n2: 0.0\n3: 1\n')

    def test_graph_pts_raises_error_for_empty_table(self):
        with self.assertRaises(ValueError) as cm:
            ti.graph_pts(LongIntTable({}))
        self.assertEqual(cm.exception.args[0], 'empty table')
    def test_graph_pts_adds_zeroes(self):
        table = LongIntTable({1: 1, 3: 1})
        self.assertEqual(ti.graph_pts(table, percent=False), ([1, 2, 3], [1, 0, 1]))
    def test_graph_pts_doesnot_add_zeroes_on_request(self):
        table = LongIntTable({1: 1, 3: 1})
        self.assertEqual(ti.graph_pts(table, percent=False, zeroes=False),
                         ([1, 3], [1, 1]))
    def test_graph_pts_return_percent(self):
        table = LongIntTable({1: 1, 3: 3})
        self.assertEqual(ti.graph_pts(table, percent=True),
                         ([1, 2, 3], [25, 0, 75]))
    def test_graph_pts_returns_percent_with_large_int_values(self):
        table = LongIntTable({1: 10**1000, 3: 3 * 10**1000})
        self.assertEqual(ti.graph_pts(table), ([1, 2, 3], [25, 0, 75]))
    def test_graph_pts_returns_xy_axes_on_request(self):
        table = LongIntTable({1:1, 3:3})
        self.assertEqual(ti.graph_pts(table, axes=True), ([1, 2, 3], [25, 0, 75]))
    def test_graph_pts_returns_xypts_on_request(self):
        table = LongIntTable({1: 1, 3: 3})
        self.assertEqual(ti.graph_pts(table, axes=False),
                         ([(1, 25), (2, 0), (3, 75)]))
    def test_graph_pts_overflow_for_small_numbers(self):
        table = LongIntTable({1: 1, 3: 1})
        self.assertEqual(ti.graph_pts_overflow(table), (([1, 2, 3], [1, 0, 1]), '1'))
    def test_graph_pts_overflow_for_larg_numbers(self):
        table = LongIntTable({1: 10**200, 2: 1})
        self.assertEqual(ti.graph_pts_overflow(table),
                         (([1, 2], [10**200, 1]), '1'))
    def test_graph_pts_overflow_for_very_large_numbers(self):
        table = LongIntTable({1:10**2000, 2:1})
        self.assertEqual(ti.graph_pts_overflow(table),
                         (([1, 2], [10**4, 0]), '1.0e+1996'))
    def test_graph_pts_overflow_raises_error_for_empty_table(self):
        with self.assertRaises(ValueError) as cm:
            ti.graph_pts_overflow(LongIntTable({}))
        self.assertEqual(cm.exception.args[0], 'empty table')

    def test_ascii_graph_helper_for_empty_table(self):
        empty_result = ti.ascii_graph_helper(LongIntTable({}))
        self.assertEqual(empty_result, [(None, 'each x represents 1 occurence')])
    def test_ascii_graph_helper_for_table_under_80(self):
        result = ti.ascii_graph_helper(LongIntTable({1: 5, 2: 80}))
        expected = [(1, '1:{}'.format(5 * 'x')), (2, '2:{}'.format(80 * 'x')),
                    (None, 'each x represents 1 occurence')]
        self.assertEqual(result, expected)
    def test_ascii_graph_helper_for_table_over_80(self):
        result = ti.ascii_graph_helper(LongIntTable({1: 5, 2: 8000}))
        expected = [(1, '1:'), (2, '2:{}'.format(80 * 'x')),
                    (None, 'each x represents 100.0 occurences')]
        self.assertEqual(result, expected)
    def tets_ascii_graph_justifies_right_for_values(self):
        result = ti.ascii_graph_helper(LongIntTable({1: 1, 2000: 1}))
        expected = [(1, '   1:x'), (2, '2000:x'),
                    (None, 'each x represents 1 occurence')]
        self.assertEqual(result, expected)
    def test_ascii_graph_works(self):
        result = ti.ascii_graph(LongIntTable({1: 1, 2: 1}))
        expected = '1:x\n2:x\neach x represents 1 occurence'
        self.assertEqual(result, expected)
    def test_ascii_graph_truncated_when_no_truncating(self):
        result = ti.ascii_graph_truncated(LongIntTable({1: 1, 2: 1}))
        expected = '1:x\n2:x\neach x represents 1 occurence'
        self.assertEqual(result, expected)
    def test_ascii_graph_truncated_when_truncating_one_side(self):
        result = ti.ascii_graph_truncated(LongIntTable({1: 1, 2: 1, 3: 8000}))
        expected = ('3:{}\neach x represents 100.0 occurences\nnot included: 1-2'
                    .format(80 * 'x'))
        self.assertEqual(result, expected)
    def test_ascii_graph_truncated_when_truncating_two_sides(self):
        result = ti.ascii_graph_truncated(LongIntTable({1: 1, 2: 1, 3: 8000, 4: 1}))
        expected = ('3:{}\n'.format(80 * 'x') +
                    'each x represents 100.0 occurences\n' +
                    'not included: 1-2 and 4')
        self.assertEqual(result, expected)
    def test_stats_empty_table(self):
        result = ti.stats(LongIntTable({}), [1, 2, 3])
        expected = ('1-3', '0.0', '0.0', 'infinity', '0.0')
        self.assertEqual(result, expected)
    def test_stats_not_in_table(self):
        result = ti.stats(LongIntTable({1: 1}), [2])
        expected = ('2', '0.0', '1', 'infinity', '0.0')
        self.assertEqual(result, expected)
    def test_stats_does_not_repeat_values(self):
        result = ti.stats(LongIntTable({1: 1}), [1, 1])
        expected = ('1', '1', '1', '1.0', '100.0')
        self.assertEqual(result, expected)
    def test_stats_includes_values_not_in_table(self):
        result = ti.stats(LongIntTable({1: 1, 2: 1}), [0, 1])
        expected = ('0-1', '1', '2', '2.0', '50.0')
        self.assertEqual(result, expected)
    def test_stats_works_for_large_values(self):
        result = ti.stats(LongIntTable({1: 10**1000, 2: (10**1002-10**1000)}), [1])
        expected = ('1', '1.000e+1000', '1.000e+1002', '100.0', '1.0')
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()

