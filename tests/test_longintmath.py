# pylint: disable=missing-docstring, invalid-name, too-many-public-methods
"""tests for the longintmath.py module"""
from __future__ import absolute_import
from sys import version_info
import unittest
import dicetables.longintmath as lim

import time

FLOAT_BIG = 1e+300
FLOAT_SMALL = 1e+100
LONG_BIG = 10 ** 1000


class TestLongIntMath(unittest.TestCase):
    def setUp(self):
        self.identity_a = lim.AdditiveEvents({0: 1})
        self.identity_b = lim.AdditiveEvents({0: 1})
        self.checker = lim.InputVerifier()
        self.types_error = 'all values must be ints'
        if version_info[0] < 3:
            self.types_error += ' or longs'

    def tearDown(self):
        del self.identity_a
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
        self.assertEqual(lim.safe_true_div(FLOAT_BIG, LONG_BIG), 0)

    def test_safe_true_div_long_long_makes_float(self):
        result = lim.safe_true_div(10 ** 300 * LONG_BIG, LONG_BIG)
        self.assertAlmostEqual(result, 10 ** 300, delta=10 ** 290)
        self.assertIsInstance(result, float)

    def test_safe_true_div_long_long_makes_float_with_negative_num(self):
        result = lim.safe_true_div(-10 ** 300 * LONG_BIG, LONG_BIG)
        self.assertAlmostEqual(result, -10 ** 300, delta=10 ** 290)
        self.assertIsInstance(result, float)

    def test_safe_true_div_float_float_makes_long(self):
        result = lim.safe_true_div(FLOAT_BIG, 1 / FLOAT_SMALL)
        self.assertAlmostEqual(result, 10 ** 400, delta=10 ** 390)

    def test_safe_true_div_float_float_makes_long_with_negative_num(self):
        result = lim.safe_true_div(FLOAT_BIG, -1 / FLOAT_SMALL)
        self.assertAlmostEqual(result, -10 ** 400, delta=10 ** 390)

    def test_safe_true_div_long_long_makes_negative_power_float(self):
        result = lim.safe_true_div(LONG_BIG, LONG_BIG * 10 ** 200)
        self.assertAlmostEqual(result, 10 ** -200, delta=10 ** -210)

    #  InputVerifier tests
    def test_InvalidEventsError_empty(self):
        error = lim.InvalidEventsError()
        self.assertEqual(str(error), '')
        self.assertEqual(error.args[0], '')

    def test_InvalidEventsError_non_empty(self):
        error = lim.InvalidEventsError('message')
        self.assertEqual(str(error), 'message')
        self.assertEqual(error.args[0], 'message')

    def test_EventsVerifier_verify_times_pass(self):
        self.assertIsNone(self.checker.verify_times(10))

    def test_EventsVerifier_verify_times_not_int(self):
        self.assert_my_regex(TypeError, 'AdditiveEvents.combine/remove: times variable must be int',
                             self.checker.verify_times, 1.0)

    def test_EventsVerifier_verify_times_negative(self):
        self.assert_my_regex(ValueError, 'AdditiveEvents.combine/remove times must be >=0',
                             self.checker.verify_times, -1)

    def test_EventsVerifier_verify_events_tuple_pass(self):
        self.assertIsNone(self.checker.verify_events_tuple([(1, 1), (-1, 2)]))

    def test_EventsVerifier_verify_events_tuple_empty(self):
        self.assert_my_regex(lim.InvalidEventsError,
                             'events may not be empty. a good alternative is the identity - [(0, 1)].',
                             self.checker.verify_events_tuple, [])

    def test_EventsVerifier_verify_events_tuple_zero_occurrences(self):
        self.assert_my_regex(lim.InvalidEventsError,
                             'events may not be empty. a good alternative is the identity - [(0, 1)].',
                             self.checker.verify_events_tuple, [(1, 0), (2, 0)])

    def test_EventsVerifier_verify_events_by_tuple_negative_occurrences(self):
        self.assert_my_regex(lim.InvalidEventsError, 'events may not occur negative times.',
                             self.checker.verify_events_tuple, [(1, 0), (2, -1)])

    def test_EventsVerifier_verify_events_tuple_non_int_occurrences(self):
        self.assert_my_regex(lim.InvalidEventsError, self.types_error,
                             self.checker.verify_events_tuple, [(1, 1.0)])

    def test_EventsVerifier_verify_events_by_tuple_non_int_event(self):
        self.assert_my_regex(lim.InvalidEventsError, self.types_error,
                             self.checker.verify_events_tuple, [(1.0, 1)])

    def test_EventsVerifier_verify_events_dictionary_empty_error_message(self):
        self.assert_my_regex(lim.InvalidEventsError,
                             'events may not be empty. a good alternative is the identity - {0: 1}.',
                             self.checker.verify_events_dictionary, {1: 0})

    def test_EventsVerifier_verify_events_dictionary_empty_dictionary(self):
        self.assert_my_regex(lim.InvalidEventsError,
                             'events may not be empty. a good alternative is the identity - {0: 1}.',
                             self.checker.verify_events_dictionary, {})

    def test_EventsVerifier_verify_events_dictionary_other_errors(self):
        self.assert_my_regex(lim.InvalidEventsError, self.types_error,
                             self.checker.verify_events_dictionary, {1: 1.0})
        self.assert_my_regex(lim.InvalidEventsError, 'events may not occur negative times.',
                             self.checker.verify_events_dictionary, {1: -1})

    def test_EventsVerifier_is_all_ints_pass(self):
        self.assertTrue(self.checker.is_all_ints([10 ** value for value in range(500)]))

    def test_EventsVerifier_all_ints_fail(self):
        self.assertFalse(self.checker.is_all_ints([1.0, 1, 1, 1, 1, 1]))

    def test_EventsVerifier_does_not_work_if_does_not_follow_minimum_requirements(self):
        self.assertRaises((TypeError, ValueError, IndexError), self.checker.verify_events_tuple, 'a')
        self.assertRaises((TypeError, ValueError, IndexError), self.checker.verify_events_tuple, [1, 2, 3])
        self.assertRaises((TypeError, ValueError, IndexError), self.checker.verify_events_tuple, [(1, 2, 3), (4, 5, 6)])
        self.assertRaises(lim.InvalidEventsError, self.checker.verify_events_tuple, [('a', 'b')])

    #  AdditiveEvents tests
    def test_AdditiveEvents_init_zero_occurrences_dict_raises_error(self):
        self.assertRaises(lim.InvalidEventsError, lim.AdditiveEvents, {1: 0, 2: 0})
        self.assertRaises(lim.InvalidEventsError, lim.AdditiveEvents, {})

    def test_AdditiveEvents_init_bad_dict_raises_error(self):
        self.assertRaises(lim.InvalidEventsError, lim.AdditiveEvents, {1: 1.0})
        self.assertRaises(lim.InvalidEventsError, lim.AdditiveEvents, {1.0: 1})
        self.assertRaises(lim.InvalidEventsError, lim.AdditiveEvents, {1: -1})

    def test_AdditiveEvents_event_keys_removes_zero_occurrences(self):
        test_table = lim.AdditiveEvents({0: 1, 1: 0})
        self.assertEqual(test_table.event_keys, [0])

    def test_AdditiveEvents_event_keys_sorts(self):
        test_table = lim.AdditiveEvents({2: 1, 1: 1, 3: 1})
        self.assertEqual(test_table.event_keys, [1, 2, 3])

    def test_AdditiveEvents_event_range(self):
        zero_to_two = lim.AdditiveEvents({0: 2, 1: 1, 2: 5, 4: 0})
        self.assertEqual(zero_to_two.event_range, (0, 2))

    def test_AdditiveEvents_get_event(self):
        zero_three = lim.AdditiveEvents({0: 3})
        self.assertEqual(zero_three.get_event(0), (0, 3))

    def test_AdditiveEvents_get_event_returns_for_empty_event(self):
        zero_three = lim.AdditiveEvents({0: 3})
        self.assertEqual(zero_three.get_event(100), (100, 0))

    def test_AdditiveEvents_get_range_of_events(self):
        table = lim.AdditiveEvents({1: 1, 2: 2})
        self.assertEqual(table.get_range_of_events(0, 4),
                         [(0, 0), (1, 1), (2, 2), (3, 0)])

    def test_AdditiveEvents_get_all_events(self):
        table = lim.AdditiveEvents({1: 1, 2: 2})
        self.assertEqual(table.all_events,
                         [(1, 1), (2, 2)])

    def test_AdditiveEvents_get_all_events_sorts(self):
        table = lim.AdditiveEvents({2: 1, 1: 2})
        self.assertEqual(table.all_events,
                         [(1, 2), (2, 1)])

    def test_AdditiveEvents_get_all_events_does_not_return_zero_frequencies(self):
        table = lim.AdditiveEvents({-1: 2, 0: 0, 1: 2})
        self.assertEqual(table.all_events, [(-1, 2), (1, 2)])

    def test_AdditiveEvents_get_biggest_event_returns_first_biggest_event(self):
        table = lim.AdditiveEvents({-1: 5, 0: 1, 2: 5})
        self.assertEqual(table.biggest_event, (-1, 5), (2, 5))

    def test_AdditiveEvents_get_biggest_event_returns_only_biggest_event(self):
        table = lim.AdditiveEvents({-1: 5, 0: 1, 2: 10})
        self.assertEqual(table.biggest_event, (2, 10))

    def test_AdditiveEvents_get_total_event_occurrences(self):
        table = lim.AdditiveEvents({1: 2, 3: 4})
        self.assertEqual(table.total_occurrences, 2 + 4)

    def test_AdditiveEvents_string_returns_min_to_max(self):
        table = lim.AdditiveEvents({-1: 1, 2: 1, 5: 1})
        self.assertEqual(str(table), 'table from -1 to 5')

    def test_AdditiveEvents_string_is_in_order_and_ignores_high_zero_values(self):
        table = lim.AdditiveEvents({2: 0, 1: 1, -1: 1, -2: 0})
        self.assertEqual(str(table), 'table from -1 to 1')

    def test_AdditiveEvents_mean_normal_case(self):
        table = lim.AdditiveEvents({-1: 5, 1: 5})
        self.assertEqual(table.mean(), 0)

    def test_AdditiveEvents_mean_with_non_uniform_table(self):
        table = lim.AdditiveEvents({1: 2, 2: 5})
        mean = (2 + 10) / float(2 + 5)
        self.assertEqual(table.mean(), mean)

    def test_AdditiveEvents_mean_with_large_number_table(self):
        table = lim.AdditiveEvents({1: 2 * 10 ** 1000, 2: 2 * 10 ** 1000})
        self.assertEqual(table.mean(), 1.5)

    def test_AdditiveEvents_stddev_low_occurrences(self):
        low_freq = lim.AdditiveEvents({2: 1, -2: 1, 1: 1, -1: 1})
        self.assertEqual(low_freq.stddev(), round((10 / 4.) ** 0.5, 4))

    def test_AdditiveEvents_stddev_low_occurrences_change_decimal_place_value(self):
        low_freq = lim.AdditiveEvents({2: 1, -2: 1, 1: 1, -1: 1})
        self.assertEqual(low_freq.stddev(decimal_place=10), round((10 / 4.) ** 0.5, 10))

    def test_AdditiveEvents_stddev_middle_high_occurrences(self):
        high_freq = lim.AdditiveEvents({2: 10 ** 50, -2: 10 ** 50, 1: 10 ** 50, -1: 10 ** 50})
        self.assertEqual(high_freq.stddev(), round((10 / 4.) ** 0.5, 4))

    def test_AdditiveEvents_stddev_middle_high_occurrences_change_decimal_place_value(self):
        high_freq = lim.AdditiveEvents({2: 10 ** 50, -2: 10 ** 50, 1: 10 ** 50, -1: 10 ** 50})
        self.assertEqual(high_freq.stddev(decimal_place=10), round(2.5 ** 0.5, 10))

    def test_AdditiveEvents_stddev_very_high_occurrences(self):
        high_freq = lim.AdditiveEvents({2: 10 ** 500, -2: 10 ** 500, 1: 10 ** 500, -1: 10 ** 500})
        self.assertEqual(high_freq.stddev(), round((10 / 4.) ** 0.5, 4))

    def test_AdditiveEvents_stddev_very_high_occurrences_change_decimal_place_value(self):
        high_freq = lim.AdditiveEvents({2: 10 ** 500, -2: 10 ** 500, 1: 10 ** 500, -1: 10 ** 500})
        self.assertEqual(high_freq.stddev(decimal_place=10), round(2.5 ** 0.5, 10))

    def test_AdditiveEvents_verify_inputs_for_combine_and_remove_raises_error_for_bad_times(self):
        self.assertRaises(ValueError, self.identity_a.raise_error_for_bad_input, -1, [(1, 1)])
        self.assertRaises(TypeError, self.identity_a.raise_error_for_bad_input, 1.0, [(1, 1)])

    def test_AdditiveEvents_verify_inputs_for_combine_and_remove_raises_error_for_bad_events(self):
        self.assertRaises(lim.InvalidEventsError, self.identity_a.raise_error_for_bad_input, 1, [(1, 0)])
        self.assertRaises(lim.InvalidEventsError, self.identity_a.raise_error_for_bad_input, 1, [(1, 1.0)])
        self.assertRaises(lim.InvalidEventsError, self.identity_a.raise_error_for_bad_input, 1, [(1.0, 1)])
        self.assertRaises(lim.InvalidEventsError, self.identity_a.raise_error_for_bad_input, 1, [(1, -1)])

    def test_AdditiveEvents_prep_new_events_removes_zeros(self):
        self.assertEqual(lim.prepare_events([(1, 1), (2, 0)]), [(1, 1)])

    def test_AdditiveEvents_prep_new_events_sorts(self):
        self.assertEqual(lim.prepare_events([(1, 1), (-1, 1)]), [(-1, 1), (1, 1)])

    def test_AdditiveEvents_combine_errors_do_not_mutate_table(self):
        identity = lim.AdditiveEvents({0: 1})
        try:
            identity.combine(1, [(1, 0)])
        except lim.InvalidEventsError:
            pass
        try:
            identity.combine(-1, [(1, 1)])
        except ValueError:
            pass
        try:
            identity.combine(1, [(1, -1)])
        except lim.InvalidEventsError:
            pass
        self.assertEqual(identity.all_events, [(0, 1)])

    def test_AdditiveEvents_combine_method_is_tuple_list_identity(self):
        to_combine = [(1, 2), (2, 2)]
        self.identity_a.combine(1, to_combine, method='tuple_list')
        self.assertEqual(self.identity_a.all_events, to_combine)

    def test_AdditiveEvents_combine_method_is_tuple_list_complex(self):
        to_combine = [(1, 1), (2, 2)]
        self.identity_a.combine(3, to_combine, method='tuple_list')
        """
        {1: 1, 2: 2}

        {2: 1, 3: 2} + {3: 2, 4: 4} = {2: 1, 3: 4, 4: 4}

        {3: 1, 4: 4, 5: 4} + {4: 2, 5: 8, 6:8} = {3:1, 4: 6, 5: 12, 6: 8}
        """
        expected = [(3, 1), (4, 6), (5, 12), (6, 8)]
        self.assertEqual(self.identity_a.all_events, expected)

    def test_AdditiveEvents_combine_method_is_tuple_list_complex_AdditiveEvents(self):
        to_combine = [(1, 1), (2, 2)]
        complex_events = lim.AdditiveEvents({2: 1, 3: 4, 4: 4})
        complex_events.combine(1, to_combine, method='tuple_list')
        """
        {2: 1, 3: 4, 4: 4}

        {3: 1, 4: 4, 5: 4} + {4: 2, 5: 8, 6:8} = {3:1, 4: 6, 5: 12, 6: 8}
        """
        expected = [(3, 1), (4, 6), (5, 12), (6, 8)]
        self.assertEqual(complex_events.all_events, expected)

    def test_AdditiveEvents_combine_method_is_flattened_list_identity(self):
        to_combine = [(1, 2), (2, 2)]
        self.identity_a.combine(1, to_combine, method='flattened_list')
        self.assertEqual(self.identity_a.all_events, to_combine)

    def test_AdditiveEvents_combine_method_is_flattened_list_complex(self):
        to_combine = [(1, 1), (2, 2)]
        self.identity_a.combine(3, to_combine, method='flattened_list')
        """
        {1: 1, 2: 2}

        {2: 1, 3: 2} + {3: 2, 4: 4} = {2:1, 3: 4, 4: 4}

        {3: 1, 4: 4, 5: 4} + {4: 2, 5: 8, 6:8} = {3:1, 4: 6, 5: 12, 6: 8}
        """
        expected = [(3, 1), (4, 6), (5, 12), (6, 8)]
        self.assertEqual(self.identity_a.all_events, expected)

    def test_AdditiveEvents_combine_method_is_flattened_list_complex_AdditiveEvents(self):
        to_combine = [(1, 1), (2, 2)]
        complex_events = lim.AdditiveEvents({2: 1, 3: 4, 4: 4})
        complex_events.combine(1, to_combine, method='flattened_list')
        """
        {2: 1, 3: 4, 4: 4}

        {3: 1, 4: 4, 5: 4} + {4: 2, 5: 8, 6:8} = {3:1, 4: 6, 5: 12, 6: 8}
        """
        expected = [(3, 1), (4, 6), (5, 12), (6, 8)]
        self.assertEqual(complex_events.all_events, expected)

    def test_AdditiveEvents_combine_method_is_indexed_values_identity(self):
        to_combine = [(1, 2), (2, 2)]
        self.identity_a.combine(1, to_combine, method='indexed_values')
        self.assertEqual(self.identity_a.all_events, to_combine)

    def test_AdditiveEvents_combine_method_is_indexed_values_complex(self):
        to_combine = [(1, 1), (2, 2)]
        self.identity_a.combine(3, to_combine, method='indexed_values')
        """
        {1: 1, 2: 2}

        {2: 1, 3: 2} + {3: 2, 4: 4} = {2:1, 3: 4, 4: 4}

        {3: 1, 4: 4, 5: 4} + {4: 2, 5: 8, 6:8} = {3:1, 4: 6, 5: 12, 6: 8}
        """
        expected = [(3, 1), (4, 6), (5, 12), (6, 8)]
        self.assertEqual(self.identity_a.all_events, expected)

    def test_AdditiveEvents_combine_method_is_indexed_values_complex_AdditiveEvents(self):
        to_combine = [(1, 1), (2, 2)]
        complex_events = lim.AdditiveEvents({2: 1, 3: 4, 4: 4})
        complex_events.combine(1, to_combine, method='indexed_values')
        """
        {2: 1, 3: 4, 4: 4}

        {3: 1, 4: 4, 5: 4} + {4: 2, 5: 8, 6:8} = {3:1, 4: 6, 5: 12, 6: 8}
        """
        expected = [(3, 1), (4, 6), (5, 12), (6, 8)]
        self.assertEqual(complex_events.all_events, expected)

    """
    the next several tests show how AdditiveEvents.get_fastest_method works.  The edge cases to choose between
    methods were determined empirically.  To see how they were derived see time_trials/flattenedlist_timetrials.py
    and time_trials/indexedvalues_timetrials.py.  Those modules require numpy and matplotlib where the actual
    project does not.  Before running either one, under "if __name__ == '__main__':" make sure to comment in
    the UI you wish to use.  The full data set for determining whether to use indexed_values is this:
        {
        2: {10: (250, 500), 50: (100, 200), 500: (1, 1)},
        3: {4: (500, 500), 10: (50, 100), 20: (10, 50), 50: (1, 10), 100: (1, 1)},
        4: {2: (500, 100), 4: (50, 100), 20: (1, 50), 50: (1, 1)},
        6: {2: (500, 500), 4: (10, 50), 20: (1, 1)},
        8: {1: (500, 1000), 2: {200, 200}, 5: (50, 50), 10: (1, 1)},
        20: {1: (50, 100), 3: (1, 50), 4: (1, 1)},
        50: {1: (50, 100), 3: (1, 1)}
        }
    data_dict = {new_event size: {times: (current_events_size_choices), ...}, ...}
    (current_events_size_choices)  is minimum size of AdditiveEvents to use with 'indexed_values'
    by ('flattened_list', 'tuple_list') methods.
    """

    def test_AdditiveEvents_get_fastest_method_one_current_events_and_one_times_never_picks_indexed_values(self):
        accepted_choices = ('tuple_list', 'flattened_list')
        current_events_one = self.identity_a.get_fastest_combine_method
        for power_of_two in range(20):
            """
            events are:
            len(events) = 2**power_of_two (start =1, end = about 10**6)
            single = 1 occurrence
            some = 0, 1, 2 occurrences
            high = 2 ** event value
            """
            single_occurrence, some_occurrence, high_occurrence = next(events_generator())
            self.assertIn(current_events_one(1, single_occurrence), accepted_choices)
            self.assertIn(current_events_one(1, some_occurrence), accepted_choices)
            self.assertIn(current_events_one(1, high_occurrence), accepted_choices)

    def test_AdditiveEvents_get_fastest_method_tuple_vs_flattened_by_total_occurrences_min(self):
        self.assertEqual(self.identity_a.get_fastest_combine_method(1, [(1, 1)]), 'flattened_list')

    def test_AdditiveEvents_get_fastest_method_tuple_vs_flattened_by_total_occurrences_mid(self):
        events = [(1, 1)] * 100
        self.assertEqual(self.identity_a.get_fastest_combine_method(1, events), 'flattened_list')

    def test_AdditiveEvents_get_fastest_method_tuple_vs_flattened_by_total_occurrences_edge(self):
        events = [(1, 1)] * 9999
        self.assertEqual(self.identity_a.get_fastest_combine_method(1, events), 'flattened_list')

    def test_AdditiveEvents_get_fastest_method_tuple_vs_flattened_by_total_occurrences_over_edge(self):
        """
        this cutoff is not for speed but for safety.  as the next test will demonstrate
        """
        events = [(1, 1)] * 10000
        self.assertEqual(self.identity_a.get_fastest_combine_method(1, events), 'tuple_list')

    def test_AdditiveEvents_demonstrate_why_there_is_cutoff_for_flattened_list(self):
        ok_events = [(1, 10 ** 4)]
        self.assertEqual(lim.flatten_events_tuple(ok_events), [1] * 10 ** 4)
        bad_events = [(1, 10 ** 20)]
        self.assertRaises((OverflowError, MemoryError), lim.flatten_events_tuple, bad_events)

    def test_AdditiveEvents_get_fastest_method_tuple_vs_flattened_by_ratio_under(self):
        events = [(1, 1), (2, 1), (3, 2), (4, 1)]
        ratio = sum([pair[1] for pair in events]) / float(len(events))
        self.assertEqual(ratio, 1.25)
        self.assertEqual(self.identity_a.get_fastest_combine_method(1, events), 'flattened_list')

    def test_AdditiveEvents_get_fastest_method_tuple_vs_flattened_by_ratio_edge(self):
        events = [(event, 1) for event in range(9)]
        events += [(10, 4)]
        ratio = sum([pair[1] for pair in events]) / float(len(events))
        self.assertEqual(ratio, 1.3)
        self.assertEqual(self.identity_a.get_fastest_combine_method(1, events), 'flattened_list')

    def test_AdditiveEvents_get_fastest_method_tuple_vs_flattened_by_ratio_over_edge(self):
        events = [(event, 1) for event in range(99)]
        events += [(100, 32)]
        ratio = sum([pair[1] for pair in events]) / float(len(events))
        self.assertEqual(ratio, 1.31)
        self.assertEqual(self.identity_a.get_fastest_combine_method(1, events), 'tuple_list')

    def test_AdditiveEvents_get_fastest_method_part_get_best_key_below_min(self):
        test_dict = {1: 1, 3: 1, 5: 1}
        self.assertEqual(lim.get_best_key(-1, test_dict), 1)

    def test_AdditiveEvents_get_fastest_method_part_get_best_key_above_max(self):
        test_dict = {1: 1, 3: 1, 5: 1}
        self.assertEqual(lim.get_best_key(1001, test_dict), 5)

    def test_AdditiveEvents_get_fastest_method_part_get_best_key_at_value(self):
        test_dict = {1: 1, 3: 1, 5: 1}
        self.assertEqual(lim.get_best_key(3, test_dict), 3)

    def test_AdditiveEvents_get_fastest_method_part_get_best_key_between_values(self):
        test_dict = {1: 1, 3: 1, 5: 1}
        self.assertEqual(lim.get_best_key(4, test_dict), 3)

    def test_AdditiveEvents_get_fastest_method_part_get_current_size_cutoff_method_variable(self):
        """
        data used for get_current_size
        {new_event_size: {times: (current_events_size_choices), ...}, ...}
        {4: {2: (500, 100), 4: (50, 100), 20: (1, 50), 50: (1, 1)},
        """
        self.assertEqual(lim.get_current_size_cutoff('flattened_list', 20, 4), 1)
        self.assertEqual(lim.get_current_size_cutoff('tuple_list', 20, 4), 50)

    def test_AdditiveEvents_get_fastest_method_part_get_current_size_cutoff_uses_get_best_key(self):
        """
        2: {10: (250, 500), 50: (100, 200), 500: (1, 1)},
        4: {2: (500, 100), 4: (50, 100), 20: (1, 50), 50: (1, 1)},
        6: ...
        """
        self.assertEqual(lim.get_current_size_cutoff('tuple_list', 20, 4), 50)
        self.assertEqual(lim.get_current_size_cutoff('tuple_list', 39, 4), 50)
        self.assertEqual(lim.get_current_size_cutoff('tuple_list', 20, 5), 50)
        self.assertEqual(lim.get_current_size_cutoff('tuple_list', 1, 1), 500)
        self.assertEqual(lim.get_current_size_cutoff('tuple_list', 10000, 100000), 1)

    def test_Additive_events_get_fastest_method_uses_size_cutoff_to_choose_size_of_one_indexed(self):
        """4: {2: (500, 100), 4: (50, 100), 20: (1, 50), 50: (1, 1)},"""
        sized_twenty = [(event, 1) for event in range(20)]
        self.assertEqual(lim.get_current_size_cutoff('flattened_list', 20, 4), 1)
        self.assertEqual(self.identity_a.get_fastest_combine_method(4, sized_twenty), 'indexed_values')

    def test_Additive_events_get_fastest_method_uses_size_cutoff_to_choose_size_of_one_other(self):
        """4: {2: (500, 100), 4: (50, 100), 20: (1, 50), 50: (1, 1)},"""
        sized_four = [(event, 2) for event in range(4)]
        self.assertEqual(lim.get_current_size_cutoff('tuple_list', 20, 4), 50)
        self.assertEqual(self.identity_a.get_fastest_combine_method(4, sized_four), 'tuple_list')

    def test_Additive_events_get_fastest_method_uses_size_cutoff_to_choose_below_cutoff(self):
        """4: {2: (500, 100), 4: (50, 100), 20: (1, 50), 50: (1, 1)},"""
        sized_four = [(event, 2) for event in range(4)]
        current_size_five = lim.AdditiveEvents(dict.fromkeys(range(5), 1))
        self.assertEqual(lim.get_current_size_cutoff('tuple_list', 20, 4), 50)
        self.assertEqual(current_size_five.get_fastest_combine_method(20, sized_four), 'tuple_list')

    def test_Additive_events_get_fastest_method_uses_size_cutoff_to_choose_at_cutoff(self):
        """4: {2: (500, 100), 4: (50, 100), 20: (1, 50), 50: (1, 1)},"""
        sized_four = [(event, 2) for event in range(4)]
        current_size_fifty = lim.AdditiveEvents(dict.fromkeys(range(50), 1))
        self.assertEqual(lim.get_current_size_cutoff('tuple_list', 20, 4), 50)
        self.assertEqual(current_size_fifty.get_fastest_combine_method(20, sized_four), 'indexed_values')

    def test_Additive_events_get_fastest_method_uses_size_cutoff_to_choose_above_cutoff(self):
        """4: {2: (500, 100), 4: (50, 100), 20: (1, 50), 50: (1, 1)},"""
        sized_four = [(event, 2) for event in range(4)]
        current_size_fifty_one = lim.AdditiveEvents(dict.fromkeys(range(51), 1))
        self.assertEqual(lim.get_current_size_cutoff('tuple_list', 20, 4), 50)
        self.assertEqual(current_size_fifty_one.get_fastest_combine_method(20, sized_four), 'indexed_values')

    def test_REGRESSION_AdditiveEvents_combine_one_event_all_methods(self):
        flattened = lim.AdditiveEvents({0: 1})
        tuple_list = lim.AdditiveEvents({0: 1})
        indexed = lim.AdditiveEvents({0: 1})
        fastest = lim.AdditiveEvents({0: 1})
        events = [(1, 1)]
        flattened.combine(1, events, 'flattened_list')
        tuple_list.combine(1, events, 'tuple_list')
        indexed.combine(1, events, 'indexed_values')
        fastest.combine(1, events, 'fastest')
        self.assertEqual(flattened.all_events, events)
        self.assertEqual(tuple_list.all_events, events)
        self.assertEqual(indexed.all_events, events)
        self.assertEqual(fastest.all_events, events)

    #  TODO check
    #  AdditiveEvents basic combine and remove tests
    def test_AdditiveEvents_combine_works_with_low_total_occurrences_events(self):
        low_ratio_tuples = [(1, 1), (2, 1)]
        self.identity_a.combine(1, low_ratio_tuples)
        self.assertEqual(self.identity_a.all_events, low_ratio_tuples)

    def test_AdditiveEvents_combine_works_with_high_total_occurrences_events(self):
        high_ratio_tuples = [(1, 10 ** 1000), (2, 10 ** 1000)]
        self.identity_a.combine(1, high_ratio_tuples)
        self.assertEqual(self.identity_a.all_events, high_ratio_tuples)

    def test_AdditiveEvents_one_multiple_combine_is_multiple_single_combines(self):
        tuples = [(1, 2), (3, 4)]
        self.identity_a.combine(1, tuples)
        self.identity_a.combine(1, tuples)
        self.identity_b.combine(2, tuples)
        self.assertEqual(self.identity_a.all_events,
                         self.identity_b.all_events)

    def test_AdditiveEvents_combine_combines_correctly(self):
        tuple_list = [(2, 2), (1, 2)]
        self.identity_a.combine(2, tuple_list)
        self.assertEqual(self.identity_a.all_events,
                         [(2, 4), (3, 8), (4, 4)])

    def test_AdditiveEvents_combine_works_with_long_large_number_list(self):
        tuple_list = [(x, 10 ** 1000) for x in range(-1000, 1000)]
        self.identity_a.combine(1, tuple_list)
        self.assertEqual(self.identity_a.all_events, tuple_list)

    def test_AdditiveEvents_remove_demonstration(self):
        a_coin_toss = [(0, 1), (1, 1)]
        arbitrary_events = [(-1, 5), (10, 7)]
        three_coin_tosses = [(0, 1), (1, 3), (2, 3), (3, 1)]
        self.identity_a.combine(3, a_coin_toss)
        self.assertEqual(self.identity_a.all_events, three_coin_tosses)

        self.identity_a.combine(3, arbitrary_events)
        self.assertNotEqual(self.identity_a.all_events, three_coin_tosses)
        self.assertEqual(self.identity_a.event_range, (-3, 33))

        self.identity_a.remove(3, arbitrary_events)
        self.assertEqual(self.identity_a.all_events, three_coin_tosses)

        self.identity_a.remove(2, a_coin_toss)
        self.assertEqual(self.identity_a.all_events, a_coin_toss)

    def test_AdditiveEvents_remove_removes_correctly(self):
        arbitrary_tuples = [(-5, 2), (0, 5), (3, 10)]
        self.identity_a.combine(5, arbitrary_tuples)
        self.identity_b.combine(10, arbitrary_tuples)
        self.identity_b.remove(5, arbitrary_tuples)
        self.assertEqual(self.identity_a.all_events,
                         self.identity_b.all_events)

    def test_AdditiveEvents_remove_works_for_large_numbers(self):
        arbitrary_tuples_large = [(-5, 10 ** 500), (0, 5 * 10 ** 700), (3, 2 ** 1000)]

        self.identity_a.combine(1, arbitrary_tuples_large)
        self.identity_b.combine(2, arbitrary_tuples_large)
        self.identity_b.remove(1, arbitrary_tuples_large)
        self.assertEqual(self.identity_a.all_events,
                         self.identity_b.all_events)

    def test_AdditiveEvents_combine_works_regardless_of_order(self):
        arbitrary_a = [(1, 2), (3, 10 ** 456)]
        arbitrary_b = [(0, 5), (-1, 2)]
        self.identity_a.combine(1, arbitrary_a)
        self.identity_a.combine(2, arbitrary_b)
        self.identity_b.combine(2, arbitrary_b)
        self.identity_b.combine(1, arbitrary_a)
        self.assertEqual(self.identity_a.all_events,
                         self.identity_b.all_events)

    def test_AdditiveEvents_remove_removes_same_regardless_of_order(self):
        arbitrary_a = [(-1, 2), (3, 5)]
        arbitrary_b = [(100, 4), (0, 9)]
        self.identity_a.combine(5, arbitrary_a)
        self.identity_a.combine(5, arbitrary_b)
        self.identity_b.combine(1, arbitrary_b)
        self.identity_b.combine(1, arbitrary_a)
        self.identity_a.remove(3, arbitrary_a)
        self.identity_a.remove(3, arbitrary_b)
        self.identity_a.remove(1, arbitrary_b)
        self.identity_a.remove(1, arbitrary_a)
        self.assertEqual(self.identity_a.all_events,
                         self.identity_b.all_events)


def events_generator():
    step_by_power_of_two = 1
    while True:
        single_occurrence = [(event, 1) for event in range(step_by_power_of_two)]
        middle_occurrences = [(event, event % 3) for event in range(step_by_power_of_two)]
        high_occurrences = [(event, 2 * event) for event in range(step_by_power_of_two)]
        step_by_power_of_two *= 2
        yield (single_occurrence, middle_occurrences, high_occurrences)


if __name__ == '__main__':
    unittest.main()
