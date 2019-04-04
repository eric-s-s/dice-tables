import unittest

from dicetables import AdditiveEvents
from dicetables.tools.orderedcombinations import (get_combination_occurrences, ordered_combinations_of_events,
                                                  count_unique_combination_keys, largest_permitted_pool_size
                                                  )


class TestOrderedCombinations(unittest.TestCase):
    def test_count_number_of_combinations_single_key(self):
        to_use = {1: 1, 2: 2, 3: 3, 4: 4}
        self.assertEqual(get_combination_occurrences((1,), to_use), 1)
        self.assertEqual(get_combination_occurrences((2,), to_use), 2)
        self.assertEqual(get_combination_occurrences((3,), to_use), 3)
        self.assertEqual(get_combination_occurrences((4,), to_use), 4)

    def test_count_number_of_combinations_single_key_repeated(self):
        to_use = {1: 1, 2: 2, 3: 3, 4: 4}
        self.assertEqual(get_combination_occurrences((1, 1, 1), to_use), 1)
        self.assertEqual(get_combination_occurrences((2, 2, 2), to_use), 8)
        self.assertEqual(get_combination_occurrences((3, 3, 3), to_use), 27)
        self.assertEqual(get_combination_occurrences((4, 4, 4), to_use), 64)

    def test_count_number_of_combinations_all_values_one_all_possible_groups(self):
        to_use = dict.fromkeys(range(1, 5), 1)
        self.assertEqual(get_combination_occurrences((1, 1, 1), to_use), 1)
        self.assertEqual(get_combination_occurrences((2, 2, 2), to_use), 1)
        self.assertEqual(get_combination_occurrences((3, 3, 3), to_use), 1)
        self.assertEqual(get_combination_occurrences((4, 4, 4), to_use), 1)
        self.assertEqual(get_combination_occurrences((1, 1, 2), to_use), 3)
        self.assertEqual(get_combination_occurrences((1, 1, 3), to_use), 3)
        self.assertEqual(get_combination_occurrences((1, 1, 4), to_use), 3)
        self.assertEqual(get_combination_occurrences((1, 2, 2), to_use), 3)
        self.assertEqual(get_combination_occurrences((1, 3, 3), to_use), 3)
        self.assertEqual(get_combination_occurrences((1, 4, 4), to_use), 3)
        self.assertEqual(get_combination_occurrences((1, 2, 3), to_use), 6)
        self.assertEqual(get_combination_occurrences((1, 2, 4), to_use), 6)
        self.assertEqual(get_combination_occurrences((1, 3, 4), to_use), 6)
        self.assertEqual(get_combination_occurrences((2, 3, 4), to_use), 6)

    def test_count_number_of_combination_all_values_one_commutative_property(self):
        to_use = dict.fromkeys(range(1, 15), 1)
        self.assertEqual(get_combination_occurrences((1, 2, 2, 3, 3, 3), to_use), 60)  # 6!/(1!*2!*3!)
        self.assertEqual(get_combination_occurrences((1, 2, 2, 2, 3, 3), to_use), 60)  # 6!/(1!*3!*2!)
        self.assertEqual(get_combination_occurrences((1, 1, 2, 3, 3, 3), to_use), 60)  # 6!/(2!*1!*3!)
        self.assertEqual(get_combination_occurrences((1, 1, 2, 2, 2, 3), to_use), 60)  # 6!/(2!*3!*1!)
        self.assertEqual(get_combination_occurrences((1, 1, 1, 2, 3, 3), to_use), 60)  # 6!/(3!*1!*2!)
        self.assertEqual(get_combination_occurrences((1, 1, 1, 2, 2, 3), to_use), 60)  # 6!/(3!*2!*1!)

    def test_count_number_of_combinations_all_values_one_different_groupings(self):
        to_use = dict.fromkeys(range(1, 15), 1)
        self.assertEqual(get_combination_occurrences((1, 2), to_use), 2)
        self.assertEqual(get_combination_occurrences((1, 2, 2, 3), to_use), 12)
        self.assertEqual(get_combination_occurrences((1, 1, 2, 2), to_use), 6)
        self.assertEqual(get_combination_occurrences((1, 2, 3, 4), to_use), 24)
        self.assertEqual(get_combination_occurrences((1, 1, 2, 2, 2), to_use), 10)  # 5!/(2!*3!)
        self.assertEqual(get_combination_occurrences((1, 2, 2, 3, 3), to_use), 30)  # 5!/(1!*2!*2!)
        self.assertEqual(get_combination_occurrences((1, 1, 2, 3, 3), to_use), 30)  # 5!/(2!*1!*2!)
        self.assertEqual(get_combination_occurrences((1, 1, 2, 2, 3, 3), to_use), 90)  # 6!/(2!*2!*2!)
        self.assertEqual(get_combination_occurrences((1, 2, 2, 2, 3, 3), to_use), 60)  # 6!/(1!*3!*2!)

    def test_count_number_of_combination_different_values(self):
        to_use = {key: key for key in range(1, 11)}
        self.assertEqual(get_combination_occurrences((1, 2), to_use), 4)
        self.assertEqual(get_combination_occurrences((1, 2, 2, 3), to_use), 12 * 4 * 3)
        self.assertEqual(get_combination_occurrences((2, 2, 3, 3), to_use), 6 * 4 * 9)
        self.assertEqual(get_combination_occurrences((5, 5, 10, 10), to_use), 6 * 25 * 100)

    def test_ordered_combinations_of_events_all_single_weight_simple_case(self):
        answer = ordered_combinations_of_events(AdditiveEvents({1: 1, 2: 1}), 3)
        self.assertEqual(answer, {(1, 1, 1): 1,
                                  (1, 1, 2): 3,
                                  (1, 2, 2): 3,
                                  (2, 2, 2): 1})

    def test_ordered_combinations_of_events_different_weight_is_same_as_combining_integer_events(self):
        answer = ordered_combinations_of_events(AdditiveEvents({1: 1, 2: 2, 3: 3}), 3)
        self.assertEqual(answer, {(1, 1, 1): 1,  # 3: 1
                                  (1, 1, 2): 6,  # 4: 6
                                  (1, 2, 2): 12, (1, 1, 3): 9,  # 5: 12+9
                                  (2, 2, 2): 8, (1, 2, 3): 36,  # 6: 8+36
                                  (1, 3, 3): 27, (2, 2, 3): 36,  # 7: 27+36
                                  (2, 3, 3): 54,  # 8: 54
                                  (3, 3, 3): 27})  # 9: 27
        answer = AdditiveEvents.new().combine(AdditiveEvents({1: 1, 2: 2, 3: 3}), 3).get_dict()
        self.assertEqual(answer, {3: 1, 4: 6, 5: 21, 6: 44, 7: 63, 8: 54, 9: 27})

    def test_count_unique_combination_keys(self):
        events = AdditiveEvents({key: key for key in range(1, 7)})
        for times in range(1, 5):
            number_of_keys = len(ordered_combinations_of_events(events, times).keys())
            self.assertEqual(number_of_keys, count_unique_combination_keys(events, times))

    def test_largest_permitted_pool_size_zero(self):
        events = AdditiveEvents(dict.fromkeys(range(3), 1))
        max_keys = 2
        self.assertEqual(largest_permitted_pool_size(events, max_keys), 0)

    def test_largest_permitted_pool_size_keys_equal_pool_size(self):
        events = AdditiveEvents(dict.fromkeys(range(3), 1))
        pool_size = 5
        self.assertEqual(count_unique_combination_keys(events, pool_size), 21)
        max_keys = 21
        self.assertEqual(largest_permitted_pool_size(events, max_keys), pool_size)

    def test_largest_permitted_pool_size_keys_gt_pool_size(self):
        events = AdditiveEvents(dict.fromkeys(range(3), 1))
        pool_size = 5
        next_pool_size = 6
        self.assertEqual(count_unique_combination_keys(events, pool_size), 21)
        self.assertEqual(count_unique_combination_keys(events, next_pool_size), 28)
        for max_keys in range(22, 28):
            self.assertEqual(largest_permitted_pool_size(events, max_keys), pool_size)
        self.assertEqual(largest_permitted_pool_size(events, 28), next_pool_size)
