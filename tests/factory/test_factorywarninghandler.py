# pylint: disable=missing-docstring, invalid-name, too-many-public-methods
"""tests for the baseevents.py module"""
from __future__ import absolute_import

import unittest
import warnings

from dicetables.factory.factorywarninghandler import EventsFactoryWarning, EventsFactoryWarningHandler


class TestEventsFactoryWarningHandler(unittest.TestCase):
    def assert_my_regex(self, error_type, regex, func, *args):
        with self.assertRaises(error_type) as cm:
            func(*args)
        error_msg = str(cm.exception)
        self.assertEqual(error_msg, regex)

    def test_assert_my_regex(self):
        self.assert_my_regex(ValueError, "invalid literal for int() with base 10: 'a'", int, 'a')

    def assert_warning(self, warning, msg, func, *args):
        with warnings.catch_warnings(record=True) as cm:
            warnings.simplefilter("always")
            func(*args)
        if len(cm) != 1:
            self.fail('Warning not raised or too many warnings')
        else:
            self.assertEqual(msg, str(cm[0].message))
            self.assertEqual(warning, cm[0].category)

    def assert_no_warning(self, func, *args):
        with warnings.catch_warnings(record=True) as cm:
            warnings.simplefilter("always")
            func(*args)
        if len(cm) != 0:
            self.fail('number of warnings: {}'.format(len(cm)))

    def test_assert_warning(self):
        def func(number):
            warnings.warn('msg', EventsFactoryWarning, stacklevel=2)
            return number
        self.assert_warning(EventsFactoryWarning, 'msg', func, 5)

    def test_assert_warning_with_no_warning(self):
        def func(number):
            return number
        with self.assertRaises(AssertionError) as cm:
            self.assert_warning(EventsFactoryWarning, 'hi', func, 5)
        self.assertEqual(cm.exception.args[0], 'Warning not raised or too many warnings')

    def test_assert_warning_with_too_many_warnings(self):
        def func(number):
            warnings.warn('msg', EventsFactoryWarning, stacklevel=2)
            warnings.warn('msg', Warning, stacklevel=2)
            return number
        with self.assertRaises(AssertionError) as cm:
            self.assert_warning(EventsFactoryWarning, 'hi', func, 5)
        self.assertEqual(cm.exception.args[0], 'Warning not raised or too many warnings')

    def test_assert_no_warning_with_no_warning(self):
        def func(number):
            return number
        self.assert_no_warning(func, 5)

    @unittest.expectedFailure
    def test_assert_no_warning_with_warning(self):
        def func(number):
            warnings.warn('msg', EventsFactoryWarning, stacklevel=2)
            return number
        self.assert_no_warning(func, 5)


if __name__ == '__main__':
    unittest.main()

