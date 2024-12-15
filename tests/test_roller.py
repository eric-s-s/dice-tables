import random
import unittest
from sys import version

from dicetables.additiveevents import AdditiveEvents
from dicetables.roller import Roller

VERSION = int(version[0])


class TestRoller(unittest.TestCase):
    def assert_alias_table_has_expected_counts(self, alias_table, expected_counts):
        actual_counts = dict.fromkeys(expected_counts.keys(), 0)
        for length_val in range(alias_table.length):
            for height_val in range(alias_table.height):
                actual_counts[alias_table.get(length_val, height_val)] += 1

        self.assertEqual(expected_counts, actual_counts)

        actual_primaries = {alias.primary for alias in alias_table.to_list()}
        expected_primaries = set(expected_counts.keys())
        self.assertEqual(actual_primaries, expected_primaries)

    def test_roller_init(self):
        events = AdditiveEvents({1: 2, 3: 4, 5: 6})
        roller = Roller(events)
        alias_table = roller.alias_table
        # see tools/test_alias_table.py
        self.assertEqual(alias_table.height, 2 + 4 + 6)
        self.assertEqual(alias_table.length, 3)
        self.assert_alias_table_has_expected_counts(alias_table, {1: 6, 3: 12, 5: 18})

    def test_roller_init_default_random_instance(self):
        events = AdditiveEvents.new()
        roller = Roller(events)
        self.assertIsInstance(roller.random_generator, random.Random)

    def test_roller_init_new_random_instance(self):
        events = AdditiveEvents.new()

        class MyRandom(random.Random):
            pass

        my_random = MyRandom()
        roller = Roller(events, my_random)
        self.assertEqual(roller.random_generator, my_random)

    def test_roller_roll_only_one_roll(self):
        events = AdditiveEvents({0: 1})
        roller = Roller(events)
        for _ in range(10):
            self.assertEqual(roller.roll(), 0)

    def test_roller_with_distribution(self):
        rng = random.Random(1346)
        events = AdditiveEvents({1: 1, 2: 2, 3: 1})
        roller = Roller(events, rng)

        times = 100
        rolls = [roller.roll() for _ in range(times)]
        ones = rolls.count(1)
        twos = rolls.count(2)
        threes = rolls.count(3)
        expected = [21, 50, 29]
        if VERSION < 3:
            expected = [30, 45, 25]
        self.assertEqual([ones, twos, threes], expected)
        self.assertEqual(sum(expected), times)

    def test_roller_with_custom_generator(self):
        class MyRandom(random.Random):
            def __init__(self, range_answer, *args, **kwargs):
                self.range_answer = range_answer
                super(MyRandom, self).__init__(*args, **kwargs)

            def randrange(self, start, stop=None, step=1, _int=int):
                return self.range_answer % start

        events = AdditiveEvents({1: 1, 2: 2})
        random_generator = MyRandom(1)

        roller = Roller(events, random_generator)
        self.assertEqual(roller.alias_table.get(1, 1), 2)

        for _ in range(10):
            self.assertEqual(roller.roll(), 2)

        random_generator = MyRandom(0)
        roller = Roller(events, random_generator)
        self.assertEqual(roller.alias_table.get(0, 0), 1)
        for _ in range(10):
            self.assertEqual(roller.roll(), 1)

    def test_roll_many_with_distribution(self):
        rng = random.Random(9876541)
        times = 100

        events = AdditiveEvents({1: 1, 2: 2, 3: 1})
        roller = Roller(events, rng)
        result = roller.roll_many(times)
        ones = result.count(1)
        twos = result.count(2)
        threes = result.count(3)
        expected = [25, 54, 21]
        if VERSION < 3:
            expected = [27, 46, 27]
        self.assertEqual([ones, twos, threes], expected)
        self.assertEqual(sum(expected), times)

    def test_roll_many_with_custom_generator(self):
        class MyRandom(random.Random):
            def __init__(self, range_answer, *args, **kwargs):
                self.range_answer = range_answer
                super(MyRandom, self).__init__(*args, **kwargs)

            def randrange(self, start, stop=None, step=1, _int=int):
                return self.range_answer % start

        events = AdditiveEvents({1: 1, 2: 2})
        random_generator = MyRandom(1)

        roller = Roller(events, random_generator)
        self.assertEqual(roller.alias_table.get(1, 1), 2)
        self.assertEqual([2] * 10, roller.roll_many(10))

        random_generator = MyRandom(0)
        roller = Roller(events, random_generator)
        self.assertEqual(roller.alias_table.get(0, 0), 1)
        self.assertEqual([1] * 10, roller.roll_many(10))

    def test_roll_with_large_numbers(self):
        rng = random.Random(34889970)
        events = AdditiveEvents({1: 1, 2: 10**1000, 3: 2 * 10**1000})
        roller = Roller(events, rng)

        times = 100
        result = [roller.roll() for _ in range(times)]
        ones = result.count(1)
        twos = result.count(2)
        threes = result.count(3)
        expected = [0, 29, 71]
        if VERSION < 3:
            expected = [0, 31, 69]
        self.assertEqual([ones, twos, threes], expected)
        self.assertEqual(sum(expected), times)

    def test_roll_with_large_numbers_still_has_remote_possibility_to_roll_small_number(self):
        class MyRandom(random.Random):
            def __init__(self, large_range_value, *args, **kwargs):
                self.large_range_value = large_range_value
                self.two_counter = 0
                super(MyRandom, self).__init__(*args, **kwargs)

            def randrange(self, start, stop=None, step=1, _int=int):
                if start == 2:
                    answer = self.two_counter % 2
                    self.two_counter += 1
                    return answer
                return self.large_range_value

        events = AdditiveEvents({1: 1, 2: 10**1000})
        random_generator = MyRandom(1)
        roller = Roller(events, random_generator)
        alias_table = roller.alias_table
        self.assertEqual(alias_table.height, 10**1000 + 1)

        self.assertEqual(alias_table.get(0, 1), 1)
        self.assertEqual(alias_table.get(1, 1), 2)

        expected = [1, 2, 1, 2, 1, 2, 1, 2, 1, 2]
        self.assertEqual(expected, roller.roll_many(10))

        # if you choose to mutate the random generator, I won't stop you.
        roller.random_generator.large_range_value = 2
        self.assertEqual(alias_table.get(0, 2), 2)
        self.assertEqual(alias_table.get(1, 2), 2)
        expected = [2] * 10
        self.assertEqual(expected, roller.roll_many(10))
