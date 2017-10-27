import unittest

from dicetables.bestworstmid import (DicePool, BestOfDicePool, WorstOfDicePool, UpperMidOfDicePool,
                                     LowerMidOfDicePool, generate_events_dict)

from dicetables import Die, WeightedDie, ModDie


class MockOfDicePool(DicePool):
    def __init__(self, input_die, pool_size, select):
        super(MockOfDicePool, self).__init__(input_die, pool_size, select)

    def _generate_dict(self):
        return {0: 1}


class TestBestWorstMid(unittest.TestCase):
    def test_DicePool_init(self):
        test = MockOfDicePool(Die(6), 3, 2)
        self.assertEqual(test.get_input_die(), Die(6))
        self.assertEqual(test.get_pool_size(), 3)
        self.assertEqual(test.get_select(), 2)
        self.assertEqual(test.get_dict(), {0: 1})

    def test_DicePool_init_raises_value_error_when_select_gt_pool_size(self):
        MockOfDicePool(Die(6), 3, 3)
        self.assertRaises(ValueError, MockOfDicePool, Die(6), 2, 3)

    def test_DicePool_size_is_input_die_size_times_select(self):
        test = MockOfDicePool(Die(6), 10, 5)
        self.assertEqual(test.get_size(), 30)

        test = MockOfDicePool(WeightedDie({1: 2, 3: 4}), 100, 3)
        self.assertEqual(test.get_size(), 9)

        test = MockOfDicePool(ModDie(6, 10), 1000, 4)
        self.assertEqual(test.get_size(), 24)

    def test_DicePool_get_weight_is_input_die_weight_times_select(self):
        die = Die(6)
        self.assertEqual(die.get_weight(), 0)
        test = MockOfDicePool(die, 10, 5)
        self.assertEqual(test.get_weight(), 0)

        die = WeightedDie({1: 2, 3: 4})
        self.assertEqual(die.get_weight(), 6)
        test = MockOfDicePool(die, 100, 3)
        self.assertEqual(test.get_weight(), 18)

    def test_DicePool_str(self):
        test = MockOfDicePool(Die(6), 3, 2)
        self.assertEqual(str(test), 'Mock 2 of 3D6')

        test = MockOfDicePool(WeightedDie({1: 2, 3: 4}), 5, 2)
        self.assertEqual(str(test), 'Mock 2 of 5D3  W:6')

    def test_DicePool_repr(self):
        test = MockOfDicePool(Die(6), 3, 2)
        self.assertEqual(repr(test), 'MockOfDicePool(Die(6), 3, 2)')

        test = MockOfDicePool(WeightedDie({1: 2, 3: 4}), 5, 2)
        self.assertEqual(repr(test), 'MockOfDicePool(WeightedDie({1: 2, 2: 0, 3: 4}), 5, 2)')

    def test_DicePool_multiply_str(self):
        test = MockOfDicePool(Die(6), 3, 2)
        self.assertEqual(test.multiply_str(3), '3(Mock 2 of 3D6)')

        test = MockOfDicePool(WeightedDie({1: 2, 3: 4}), 5, 2)
        self.assertEqual(test.multiply_str(10), '10(Mock 2 of 5D3  W:6)')

    def test_DicePool_weight_info(self):
        test = MockOfDicePool(Die(6), 3, 2)
        self.assertEqual(test.weight_info(), 'Mock 2 of 3D6\ninput die info:\n    No weights')

        test = MockOfDicePool(WeightedDie({1: 2, 2: 4}), 5, 2)
        expected = (
            'Mock 2 of 5D2  W:6\ninput die info:\n' +
            '    a roll of 1 has a weight of 2\n' +
            '    a roll of 2 has a weight of 4'
        )
        self.assertEqual(test.weight_info(), expected)

    def test_generate_events_dict(self):
        combinations = [(1, 1, 1), (1, 1, 2), (1, 1, 3), (1, 2, 2), (1, 2, 3), (1, 3, 3),
                        (2, 2, 2), (2, 2, 3), (2, 3, 3), (3, 3, 3)]
        combinations_dict = dict.fromkeys(combinations, 1)

        self.assertEqual(generate_events_dict(combinations_dict, 0, 3), {3: 1, 4: 1, 5: 2, 6: 2, 7: 2, 8: 1, 9: 1})
        self.assertEqual(generate_events_dict(combinations_dict, 1, 3), {2: 1, 3: 1, 4: 3, 5: 2, 6: 3})
        self.assertEqual(generate_events_dict(combinations_dict, 0, 2), {2: 3, 3: 2, 4: 3, 5: 1, 6: 1})
        self.assertEqual(generate_events_dict(combinations_dict, 1, 2), {1: 3, 2: 4, 3: 3})
        self.assertEqual(generate_events_dict(combinations_dict, 2, 2), {0: 10})


