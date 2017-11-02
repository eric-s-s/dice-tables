import unittest

from dicetables.tools.orderedcombinations import ordered_combinations_of_events
from dicetables.bestworstmid import (DicePool, BestOfDicePool, WorstOfDicePool, UpperMidOfDicePool,
                                     LowerMidOfDicePool, generate_events_dict)

from dicetables import Die, WeightedDie, ModDie


class MockOfDicePool(DicePool):
    def __init__(self, input_die, pool_size, select):
        super(MockOfDicePool, self).__init__(input_die, pool_size, select)

    def _generate_dict(self):
        return {0: 1}


class TestBestWorstMid(unittest.TestCase):

    def test_cannot_instantiate_DicePool(self):
        #  Damn you coveralls!
        self.assertRaises(NotImplementedError, DicePool, Die(6), 3, 2)

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
        self.assertEqual(test.weight_info(), 'Mock 2 of 3D6\ninput_die info:\n    No weights')

        test = MockOfDicePool(WeightedDie({1: 2, 2: 4}), 5, 2)
        expected = (
            'Mock 2 of 5D2  W:6\ninput_die info:\n' +
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

    def test_BestOfDicePool_get_dict_edge_case_pool_and_select_equal(self):
        test = BestOfDicePool(Die(2), 2, 2)
        self.assertEqual(test.get_dict(), {2: 1, 3: 2, 4: 1})  # same as 2D2

    def test_BestOfDicePool_get_dict_edge_case_select_zero(self):
        test = BestOfDicePool(Die(2), 2, 0)
        self.assertEqual(test.get_dict(), {0: 4})

    def test_BestOfDicePool_get_dict_Die(self):
        test = BestOfDicePool(Die(3), 3, 2)
        self.assertEqual(test.get_dict(), {2: 1, 3: 3, 4: 7, 5: 9, 6: 7})

        test = BestOfDicePool(Die(3), 3, 1)
        self.assertEqual(test.get_dict(), {1: 1, 2: 7, 3: 19})

    def test_BestOfDicePool_get_dict_ModDie(self):
        test = BestOfDicePool(ModDie(3, -1), 3, 2)
        self.assertEqual(test.get_dict(), {0: 1, 1: 3, 2: 7, 3: 9, 4: 7})

        test = BestOfDicePool(ModDie(3, -1), 3, 1)
        self.assertEqual(test.get_dict(), {0: 1, 1: 7, 2: 19})

    def test_BestOfDicePool_get_dict_WeightedDie(self):
        test = BestOfDicePool(WeightedDie({1: 2, 3: 3}), 3, 2)
        self.assertEqual(test.get_dict(), {2: 1*(2*2*2), 4: 3*(2*2*3), 6: 3*(2*3*3)+1*(3*3*3)})

        test = BestOfDicePool(WeightedDie({1: 2, 3: 3}), 3, 1)
        self.assertEqual(test.get_dict(), {1: 8, 3: 3*(2*2*3)+3*(2*3*3)+1*(3*3*3)})

    def test_BestOfDicePool_str(self):
        self.assertEqual(str(BestOfDicePool(Die(2), 2, 1)), 'Best 1 of 2D2')

    def test_BestOfDicePool_repr(self):
        self.assertEqual(repr(BestOfDicePool(Die(2), 2, 1)), 'BestOfDicePool(Die(2), 2, 1)')

    def test_BestOfDicePool_multiply_str(self):
        self.assertEqual(BestOfDicePool(Die(2), 2, 1).multiply_str(3), '3(Best 1 of 2D2)')

    def test_BestOfDicePool_weight_info(self):
        self.assertEqual(BestOfDicePool(Die(2), 2, 1).weight_info(), 'Best 1 of 2D2\ninput_die info:\n    No weights')

    def test_WorstOfDicePool_get_dict_edge_case_pool_and_select_equal(self):
        test = WorstOfDicePool(Die(2), 2, 2)
        self.assertEqual(test.get_dict(), {2: 1, 3: 2, 4: 1})  # same as 2D2

    def test_WorstOfDicePool_get_dict_edge_case_select_zero(self):
        test = WorstOfDicePool(Die(2), 2, 0)
        self.assertEqual(test.get_dict(), {0: 4})

    def test_WorstOfDicePool_get_dict_Die(self):
        test = WorstOfDicePool(Die(3), 3, 2)
        self.assertEqual(test.get_dict(), {2: 7, 3: 9, 4: 7, 5: 3, 6: 1})

        test = WorstOfDicePool(Die(3), 3, 1)
        self.assertEqual(test.get_dict(), {1: 19, 2: 7, 3: 1})

    def test_WorstOfDicePool_get_dict_ModDie(self):
        test = WorstOfDicePool(ModDie(3, -1), 3, 2)
        self.assertEqual(test.get_dict(), {0: 7, 1: 9, 2: 7, 3: 3, 4: 1})

        test = WorstOfDicePool(ModDie(3, -1), 3, 1)
        self.assertEqual(test.get_dict(), {0: 19, 1: 7, 2: 1})

    def test_WorstOfDicePool_get_dict_WeightedDie(self):
        test = WorstOfDicePool(WeightedDie({1: 2, 3: 3}), 3, 2)
        self.assertEqual(test.get_dict(), {2: (2*2*2)+3*(2*2*3), 4: 3*(2*3*3), 6: 1*(3*3*3)})

        test = WorstOfDicePool(WeightedDie({1: 2, 3: 3}), 3, 1)
        self.assertEqual(test.get_dict(), {1: 8+3*(2*2*3)+3*(2*3*3), 3: 1*(3*3*3)})

    def test_WorstOfDicePool_str(self):
        self.assertEqual(str(WorstOfDicePool(Die(2), 2, 1)), 'Worst 1 of 2D2')

    def test_WorstOfDicePool_repr(self):
        self.assertEqual(repr(WorstOfDicePool(Die(2), 2, 1)), 'WorstOfDicePool(Die(2), 2, 1)')

    def test_WorstOfDicePool_multiply_str(self):
        self.assertEqual(WorstOfDicePool(Die(2), 2, 1).multiply_str(3), '3(Worst 1 of 2D2)')

    def test_WorstOfDicePool_weight_info(self):
        self.assertEqual(WorstOfDicePool(Die(2), 2, 1).weight_info(), 'Worst 1 of 2D2\ninput_die info:\n    No weights')

    def test_UpperMidOfDicePool_get_dict_edge_case_pool_and_select_equal(self):
        test = UpperMidOfDicePool(Die(2), 2, 2)
        self.assertEqual(test.get_dict(), {2: 1, 3: 2, 4: 1})  # same as 2D2

    def test_UpperMidOfDicePool_get_dict_edge_case_select_zero(self):
        test = UpperMidOfDicePool(Die(2), 2, 0)
        self.assertEqual(test.get_dict(), {0: 4})

    def test_UpperMidOfDicePool_get_dict_Die(self):
        test = UpperMidOfDicePool(Die(2), 4, 2)
        self.assertEqual(test.get_dict(), {2: 5, 3: 6, 4: 5})

        test = UpperMidOfDicePool(Die(3), 3, 1)
        self.assertEqual(test.get_dict(), {1: 7, 2: 13, 3: 7})

    def test_UpperMidOfDicePool_get_dict_takes_higher_when_no_even_split(self):
        self.assertEqual(ordered_combinations_of_events(Die(2), 4),
                         {(1, 1, 1, 1): 1,
                          (1, 1, 1, 2): 4,
                          (1, 1, 2, 2): 6,
                          (1, 2, 2, 2): 4,
                          (2, 2, 2, 2): 1}
                         )

        test = UpperMidOfDicePool(Die(2), 4, 3)
        self.assertEqual(test.get_dict(), {3: 1, 4: 4, 5: 6, 6: 5})

        test = UpperMidOfDicePool(Die(2), 4, 2)
        self.assertEqual(test.get_dict(), {2: 5, 3: 6, 4: 5})

        test = UpperMidOfDicePool(Die(2), 4, 1)
        self.assertEqual(test.get_dict(), {1: 5, 2: 11})

    def test_UpperMidOfDicePool_get_dict_ModDie(self):
        """
        {(0, 0, 0): 1,
         (0, 0, 1): 3,
         (0, 0, 2): 3,
         (0, 1, 1): 3,
         (0, 1, 2): 6,
         (0, 2, 2): 3,
         (1, 1, 1): 1,
         (1, 1, 2): 3,
         (1, 2, 2): 3,
         (2, 2, 2): 1}
        """
        test = UpperMidOfDicePool(ModDie(3, -1), 3, 2)
        self.assertEqual(test.get_dict(), {0: 1, 1: 3, 2: 7, 3: 9, 4: 7})

        test = UpperMidOfDicePool(ModDie(3, -1), 3, 1)
        self.assertEqual(test.get_dict(), {0: 7, 1: 13, 2: 7})

    def test_UpperMidOfDicePool_get_dict_WeightedDie(self):
        """
        {(1, 1, 1): 8,
         (1, 1, 3): 36,
         (1, 3, 3): 54,
         (3, 3, 3): 27}
        """
        test = UpperMidOfDicePool(WeightedDie({1: 2, 3: 3}), 3, 2)
        self.assertEqual(test.get_dict(), {2: 8, 4: 36, 6: 54+27})

        test = UpperMidOfDicePool(WeightedDie({1: 2, 3: 3}), 3, 1)
        self.assertEqual(test.get_dict(), {1: 44, 3: 54+27})

    def test_UpperMidOfDicePool_str(self):
        self.assertEqual(str(UpperMidOfDicePool(Die(2), 2, 1)), 'UpperMid 1 of 2D2')

    def test_UpperMidOfDicePool_repr(self):
        self.assertEqual(repr(UpperMidOfDicePool(Die(2), 2, 1)), 'UpperMidOfDicePool(Die(2), 2, 1)')

    def test_UpperMidOfDicePool_multiply_str(self):
        self.assertEqual(UpperMidOfDicePool(Die(2), 2, 1).multiply_str(3), '3(UpperMid 1 of 2D2)')

    def test_UpperMidOfDicePool_weight_info(self):
        self.assertEqual(UpperMidOfDicePool(Die(2), 2, 1).weight_info(),
                         'UpperMid 1 of 2D2\ninput_die info:\n    No weights')

    def test_LowerMidOfDicePool_get_dict_edge_case_pool_and_select_equal(self):
        test = LowerMidOfDicePool(Die(2), 2, 2)
        self.assertEqual(test.get_dict(), {2: 1, 3: 2, 4: 1})  # same as 2D2

    def test_LowerMidOfDicePool_get_dict_edge_case_select_zero(self):
        test = LowerMidOfDicePool(Die(2), 2, 0)
        self.assertEqual(test.get_dict(), {0: 4})

    def test_LowerMidOfDicePool_get_dict_Die(self):
        test = LowerMidOfDicePool(Die(2), 4, 2)
        self.assertEqual(test.get_dict(), {2: 5, 3: 6, 4: 5})

        test = LowerMidOfDicePool(Die(3), 3, 1)
        self.assertEqual(test.get_dict(), {1: 7, 2: 13, 3: 7})

    def test_LowerMidOfDicePool_get_dict_takes_higher_when_no_even_split(self):
        self.assertEqual(ordered_combinations_of_events(Die(2), 4),
                         {(1, 1, 1, 1): 1,
                          (1, 1, 1, 2): 4,
                          (1, 1, 2, 2): 6,
                          (1, 2, 2, 2): 4,
                          (2, 2, 2, 2): 1}
                         )

        test = LowerMidOfDicePool(Die(2), 4, 3)
        self.assertEqual(test.get_dict(), {3: 5, 4: 6, 5: 4, 6: 1})

        test = LowerMidOfDicePool(Die(2), 4, 2)
        self.assertEqual(test.get_dict(), {2: 5, 3: 6, 4: 5})

        test = LowerMidOfDicePool(Die(2), 4, 1)
        self.assertEqual(test.get_dict(), {1: 11, 2: 5})

    def test_LowerMidOfDicePool_get_dict_ModDie(self):
        """
        {(0, 0, 0): 1,
         (0, 0, 1): 3,
         (0, 0, 2): 3,
         (0, 1, 1): 3,
         (0, 1, 2): 6,
         (0, 2, 2): 3,
         (1, 1, 1): 1,
         (1, 1, 2): 3,
         (1, 2, 2): 3,
         (2, 2, 2): 1}
        """
        test = LowerMidOfDicePool(ModDie(3, -1), 3, 2)
        self.assertEqual(test.get_dict(), {0: 7, 1: 9, 2: 7, 3: 3, 4: 1})

        test = LowerMidOfDicePool(ModDie(3, -1), 3, 1)
        self.assertEqual(test.get_dict(), {0: 7, 1: 13, 2: 7})

    def test_LowerMidOfDicePool_get_dict_WeightedDie(self):
        """
        {(1, 1, 1): 8,
         (1, 1, 3): 36,
         (1, 3, 3): 54,
         (3, 3, 3): 27}
        """
        test = LowerMidOfDicePool(WeightedDie({1: 2, 3: 3}), 3, 2)
        self.assertEqual(test.get_dict(), {2: 8+36, 4: 54, 6: 27})

        test = LowerMidOfDicePool(WeightedDie({1: 2, 3: 3}), 3, 1)
        self.assertEqual(test.get_dict(), {1: 44, 3: 54+27})

    def test_LowerMidOfDicePool_str(self):
        self.assertEqual(str(LowerMidOfDicePool(Die(2), 2, 1)), 'LowerMid 1 of 2D2')

    def test_LowerMidOfDicePool_repr(self):
        self.assertEqual(repr(LowerMidOfDicePool(Die(2), 2, 1)), 'LowerMidOfDicePool(Die(2), 2, 1)')

    def test_LowerMidOfDicePool_multiply_str(self):
        self.assertEqual(LowerMidOfDicePool(Die(2), 2, 1).multiply_str(3), '3(LowerMid 1 of 2D2)')

    def test_LowerMidOfDicePool_weight_info(self):
        self.assertEqual(LowerMidOfDicePool(Die(2), 2, 1).weight_info(),
                         'LowerMid 1 of 2D2\ninput_die info:\n    No weights')
