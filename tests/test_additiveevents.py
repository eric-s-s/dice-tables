# pylint: disable=missing-docstring, invalid-name, too-many-public-methods


import unittest

from dicetables.additiveevents import AdditiveEvents, scrub_zeroes
from dicetables.eventsbases.eventerrors import InvalidEventsError


class TestAdditiveEvents(unittest.TestCase):
    def test_scrub_zeroes_no_zeroes_dict(self):
        self.assertEqual(scrub_zeroes({1: 2, 3: 4}), {1: 2, 3: 4})

    def test_scrub_zeroes_zeroes_in_dict(self):
        self.assertEqual(scrub_zeroes({1: 2, 3: 0, 4: 1, 5: 0}), {1: 2, 4: 1})

    def test_AdditiveEvents__class_method__new(self):
        self.assertEqual(AdditiveEvents.new().get_dict(), {0: 1})

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

    def test_AdditiveEvents_input_dict_mutation_has_no_effect(self):
        input_dict = {1: 1}
        events = AdditiveEvents(input_dict)
        input_dict[1] = "banana"
        self.assertEqual(events.get_dict(), {1: 1})

    def test_AdditiveEvents_string_returns_min_to_max(self):
        table = AdditiveEvents({-1: 1, 2: 1, 5: 1})
        self.assertEqual(str(table), "table from -1 to 5")

    def test_AdditiveEvents_string_is_in_order_and_ignores_high_zero_values(self):
        table = AdditiveEvents({2: 0, 1: 1, -1: 1, -2: 0})
        self.assertEqual(str(table), "table from -1 to 1")

    def test_AdditiveEvents_combine_negative_times_does_nothing(self):
        new = AdditiveEvents.new().combine(AdditiveEvents({1: 1}), -1)
        self.assertEqual(new.get_dict(), {0: 1})

    def test_AdditiveEvents_combine_by_dictionary(self):
        to_combine = AdditiveEvents({1: 2, 2: 2})
        new = AdditiveEvents.new().combine_by_dictionary(to_combine, 1)
        self.assertEqual(new, to_combine)

    def test_AdditiveEvents_combine_by_flattened_list(self):
        to_combine = AdditiveEvents({1: 1, 2: 2})
        new = AdditiveEvents.new().combine_by_flattened_list(to_combine, 1)
        self.assertEqual(new, to_combine)

    def test_AdditiveEvents_combine_by_indexed_values(self):
        to_combine = AdditiveEvents({1: 1, 2: 2})
        new = AdditiveEvents.new().combine_by_indexed_values(to_combine, 1)
        self.assertEqual(new, to_combine)

    def test_AdditiveEvents_combine(self):
        to_combine = AdditiveEvents({1: 1, 2: 2})
        new = AdditiveEvents.new().combine(to_combine, 1)
        self.assertEqual(new, to_combine)

    def test_AdditiveEvents_combine_works_with_low_total_occurrences_events(self):
        low_ratio_events = AdditiveEvents({1: 1, 2: 1})
        new = AdditiveEvents.new().combine(low_ratio_events, 1)
        self.assertEqual(new.get_dict(), low_ratio_events.get_dict())

    def test_AdditiveEvents_combine_works_with_high_total_occurrences_events(self):
        high_ratio_dict = {1: 10**1000, 2: 10**1000}
        new = AdditiveEvents.new().combine(AdditiveEvents(high_ratio_dict), 1)
        self.assertEqual(new.get_dict(), high_ratio_dict)

    def test_AdditiveEvents_one_multiple_combine_is_multiple_single_combines(self):
        to_add = AdditiveEvents({1: 2, 3: 4})
        one = AdditiveEvents.new().combine(to_add, 1)
        two = one.combine(to_add, 1)
        two_alt = AdditiveEvents.new().combine(to_add, 2)
        self.assertEqual(two.get_dict(), two_alt.get_dict())

    def test_AdditiveEvents_combine_combines_correctly(self):
        to_add = AdditiveEvents({1: 2, 2: 2})
        new = AdditiveEvents.new().combine(to_add, 2)
        self.assertEqual(new.get_dict(), {2: 4, 3: 8, 4: 4})

    def test_AdditiveEvents_combine_works_with_long_large_number_list(self):
        silly_dict = dict.fromkeys(range(-1000, 1000), 10**1000)
        to_add = AdditiveEvents(silly_dict)
        new = AdditiveEvents.new().combine(to_add, 1)
        self.assertEqual(new.get_dict(), silly_dict)

    def test_AdditiveEvents_remove_removes_correctly(self):
        arbitrary_events = AdditiveEvents({-5: 3, 4: 10, 7: 1})
        five_a = AdditiveEvents.new().combine(arbitrary_events, 5)
        ten_b = AdditiveEvents.new().combine(arbitrary_events, 10)
        five_b = ten_b.remove(arbitrary_events, 5)
        self.assertEqual(five_a, five_b)

    def test_AdditiveEvents_remove_works_for_large_numbers(self):
        arbitrary_large_events = AdditiveEvents({-5: 10**500, 0: 5 * 10**700, 3: 2**1000})
        one_large = AdditiveEvents.new().combine(arbitrary_large_events, 1)
        two_large = AdditiveEvents.new().combine(arbitrary_large_events, 2)
        alt_one_large = two_large.remove(arbitrary_large_events, 1)
        self.assertEqual(one_large, alt_one_large)

    def test_AdditiveEvents_combine_works_regardless_of_order(self):
        arbitrary_a = AdditiveEvents({1: 2, 3: 10**456})
        arbitrary_b = AdditiveEvents({-1: 2, 0: 5})
        one_a = AdditiveEvents.new().combine(arbitrary_a, 1)
        one_a_two_b = one_a.combine(arbitrary_b, 2)
        two_b = AdditiveEvents.new().combine(arbitrary_b, 2)
        two_b_one_a = two_b.combine(arbitrary_a, 1)
        self.assertEqual(one_a_two_b, two_b_one_a)

    def test_AdditiveEvents_remove_removes_same_regardless_of_order(self):
        arbitrary_a = AdditiveEvents({-1: 2, 3: 5})
        arbitrary_b = AdditiveEvents({0: 9, 100: 4})
        five_a = AdditiveEvents.new().combine(arbitrary_a, 5)
        five_a_five_b = five_a.combine(arbitrary_b, 5)
        two_a_five_b = five_a_five_b.remove(arbitrary_a, 3)
        two_a_two_b = two_a_five_b.remove(arbitrary_b, 3)
        two_a_one_b = two_a_two_b.remove(arbitrary_b, 1)
        one_a_one_b = two_a_one_b.remove(arbitrary_a, 1)

        one_b = AdditiveEvents.new().combine(arbitrary_b, 1)
        one_b_one_a = one_b.combine(arbitrary_a, 1)
        self.assertEqual(one_a_one_b, one_b_one_a)

    def test_AdditiveEvents_combine_defaults_to_one_time(self):
        to_use = AdditiveEvents({1: 2})
        test = AdditiveEvents.new().combine(to_use)
        self.assertEqual(test.get_dict(), {1: 2})

    def test_AdditiveEvents_combine_by_dictionary_defaults_to_one_time(self):
        to_use = AdditiveEvents({1: 2})
        test = AdditiveEvents.new().combine_by_dictionary(to_use)
        self.assertEqual(test.get_dict(), {1: 2})

    def test_AdditiveEvents_combine_by_indexed_values_defaults_to_one_time(self):
        to_use = AdditiveEvents({1: 2})
        test = AdditiveEvents.new().combine_by_indexed_values(to_use)
        self.assertEqual(test.get_dict(), {1: 2})

    def test_AdditiveEvents_combine_by_flattened_list_defaults_to_one_time(self):
        to_use = AdditiveEvents({1: 2})
        test = AdditiveEvents.new().combine_by_flattened_list(to_use)
        self.assertEqual(test.get_dict(), {1: 2})

    def test_AdditiveEvents_remove_defaults_to_one_time(self):
        to_use = AdditiveEvents({1: 2})
        test = AdditiveEvents({1: 2}).remove(to_use)
        self.assertEqual(test, AdditiveEvents.new())


if __name__ == "__main__":
    unittest.main()
