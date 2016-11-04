from __future__ import absolute_import

import unittest
from decimal import Decimal

from dicetables.tools import numberforamtter as nf


class TestTableInfo(unittest.TestCase):

    def assert_format_number(self, number, number_str):
        self.assertEqual(nf.NumberFormatter().format(number), number_str)

    def test_NumberFormatter_init_defaults(self):
        test = nf.NumberFormatter()
        self.assertEqual(test.min_fixed_pt_exp, -3)
        self.assertEqual(test.shown_digits, 4)
        self.assertEqual(test.max_comma_exp, 6)

    def test_NumberFormatter_show_digits(self):
        test = nf.NumberFormatter()
        test.shown_digits = 2.5
        self.assertEqual(test.shown_digits, 2)
        test.shown_digits = -5
        self.assertEqual(test.shown_digits, 1)

    def test_NumberFormatter_comma_cutoff(self):
        test = nf.NumberFormatter()
        test.max_comma_exp = 2.5
        self.assertEqual(test.max_comma_exp, 2)
        test.max_comma_exp = -5
        self.assertEqual(test.max_comma_exp, -1)

    def test_NumberFormatter_fixed_pt_cutoff(self):
        test = nf.NumberFormatter()
        test.min_fixed_pt_exp = -5
        self.assertEqual(test.min_fixed_pt_exp, -5)
        test.min_fixed_pt_exp = 5
        self.assertEqual(test.min_fixed_pt_exp, 0)
        test.min_fixed_pt_exp = -5.2
        self.assertEqual(test.min_fixed_pt_exp, -5)

    def test_NumberFormatter_init_out_of_range(self):
        test = nf.NumberFormatter(-1, -2, 1)
        self.assertEqual(test.shown_digits, 1)
        self.assertEqual(test.max_comma_exp, -1)
        self.assertEqual(test.min_fixed_pt_exp, 0)

    def test_NumberFormatter_init_in_range(self):
        test = nf.NumberFormatter(5, 4, -5)
        self.assertEqual(test.min_fixed_pt_exp, -5)
        self.assertEqual(test.shown_digits, 5)
        self.assertEqual(test.max_comma_exp, 4)

    def test_NumberFormatter_show_digits_setter_getter(self):
        test = nf.NumberFormatter()
        test.shown_digits = 100
        self.assertEqual(test.shown_digits, 100)

    def test_NumberFormatter_min_fixed_pt_exp_setter_getter(self):
        test = nf.NumberFormatter()
        test.min_fixed_pt_exp = 100
        self.assertEqual(test.min_fixed_pt_exp, 0)

    def test_NumberFormatter_max_comma_exp_setter_getter(self):
        test = nf.NumberFormatter()
        test.max_comma_exp = 100
        self.assertEqual(test.max_comma_exp, 100)

    def test_NumberFormatter_max_comma_exp_ridiculous_case_safety(self):
        test = nf.NumberFormatter()
        test.max_comma_exp = 1000
        num = int('9'*999)
        self.assertEqual(test.format(num), '{:,}'.format(num))

    def test_NumberFormatter_get_exponent_below_one_big_small_pos_neg_no_rounding(self):
        formatter = nf.NumberFormatter()
        self.assertEqual(formatter.get_exponent(1e-5), -5)
        self.assertEqual(formatter.get_exponent(-1e-5), -5)
        self.assertEqual(formatter.get_exponent(Decimal('1e-1000')), -1000)
        self.assertEqual(formatter.get_exponent(Decimal('-1e-1000')), -1000)

    def test_NumberFormatter_get_exponent_above_one_float_pos_neg_no_rounding(self):
        formatter = nf.NumberFormatter()
        self.assertEqual(formatter.get_exponent(1e+5), 5)
        self.assertEqual(formatter.get_exponent(-1e+5), 5)
        self.assertEqual(formatter.get_exponent(Decimal('1e+1000')), 1000)
        self.assertEqual(formatter.get_exponent(Decimal('-1e+1000')), 1000)

    def test_NumberFormatter_get_exponent_int_big_small_pos_neg(self):
        formatter = nf.NumberFormatter()
        self.assertEqual(formatter.get_exponent(50), 1)
        self.assertEqual(formatter.get_exponent(-50), 1)
        self.assertEqual(formatter.get_exponent(5*10**1000), 1000)
        self.assertEqual(formatter.get_exponent(-5*10**1000), 1000)

    def test_NumberFormatter_get_exponent_rounding(self):
        formatter = nf.NumberFormatter()
        self.assertEqual(formatter.get_exponent(99.95), 1)
        formatter.shown_digits = 3
        self.assertEqual(formatter.get_exponent(99.95), 2)

    def test_NumberFormatter_format_as_fixed_point_no_round(self):
        formatter = nf.NumberFormatter()
        self.assertEqual(formatter.format_fixed_point(1.2e-5), '0.00001200')

    def test_NumberFormatter_format_as_fixed_point_round(self):
        formatter = nf.NumberFormatter()
        self.assertEqual(formatter.format_fixed_point(9.9999e-5), '0.0001000')

    def test_NumberFormatter_format_as_fixed_point_neg(self):
        formatter = nf.NumberFormatter()
        self.assertEqual(formatter.format_fixed_point(-9.9999e-5), '-0.0001000')

    def test_NumberFormatter_format_using_commas_no_round(self):
        formatter = nf.NumberFormatter()
        formatter.shown_digits = 10
        self.assertEqual(formatter.format_commaed(9999.99), '9,999.990000')

    def test_NumberFormatter_format_using_commas_round(self):
        formatter = nf.NumberFormatter()
        self.assertEqual(formatter.format_commaed(9999.99), '10,000')
        self.assertEqual(formatter.format_commaed(99.999), '100.0')

    def test_NumberFormatter_format_using_commas_shows_number_as_int_if_too_long(self):
        formatter = nf.NumberFormatter()
        formatter.shown_digits = 5
        self.assertEqual(formatter.format_commaed(123456.789), '123,457')

    def test_NumberFormatter_format_using_commas_negative_number(self):
        formatter = nf.NumberFormatter()
        self.assertEqual(formatter.format_commaed(-123456.789), '-123,457')

    def test_NumberFormatter_format_using_commas_small_int(self):
        formatter = nf.NumberFormatter()
        self.assertEqual(formatter.format_commaed(12), '12')

    def test_NumberFormatter_format_using_commas_shows_whole_int(self):
        formatter = nf.NumberFormatter()
        formatter.shown_digits = 5
        self.assertEqual(formatter.format_commaed(123456789), '123,456,789')

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

        self.assertEqual(nf.remove_extra_zero_from_single_digit_exponent(float_format), '1.23e+2')
        self.assertEqual(nf.remove_extra_zero_from_single_digit_exponent(dec_format), '1.23e+2')
        self.assertEqual(nf.remove_extra_zero_from_single_digit_exponent(dec_zero_exponent), '1.00e+0')

    def test_remove_extra_zero_from_exponent(self):
        self.assertEqual(nf.remove_extra_zero_from_single_digit_exponent(str(1.23e-5)), '1.23e-5')
        self.assertEqual(nf.remove_extra_zero_from_single_digit_exponent('{:.2e}'.format(123000)),
                         '1.23e+5')
        self.assertEqual(nf.remove_extra_zero_from_single_digit_exponent('{:.2e}'.format(1)),
                         '1.00e+0')

    def test_NumberFormatter_format_as_exponent_not_remove_extra_zero(self):
        formatter = nf.NumberFormatter()
        test = 1.23456789 * 10 ** 12
        self.assertEqual(formatter.format_exponent(test), '1.235e+12')

    def test_NumberFormatter_format_as_exponent_remove_extra_zero(self):
        formatter = nf.NumberFormatter()
        test = 1.23456789*10**5
        self.assertEqual('{:.3e}'.format(test), '1.235e+05')
        self.assertEqual(formatter.format_exponent(test), '1.235e+5')

    def test_NumberFormatter_format_as_exponent_negative_number(self):
        formatter = nf.NumberFormatter()
        test = -1.23456789*10**5
        self.assertEqual(formatter.format_exponent(test), '-1.235e+5')

    def test_NumberFormatter_OverflowError_calls_new_func_does_not_raise_error(self):
        formatter = nf.NumberFormatter()
        test = 10 ** 5000
        self.assertRaises(OverflowError, '{:e}'.format, test)
        self.assertEqual(formatter.format_exponent(test), '1.000e+5000')

    def test_NumberFormatter_format_huge_int_pos_rounds(self):
        formatter = nf.NumberFormatter()
        test_1 = 123449*10**500
        test_2 = 123451*10**500
        self.assertEqual(formatter.format_exponent(test_1), '1.234e+505')
        self.assertEqual(formatter.format_exponent(test_2), '1.235e+505')

    def test_NumberFormatter_format_huge_int_neg_rounds(self):
        formatter = nf.NumberFormatter()
        test_1 = -123449*10**500
        test_2 = -123451*10**500
        self.assertEqual(formatter.format_exponent(test_1), '-1.234e+505')
        self.assertEqual(formatter.format_exponent(test_2), '-1.235e+505')

    def test_NumberFormatter_format_huge_int_round_to_next_power(self):
        formatter = nf.NumberFormatter()
        test = 999951*10**500
        self.assertEqual(formatter.format_exponent(test), '1.000e+506')

    def test_NumberFormatter_format_number_min_fixed_pt_exp_at_zero(self):
        test = nf.NumberFormatter()
        test.min_fixed_pt_exp = 0
        self.assertEqual(test.format(0.1), '1.000e-1')

    def test_NumberFormatter_format_number_min_fixed_pt_exp_at_zero_max_comma_exp_at_zero(self):
        test = nf.NumberFormatter()
        test.min_fixed_pt_exp = 0
        test.max_comma_exp = 0
        self.assertEqual(test.format(0.1), '1.000e-1')

        self.assertEqual(test.format(1.0), '1.000')
        self.assertEqual(test.format(1), '1')

        self.assertEqual(test.format(10.0), '1.000e+1')
        self.assertEqual(test.format(10), '1.000e+1')

    def test_NumberFormatter_format_number_max_comma_exp_at_neg_one(self):
        test = nf.NumberFormatter()
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
        formatter = nf.NumberFormatter()
        formatter.shown_digits = 10
        nine_digits = 9999999.99
        self.assertEqual(formatter.format(nine_digits), '9,999,999.990')
        formatter.shown_digits = 8
        self.assertEqual(formatter.format(nine_digits), '1.0000000e+7')


if __name__ == '__main__':
    unittest.main()
