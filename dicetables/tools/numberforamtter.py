"""fancy number formatting"""

from math import log10
from sys import version_info


def is_int(number):
    if version_info[0] < 3:
        int_types = (int, long)
    else:
        int_types = (int,)
    return isinstance(number, int_types)


class NumberFormatter(object):
    def __init__(self, shown_digits=4, max_comma_exp=6, min_fixed_pt_exp=-3):
        """

        :param shown_digits: int >= 1
        :param max_comma_exp: int >= -1
        :param min_fixed_pt_exp: int <= 0
        """
        self._shown_digits = None
        self._max_comma_exp = None
        self._min_fixed_pt_exp = None

        self.shown_digits = shown_digits
        self.max_comma_exp = max_comma_exp
        self.min_fixed_pt_exp = min_fixed_pt_exp

    @property
    def shown_digits(self):
        return self._shown_digits

    @shown_digits.setter
    def shown_digits(self, sig_figs):
        self._shown_digits = int(max(1, sig_figs))

    @property
    def max_comma_exp(self):
        return self._max_comma_exp

    @max_comma_exp.setter
    def max_comma_exp(self, value):
        self._max_comma_exp = int(max(-1, value))

    @property
    def min_fixed_pt_exp(self):
        return self._min_fixed_pt_exp

    @min_fixed_pt_exp.setter
    def min_fixed_pt_exp(self, value):
        self._min_fixed_pt_exp = min(0, int(value))

    def get_exponent(self, number):
        if is_int(number):
            return int(log10(abs(number)))
        return int('{:.{}e}'.format(number, self.shown_digits - 1).split('e')[1])

    def _format_number_and_exponent_to_fixed_point(self, number, exponent):
        return '{:.{}f}'.format(number, self.shown_digits - 1 - exponent)

    def _format_number_and_exponent_to_commas(self, number, exponent):
        if is_int(number):
            return '{:,}'.format(number)
        else:
            return '{:,.{}f}'.format(number, max(0, self.shown_digits - 1 - exponent))

    def _format_number_and_exponent_to_exponent(self, number, exponent):
        try:
            answer = '{:.{}e}'.format(number, self.shown_digits - 1)
            if -10 < exponent < 10:
                return remove_extra_zero_from_single_digit_exponent(answer)
            return answer
        except OverflowError:
            return self._format_huge_int_and_exponent_to_exponent(number, exponent)

    def _format_huge_int_and_exponent_to_exponent(self, number, exponent):
        extra_digits = 10
        mantissa = number // 10 ** (exponent - self.shown_digits - extra_digits)
        mantissa /= 10. ** (self.shown_digits + extra_digits)
        mantissa = round(mantissa, self.shown_digits - 1)
        if mantissa == 10.0 or mantissa == -10.0:
            mantissa /= 10.0
            exponent += 1
        return '{:.{}f}e+{}'.format(mantissa, self.shown_digits - 1, exponent)

    def format_fixed_point(self, number):
        exponent = self.get_exponent(number)
        return self._format_number_and_exponent_to_fixed_point(number, exponent)

    def format_commaed(self, number):
        exponent = self.get_exponent(number)
        return self._format_number_and_exponent_to_commas(number, exponent)

    def format_exponent(self, number):
        exponent = self.get_exponent(number)
        return self._format_number_and_exponent_to_exponent(number, exponent)

    def format(self, number):
        if number == 0:
            return '0'
        exponent = self.get_exponent(number)
        if 0 > exponent >= self.min_fixed_pt_exp:
            return self._format_number_and_exponent_to_fixed_point(number, exponent)
        elif 0 <= exponent <= self.max_comma_exp:
            return self._format_number_and_exponent_to_commas(number, exponent)
        else:
            return self._format_number_and_exponent_to_exponent(number, exponent)


def remove_extra_zero_from_single_digit_exponent(answer):
    if answer[-2] == '0':
        return answer[:-2] + answer[-1:]
    return answer