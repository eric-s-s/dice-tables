# pylint: disable=missing-docstring, invalid-name, too-many-public-methods
"""tests for the baseevents.py module"""
from __future__ import absolute_import
from sys import version_info
import unittest
from dicetables.baseevents import AdditiveEvents, InvalidEventsError, InputVerifier, safe_true_div

FLOAT_BIG = 1e+300
FLOAT_SMALL = 1e+100
LONG_BIG = 10 ** 1000


class TestLongIntMath(unittest.TestCase):
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

    #  safe_true_div tests
    def test_safe_true_div_returns_zero_when_answer_power_below_neg_300ish(self):
        self.assertEqual(safe_true_div(FLOAT_BIG, LONG_BIG), 0)

    def test_safe_true_div_long_long_makes_float(self):
        result = safe_true_div(10 ** 300 * LONG_BIG, LONG_BIG)
        self.assertAlmostEqual(result, 10 ** 300, delta=10 ** 290)
        self.assertIsInstance(result, float)

    def test_safe_true_div_long_long_makes_float_with_negative_num(self):
        result = safe_true_div(-10 ** 300 * LONG_BIG, LONG_BIG)
        self.assertAlmostEqual(result, -10 ** 300, delta=10 ** 290)
        self.assertIsInstance(result, float)

    def test_safe_true_div_float_float_makes_long(self):
        result = safe_true_div(FLOAT_BIG, 1 / FLOAT_SMALL)
        self.assertAlmostEqual(result, 10 ** 400, delta=10 ** 390)

    def test_safe_true_div_float_float_makes_long_with_negative_num(self):
        result = safe_true_div(FLOAT_BIG, -1 / FLOAT_SMALL)
        self.assertAlmostEqual(result, -10 ** 400, delta=10 ** 390)

    def test_safe_true_div_long_long_makes_negative_power_float(self):
        result = safe_true_div(LONG_BIG, LONG_BIG * 10 ** 200)
        self.assertAlmostEqual(result, 10 ** -200, delta=10 ** -210)

    #  InputVerifier tests
    def test_InvalidEventsError_empty(self):
        error = InvalidEventsError()
        self.assertEqual(str(error), '')
        self.assertEqual(error.args[0], '')

    def test_InvalidEventsError_non_empty(self):
        error = InvalidEventsError('message')
        self.assertEqual(str(error), 'message')
        self.assertEqual(error.args[0], 'message')

    def test_EventsVerifier_verify_all_events_pass(self):
        self.assertIsNone(self.checker.verify_get_dict({1: 1}))

    def test_EventsVerifier_verify_all_events_empty(self):
        self.assert_my_regex(InvalidEventsError,
                             'events may not be empty. a good alternative is the identity - {0: 1}.',
                             self.checker.verify_get_dict, {})

    def test_EventsVerifier_verify_all_events_zero_occurrences(self):
        self.assert_my_regex(InvalidEventsError,
                             'no negative or zero occurrences in Events.get_dict()',
                             self.checker.verify_get_dict, {1: 0, 2: 0})

    def test_EventsVerifier_verify_events_by_tuple_negative_occurrences(self):
        self.assert_my_regex(InvalidEventsError, 'no negative or zero occurrences in Events.get_dict()',
                             self.checker.verify_get_dict, {1: -1})

    def test_EventsVerifier_verify_all_events_non_int_occurrences(self):
        self.assert_my_regex(InvalidEventsError, self.types_error,
                             self.checker.verify_get_dict, {1: 1.0})

    def test_EventsVerifier_verify_events_by_tuple_non_int_event(self):
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

    #  AdditiveEvents tests
    def test_AdditiveEvents_init_zero_occurrences_dict_raises_error(self):
        self.assertRaises(InvalidEventsError, AdditiveEvents, {1: 0, 2: 0})

    def test_AdditiveEvents_init_empty_dict_raises_error(self):
        self.assertRaises(InvalidEventsError, AdditiveEvents, {})

    def test_AdditiveEvents_init_bad_dict_raises_error(self):
        self.assertRaises(InvalidEventsError, AdditiveEvents, {1: 1.0})
        self.assertRaises(InvalidEventsError, AdditiveEvents, {1.0: 1})
        self.assertRaises(InvalidEventsError, AdditiveEvents, {1: -1})

    def test_AdditiveEvents_event_keys_removes_zero_occurrences(self):
        test_table = AdditiveEvents({0: 1, 1: 0})
        self.assertEqual(test_table.event_keys, [0])

    def test_AdditiveEvents_event_keys_sorts(self):
        test_table = AdditiveEvents({2: 1, 1: 1, 3: 1})
        self.assertEqual(test_table.event_keys, [1, 2, 3])

    def test_AdditiveEvents_event_range(self):
        zero_to_two = AdditiveEvents({0: 2, 1: 1, 2: 5, 4: 0})
        self.assertEqual(zero_to_two.event_range, (0, 2))

    def test_AdditiveEvents_get_event(self):
        zero_three = AdditiveEvents({0: 3})
        self.assertEqual(zero_three.get_event(0), (0, 3))

    def test_AdditiveEvents_get_event_returns_for_empty_event(self):
        zero_three = AdditiveEvents({0: 3})
        self.assertEqual(zero_three.get_event(100), (100, 0))

    def test_AdditiveEvents_get_range_of_events(self):
        table = AdditiveEvents({1: 1, 2: 2})
        self.assertEqual(table.get_range_of_events(0, 4),
                         [(0, 0), (1, 1), (2, 2), (3, 0)])

    def test_AdditiveEvents_get_all_events(self):
        table = AdditiveEvents({1: 1, 2: 2})
        self.assertEqual(table.all_events,
                         [(1, 1), (2, 2)])

    def test_AdditiveEvents_get_all_events_sorts(self):
        table = AdditiveEvents({2: 1, 1: 2})
        self.assertEqual(table.all_events,
                         [(1, 2), (2, 1)])

    def test_AdditiveEvents_get_all_events_does_not_return_zero_frequencies(self):
        table = AdditiveEvents({-1: 2, 0: 0, 1: 2})
        self.assertEqual(table.all_events, [(-1, 2), (1, 2)])

    def test_AdditiveEvents_get_biggest_event_returns_first_biggest_event(self):
        table = AdditiveEvents({-1: 5, 0: 1, 2: 5})
        self.assertEqual(table.biggest_event, (-1, 5), (2, 5))

    def test_AdditiveEvents_get_biggest_event_returns_only_biggest_event(self):
        table = AdditiveEvents({-1: 5, 0: 1, 2: 10})
        self.assertEqual(table.biggest_event, (2, 10))

    def test_AdditiveEvents_get_total_event_occurrences(self):
        table = AdditiveEvents({1: 2, 3: 4})
        self.assertEqual(table.total_occurrences, 2 + 4)

    def test_AdditiveEvents_string_returns_min_to_max(self):
        table = AdditiveEvents({-1: 1, 2: 1, 5: 1})
        self.assertEqual(str(table), 'table from -1 to 5')

    def test_AdditiveEvents_string_is_in_order_and_ignores_high_zero_values(self):
        table = AdditiveEvents({2: 0, 1: 1, -1: 1, -2: 0})
        self.assertEqual(str(table), 'table from -1 to 1')

    def test_AdditiveEvents_mean_normal_case(self):
        table = AdditiveEvents({-1: 5, 1: 5})
        self.assertEqual(table.mean(), 0)

    def test_AdditiveEvents_mean_with_non_uniform_table(self):
        table = AdditiveEvents({1: 2, 2: 5})
        mean = (2 + 10) / float(2 + 5)
        self.assertEqual(table.mean(), mean)

    def test_AdditiveEvents_mean_with_large_number_table(self):
        table = AdditiveEvents({1: 2 * 10 ** 1000, 2: 2 * 10 ** 1000})
        self.assertEqual(table.mean(), 1.5)

    def test_AdditiveEvents_stddev_low_occurrences(self):
        low_freq = AdditiveEvents({2: 1, -2: 1, 1: 1, -1: 1})
        self.assertEqual(low_freq.stddev(), round((10 / 4.) ** 0.5, 4))

    def test_AdditiveEvents_stddev_low_occurrences_change_decimal_place_value(self):
        low_freq = AdditiveEvents({2: 1, -2: 1, 1: 1, -1: 1})
        self.assertEqual(low_freq.stddev(decimal_place=10), round((10 / 4.) ** 0.5, 10))

    def test_AdditiveEvents_stddev_middle_high_occurrences(self):
        high_freq = AdditiveEvents({2: 10 ** 50, -2: 10 ** 50, 1: 10 ** 50, -1: 10 ** 50})
        self.assertEqual(high_freq.stddev(), round((10 / 4.) ** 0.5, 4))

    def test_AdditiveEvents_stddev_middle_high_occurrences_change_decimal_place_value(self):
        high_freq = AdditiveEvents({2: 10 ** 50, -2: 10 ** 50, 1: 10 ** 50, -1: 10 ** 50})
        self.assertEqual(high_freq.stddev(decimal_place=10), round(2.5 ** 0.5, 10))

    def test_AdditiveEvents_stddev_very_high_occurrences(self):
        high_freq = AdditiveEvents({2: 10 ** 500, -2: 10 ** 500, 1: 10 ** 500, -1: 10 ** 500})
        self.assertEqual(high_freq.stddev(), round((10 / 4.) ** 0.5, 4))

    def test_AdditiveEvents_stddev_very_high_occurrences_change_decimal_place_value(self):
        high_freq = AdditiveEvents({2: 10 ** 500, -2: 10 ** 500, 1: 10 ** 500, -1: 10 ** 500})
        self.assertEqual(high_freq.stddev(decimal_place=10), round(2.5 ** 0.5, 10))

    def test_AdditiveEvents_combine_negative_times_does_nothing(self):
        identity = AdditiveEvents({0: 1})
        identity.combine(-1, AdditiveEvents({1: 1}))
        self.assertEqual(identity.get_dict(), {0: 1})

    def test_AdditiveEvents_combine_by_dictionary(self):
        to_combine = AdditiveEvents({1: 2, 2: 2})
        self.identity.combine_by_dictionary(1, to_combine)
        self.assertEqual(self.identity.get_dict(), to_combine.get_dict())

    def test_AdditiveEvents_combine_by_flattened_list(self):
        to_combine = AdditiveEvents({1: 1, 2: 2})
        self.identity.combine_by_flattened_list(1, to_combine)
        self.assertEqual(self.identity.get_dict(), to_combine.get_dict())

    def test_AdditiveEvents_combine_by_indexed_values(self):
        to_combine = AdditiveEvents({1: 1, 2: 2})
        self.identity.combine_by_indexed_values(1, to_combine)
        self.assertEqual(self.identity.get_dict(), to_combine.get_dict())

    def test_AdditiveEvents_combine(self):
        to_combine = AdditiveEvents({1: 1, 2: 2})
        self.identity.combine(1, to_combine)
        self.assertEqual(self.identity.get_dict(), to_combine.get_dict())

    def test_AdditiveEvents_combine_works_with_low_total_occurrences_events(self):
        low_ratio_events = AdditiveEvents({1: 1, 2: 1})
        self.identity.combine(1, low_ratio_events)
        self.assertEqual(self.identity.all_events, low_ratio_events.all_events)

    def test_AdditiveEvents_combine_works_with_high_total_occurrences_events(self):
        high_ratio_tuples = [(1, 10 ** 1000), (2, 10 ** 1000)]
        self.identity.combine(1, AdditiveEvents(dict(high_ratio_tuples)))
        self.assertEqual(self.identity.all_events, high_ratio_tuples)

    def test_AdditiveEvents_one_multiple_combine_is_multiple_single_combines(self):
        to_add = AdditiveEvents({1: 2, 3: 4})
        self.identity.combine(1, to_add)
        self.identity.combine(1, to_add)
        self.identity_b.combine(2, to_add)
        self.assertEqual(self.identity.all_events, self.identity_b.all_events)

    def test_AdditiveEvents_combine_combines_correctly(self):
        to_add = AdditiveEvents({1: 2, 2: 2})
        self.identity.combine(2, to_add)
        self.assertEqual(self.identity.get_dict(), {2: 4, 3: 8, 4: 4})

    def test_AdditiveEvents_combine_works_with_long_large_number_list(self):
        silly_dict = dict.fromkeys(range(-1000, 1000), 10 ** 1000)
        to_add = AdditiveEvents(silly_dict)
        self.identity.combine(1, to_add)
        self.assertEqual(self.identity.get_dict(), silly_dict)

    def test_AdditiveEvents_remove_removes_correctly(self):
        arbitrary_events = AdditiveEvents({-5: 3, 4: 10, 7: 1})
        self.identity.combine(5, arbitrary_events)
        self.identity_b.combine(10, arbitrary_events)
        self.identity_b.remove(5, arbitrary_events)
        self.assertEqual(self.identity.get_dict(), self.identity_b.get_dict())

    def test_AdditiveEvents_remove_works_for_large_numbers(self):
        arbitrary_large_events = AdditiveEvents({-5: 10 ** 500, 0: 5 * 10 ** 700, 3: 2 ** 1000})
        self.identity.combine(1, arbitrary_large_events)
        self.identity_b.combine(2, arbitrary_large_events)
        self.identity_b.remove(1, arbitrary_large_events)
        self.assertEqual(self.identity.get_dict(), self.identity_b.get_dict())

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
        self.identity.combine(5, arbitrary_a)
        self.identity.combine(5, arbitrary_b)
        self.identity.remove(3, arbitrary_a)
        self.identity.remove(3, arbitrary_b)
        self.identity.remove(1, arbitrary_b)
        self.identity.remove(1, arbitrary_a)

        self.identity_b.combine(1, arbitrary_b)
        self.identity_b.combine(1, arbitrary_a)
        self.assertEqual(self.identity.get_dict(), self.identity_b.get_dict())


if __name__ == '__main__':
    unittest.main()
