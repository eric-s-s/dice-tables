# pylint: disable=missing-docstring, invalid-name, too-many-public-methods
from __future__ import absolute_import

import unittest
from sys import version_info

from dicetables.eventsbases.integerevents import IntegerEvents, EventsVerifier
from dicetables.eventsbases.eventerrors import InvalidEventsError


class TestIntegerEvents(unittest.TestCase):
    def setUp(self):
        self.checker = EventsVerifier()
        self.types_error = 'all values must be ints'
        if version_info[0] < 3:
            self.types_error += ' or longs'

    def tearDown(self):
        del self.checker
        del self.types_error

    def assert_my_regex(self, error_type, regex, func, *args):
        with self.assertRaises(error_type) as cm:
            func(*args)
        error_msg = cm.exception.args[0]
        self.assertEqual(error_msg, regex)

    def test_assert_my_regex(self):
        self.assert_my_regex(ValueError, "invalid literal for int() with base 10: 'a'", int, 'a')

    def test_EventsVerifier_verify_get_dict_pass(self):
        self.assertIsNone(self.checker.verify_get_dict({1: 1}))

    def test_EventsVerifier_verify_get_dict_empty(self):
        self.assert_my_regex(InvalidEventsError,
                             'events may not be empty. a good alternative is the identity - {0: 1}.',
                             self.checker.verify_get_dict, {})

    def test_EventsVerifier_verify_get_dict_zero_occurrences(self):
        self.assert_my_regex(InvalidEventsError,
                             'no negative or zero occurrences in Events.get_dict()',
                             self.checker.verify_get_dict, {1: 0, 2: 0})

    def test_EventsVerifier_verify_get_dict_negative_occurrences(self):
        self.assert_my_regex(InvalidEventsError, 'no negative or zero occurrences in Events.get_dict()',
                             self.checker.verify_get_dict, {1: -1})

    def test_EventsVerifier_verify_get_dict_non_int_occurrences(self):
        self.assert_my_regex(InvalidEventsError, self.types_error,
                             self.checker.verify_get_dict, {1: 1.0})

    def test_EventsVerifier_verify_get_dict_non_int_event(self):
        self.assert_my_regex(InvalidEventsError, self.types_error,
                             self.checker.verify_get_dict, {1.0: 1})

    def test_EventsVerifier_is_all_ints_pass(self):
        self.assertTrue(self.checker.is_all_ints([10 ** value for value in range(500)]))

    def test_EventsVerifier_all_ints_fail(self):
        self.assertFalse(self.checker.is_all_ints([1.0, 1, 1, 1, 1, 1]))

    def test_EventsVerifier_does_not_work_if_does_not_follow_minimum_requirements(self):
        self.assertRaises(AttributeError, self.checker.verify_get_dict, 'a')
        self.assertRaises(AttributeError, self.checker.verify_get_dict, [1, 2, 3])
        self.assertRaises(AttributeError, self.checker.verify_get_dict, [(1, 2, 3), (4, 5, 6)])
        self.assertRaises(InvalidEventsError, self.checker.verify_get_dict, {'a': 'b'})

    def test_IntegerEvents_checks_get_dict_at_init(self):
        self.assertRaises(NotImplementedError, IntegerEvents)

    def test_IntegerEvents_init_error_message(self):
        message = ('get_dict() must return a dictionary\n' +
                   '{event: occurrences, ...} event=int, occurrence=int>0.')
        self.assert_my_regex(NotImplementedError, message, IntegerEvents)

if __name__ == '__main__':
    unittest.main()
