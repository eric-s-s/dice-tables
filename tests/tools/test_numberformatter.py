# pylint: disable=missing-docstring, invalid-name, too-many-public-methods, line-too-long

from __future__ import absolute_import

import unittest
from decimal import Decimal

from dicetables.tools.numberforamtter import NumberFormatter, remove_extra_zero_from_single_digit_exponent


class TestNumberFormatter(unittest.TestCase):

    def assert_format_number(self, number, number_str):
        self.assertEqual(NumberFormatter().format(number), number_str)

    def test_NumberFormatter_init_defaults(self):
        test = NumberFormatter()
        self.assertEqual(test.min_fixed_pt_exp, -3)
        self.assertEqual(test.shown_digits, 4)
        self.assertEqual(test.max_comma_exp, 6)

    def test_NumberFormatter_shown_digits_setter(self):
        test = NumberFormatter()
        test.shown_digits = 2.5
        self.assertEqual(test.shown_digits, 2)
        test.shown_digits = -5
        self.assertEqual(test.shown_digits, 1)

    def test_NumberFormatter_max_comma_exp_setter(self):
        test = NumberFormatter()
        test.max_comma_exp = 2.5
        self.assertEqual(test.max_comma_exp, 2)
        test.max_comma_exp = -5
        self.assertEqual(test.max_comma_exp, -1)

    def test_NumberFormatter_min_fixed_pt_exp_setter(self):
        test = NumberFormatter()
        test.min_fixed_pt_exp = -5
        self.assertEqual(test.min_fixed_pt_exp, -5)
        test.min_fixed_pt_exp = 5
        self.assertEqual(test.min_fixed_pt_exp, 0)
        test.min_fixed_pt_exp = -5.2
        self.assertEqual(test.min_fixed_pt_exp, -5)

    def test_NumberFormatter_init_out_of_range(self):
        test = NumberFormatter(-1, -2, 1)
        self.assertEqual(test.shown_digits, 1)
        self.assertEqual(test.max_comma_exp, -1)
        self.assertEqual(test.min_fixed_pt_exp, 0)

    def test_NumberFormatter_init_in_range(self):
        test = NumberFormatter(5, 4, -5)
        self.assertEqual(test.min_fixed_pt_exp, -5)
        self.assertEqual(test.shown_digits, 5)
        self.assertEqual(test.max_comma_exp, 4)

    def test_NumberFormatter_get_exponent_between_pos_one_and_neg_one__big_small_pos_neg_no_rounding(self):
        formatter = NumberFormatter()
        self.assertEqual(formatter.get_exponent(1e-5), -5)
        self.assertEqual(formatter.get_exponent(-1e-5), -5)
        self.assertEqual(formatter.get_exponent(Decimal('1e-1000')), -1000)
        self.assertEqual(formatter.get_exponent(Decimal('-1e-1000')), -1000)

    def test_NumberFormatter_get_exponent_gt_one__float_pos_neg_no_rounding(self):
        formatter = NumberFormatter()
        self.assertEqual(formatter.get_exponent(1e+5), 5)
        self.assertEqual(formatter.get_exponent(-1e+5), 5)
        self.assertEqual(formatter.get_exponent(Decimal('1e+1000')), 1000)
        self.assertEqual(formatter.get_exponent(Decimal('-1e+1000')), 1000)

    def test_NumberFormatter_get_exponent_int__big_small_pos_neg(self):
        formatter = NumberFormatter()
        self.assertEqual(formatter.get_exponent(50), 1)
        self.assertEqual(formatter.get_exponent(-50), 1)
        self.assertEqual(formatter.get_exponent(5 * 10**1000), 1000)
        self.assertEqual(formatter.get_exponent(-5 * 10**1000), 1000)

    def test_NumberFormatter_get_exponent__rounding(self):
        four_digits = NumberFormatter()
        three_digits = NumberFormatter(shown_digits=3)
        self.assertEqual(four_digits.get_exponent(99.95), 1)
        self.assertEqual(three_digits.get_exponent(99.95), 2)

    def test_NumberFormatter_get_exponent__rounding_lt_one(self):
        four_digits = NumberFormatter()
        three_digits = NumberFormatter(shown_digits=3)
        self.assertEqual(four_digits.get_exponent(0.0099951), -3)
        self.assertEqual(three_digits.get_exponent(0.0099951), -2)

    def test_NumberFormatter_format_fixed_point_no_round(self):
        formatter = NumberFormatter()
        self.assertEqual(formatter.format_fixed_point(1.2e-5), '0.00001200')

    def test_NumberFormatter_format_fixed_point_round(self):
        formatter = NumberFormatter()
        self.assertEqual(formatter.format_fixed_point(9.9999e-5), '0.0001000')

    def test_NumberFormatter_format_fixed_point_neg(self):
        formatter = NumberFormatter()
        self.assertEqual(formatter.format_fixed_point(-9.9999e-5), '-0.0001000')

    def test_NumberFormatter_format_commaed_no_round(self):
        formatter = NumberFormatter()
        formatter.shown_digits = 10
        self.assertEqual(formatter.format_commaed(9999.99), '9,999.990000')

    def test_NumberFormatter_format_commaed_round(self):
        formatter = NumberFormatter()
        self.assertEqual(formatter.format_commaed(9999.99), '10,000')
        self.assertEqual(formatter.format_commaed(99.999), '100.0')

    def test_NumberFormatter_format_commaed_shows_number_as_int_if_too_long(self):
        formatter = NumberFormatter()
        formatter.shown_digits = 5
        self.assertEqual(formatter.format_commaed(123456.789), '123,457')

    def test_NumberFormatter_format_commaed_negative_number(self):
        formatter = NumberFormatter()
        self.assertEqual(formatter.format_commaed(-123456.789), '-123,457')

    def test_NumberFormatter_format_commaed_small_int(self):
        formatter = NumberFormatter()
        self.assertEqual(formatter.format_commaed(12), '12')

    def test_NumberFormatter_format_commaed_shows_whole_int(self):
        formatter = NumberFormatter()
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

        self.assertEqual(remove_extra_zero_from_single_digit_exponent(float_format), '1.23e+2')
        self.assertEqual(remove_extra_zero_from_single_digit_exponent(dec_format), '1.23e+2')
        self.assertEqual(remove_extra_zero_from_single_digit_exponent(dec_zero_exponent), '1.00e+0')

    def test_remove_extra_zero_from_exponent_removes(self):
        self.assertEqual(remove_extra_zero_from_single_digit_exponent('1.23e-05'), '1.23e-5')
        self.assertEqual(remove_extra_zero_from_single_digit_exponent('1.23e+06'), '1.23e+6')
        self.assertEqual(remove_extra_zero_from_single_digit_exponent('1.00e+00'), '1.00e+0')

    def test_remove_extra_zero_from_exponent_does_not_remove(self):
        self.assertEqual(remove_extra_zero_from_single_digit_exponent('1.23e-5'), '1.23e-5')
        self.assertEqual(remove_extra_zero_from_single_digit_exponent('1.23e+6'), '1.23e+6')
        self.assertEqual(remove_extra_zero_from_single_digit_exponent('1.00e+0'), '1.00e+0')
        self.assertEqual(remove_extra_zero_from_single_digit_exponent('1.00e+10'), '1.00e+10')

    def test_remove_extra_zero_from_exponent_safe_for_others(self):
        self.assertEqual(remove_extra_zero_from_single_digit_exponent('1.00e+10'), '1.00e+10')
        self.assertEqual(remove_extra_zero_from_single_digit_exponent('1.00e+100'), '1.00e+100')
        self.assertEqual(remove_extra_zero_from_single_digit_exponent('1.00e-10'), '1.00e-10')
        self.assertEqual(remove_extra_zero_from_single_digit_exponent('1.00e-100'), '1.00e-100')
        self.assertEqual(remove_extra_zero_from_single_digit_exponent('1.00e+000'), '1.00e+000')

    def test_NumberFormatter_format_as_exponent_not_remove_extra_zero(self):
        formatter = NumberFormatter()
        test = 1.23456789 * 10**12
        self.assertEqual(formatter.format_exponent(test), '1.235e+12')

    def test_NumberFormatter_format_as_exponent_remove_extra_zero(self):
        formatter = NumberFormatter()
        test = 1.23456789 * 10**5
        self.assertEqual('{:.3e}'.format(test), '1.235e+05')
        self.assertEqual(formatter.format_exponent(test), '1.235e+5')

    def test_NumberFormatter_format_as_exponent_negative_number(self):
        formatter = NumberFormatter()
        test = -1.23456789 * 10**5
        self.assertEqual(formatter.format_exponent(test), '-1.235e+5')

    def test_NumberFormatter_format_as_exponent_lt_one(self):
        formatter = NumberFormatter()
        test = -1.23456789 * 10**(-5)
        self.assertEqual(formatter.format_exponent(test), '-1.235e-5')

    def test_NumberFormatter_white_box_test_OverflowError_calls_new_func_does_not_raise_error(self):
        formatter = NumberFormatter()
        test = 10**5000
        self.assertRaises(OverflowError, '{:e}'.format, test)
        self.assertEqual(formatter.format_exponent(test), '1.000e+5000')

    def test_NumberFormatter_format_huge_int_pos_rounds(self):
        formatter = NumberFormatter()
        test_1 = 123449 * 10**500
        test_2 = 123451 * 10**500
        self.assertEqual(formatter.format_exponent(test_1), '1.234e+505')
        self.assertEqual(formatter.format_exponent(test_2), '1.235e+505')

    def test_NumberFormatter_format_huge_int_neg_rounds(self):
        formatter = NumberFormatter()
        test_1 = -123449 * 10**500
        test_2 = -123451 * 10**500
        self.assertEqual(formatter.format_exponent(test_1), '-1.234e+505')
        self.assertEqual(formatter.format_exponent(test_2), '-1.235e+505')

    def test_NumberFormatter_format_huge_int_round_to_next_power(self):
        four_digits = NumberFormatter()
        eight_digits = NumberFormatter(shown_digits=8)
        test = 999951 * 10**500
        self.assertEqual(four_digits.format_exponent(test), '1.000e+506')
        self.assertEqual(eight_digits.format(test), '9.9995100e+505')

    def test_NumberFormatter_format_huge_int_round_to_next_power_negative_number(self):
        four_digits = NumberFormatter()
        eight_digits = NumberFormatter(shown_digits=8)
        test = -999951 * 10**500
        self.assertEqual(four_digits.format_exponent(test), '-1.000e+506')
        self.assertEqual(eight_digits.format(test), '-9.9995100e+505')

    def test_NumberFormatter_format_min_fixed_pt_exp_at_zero(self):
        test = NumberFormatter(min_fixed_pt_exp=0)
        self.assertEqual(test.format(0.1), '1.000e-1')

    def test_NumberFormatter_format_min_fixed_pt_exp_at_zero_max_comma_exp_at_zero(self):
        test = NumberFormatter(min_fixed_pt_exp=0, max_comma_exp=0)

        self.assertEqual(test.format(0.1), '1.000e-1')

        self.assertEqual(test.format(1.0), '1.000')
        self.assertEqual(test.format(1), '1')

        self.assertEqual(test.format(10.0), '1.000e+1')
        self.assertEqual(test.format(10), '1.000e+1')

    def test_NumberFormatter_format__min_fixed_pt_exp_at_zero_max_comma_exp_at_neg_one(self):
        test = NumberFormatter(max_comma_exp=-1, min_fixed_pt_exp=0)
        self.assertEqual(test.format(0.1), '1.000e-1')
        self.assertEqual(test.format(1.0), '1.000e+0')
        self.assertEqual(test.format(1), '1.000e+0')
        self.assertEqual(test.format(10.0), '1.000e+1')

    def test_NumberFormatter_max_comma_exp_ridiculous_case(self):
        test = NumberFormatter(max_comma_exp=1000)
        num = int('9' * 999)
        num_string = '999,' * 333
        num_string = num_string.rstrip(',')
        self.assertEqual(test.format(num), num_string)

    def test_NumberFormatter_format_zero(self):
        self.assert_format_number(0, '0')

    def test_NumberFormatter_format_edge_of_min_fixed_pt_exp(self):
        self.assert_format_number(0.000999949, '9.999e-4')
        self.assert_format_number(0.000999951, '0.001000')

    def test_NumberFormatter_format_edge_of_one_switches_algorithm(self):
        exponent_formatter = NumberFormatter(min_fixed_pt_exp=0)
        fixed_point_formatter = NumberFormatter(min_fixed_pt_exp=-5)
        self.assertEqual(exponent_formatter.format(.999949), '9.999e-1')
        self.assertEqual(exponent_formatter.format(.999951), '1.000')
        self.assertEqual(fixed_point_formatter.format(.999949), '0.9999')
        self.assertEqual(fixed_point_formatter.format(.999951), '1.000')

    def test_NumberFormatter_format_edge_of_max_comma_exp_int(self):
        self.assert_format_number(9999999, '9,999,999')

    def test_NumberFormatter_format_edge_of_max_comma_exp_float(self):
        self.assert_format_number(9999999.0, '1.000e+7')
        self.assert_format_number(9999499.0, '9,999,499')
        self.assert_format_number(9999501.0, '1.000e+7')

    def test_NumberFormatter_format_at_edge_of_max_commas_exp_with_large_show_digits(self):
        ten_digits = NumberFormatter(shown_digits=10)
        eight_digits = NumberFormatter(shown_digits=8)
        nine_digit_number = 9999999.99
        self.assertEqual(ten_digits.format(nine_digit_number), '9,999,999.990')
        self.assertEqual(eight_digits.format(nine_digit_number), '1.0000000e+7')

    def test_NumberFormatter_format_ints(self):
        self.assert_format_number(-3, '-3')
        self.assert_format_number(1000, '1,000')
        self.assert_format_number(-9999999, '-9,999,999')
        self.assert_format_number(10000000, '1.000e+7')
        self.assert_format_number(-99999999, '-1.000e+8')
        self.assert_format_number(999999999, '1.000e+9')
        self.assert_format_number(9999999999, '1.000e+10')
        self.assert_format_number(123451 * 10**1000, '1.235e+1005')

    def test_NumberFormatter_is_special_case_zero(self):
        self.assertTrue(NumberFormatter().is_special_case(0))
        self.assertTrue(NumberFormatter().is_special_case(0.0))

    def test_NumberFormatter_is_special_case_infinity(self):
        self.assertTrue(NumberFormatter().is_special_case(float('inf')))
        self.assertTrue(NumberFormatter().is_special_case(Decimal('inf')))

    def test_NumberFormatter_is_special_case_neg_infinity(self):
        self.assertTrue(NumberFormatter().is_special_case(float('-inf')))
        self.assertTrue(NumberFormatter().is_special_case(Decimal('-inf')))

    def test_NumberFormatter_is_special_case_false(self):
        self.assertFalse(NumberFormatter().is_special_case(1.23))
        self.assertFalse(NumberFormatter().is_special_case(-10 * 1111))
        self.assertFalse(NumberFormatter().is_special_case(Decimal('1e-1000')))
        self.assertFalse(NumberFormatter().is_special_case(Decimal('1e+1000')))
        self.assertFalse(NumberFormatter().is_special_case(Decimal('-1e+1000')))

    def test_NumberFormatter_get_special_case_zero(self):
        self.assertEqual(NumberFormatter().get_special_case(0), '0')
        self.assertEqual(NumberFormatter().get_special_case(0.0), '0')

    def test_NumberFormatter_get_special_case_infinity(self):
        self.assertEqual(NumberFormatter().get_special_case(float('inf')), 'Infinity')
        self.assertEqual(NumberFormatter().get_special_case(Decimal('inf')), 'Infinity')

    def test_NumberFormatter_get_special_case_neg_infinity(self):
        self.assertEqual(NumberFormatter().get_special_case(float('-inf')), '-Infinity')
        self.assertEqual(NumberFormatter().get_special_case(Decimal('-inf')), '-Infinity')

    def test_NumberFormatter_format_special_cases(self):
        self.assertEqual(NumberFormatter().format(0), '0')
        self.assertEqual(NumberFormatter().format(float('inf')), 'Infinity')
        self.assertEqual(NumberFormatter().format(float('-inf')), '-Infinity')

    def test_NumberFormatter_format_fixed_point_special_cases(self):
        self.assertEqual(NumberFormatter().format_fixed_point(0), '0')
        self.assertEqual(NumberFormatter().format_fixed_point(float('inf')), 'Infinity')
        self.assertEqual(NumberFormatter().format_fixed_point(float('-inf')), '-Infinity')

    def test_NumberFormatter_format_commaed_special_cases(self):
        self.assertEqual(NumberFormatter().format_commaed(0), '0')
        self.assertEqual(NumberFormatter().format_commaed(float('inf')), 'Infinity')
        self.assertEqual(NumberFormatter().format_commaed(float('-inf')), '-Infinity')

    def test_NumberFormatter_format_exponent_special_cases(self):
        self.assertEqual(NumberFormatter().format_exponent(0), '0')
        self.assertEqual(NumberFormatter().format_exponent(float('inf')), 'Infinity')
        self.assertEqual(NumberFormatter().format_exponent(float('-inf')), '-Infinity')


if __name__ == '__main__':
    unittest.main()
