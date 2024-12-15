import unittest

from dicetables import Die, WeightedDie, ModDie
from dicetables.dicepool_collection import (
    DicePoolCollection,
    BestOfDicePool,
    WorstOfDicePool,
    UpperMidOfDicePool,
    LowerMidOfDicePool,
    generate_events_dict,
)
from dicetables.dicepool import DicePool
from dicetables.tools.orderedcombinations import ordered_combinations_of_events


class MockOfDicePoolCollection(DicePoolCollection):
    def __init__(self, pool: DicePool, select: int):
        super().__init__(pool, select)

    def _generate_dict(self):
        return {0: 1}


class TestBestWorstMid(unittest.TestCase):
    def test_cannot_instantiate_DicePool(self):
        #  Damn you coveralls!
        pool = DicePool(Die(6), 3)
        self.assertRaises(NotImplementedError, DicePoolCollection, pool, 2)

    def test_DicePool_init(self):
        pool = DicePool(Die(6), 3)
        test = MockOfDicePoolCollection(pool, 2)
        self.assertEqual(test.get_pool(), pool)
        self.assertEqual(test.get_select(), 2)
        self.assertEqual(test.get_dict(), {0: 1})

    def test_DicePool_init_raises_value_error_when_select_gt_pool_size(self):
        pool = DicePool(Die(6), 3)
        MockOfDicePoolCollection(pool, pool.size)
        self.assertRaises(ValueError, MockOfDicePoolCollection, pool, pool.size + 1)

    def test_DicePool_size_is_input_die_size_times_select(self):
        test = MockOfDicePoolCollection(DicePool(Die(6), 10), 5)
        self.assertEqual(test.get_size(), 30)

        test = MockOfDicePoolCollection(DicePool(WeightedDie({1: 2, 3: 4}), 100), 3)
        self.assertEqual(test.get_size(), 9)

    def test_DicePool_get_weight_is_input_die_weight_times_select(self):
        die = Die(6)
        self.assertEqual(die.get_weight(), 0)
        test = MockOfDicePoolCollection(DicePool(die, 10), 5)
        self.assertEqual(test.get_weight(), 0)

        die = WeightedDie({1: 2, 3: 4})
        self.assertEqual(die.get_weight(), 6)
        test = MockOfDicePoolCollection(DicePool(die, 100), 3)
        self.assertEqual(test.get_weight(), 18)

    def test_DicePool_str(self):
        test = MockOfDicePoolCollection(DicePool(Die(6), 3), 2)
        self.assertEqual(str(test), "MockCollection 2 of 3D6")

        test = MockOfDicePoolCollection(DicePool(WeightedDie({1: 2, 3: 4}), 5), 2)
        self.assertEqual(str(test), "MockCollection 2 of 5D3  W:6")

    def test_DicePool_repr(self):
        test = MockOfDicePoolCollection(DicePool(Die(6), 3), 2)
        expected = "MockOfDicePoolCollection(DicePool(Die(6), 3), 2)"
        self.assertEqual(repr(test), expected)

        test = MockOfDicePoolCollection(DicePool(WeightedDie({1: 2, 3: 4}), 5), 2)
        expected = "MockOfDicePoolCollection(DicePool(WeightedDie({1: 2, 2: 0, 3: 4}), 5), 2)"
        self.assertEqual(repr(test), expected)

    def test_DicePool_multiply_str(self):
        test = MockOfDicePoolCollection(DicePool(Die(6), 3), 2)
        self.assertEqual(test.multiply_str(3), "3(MockCollection 2 of 3D6)")

        test = MockOfDicePoolCollection(DicePool(WeightedDie({1: 2, 3: 4}), 5), 2)
        self.assertEqual(test.multiply_str(10), "10(MockCollection 2 of 5D3  W:6)")

    def test_DicePool_weight_info(self):
        test = MockOfDicePoolCollection(DicePool(Die(6), 3), 2)
        self.assertEqual(
            test.weight_info(), "MockCollection 2 of 3D6\ninput_die info:\n    No weights"
        )

        test = MockOfDicePoolCollection(DicePool(WeightedDie({1: 2, 2: 4}), 5), 2)
        expected = (
            "MockCollection 2 of 5D2  W:6\ninput_die info:\n"
            + "    a roll of 1 has a weight of 2\n"
            + "    a roll of 2 has a weight of 4"
        )
        self.assertEqual(test.weight_info(), expected)

    def test_generate_events_dict(self):
        combinations = [
            (1, 1, 1),
            (1, 1, 2),
            (1, 1, 3),
            (1, 2, 2),
            (1, 2, 3),
            (1, 3, 3),
            (2, 2, 2),
            (2, 2, 3),
            (2, 3, 3),
            (3, 3, 3),
        ]
        combinations_dict = dict.fromkeys(combinations, 1)

        self.assertEqual(
            generate_events_dict(combinations_dict, 0, 3),
            {3: 1, 4: 1, 5: 2, 6: 2, 7: 2, 8: 1, 9: 1},
        )
        self.assertEqual(
            generate_events_dict(combinations_dict, 1, 3), {2: 1, 3: 1, 4: 3, 5: 2, 6: 3}
        )
        self.assertEqual(
            generate_events_dict(combinations_dict, 0, 2), {2: 3, 3: 2, 4: 3, 5: 1, 6: 1}
        )
        self.assertEqual(generate_events_dict(combinations_dict, 1, 2), {1: 3, 2: 4, 3: 3})
        self.assertEqual(generate_events_dict(combinations_dict, 2, 2), {0: 10})

    def test_BestOfDicePool_get_dict_edge_case_pool_and_select_equal(self):
        test = BestOfDicePool(DicePool(Die(2), 2), 2)
        self.assertEqual(test.get_dict(), {2: 1, 3: 2, 4: 1})  # same as 2D2

    def test_BestOfDicePool_get_dict_edge_case_select_zero(self):
        test = BestOfDicePool(DicePool(Die(2), 2), 0)
        self.assertEqual(test.get_dict(), {0: 4})

    def test_BestOfDicePool_get_dict_Die(self):
        test = BestOfDicePool(DicePool(Die(3), 3), 2)
        self.assertEqual(test.get_dict(), {2: 1, 3: 3, 4: 7, 5: 9, 6: 7})

        test = BestOfDicePool(DicePool(Die(3), 3), 1)
        self.assertEqual(test.get_dict(), {1: 1, 2: 7, 3: 19})

    def test_BestOfDicePool_get_dict_ModDie(self):
        test = BestOfDicePool(DicePool(ModDie(3, -1), 3), 2)
        self.assertEqual(test.get_dict(), {0: 1, 1: 3, 2: 7, 3: 9, 4: 7})

        test = BestOfDicePool(DicePool(ModDie(3, -1), 3), 1)
        self.assertEqual(test.get_dict(), {0: 1, 1: 7, 2: 19})

    def test_BestOfDicePool_get_dict_WeightedDie(self):
        test = BestOfDicePool(DicePool(WeightedDie({1: 2, 3: 3}), 3), 2)
        self.assertEqual(
            test.get_dict(),
            {2: 1 * (2 * 2 * 2), 4: 3 * (2 * 2 * 3), 6: (3 * (2 * 3 * 3) + 1 * (3 * 3 * 3))},
        )

        test = BestOfDicePool(DicePool(WeightedDie({1: 2, 3: 3}), 3), 1)
        self.assertEqual(
            test.get_dict(), {1: 8, 3: (3 * (2 * 2 * 3) + 3 * (2 * 3 * 3) + 1 * (3 * 3 * 3))}
        )

    def test_BestOfDicePool_str(self):
        self.assertEqual(str(BestOfDicePool(DicePool(Die(2), 2), 1)), "Best 1 of 2D2")

    def test_BestOfDicePool_repr(self):
        expected = "BestOfDicePool(DicePool(Die(2), 2), 1)"
        self.assertEqual(repr(BestOfDicePool(DicePool(Die(2), 2), 1)), expected)

    def test_BestOfDicePool_multiply_str(self):
        self.assertEqual(BestOfDicePool(DicePool(Die(2), 2), 1).multiply_str(3), "3(Best 1 of 2D2)")

    def test_BestOfDicePool_weight_info(self):
        weights_str = "Best 1 of 2D2\ninput_die info:\n    No weights"
        self.assertEqual(BestOfDicePool(DicePool(Die(2), 2), 1).weight_info(), weights_str)

    def test_WorstOfDicePool_get_dict_edge_case_pool_and_select_equal(self):
        test = WorstOfDicePool(DicePool(Die(2), 2), 2)
        self.assertEqual(test.get_dict(), {2: 1, 3: 2, 4: 1})  # same as 2D2

    def test_WorstOfDicePool_get_dict_edge_case_select_zero(self):
        test = WorstOfDicePool(DicePool(Die(2), 2), 0)
        self.assertEqual(test.get_dict(), {0: 4})

    def test_WorstOfDicePool_get_dict_Die(self):
        test = WorstOfDicePool(DicePool(Die(3), 3), 2)
        self.assertEqual(test.get_dict(), {2: 7, 3: 9, 4: 7, 5: 3, 6: 1})

        test = WorstOfDicePool(DicePool(Die(3), 3), 1)
        self.assertEqual(test.get_dict(), {1: 19, 2: 7, 3: 1})

    def test_WorstOfDicePool_get_dict_ModDie(self):
        test = WorstOfDicePool(DicePool(ModDie(3, -1), 3), 2)
        self.assertEqual(test.get_dict(), {0: 7, 1: 9, 2: 7, 3: 3, 4: 1})

        test = WorstOfDicePool(DicePool(ModDie(3, -1), 3), 1)
        self.assertEqual(test.get_dict(), {0: 19, 1: 7, 2: 1})

    def test_WorstOfDicePool_get_dict_WeightedDie(self):
        test = WorstOfDicePool(DicePool(WeightedDie({1: 2, 3: 3}), 3), 2)
        self.assertEqual(
            test.get_dict(),
            {2: ((2 * 2 * 2) + 3 * (2 * 2 * 3)), 4: 3 * (2 * 3 * 3), 6: 1 * (3 * 3 * 3)},
        )

        test = WorstOfDicePool(DicePool(WeightedDie({1: 2, 3: 3}), 3), 1)
        self.assertEqual(
            test.get_dict(), {1: (8 + 3 * (2 * 2 * 3) + 3 * (2 * 3 * 3)), 3: 1 * (3 * 3 * 3)}
        )

    def test_WorstOfDicePool_str(self):
        self.assertEqual(str(WorstOfDicePool(DicePool(Die(2), 2), 1)), "Worst 1 of 2D2")

    def test_WorstOfDicePool_repr(self):
        expected = "WorstOfDicePool(DicePool(Die(2), 2), 1)"
        self.assertEqual(repr(WorstOfDicePool(DicePool(Die(2), 2), 1)), expected)

    def test_WorstOfDicePool_multiply_str(self):
        self.assertEqual(
            WorstOfDicePool(DicePool(Die(2), 2), 1).multiply_str(3), "3(Worst 1 of 2D2)"
        )

    def test_WorstOfDicePool_weight_info(self):
        weights_str = "Worst 1 of 2D2\ninput_die info:\n    No weights"
        self.assertEqual(WorstOfDicePool(DicePool(Die(2), 2), 1).weight_info(), weights_str)

    def test_UpperMidOfDicePool_get_dict_edge_case_pool_and_select_equal(self):
        test = UpperMidOfDicePool(DicePool(Die(2), 2), 2)
        self.assertEqual(test.get_dict(), {2: 1, 3: 2, 4: 1})  # same as 2D2

    def test_UpperMidOfDicePool_get_dict_edge_case_select_zero(self):
        test = UpperMidOfDicePool(DicePool(Die(2), 2), 0)
        self.assertEqual(test.get_dict(), {0: 4})

    def test_UpperMidOfDicePool_get_dict_Die(self):
        test = UpperMidOfDicePool(DicePool(Die(2), 4), 2)
        self.assertEqual(test.get_dict(), {2: 5, 3: 6, 4: 5})

        test = UpperMidOfDicePool(DicePool(Die(3), 3), 1)
        self.assertEqual(test.get_dict(), {1: 7, 2: 13, 3: 7})

    def test_UpperMidOfDicePool_get_dict_takes_higher_when_no_even_split(self):
        self.assertEqual(
            ordered_combinations_of_events(Die(2), 4),
            {(1, 1, 1, 1): 1, (1, 1, 1, 2): 4, (1, 1, 2, 2): 6, (1, 2, 2, 2): 4, (2, 2, 2, 2): 1},
        )

        test = UpperMidOfDicePool(DicePool(Die(2), 4), 3)
        self.assertEqual(test.get_dict(), {3: 1, 4: 4, 5: 6, 6: 5})

        test = UpperMidOfDicePool(DicePool(Die(2), 4), 2)
        self.assertEqual(test.get_dict(), {2: 5, 3: 6, 4: 5})

        test = UpperMidOfDicePool(DicePool(Die(2), 4), 1)
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
        test = UpperMidOfDicePool(DicePool(ModDie(3, -1), 3), 2)
        self.assertEqual(test.get_dict(), {0: 1, 1: 3, 2: 7, 3: 9, 4: 7})

        test = UpperMidOfDicePool(DicePool(ModDie(3, -1), 3), 1)
        self.assertEqual(test.get_dict(), {0: 7, 1: 13, 2: 7})

    def test_UpperMidOfDicePool_get_dict_WeightedDie(self):
        """
        {(1, 1, 1): 8,
         (1, 1, 3): 36,
         (1, 3, 3): 54,
         (3, 3, 3): 27}
        """
        test = UpperMidOfDicePool(DicePool(WeightedDie({1: 2, 3: 3}), 3), 2)
        self.assertEqual(test.get_dict(), {2: 8, 4: 36, 6: 54 + 27})

        test = UpperMidOfDicePool(DicePool(WeightedDie({1: 2, 3: 3}), 3), 1)
        self.assertEqual(test.get_dict(), {1: 44, 3: 54 + 27})

    def test_UpperMidOfDicePool_str(self):
        self.assertEqual(str(UpperMidOfDicePool(DicePool(Die(2), 2), 1)), "UpperMid 1 of 2D2")

    def test_UpperMidOfDicePool_repr(self):
        expected = "UpperMidOfDicePool(DicePool(Die(2), 2), 1)"
        self.assertEqual(repr(UpperMidOfDicePool(DicePool(Die(2), 2), 1)), expected)

    def test_UpperMidOfDicePool_multiply_str(self):
        self.assertEqual(
            UpperMidOfDicePool(DicePool(Die(2), 2), 1).multiply_str(3), "3(UpperMid 1 of 2D2)"
        )

    def test_UpperMidOfDicePool_weight_info(self):
        self.assertEqual(
            UpperMidOfDicePool(DicePool(Die(2), 2), 1).weight_info(),
            "UpperMid 1 of 2D2\ninput_die info:\n    No weights",
        )

    def test_LowerMidOfDicePool_get_dict_edge_case_pool_and_select_equal(self):
        test = LowerMidOfDicePool(DicePool(Die(2), 2), 2)
        self.assertEqual(test.get_dict(), {2: 1, 3: 2, 4: 1})  # same as 2D2

    def test_LowerMidOfDicePool_get_dict_edge_case_select_zero(self):
        test = LowerMidOfDicePool(DicePool(Die(2), 2), 0)
        self.assertEqual(test.get_dict(), {0: 4})

    def test_LowerMidOfDicePool_get_dict_Die(self):
        test = LowerMidOfDicePool(DicePool(Die(2), 4), 2)
        self.assertEqual(test.get_dict(), {2: 5, 3: 6, 4: 5})

        test = LowerMidOfDicePool(DicePool(Die(3), 3), 1)
        self.assertEqual(test.get_dict(), {1: 7, 2: 13, 3: 7})

    def test_LowerMidOfDicePool_get_dict_takes_higher_when_no_even_split(self):
        self.assertEqual(
            ordered_combinations_of_events(Die(2), 4),
            {(1, 1, 1, 1): 1, (1, 1, 1, 2): 4, (1, 1, 2, 2): 6, (1, 2, 2, 2): 4, (2, 2, 2, 2): 1},
        )

        test = LowerMidOfDicePool(DicePool(Die(2), 4), 3)
        self.assertEqual(test.get_dict(), {3: 5, 4: 6, 5: 4, 6: 1})

        test = LowerMidOfDicePool(DicePool(Die(2), 4), 2)
        self.assertEqual(test.get_dict(), {2: 5, 3: 6, 4: 5})

        test = LowerMidOfDicePool(DicePool(Die(2), 4), 1)
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
        test = LowerMidOfDicePool(DicePool(ModDie(3, -1), 3), 2)
        self.assertEqual(test.get_dict(), {0: 7, 1: 9, 2: 7, 3: 3, 4: 1})

        test = LowerMidOfDicePool(DicePool(ModDie(3, -1), 3), 1)
        self.assertEqual(test.get_dict(), {0: 7, 1: 13, 2: 7})

    def test_LowerMidOfDicePool_get_dict_WeightedDie(self):
        """
        {(1, 1, 1): 8,
         (1, 1, 3): 36,
         (1, 3, 3): 54,
         (3, 3, 3): 27}
        """
        test = LowerMidOfDicePool(DicePool(WeightedDie({1: 2, 3: 3}), 3), 2)
        self.assertEqual(test.get_dict(), {2: 8 + 36, 4: 54, 6: 27})

        test = LowerMidOfDicePool(DicePool(WeightedDie({1: 2, 3: 3}), 3), 1)
        self.assertEqual(test.get_dict(), {1: 44, 3: 54 + 27})

    def test_LowerMidOfDicePool_str(self):
        self.assertEqual(str(LowerMidOfDicePool(DicePool(Die(2), 2), 1)), "LowerMid 1 of 2D2")

    def test_LowerMidOfDicePool_repr(self):
        expected = "LowerMidOfDicePool(DicePool(Die(2), 2), 1)"
        self.assertEqual(repr(LowerMidOfDicePool(DicePool(Die(2), 2), 1)), expected)

    def test_LowerMidOfDicePool_multiply_str(self):
        self.assertEqual(
            LowerMidOfDicePool(DicePool(Die(2), 2), 1).multiply_str(3), "3(LowerMid 1 of 2D2)"
        )

    def test_LowerMidOfDicePool_weight_info(self):
        self.assertEqual(
            LowerMidOfDicePool(DicePool(Die(2), 2), 1).weight_info(),
            "LowerMid 1 of 2D2\ninput_die info:\n    No weights",
        )
