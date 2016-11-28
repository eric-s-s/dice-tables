# pylint: disable=missing-docstring, invalid-name, too-many-public-methods
"""tests for the baseevents.py module"""
from __future__ import absolute_import
from sys import version_info
import unittest
from dicetables.baseevents import AdditiveEvents, InvalidEventsError, InputVerifier, scrub_zeroes


class TestBaseEvents(unittest.TestCase):
    def setUp(self):
        self.identity = AdditiveEvents({0: 1})
        self.identity_b = AdditiveEvents({0: 1})
        self.checker = InputVerifier()
        self.types_error = 'all values must be ints'
        if version_info[0] < 3:
            self.types_error += ' or longs'

    def tearDown(self):
        del self.identity
        del self.identity_b
        del self.checker
        del self.types_error

    def assert_my_regex(self, error_type, regex, func, *args):
        with self.assertRaises(error_type) as cm:
            func(*args)
        error_msg = str(cm.exception)
        self.assertEqual(error_msg, regex)

    def test_assert_my_regex(self):
        self.assert_my_regex(ValueError, "invalid literal for int() with base 10: 'a'", int, 'a')

    #  InputVerifier tests
    def test_InvalidEventsError_empty(self):
        error = InvalidEventsError()
        self.assertEqual(str(error), '')
        self.assertEqual(error.args[0], '')

    def test_InvalidEventsError_non_empty(self):
        error = InvalidEventsError('message')
        self.assertEqual(str(error), 'message')
        self.assertEqual(error.args[0], 'message')

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

    def test_scrub_zeroes_no_zeroes_dict(self):
        self.assertEqual(scrub_zeroes({1: 2, 3: 4}), {1: 2, 3: 4})

    def test_scrub_zeroes_zeroes_in_dict(self):
        self.assertEqual(scrub_zeroes({1: 2, 3: 0, 4: 1, 5: 0}), {1: 2, 4: 1})

    #  AdditiveEvents tests
    def test_AdditiveEvents_init_zero_occurrences_dict_raises_error(self):
        self.assertRaises(InvalidEventsError, AdditiveEvents, {1: 0, 2: 0})

    def test_AdditiveEvents_init_empty_dict_raises_error(self):
        self.assertRaises(InvalidEventsError, AdditiveEvents, {})

    def test_AdditiveEvents_init_bad_dict_raises_error(self):
        self.assertRaises(InvalidEventsError, AdditiveEvents, {1: 1.0})
        self.assertRaises(InvalidEventsError, AdditiveEvents, {1.0: 1})
        self.assertRaises(InvalidEventsError, AdditiveEvents, {1: -1})

    def test_AdditiveEvents_get_dict(self):
        self.assertEqual(AdditiveEvents({1: 2, 3: 4}).get_dict(), {1: 2, 3: 4})

    def test_AdditiveEvents_get_dict_removes_zeroes(self):
        self.assertEqual(AdditiveEvents({1: 2, 3: 0, 4: 1, 5: 0}).get_dict(), {1: 2, 4: 1})

    def test_AdditiveEvents_get_dict_will_not_mutate_original(self):
        events = AdditiveEvents({1: 2, 3: 4})
        dictionary = events.get_dict()
        dictionary[1] = 100
        self.assertEqual(AdditiveEvents({1: 2, 3: 4}).get_dict(), {1: 2, 3: 4})

    def test_AdditiveEvents_string_returns_min_to_max(self):
        table = AdditiveEvents({-1: 1, 2: 1, 5: 1})
        self.assertEqual(str(table), 'table from -1 to 5')

    def test_AdditiveEvents_string_is_in_order_and_ignores_high_zero_values(self):
        table = AdditiveEvents({2: 0, 1: 1, -1: 1, -2: 0})
        self.assertEqual(str(table), 'table from -1 to 1')

    def test_AdditiveEvents_combine_negative_times_does_nothing(self):
        self.identity = AdditiveEvents({0: 1})
        new = self.identity.combine(-1, AdditiveEvents({1: 1}))
        self.assertEqual(new.get_dict(), {0: 1})

    def test_AdditiveEvents_combine_by_dictionary(self):
        to_combine = AdditiveEvents({1: 2, 2: 2})
        new = self.identity.combine_by_dictionary(1, to_combine)
        self.assertEqual(new.get_dict(), to_combine.get_dict())

    def test_AdditiveEvents_combine_by_flattened_list(self):
        to_combine = AdditiveEvents({1: 1, 2: 2})
        new = self.identity.combine_by_flattened_list(1, to_combine)
        self.assertEqual(new.get_dict(), to_combine.get_dict())

    def test_AdditiveEvents_combine_by_indexed_values(self):
        to_combine = AdditiveEvents({1: 1, 2: 2})
        new = self.identity.combine_by_indexed_values(1, to_combine)
        self.assertEqual(new.get_dict(), to_combine.get_dict())

    def test_AdditiveEvents_combine(self):
        to_combine = AdditiveEvents({1: 1, 2: 2})
        new = self.identity.combine(1, to_combine)
        self.assertEqual(new.get_dict(), to_combine.get_dict())

    def test_AdditiveEvents_combine_works_with_low_total_occurrences_events(self):
        low_ratio_events = AdditiveEvents({1: 1, 2: 1})
        new = self.identity.combine(1, low_ratio_events)
        self.assertEqual(new.get_dict(), low_ratio_events.get_dict())

    def test_AdditiveEvents_combine_works_with_high_total_occurrences_events(self):
        high_ratio_dict = {1: 10 ** 1000, 2: 10 ** 1000}
        new = self.identity.combine(1, AdditiveEvents(high_ratio_dict))
        self.assertEqual(new.get_dict(), high_ratio_dict)

    def test_AdditiveEvents_one_multiple_combine_is_multiple_single_combines(self):
        to_add = AdditiveEvents({1: 2, 3: 4})
        one = self.identity.combine(1, to_add)
        two = one.combine(1, to_add)
        two_alt = self.identity.combine(2, to_add)
        self.assertEqual(two.get_dict(), two_alt.get_dict())

    def test_AdditiveEvents_combine_combines_correctly(self):
        to_add = AdditiveEvents({1: 2, 2: 2})
        new = self.identity.combine(2, to_add)
        self.assertEqual(new.get_dict(), {2: 4, 3: 8, 4: 4})

    def test_AdditiveEvents_combine_works_with_long_large_number_list(self):
        silly_dict = dict.fromkeys(range(-1000, 1000), 10 ** 1000)
        to_add = AdditiveEvents(silly_dict)
        new = self.identity.combine(1, to_add)
        self.assertEqual(new.get_dict(), silly_dict)

    def test_AdditiveEvents_remove_removes_correctly(self):
        arbitrary_events = AdditiveEvents({-5: 3, 4: 10, 7: 1})
        five_a = self.identity.combine(5, arbitrary_events)
        ten_b = self.identity.combine(10, arbitrary_events)
        five_b = ten_b.remove(5, arbitrary_events)
        self.assertEqual(five_a.get_dict(), five_b.get_dict())

    def test_AdditiveEvents_remove_works_for_large_numbers(self):
        arbitrary_large_events = AdditiveEvents({-5: 10 ** 500, 0: 5 * 10 ** 700, 3: 2 ** 1000})
        one_large = self.identity.combine(1, arbitrary_large_events)
        two_large = self.identity.combine(2, arbitrary_large_events)
        alt_one_large = two_large.remove(1, arbitrary_large_events)
        self.assertEqual(one_large.get_dict(), alt_one_large.get_dict())

    def test_AdditiveEvents_combine_works_regardless_of_order(self):
        arbitrary_a = AdditiveEvents({1: 2, 3: 10 ** 456})
        arbitrary_b = AdditiveEvents({-1: 2, 0: 5})
        self.identity.combine(1, arbitrary_a)
        self.identity.combine(2, arbitrary_b)
        self.identity_b.combine(2, arbitrary_b)
        self.identity_b.combine(1, arbitrary_a)
        self.assertEqual(self.identity.get_dict(),
                         self.identity_b.get_dict())

    def test_AdditiveEvents_remove_removes_same_regardless_of_order(self):
        arbitrary_a = AdditiveEvents({-1: 2, 3: 5})
        arbitrary_b = AdditiveEvents({0: 9, 100: 4})
        five_a = self.identity.combine(5, arbitrary_a)
        five_a_five_b = five_a.combine(5, arbitrary_b)
        two_a_five_b = five_a_five_b.remove(3, arbitrary_a)
        two_a_two_b = two_a_five_b.remove(3, arbitrary_b)
        two_a_one_b = two_a_two_b.remove(1, arbitrary_b)
        one_a_one_b = two_a_one_b.remove(1, arbitrary_a)

        one_b = self.identity.combine(1, arbitrary_b)
        one_b_one_a = one_b.combine(1, arbitrary_a)
        self.assertEqual(one_a_one_b.get_dict(), one_b_one_a.get_dict())


if __name__ == '__main__':
    unittest.main()
