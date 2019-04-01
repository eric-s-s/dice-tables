# pylint: disable=missing-docstring, invalid-name, too-many-public-methods, line-too-long

from __future__ import absolute_import

import unittest
from sys import version_info

if version_info[0] < 3:
    import dicetables.tools.py2funcs as pf
else:
    import dicetables.tools.py3funcs as pf


class TestPyXFuncs(unittest.TestCase):

    def test_is_int_true_small(self):
        self.assertTrue(pf.is_int(10))

    def test_is_int_true_big(self):
        self.assertTrue(pf.is_int(10 ** 1000))

    def test_is_int_true_small_neg(self):
        self.assertTrue(pf.is_int(-10))

    def test_is_int_true_big_neg(self):
        self.assertTrue(pf.is_int(-1 * 10 ** 1000))

    def test_is_int_true_zero(self):
        self.assertTrue(pf.is_int(0))

    def test_is_int_false_float(self):
        self.assertFalse(pf.is_int(10.0))

    def test_is_int_false_other(self):
        self.assertFalse(pf.is_int('a'))
        self.assertFalse(pf.is_int({}))
        self.assertFalse(pf.is_int([]))
