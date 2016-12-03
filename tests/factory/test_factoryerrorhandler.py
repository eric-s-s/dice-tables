# pylint: disable=missing-docstring, invalid-name, too-many-public-methods
"""tests for the baseevents.py module"""
from __future__ import absolute_import

import unittest

from dicetables.factory.factoryerrorhandler import EventsFactoryError, EventsFactoryErrorHandler


class TestEventsFactoryErrorHandler(unittest.TestCase):
    def assert_my_regex(self, error_type, regex, func, *args):
        with self.assertRaises(error_type) as cm:
            func(*args)
        error_msg = cm.exception.args[0]
        self.assertEqual(error_msg, regex)

    def test_assert_my_regex(self):
        self.assert_my_regex(ValueError, "invalid literal for int() with base 10: 'a'", int, 'a')


if __name__ == '__main__':
    unittest.main()

