# pylint: disable=missing-docstring, invalid-name, too-many-public-methods
"""tests for the tableinfo.py module"""

from __future__ import absolute_import

import unittest
from decimal import Decimal
from dicetables import AdditiveEvents
import dicetables.tableinfo as ti


class TestTableInfo(unittest.TestCase):

    def assert_format_number(self, number, number_str):
        self.assertEqual(ti.NumberFormatter().format(number), number_str)

    def test_NumberFormatter_init_defaults(self):
        test = ti.NumberFormatter()
        self.assertEqual(test.min_fixed_pt_exp, -3)
        self.assertEqual(test.shown_digits, 4)
        self.assertEqual(test.max_comma_exp, 6)

    def test_NumberFormatter_show_digits(self):
        test = ti.NumberFormatter()
        test.shown_digits = 2.5
        self.assertEqual(test.shown_digits, 2)
        test.shown_digits = -5
        self.assertEqual(test.shown_digits, 1)

    def test_NumberFormatter_comma_cutoff(self):
        test = ti.NumberFormatter()
        test.max_comma_exp = 2.5
        self.assertEqual(test.max_comma_exp, 2)
        test.max_comma_exp = -5
        self.assertEqual(test.max_comma_exp, -1)

    def test_NumberFormatter_fixed_pt_cutoff(self):
        test = ti.NumberFormatter()
        test.min_fixed_pt_exp = -5
        self.assertEqual(test.min_fixed_pt_exp, -5)
        test.min_fixed_pt_exp = 5
        self.assertEqual(test.min_fixed_pt_exp, 0)
        test.min_fixed_pt_exp = -5.2
        self.assertEqual(test.min_fixed_pt_exp, -5)

    def test_NumberFormatter_init_out_of_range(self):
        test = ti.NumberFormatter(-1, -2, 1)
        self.assertEqual(test.shown_digits, 1)
        self.assertEqual(test.max_comma_exp, -1)
        self.assertEqual(test.min_fixed_pt_exp, 0)

    def test_NumberFormatter_init_in_range(self):
        test = ti.NumberFormatter(5, 4, -5)
        self.assertEqual(test.min_fixed_pt_exp, -5)
        self.assertEqual(test.shown_digits, 5)
        self.assertEqual(test.max_comma_exp, 4)

    def test_NumberFormatter_show_digits_setter_getter(self):
        test = ti.NumberFormatter()
        test.shown_digits = 100
        self.assertEqual(test.shown_digits, 100)

    def test_NumberFormatter_min_fixed_pt_exp_setter_getter(self):
        test = ti.NumberFormatter()
        test.min_fixed_pt_exp = 100
        self.assertEqual(test.min_fixed_pt_exp, 0)

    def test_NumberFormatter_max_comma_exp_setter_getter(self):
        test = ti.NumberFormatter()
        test.max_comma_exp = 100
        self.assertEqual(test.max_comma_exp, 100)

    def test_NumberFormatter_max_comma_exp_ridiculous_case_safety(self):
        test = ti.NumberFormatter()
        test.max_comma_exp = 1000
        num = int('9'*999)
        self.assertEqual(test.format(num), '{:,}'.format(num))

    def test_NumberFormatter_get_exponent_below_one_big_small_pos_neg_no_rounding(self):
        formatter = ti.NumberFormatter()
        self.assertEqual(formatter.get_exponent(1e-5), -5)
        self.assertEqual(formatter.get_exponent(-1e-5), -5)
        self.assertEqual(formatter.get_exponent(Decimal('1e-1000')), -1000)
        self.assertEqual(formatter.get_exponent(Decimal('-1e-1000')), -1000)

    def test_NumberFormatter_get_exponent_above_one_float_pos_neg_no_rounding(self):
        formatter = ti.NumberFormatter()
        self.assertEqual(formatter.get_exponent(1e+5), 5)
        self.assertEqual(formatter.get_exponent(-1e+5), 5)
        self.assertEqual(formatter.get_exponent(Decimal('1e+1000')), 1000)
        self.assertEqual(formatter.get_exponent(Decimal('-1e+1000')), 1000)

    def test_NumberFormatter_get_exponent_int_big_small_pos_neg(self):
        formatter = ti.NumberFormatter()
        self.assertEqual(formatter.get_exponent(50), 1)
        self.assertEqual(formatter.get_exponent(-50), 1)
        self.assertEqual(formatter.get_exponent(5*10**1000), 1000)
        self.assertEqual(formatter.get_exponent(-5*10**1000), 1000)

    def test_NumberFormatter_get_exponent_rounding(self):
        formatter = ti.NumberFormatter()
        self.assertEqual(formatter.get_exponent(99.95), 1)
        formatter.shown_digits = 3
        self.assertEqual(formatter.get_exponent(99.95), 2)

    def test_NumberFormatter_format_as_fixed_point_no_round(self):
        formatter = ti.NumberFormatter()
        self.assertEqual(formatter.format_as_fixed_point(1.2e-5, -5), '0.00001200')

    def test_NumberFormatter_format_as_fixed_point_round(self):
        formatter = ti.NumberFormatter()
        exp = formatter.get_exponent(9.9999e-5)
        self.assertEqual(formatter.format_as_fixed_point(9.9999e-5, exp), '0.0001000')

    def test_NumberFormatter_format_as_fixed_point_neg(self):
        formatter = ti.NumberFormatter()
        exp = formatter.get_exponent(-9.9999e-5)
        self.assertEqual(formatter.format_as_fixed_point(-9.9999e-5, exp), '-0.0001000')

    def test_NumberFormatter_format_using_commas_no_round(self):
        formatter = ti.NumberFormatter()
        formatter.shown_digits = 10
        exp = formatter.get_exponent(9999.99)
        self.assertEqual(formatter.format_using_commas(9999.99, exp), '9,999.990000')

    def test_NumberFormatter_format_using_commas_round(self):
        formatter = ti.NumberFormatter()
        exp = formatter.get_exponent(9999.99)
        self.assertEqual(formatter.format_using_commas(9999.99, exp), '10,000')
        exp = formatter.get_exponent(99.999)
        self.assertEqual(formatter.format_using_commas(99.999, exp), '100.0')

    def test_NumberFormatter_format_using_commas_shows_number_as_int_if_too_long(self):
        formatter = ti.NumberFormatter()
        formatter.shown_digits = 5
        exp = formatter.get_exponent(123456.789)
        self.assertEqual(formatter.format_using_commas(123456.789, exp), '123,457')

    def test_NumberFormatter_format_using_commas_negative_number(self):
        formatter = ti.NumberFormatter()
        exp = formatter.get_exponent(-123456.789)
        self.assertEqual(formatter.format_using_commas(-123456.789, exp), '-123,457')

    def test_NumberFormatter_format_using_commas_small_int(self):
        formatter = ti.NumberFormatter()
        exp = formatter.get_exponent(12)
        self.assertEqual(formatter.format_using_commas(12, exp), '12')

    def test_NumberFormatter_format_using_commas_shows_whole_int(self):
        formatter = ti.NumberFormatter()
        formatter.shown_digits = 5
        exp = formatter.get_exponent(123456789)
        self.assertEqual(formatter.format_using_commas(123456789, exp), '123,456,789')

    def test_remove_extra_zero_Decimal_regression_test(self):
        """
        why does formatting a number stick in that damn extra zero???  Decimal has figured this out.
        it's not that hard. arrrrrggggghhhhhhhh!
        """
        float_format = '{:.2e}'.format(123)
        dec_format = '{:.2e}'.format(Decimal(123))
        dec_zero_exponent = '{:.2e}'.format(Decimal(1))
        self.assertEqual(float_format, '1.23e+02')
        self.assertEqual(dec_format, '1.23e+2')

        self.assertEqual(ti.remove_extra_zero_from_exponent(float_format), '1.23e+2')
        self.assertEqual(ti.remove_extra_zero_from_exponent(dec_format), '1.23e+2')
        self.assertEqual(ti.remove_extra_zero_from_exponent(dec_zero_exponent), '1.00e+0')

    def test_remove_extra_zero_from_exponent(self):
        self.assertEqual(ti.remove_extra_zero_from_exponent(str(1.23e-5)), '1.23e-5')
        self.assertEqual(ti.remove_extra_zero_from_exponent('{:.2e}'.format(123000)),
                         '1.23e+5')
        self.assertEqual(ti.remove_extra_zero_from_exponent('{:.2e}'.format(1)),
                         '1.00e+0')

    def test_NumberFormatter_format_as_exponent_not_remove_extra_zero(self):
        formatter = ti.NumberFormatter()
        test = 1.23456789 * 10 ** 12
        exp = formatter.get_exponent(test)
        self.assertEqual(formatter.format_as_exponent(test, exp), '1.235e+12')

    def test_NumberFormatter_format_as_exponent_remove_extra_zero(self):
        formatter = ti.NumberFormatter()
        test = 1.23456789*10**5
        exp = formatter.get_exponent(test)
        self.assertEqual('{:.3e}'.format(test), '1.235e+05')
        self.assertEqual(formatter.format_as_exponent(test, exp), '1.235e+5')

    def test_NumberFormatter_format_as_exponent_negative_number(self):
        formatter = ti.NumberFormatter()
        test = -1.23456789*10**5
        exp = formatter.get_exponent(test)
        self.assertEqual(formatter.format_as_exponent(test, exp), '-1.235e+5')

    def test_NumberFormatter_OverflowError_calls_new_func_does_not_raise_error(self):
        formatter = ti.NumberFormatter()
        test = 10 ** 5000
        exp = formatter.get_exponent(test)
        self.assertRaises(OverflowError, '{:e}'.format, test)
        self.assertEqual(formatter.format_as_exponent(test, exp), '1.000e+5000')

    def test_NumberFormatter_format_huge_int_pos_rounds(self):
        formatter = ti.NumberFormatter()
        test_1 = 123449*10**500
        test_2 = 123451*10**500
        exp = formatter.get_exponent(test_1)
        self.assertEqual(formatter.format_huge_int(test_1, exp), '1.234e+505')
        self.assertEqual(formatter.format_huge_int(test_2, exp), '1.235e+505')

    def test_NumberFormatter_format_huge_int_neg_rounds(self):
        formatter = ti.NumberFormatter()
        test_1 = -123449*10**500
        test_2 = -123451*10**500
        exp = formatter.get_exponent(test_1)
        self.assertEqual(formatter.format_huge_int(test_1, exp), '-1.234e+505')
        self.assertEqual(formatter.format_huge_int(test_2, exp), '-1.235e+505')

    def test_NumberFormatter_format_huge_int_round_to_next_power(self):
        formatter = ti.NumberFormatter()
        test = 999951*10**500
        exp = formatter.get_exponent(test)
        self.assertEqual(formatter.format_huge_int(test, exp), '1.000e+506')

    def test_NumberFormatter_format_number_min_fixed_pt_exp_at_zero(self):
        test = ti.NumberFormatter()
        test.min_fixed_pt_exp = 0
        self.assertEqual(test.format(0.1), '1.000e-1')

    def test_NumberFormatter_format_number_min_fixed_pt_exp_at_zero_max_comma_exp_at_zero(self):
        test = ti.NumberFormatter()
        test.min_fixed_pt_exp = 0
        test.max_comma_exp = 0
        self.assertEqual(test.format(0.1), '1.000e-1')

        self.assertEqual(test.format(1.0), '1.000')
        self.assertEqual(test.format(1), '1')

        self.assertEqual(test.format(10.0), '1.000e+1')
        self.assertEqual(test.format(10), '1.000e+1')

    def test_NumberFormatter_format_number_max_comma_exp_at_neg_one(self):
        test = ti.NumberFormatter()
        test.max_comma_exp = -1
        self.assertEqual(test.format(0.1), '0.1000')
        self.assertEqual(test.format(1.0), '1.000e+0')
        self.assertEqual(test.format(1), '1.000e+0')
        self.assertEqual(test.format(10.0), '1.000e+1')

    def test_NumberFormatter_format_number_zero(self):
        self.assert_format_number(0, '0')

    def test_NumberFormatter_format_number_edge_of_min_fixed_pt_exp(self):
        self.assert_format_number(0.000999949, '9.999e-4')
        self.assert_format_number(0.000999951, '0.001000')

    def test_NumberFormatter_format_number_edge_of_one(self):
        self.assert_format_number(0.999949, '0.9999')
        self.assert_format_number(0.999951, '1.000')

    def test_NumberFormatter_format_number_edge_of_max_comma_exp_int(self):
        self.assert_format_number(9999999, '9,999,999')

    def test_NumberFormatter_format_number_edge_of_max_comma_exp_float(self):
        self.assert_format_number(9999999., '1.000e+7')
        self.assert_format_number(9999499., '9,999,499')
        self.assert_format_number(9999501., '1.000e+7')

    def test_NumberFormatter_format_number_at_edge_of_max_commas_exp_with_large_show_digits(self):
        formatter = ti.NumberFormatter()
        formatter.shown_digits = 10
        nine_digits = 9999999.99
        self.assertEqual(formatter.format(nine_digits), '9,999,999.990')
        formatter.shown_digits = 8
        self.assertEqual(formatter.format(nine_digits), '1.0000000e+7')

# todo start graphdataarea
    def test_GraphDataGenerator_init_default(self):
        test = ti.GraphDataGenerator()
        self.assertTrue(test.include_zeroes)
        self.assertTrue(test.percent)
        self.assertFalse(test.exact)

    def test_get_pts_list_false(self):
        table = AdditiveEvents({1: 1, 3: 1})
        self.assertEqual(ti.get_raw_graph_points(table, False), [(1, 1), (3, 1)])

    def test_get_pts_list_True(self):
        table = AdditiveEvents({1: 1, 3: 1})
        self.assertEqual(ti.get_raw_graph_points(table, True), [(1, 1), (2, 0), (3, 1)])

    def test_graph_pts_adds_zeroes(self):
        table = AdditiveEvents({1: 1, 3: 1})
        self.assertEqual(ti.graph_pts(table, percent=False),
                         [(1, 2, 3), (1, 0, 1)])

    def test_graph_pts_doesnot_add_zeroes_on_request(self):
        table = AdditiveEvents({1: 1, 3: 1})
        self.assertEqual(ti.graph_pts(table, percent=False, include_zeroes=False),
                         [(1, 3), (1, 1)])

    def test_graph_pts_return_percent(self):
        table = AdditiveEvents({1: 1, 3: 3})
        self.assertEqual(ti.graph_pts(table, percent=True),
                         [(1, 2, 3), (25, 0, 75)])

    def test_graph_pts_returns_percent_with_large_int_values(self):
        table = AdditiveEvents({1: 10 ** 1000, 3: 3 * 10 ** 1000})
        self.assertEqual(ti.graph_pts(table), [(1, 2, 3), (25, 0, 75)])

    def test_graph_pts_returns_xy_axes_on_request(self):
        table = AdditiveEvents({1: 1, 3: 3})
        self.assertEqual(ti.graph_pts(table, axes=True), [(1, 2, 3), (25, 0, 75)])

    def test_graph_pts_returns_xypts_on_request(self):
        table = AdditiveEvents({1: 1, 3: 3})
        self.assertEqual(ti.graph_pts(table, axes=False),
                         [(1, 25), (2, 0), (3, 75)])

    def test_graph_pts_not_exact_x_vals_equals_exact_x_vals(self):
        table = AdditiveEvents({1: 2, 3: 4, 5: 6})
        self.assertEqual(ti.graph_pts(table, exact=True)[0],
                         ti.graph_pts(table, exact=False)[0])

    def test_graph_pts_not_exact_equals_exact_to_ten_dec_places(self):
        table = AdditiveEvents(dict([(num, num ** 2) for num in range(1000)]))
        exact_y = ti.graph_pts(table, exact=True)[1]
        inexact_y = ti.graph_pts(table, exact=False)[1]
        for index in range(len(exact_y)):
            self.assertAlmostEqual(exact_y[index], inexact_y[index], places=10)

    def test_graph_pts_overflow_for_small_numbers(self):
        table = AdditiveEvents({1: 1, 3: 1})
        self.assertEqual(ti.graph_pts_overflow(table), ([(1, 2, 3), (1, 0, 1)], '1'))

    def test_graph_pts_overflow_for_larg_numbers(self):
        table = AdditiveEvents({1: 10 ** 200, 2: 1})
        self.assertEqual(ti.graph_pts_overflow(table),
                         ([(1, 2), (10 ** 200, 1)], '1'))

    def test_graph_pts_overflow_for_very_large_numbers(self):
        table = AdditiveEvents({1: 10 ** 2000, 2: 1})
        self.assertEqual(ti.graph_pts_overflow(table),
                         ([(1, 2), (10 ** 4, 0)], '1.0e+1996'))

# TODO end graphdataarea

    def test_full_table_string_include_zeroes_true(self):
        table = AdditiveEvents({1: 1, 3: 1})
        self.assertEqual(ti.full_table_string(table, include_zeroes=True),
                         '1: 1\n2: 0\n3: 1\n')

    def test_full_table_string_include_zeroes_False(self):
        table = AdditiveEvents({1: 1, 3: 1})
        self.assertEqual(ti.full_table_string(table, include_zeroes=False),
                         '1: 1\n3: 1\n')

    def test_full_table_string_right_justifies_all_values(self):
        table = AdditiveEvents({1: 10, 10: 200, 1000: 3000})
        self.assertEqual(ti.full_table_string(table, include_zeroes=False),
                         '   1: 10\n  10: 200\n1000: 3,000\n')

    def test_full_table_string_edge_case(self):
        table = AdditiveEvents({0: 1})
        self.assertEqual(ti.full_table_string(table), '0: 1\n')

    def test_ascii_graph_helper_for_table_under_80(self):
        result = ti.ascii_graph_helper(AdditiveEvents({1: 5, 2: 80}))
        expected = [(1, '1:{}'.format(5 * 'x')), (2, '2:{}'.format(80 * 'x')),
                    (None, 'each x represents 1 occurrence')]
        self.assertEqual(result, expected)

    def test_ascii_graph_helper_for_table_over_80(self):
        result = ti.ascii_graph_helper(AdditiveEvents({1: 5, 2: 8000}))
        expected = [(1, '1:'), (2, '2:{}'.format(80 * 'x')),
                    (None, 'each x represents 100.0 occurrences')]
        self.assertEqual(result, expected)

    def test_ascii_graph_justifies_right_for_values(self):
        result = ti.ascii_graph_helper(AdditiveEvents({1: 1, 2000: 1}))
        expected = [(1, '   1:x'), (2000, '2000:x'),
                    (None, 'each x represents 1 occurrence')]
        self.assertEqual(result, expected)

    def test_ascii_graph_works(self):
        result = ti.ascii_graph(AdditiveEvents({1: 1, 2: 1}))
        expected = '1:x\n2:x\neach x represents 1 occurrence'
        self.assertEqual(result, expected)

    def test_ascii_graph_truncated_when_no_truncating(self):
        result = ti.ascii_graph_truncated(AdditiveEvents({1: 1, 2: 1}))
        expected = '1:x\n2:x\neach x represents 1 occurrence'
        self.assertEqual(result, expected)

    def test_ascii_graph_truncated_when_truncating_one_side(self):
        result = ti.ascii_graph_truncated(AdditiveEvents({1: 1, 2: 1, 3: 8000}))
        expected = ('3:{}\neach x represents 100.0 occurrences\nnot included: 1-2'
                    .format(80 * 'x'))
        self.assertEqual(result, expected)

    def test_ascii_graph_truncated_when_truncating_two_sides(self):
        result = ti.ascii_graph_truncated(AdditiveEvents({1: 1, 2: 1, 3: 8000, 4: 1}))
        expected = ('3:{}\n'.format(80 * 'x') +
                    'each x represents 100.0 occurrences\n' +
                    'not included: 1-2 and 4')
        self.assertEqual(result, expected)

    def test_list_to_string_returns_single_number(self):
        self.assertEqual(ti.get_string_for_sequence([1, 1, 1]), '1')

    def test_list_to_string_puts_parentheses_around_negative_numbers(self):
        self.assertEqual(ti.get_string_for_sequence([-1]), '(-1)')

    def test_list_to_string_returns_proper_output_for_a_run_of_numbers(self):
        self.assertEqual(ti.get_string_for_sequence([1, 1, 2, 3, 4, 5]), '1-5')

    def test_list_to_string_returns_values_separated_by_commas(self):
        the_list = [-5, -4, -3, -1, 0, 1, 2, 3, 5]
        self.assertEqual(ti.get_string_for_sequence(the_list), '(-5)-(-3), (-1)-3, 5')

    def test_list_to_string_returns_numbers_with_commas(self):
        the_list = [-1234567, 1234567]
        self.assertEqual(ti.get_string_for_sequence(the_list), '(-1,234,567), 1,234,567')

    def test_stats_not_in_table(self):
        result = ti.stats(AdditiveEvents({1: 1}), [2])
        expected = ('2', '0', '1', 'infinity', '0')
        self.assertEqual(result, expected)

    def test_stats_does_not_repeat_values(self):
        result = ti.stats(AdditiveEvents({1: 1}), [1, 1])
        expected = ('1', '1', '1', '1.000', '100.0')
        self.assertEqual(result, expected)

    def test_stats_includes_values_not_in_table(self):
        result = ti.stats(AdditiveEvents({1: 1, 2: 1}), [0, 1])
        expected = ('0-1', '1', '2', '2.000', '50.00')
        self.assertEqual(result, expected)

    def test_stats_works_for_large_values(self):
        result = ti.stats(AdditiveEvents({1: 10 ** 1000, 2: (10 ** 1002 - 10 ** 1000)}), [1])
        expected = ('1', '1.000e+1000', '1.000e+1002', '100.0', '1.000')
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
