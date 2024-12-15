# pylint: disable=missing-docstring, invalid-name, too-many-public-methods


import unittest

from dicetables.dieevents import (
    Die,
    ModDie,
    WeightedDie,
    ModWeightedDie,
    StrongDie,
    Modifier,
    Exploding,
    ExplodingOn,
    add_dicts,
    remove_keys_after_applying_modifier,
    remove_duplicates,
    calc_roll_and_weight_mods,
    combine_rollweights_with_same_roll_value,
)
from dicetables.eventsbases.eventerrors import InvalidEventsError


class TestDieEvents(unittest.TestCase):
    def test_lt_all_die_types_can_sort_with_each_other(self):
        dice = [
            StrongDie(Die(2), 1),
            ModWeightedDie({1: 1, 2: 1}, 0),
            WeightedDie({1: 1, 2: 1}),
            ModDie(2, 0),
            Die(2),
            Die(3),
            Modifier(2),
            Exploding(Die(2)),
            ExplodingOn(Die(2), (1,)),
        ]
        self.assertIsNone(dice.sort())

    def test_lt_all_die_types_sort_as_expected(self):
        dice = [
            StrongDie(Die(2), 1),
            StrongDie(WeightedDie({1: 2, 2: 0}), 1),
            ModWeightedDie({1: 1, 2: 1}, 0),
            WeightedDie({1: 2, 2: 0}),
            ModDie(2, 0),
            Die(2),
            Die(3),
            Modifier(2),
            Exploding(Die(2)),
            ExplodingOn(Die(2), (1, 2)),
        ]
        sorted_dice = [
            Modifier(2),
            Die(2),
            ModDie(2, 0),
            StrongDie(Die(2), 1),
            Exploding(Die(2)),
            ModWeightedDie({1: 1, 2: 1}, 0),
            StrongDie(WeightedDie({1: 2, 2: 0}), 1),
            WeightedDie({1: 2, 2: 0}),
            ExplodingOn(Die(2), (1, 2)),
            Die(3),
        ]
        self.assertEqual(sorted(dice), sorted_dice)

    def test_ProtoDie_hash_with_Die(self):
        one_a = Die(1)
        one_b = Die(1)
        self.assertEqual(hash(one_a), hash(one_b))
        self.assertNotEqual(hash(one_a), hash(Die(2)))

    def test_ProtoDie_hash_with_Die_and_ModDie(self):
        one_a = ModDie(1, 0)
        one_b = ModDie(1, 0)
        not_same_a = Die(1)
        not_same_b = ModDie(2, 0)
        not_same_c = ModDie(1, 1)
        self.assertEqual(hash(one_a), hash(one_b))
        self.assertNotEqual(hash(one_a), hash(not_same_a))
        self.assertNotEqual(hash(one_a), hash(not_same_b))
        self.assertNotEqual(hash(one_a), hash(not_same_c))

    def test_Modifier_init_raises_InvalidEventsError_only_for_non_int_values(self):
        Modifier(5)
        Modifier(0)
        Modifier(-100)

        self.assertRaises(InvalidEventsError, Modifier, "a")
        self.assertRaises(InvalidEventsError, Modifier, 1.0)

    def test_Modifier_get_size_is_zero(self):
        self.assertEqual(Modifier(5).get_size(), 0)
        self.assertEqual(Modifier(0).get_size(), 0)
        self.assertEqual(Modifier(-5).get_size(), 0)

    def test_Modifier_get_weight_is_zero(self):
        self.assertEqual(Modifier(5).get_weight(), 0)
        self.assertEqual(Modifier(0).get_weight(), 0)
        self.assertEqual(Modifier(-5).get_weight(), 0)

    def test_Modifier_get_dict(self):
        self.assertEqual(Modifier(5).get_dict(), {5: 1})
        self.assertEqual(Modifier(0).get_dict(), {0: 1})
        self.assertEqual(Modifier(-5).get_dict(), {-5: 1})

    def test_Modifier_str(self):
        self.assertEqual(str(Modifier(1)), "+1")
        self.assertEqual(str(Modifier(-1)), "-1")

    def test_Modifier_multiply_str(self):
        self.assertEqual(Modifier(-2).multiply_str(3), "-2\n-2\n-2")
        self.assertEqual(Modifier(2).multiply_str(3), "+2\n+2\n+2")
        self.assertEqual(Modifier(2).multiply_str(1), "+2")

    def test_Modifier_weight_info(self):
        self.assertEqual(Modifier(3).weight_info(), "+3")

    def test_Modifier_get_modifier(self):
        self.assertEqual(Modifier(3).get_modifier(), 3)

    def test_Modifier_repr(self):
        self.assertEqual(repr(Modifier(3)), "Modifier(3)")

    def test_Die_init_raises_InvalidEventsError_for_illegal_size(self):
        self.assertRaises(InvalidEventsError, Die, 0)
        self.assertRaises(InvalidEventsError, Die, -2)

    def test_Die_get_size(self):
        self.assertEqual(Die(6).get_size(), 6)

    def test_Die_get_weight(self):
        self.assertEqual(Die(10).get_weight(), 0)

    def test_Die_get_dict(self):
        self.assertEqual(Die(3).get_dict(), {1: 1, 2: 1, 3: 1})

    def test_Die_weight_info(self):
        self.assertEqual(Die(10000).weight_info(), "D10000\n    No weights")

    def test_Die_str(self):
        self.assertEqual(str(Die(1234)), "D1234")

    def test_Die_repr(self):
        self.assertEqual(repr(Die(123)), "Die(123)")

    def test_Die_multiply_str(self):
        self.assertEqual(Die(5).multiply_str(101), "101D5")

    def test_ModDie_get_modifier(self):
        self.assertEqual(ModDie(7, 33).get_modifier(), 33)

    def test_ModDie_get_dict(self):
        self.assertEqual(ModDie(2, 5).get_dict(), {6: 1, 7: 1})

    def test_ModDie_string(self):
        self.assertEqual(str(ModDie(10, 0)), "D10+0")

    def test_ModDie_repr(self):
        self.assertEqual(repr(ModDie(5, -1)), "ModDie(5, -1)")

    def test_ModDie_multiply_str_pos_mod(self):
        self.assertEqual(ModDie(5, 3).multiply_str(2), "2D5+6")

    def test_ModDie_multiply_str_neg_mod(self):
        self.assertEqual(ModDie(5, -3).multiply_str(2), "2D5-6")

    def test_WeightedDie_init_raises_ValueError_on_zero_key(self):
        self.assertRaises(ValueError, WeightedDie, {0: 1, 2: 1})

    def test_WeightedDie_init_raises_ValueError_on_negative_key(self):
        self.assertRaises(ValueError, WeightedDie, {-5: 1, 2: 1})

    def test_WeightedDie_init_raises_InvalidEvents_error_on_bad_dict(self):
        self.assertRaises(InvalidEventsError, WeightedDie, {1: -1})
        self.assertRaises(InvalidEventsError, WeightedDie, {1: 0})

    def test_WeightedDie_init_does_not_raise_error_if_zero_values_in_dict(self):
        self.assertIsNotNone(WeightedDie({1: 1, 2: 0, 3: 0}))

    def test_WeightedDie_get_size(self):
        self.assertEqual(WeightedDie({5: 2, 2: 5}).get_size(), 5)

    def test_WeightedDie_get_size_edge_case(self):
        self.assertEqual(WeightedDie({1: 1, 3: 0}).get_size(), 3)

    def test_WeightedDie_get_weight(self):
        self.assertEqual(WeightedDie({1: 2, 3: 5}).get_weight(), 2 + 5)

    def test_WeightedDie_get_dict(self):
        self.assertEqual(WeightedDie({1: 2, 3: 4}).get_dict(), {1: 2, 3: 4})

    def test_WeightedDie_get_dict_doesnt_return_zero_frequencies(self):
        self.assertEqual(WeightedDie({1: 2, 3: 0}).get_dict(), {1: 2})

    def test_WeightedDie_weight_info(self):
        dic = dict((x, x + 1) for x in range(1, 6, 2))
        weights_str = (
            "D5  W:12\n"
            + "    a roll of 1 has a weight of 2\n"
            + "    a roll of 2 has a weight of 0\n"
            + "    a roll of 3 has a weight of 4\n"
            + "    a roll of 4 has a weight of 0\n"
            + "    a roll of 5 has a weight of 6"
        )
        self.assertEqual(WeightedDie(dic).weight_info(), weights_str)

    def test_WeightedDie_weight_info_formatting_large_num(self):
        dic = dict((x, x + 1) for x in range(1, 12, 2))
        weights_str = (
            "D11  W:42\n"
            + "    a roll of  1 has a weight of 2\n"
            + "    a roll of  2 has a weight of 0\n"
            + "    a roll of  3 has a weight of 4\n"
            + "    a roll of  4 has a weight of 0\n"
            + "    a roll of  5 has a weight of 6\n"
            + "    a roll of  6 has a weight of 0\n"
            + "    a roll of  7 has a weight of 8\n"
            + "    a roll of  8 has a weight of 0\n"
            + "    a roll of  9 has a weight of 10\n"
            + "    a roll of 10 has a weight of 0\n"
            + "    a roll of 11 has a weight of 12"
        )
        self.assertEqual(WeightedDie(dic).weight_info(), weights_str)

    def test_WeightedDie_str(self):
        self.assertEqual(str(WeightedDie({1: 1, 5: 3})), "D5  W:4")

    def test_WeightedDie_repr(self):
        self.assertEqual(repr(WeightedDie({1: 1, 2: 3})), "WeightedDie({1: 1, 2: 3})")

    def test_WeightedDie_repr_edge_case(self):
        die1 = WeightedDie({1: 1, 3: 0})
        die2 = WeightedDie({1: 1, 2: 0, 3: 0})
        the_repr = "WeightedDie({1: 1, 2: 0, 3: 0})"
        self.assertEqual(repr(die1), the_repr)
        self.assertEqual(repr(die2), the_repr)
        self.assertEqual(die1, die2)

    def test_WeightedDie_multiply_str(self):
        self.assertEqual(WeightedDie({1: 1, 5: 3}).multiply_str(2), "2D5  W:4")

    def test_WeightedDie_get_raw_dict(self):
        self.assertEqual(WeightedDie({1: 2, 2: 4}).get_raw_dict(), {1: 2, 2: 4})

    def test_WeightedDie_get_raw_dict_includes_zeroes(self):
        self.assertEqual(
            WeightedDie({2: 1, 4: 1, 5: 0}).get_raw_dict(), {1: 0, 2: 1, 3: 0, 4: 1, 5: 0}
        )

    def test_ModWeightedDie_get_mod(self):
        self.assertEqual(ModWeightedDie({1: 2}, 3).get_modifier(), 3)

    def test_ModWeightedDie_get_dict(self):
        self.assertEqual(ModWeightedDie({1: 2, 3: 4}, -2).get_dict(), {1 - 2: 2, 3 - 2: 4})

    def test_ModWeightedDie_string_for_positive_mod(self):
        self.assertEqual(str(ModWeightedDie({1: 2}, 3)), "D1+3  W:2")

    def test_ModWeightedDie_string_for_negative_mod(self):
        self.assertEqual(str(ModWeightedDie({1: 2}, -3)), "D1-3  W:2")

    def test_ModWeightedDie_repr(self):
        self.assertEqual(repr(ModWeightedDie({1: 2}, -3)), "ModWeightedDie({1: 2}, -3)")

    def test_ModWeightedDie_multiply_str_for_positive_mod(self):
        self.assertEqual(ModWeightedDie({1: 2}, 3).multiply_str(5), "5D1+15  W:2")

    def test_ModWeightedDie_multiply_str_for_negative_mod(self):
        self.assertEqual(ModWeightedDie({1: 2}, -3).multiply_str(5), "5D1-15  W:2")

    def test_StrongDie_get_size(self):
        orig = ModWeightedDie({1: 2}, -3)
        self.assertEqual(StrongDie(orig, 100).get_size(), orig.get_size())

    def test_StrongDie_get_weight(self):
        orig = ModWeightedDie({1: 2}, -3)
        self.assertEqual(StrongDie(orig, 100).get_weight(), orig.get_weight())

    def test_StrongDie_get_multiplier(self):
        self.assertEqual(StrongDie(Die(3), 5).get_multiplier(), 5)

    def test_StrongDie_get_input_die(self):
        self.assertEqual(StrongDie(Die(3), 5).get_input_die(), Die(3))

    def test_StrongDie_get_dict(self):
        orig = ModWeightedDie({1: 2, 2: 1}, 1)
        self.assertEqual(StrongDie(orig, 100).get_dict(), {200: 2, 300: 1})

    def test_StrongDie_zero_multiplier(self):
        die = StrongDie(WeightedDie({1: 2, 3: 4}), 0)
        self.assertEqual(die.get_dict(), {0: 4})

    def test_StrongDie_negative_multiplier(self):
        die = StrongDie(WeightedDie({1: 2, 3: 4}), -2)
        self.assertEqual(die.get_dict(), {-2: 2, -6: 4})

    def test_StrongDie_weight_info(self):
        dic = dict((x, x + 1) for x in range(1, 6, 2))
        weights_str = (
            "(D5  W:12)X(10)\n"
            + "    a roll of 1 has a weight of 2\n"
            + "    a roll of 2 has a weight of 0\n"
            + "    a roll of 3 has a weight of 4\n"
            + "    a roll of 4 has a weight of 0\n"
            + "    a roll of 5 has a weight of 6"
        )
        self.assertEqual(StrongDie(WeightedDie(dic), 10).weight_info(), weights_str)

    def test_StrongDie_multiply_str(self):
        orig = ModWeightedDie({1: 2}, -3)
        expected = "(5D1-15  W:2)X(100)"
        self.assertEqual(StrongDie(orig, 100).multiply_str(5), expected)

    def test_StrongDie_str(self):
        self.assertEqual(str(StrongDie(Die(7), 5)), "(D7)X(5)")

    def test_StrongDie_repr(self):
        self.assertEqual(repr(StrongDie(Die(7), 5)), "StrongDie(Die(7), 5)")

    def test_StrongDie_edge_StrongDie_of_StrongDie_size(self):
        die = StrongDie(Die(5), 2)
        self.assertEqual(StrongDie(die, 3).get_size(), 5)

    def test_StrongDie_edge_StrongDie_of_StrongDie_weight(self):
        die = StrongDie(WeightedDie({1: 5}), 2)
        self.assertEqual(StrongDie(die, 3).get_weight(), 5)

    def test_StrongDie_edge_case_StrongDie_of_StrongDie_get_dict(self):
        die = StrongDie(ModDie(3, 1), 2)
        expected_tuple = dict((roll * 6, 1) for roll in [2, 3, 4])
        self.assertEqual(StrongDie(die, 3).get_dict(), expected_tuple)

    def test_StrongDie_edge_case_StrongDie_of_StrongDie_get_multiplier(self):
        die = StrongDie(ModDie(3, 1), 2)
        self.assertEqual(StrongDie(die, 3).get_multiplier(), 3)

    def test_StrongDie_edge_case_StrongDie_of_StrongDie_get_original(self):
        die = StrongDie(ModDie(3, 1), 2)
        self.assertEqual(StrongDie(die, 3).get_input_die(), die)

    def test_StrongDie_edge_case_StrongDie_of_StrongDie_str(self):
        die = StrongDie(ModDie(3, 1), 2)
        self.assertEqual(StrongDie(die, 3).__str__(), "((D3+1)X(2))X(3)")

    def test_StrongDie_edge_case_StrongDie_of_StrongDie_repr(self):
        die = StrongDie(ModDie(3, 1), 2)
        self.assertEqual(StrongDie(die, 3).__repr__(), "StrongDie(StrongDie(ModDie(3, 1), 2), 3)")

    def test_StrongDie_edge_case_StrongDie_of_StrongDie_multiply_str(self):
        die = StrongDie(ModDie(3, 1), 2)
        self.assertEqual(StrongDie(die, 3).multiply_str(5), "((5D3+5)X(2))X(3)")

    def test_StrongDie_edge_case_StrongDie_of_StrongDie_weight_info(self):
        die = StrongDie(ModWeightedDie({1: 4}, 1), 2)
        self.assertEqual(
            StrongDie(die, 3).weight_info(),
            "((D1+1  W:4)X(2))X(3)\n    a roll of 1 has a weight of 4",
        )

    def test_Exploding_negative_explosions_raises_ValueError(self):
        self.assertRaises(ValueError, Exploding, Die(6), -1)

    def test_Exploding_get_dict_on_Die(self):
        die = Exploding(Die(3))
        self.assertEqual(die.get_dict(), {1: 9, 2: 9, 4: 3, 5: 3, 7: 1, 8: 1, 9: 1})

    def test_Exploding_get_dict_on_Die_set_explosions(self):
        die = Exploding(Die(3), explosions=3)
        self.assertEqual(
            die.get_dict(), {1: 27, 2: 27, 4: 9, 5: 9, 7: 3, 8: 3, 10: 1, 11: 1, 12: 1}
        )

    def test_Exploding_get_dict_on_WeightedDie(self):
        die = Exploding(WeightedDie({1: 2, 2: 1, 3: 3}))
        self.assertEqual(
            die.get_dict(),
            {
                1: 1 * 36 * 2,
                2: 1 * 36 * 1,
                4: 3 * 6 * 2,
                5: 3 * 6 * 1,
                7: 9 * 1 * 2,
                8: 9 * 1 * 1,
                9: 9 * 1 * 3,
            },
        )

    def test_Exploding_get_dict_on_ModWeightedDieDie_set_explosions(self):
        die = Exploding(ModWeightedDie({1: 2, 2: 1, 3: 3}, -1), explosions=3)
        self.assertEqual(
            die.get_dict(),
            {
                0: 1 * 216 * 2,
                1: 1 * 216 * 1,
                2: 3 * 36 * 2,
                3: 3 * 36 * 1,
                4: 9 * 6 * 2,
                5: 9 * 6 * 1,
                6: 27 * 1 * 2,
                7: 27 * 1 * 1,
                8: 27 * 1 * 3,
            },
        )

    def test_Exploding_works_according_to_get_dict_and_not_get_size(self):
        silly_die = WeightedDie({1: 1, 2: 1, 3: 0})
        self.assertEqual(silly_die.get_size(), 3)
        self.assertEqual(silly_die.get_dict(), {1: 1, 2: 1})
        self.assertEqual(Exploding(silly_die).get_dict(), {1: 4, 3: 2, 5: 1, 6: 1})

    def test_Exploding_get_dict_edge_case_explosions_are_zero(self):
        self.assertEqual(Exploding(Die(2), 0).get_dict(), {1: 1, 2: 1})

    def test_Exploding_get_dict_edge_case_Modifier(self):
        self.assertEqual(Exploding(Modifier(-3)).get_dict(), {-9: 1})

    def test_Exploding_get_dict_edge_case_ModDie_repeats_values(self):
        die = Exploding(ModDie(3, -2))
        first_set = {-1: 9, 0: 9}
        second_set = {0: 3, 1: 3}
        third_set = {1: 1, 2: 1, 3: 1}
        answer = {
            roll: first_set.get(roll, 0) + second_set.get(roll, 0) + third_set.get(roll, 0)
            for roll in range(-1, 4)
        }
        self.assertEqual(answer, die.get_dict())

    def test_Exploding_get_dict_edge_case_StrongDie(self):
        self.assertEqual(
            Exploding(StrongDie(Die(3), 4)).get_dict(),
            {4: 9, 8: 9, 16: 3, 20: 3, 28: 1, 32: 1, 36: 1},
        )

        mod = ModDie(3, -2)
        self.assertEqual(Exploding(mod).get_dict(), {-1: 9, 0: 12, 1: 4, 2: 1, 3: 1})
        self.assertEqual(Exploding(StrongDie(mod, 4)).get_dict(), {-4: 9, 0: 12, 4: 4, 8: 1, 12: 1})

    def test_Exploding_get_size(self):
        dice = [
            Die(3),
            ModDie(3, 4),
            WeightedDie({1: 2, 3: 4}),
            ModWeightedDie({1: 2, 3: 4}, -1),
            StrongDie(Die(4), 3),
        ]
        for die in dice:
            self.assertEqual(Exploding(die, 3).get_size(), die.get_size())

    def test_Exploding_get_weight(self):
        dice = [
            Die(3),
            ModDie(3, 4),
            WeightedDie({1: 2, 3: 4}),
            ModWeightedDie({1: 2, 3: 4}, -1),
            StrongDie(Die(4), 3),
        ]
        for die in dice:
            self.assertEqual(Exploding(die, 3).get_weight(), die.get_weight() + 1)

    def test_Exploding_get_input_die(self):
        dice = [
            Die(3),
            ModDie(3, 4),
            WeightedDie({1: 2, 3: 4}),
            ModWeightedDie({1: 2, 3: 4}, -1),
            StrongDie(Die(4), 3),
        ]
        for die in dice:
            self.assertEqual(Exploding(die, 3).get_input_die(), die)

    def test_Exploding_get_explosions(self):
        two = Exploding(Modifier(1))
        five = Exploding(Modifier(1), 5)
        self.assertEqual(two.get_explosions(), 2)
        self.assertEqual(five.get_explosions(), 5)

    def test_Exploding__str__(self):
        self.assertEqual(Exploding(Die(6), 3).__str__(), "D6: Explosions=3")
        self.assertEqual(
            Exploding(ModWeightedDie({1: 1, 2: 2}, -2), 1).__str__(), "D2-2  W:3: Explosions=1"
        )

    def test_Exploding_multiply_str(self):
        self.assertEqual(Exploding(Die(6), 3).multiply_str(3), "3(D6: Explosions=3)")
        self.assertEqual(
            Exploding(ModWeightedDie({1: 1, 2: 2}, -2), 1).multiply_str(5),
            "5(D2-2  W:3: Explosions=1)",
        )

    def test_Exploding_weight_info(self):
        self.assertEqual(
            Exploding(Die(6)).weight_info(),
            "D6: Explosions=2\n    No weights\nExploding adds weight: 1",
        )
        self.assertEqual(
            Exploding(ModWeightedDie({1: 1, 2: 2}, -2), 1).weight_info(),
            (
                "D2-2  W:3: Explosions=1\n"
                + "    a roll of 1 has a weight of 1\n"
                + "    a roll of 2 has a weight of 2\n"
                + "Exploding adds weight: 1"
            ),
        )

    def test_Exploding_repr(self):
        self.assertEqual(repr(Exploding(Die(6))), "Exploding(Die(6), 2)")
        self.assertEqual(
            repr(Exploding(StrongDie(Die(6), 3), explosions=10)),
            "Exploding(StrongDie(Die(6), 3), 10)",
        )

    def test_module_level_helper_function_remove_duplicates_empty(self):
        self.assertEqual(remove_duplicates(()), ())

    def test_module_level_helper_function_remove_duplicates_no_duplicates(self):
        self.assertEqual(remove_duplicates((1, 4, 3, 2)), (1, 4, 3, 2))

    def test_module_level_helper_function_remove_duplicates_has_duplicates_orders_by_first_appearance(
        self,
    ):
        self.assertEqual(remove_duplicates((1, 4, 1, 3, 3, 4, 2, 3, 1, 1)), (1, 4, 3, 2))

    def test_module_level_helper_function_add_dicts_empty_empty(self):
        a = {}
        b = {}
        answer = add_dicts(a, b)
        self.assertEqual(answer, {})
        self.assertIsNot(answer, a)
        self.assertIsNot(answer, b)

    def test_module_level_helper_function_add_dicts_first_empty(self):
        a = {1: 1}
        b = {}
        answer = add_dicts(a, b)
        self.assertEqual(answer, {1: 1})
        self.assertIsNot(answer, a)
        self.assertIsNot(answer, b)

    def test_module_level_helper_function_add_dicts_second_empty(self):
        a = {1: 1}
        b = {}
        answer = add_dicts(b, a)
        self.assertEqual(answer, {1: 1})
        self.assertIsNot(answer, a)
        self.assertIsNot(answer, b)

    def test_module_level_helper_function_add_dicts_no_overlap(self):
        a = {1: 1}
        b = {2: 3}
        answer = add_dicts(b, a)
        self.assertEqual(answer, {1: 1, 2: 3})
        self.assertIsNot(answer, a)
        self.assertIsNot(answer, b)

    def test_module_level_helper_function_add_dicts_overlap(self):
        a = {1: 1, 2: 3}
        b = {2: 3, 4: 5}
        answer = add_dicts(b, a)
        self.assertEqual(answer, {1: 1, 2: 6, 4: 5})
        self.assertIsNot(answer, a)
        self.assertIsNot(answer, b)

    def test_module_level_helper_function_calc_roll_and_weight_mods(self):
        rolls_and_weights = [(-1, 2), (0, 3), (4, 5)]
        self.assertEqual(calc_roll_and_weight_mods(rolls_and_weights), (-1 + 0 + 4, 2 * 3 * 5))

    def test_module_level_helper_function_combine_rollweights_with_same_roll_value_rolls_all_different(
        self,
    ):
        roll_mods_and_weight_mods = [(1, 2), (3, 4), (5, 6)]
        expected = {1: 2, 3: 4, 5: 6}
        self.assertEqual(
            combine_rollweights_with_same_roll_value(roll_mods_and_weight_mods), expected
        )

    def test_module_level_helper_function_combine_rollweights_with_same_roll_value_some_rolls_the_same(
        self,
    ):
        roll_mods_and_weight_mods = [(1, 2), (3, 4), (5, 6), (1, 3)]
        expected = {1: 5, 3: 4, 5: 6}
        self.assertEqual(
            combine_rollweights_with_same_roll_value(roll_mods_and_weight_mods), expected
        )

    def test_module_level_helper_function_remove_keys_after_applying_modifier(self):
        modifier = 4
        to_remove = (1, 2)
        base_dict = dict.fromkeys(range(10), 1)
        answer = remove_keys_after_applying_modifier(base_dict, to_remove, modifier)
        self.assertEqual(answer, {0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 7: 1, 8: 1, 9: 1})
        self.assertIsNot(base_dict, answer)

    def test_ExplodingOn_get_dict_regular_die(self):
        die = ExplodingOn(Die(4), (3, 4), explosions=2)
        level_zero = {1: 16, 2: 16}
        level_one = [{4: 4, 5: 4}, {5: 4, 6: 4}]  # 3 + roll / 4 + roll
        level_two = [
            {7: 1, 8: 1, 9: 1, 10: 1},  # 3 + 3 + roll
            {8: 1, 9: 1, 10: 1, 11: 1},  # 3 + 4 + roll
            {8: 1, 9: 1, 10: 1, 11: 1},  # 4 + 3 + roll
            {9: 1, 10: 1, 11: 1, 12: 1},
        ]  # 4 + 4 + roll
        answer = level_zero.copy()
        for sub_dict in level_one + level_two:
            answer = add_dicts(answer, sub_dict)
        self.assertEqual(
            answer, {1: 16, 2: 16, 4: 4, 5: 8, 6: 4, 7: 1, 8: 3, 9: 4, 10: 4, 11: 3, 12: 1}
        )
        self.assertEqual(answer, die.get_dict())

    def test_ExplodingOn_explodes_on_roll_not_in_die(self):
        self.assertRaises(ValueError, ExplodingOn, Die(3), (1, 2, 3, 4))
        self.assertRaises(ValueError, ExplodingOn, Die(3), (5,))

    def test_ExplodingOn_negative_explosions(self):
        self.assertRaises(ValueError, ExplodingOn, Die(3), (1,), -1)

    def test_ExplodingOn_get_dict_one_explodes_on_value(self):
        die = ExplodingOn(Die(3), (2,))
        self.assertEqual(die.get_dict(), {1: 9, 3: 12, 5: 4, 6: 1, 7: 1})

    def test_ExplodingOn_get_dict_regular_die_different_numbers(self):
        die = ExplodingOn(WeightedDie({1: 1, 2: 1, 3: 1, 4: 1}), (1, 4), explosions=2)

        level_zero = {2: 16, 3: 16}
        level_one = [{3: 4, 4: 4}, {6: 4, 7: 4}]  # 1 + roll / 4 + roll
        level_two = [
            {3: 1, 4: 1, 5: 1, 6: 1},  # 1 + 1 + roll
            {6: 1, 7: 1, 8: 1, 9: 1},  # 1 + 4 + roll
            {6: 1, 7: 1, 8: 1, 9: 1},  # 4 + 1 + roll
            {9: 1, 10: 1, 11: 1, 12: 1},
        ]  # 4 + 4 + roll
        answer = level_zero.copy()
        for sub_dict in level_one + level_two:
            answer = add_dicts(answer, sub_dict)

        self.assertEqual(
            answer, {2: 16, 3: 21, 4: 5, 5: 1, 6: 7, 7: 6, 8: 2, 9: 3, 10: 1, 11: 1, 12: 1}
        )
        self.assertEqual(answer, die.get_dict())

    def test_ExplodingOn_get_dict_WeightedDie_one(self):
        die = ExplodingOn(WeightedDie({1: 1, 2: 1, 3: 1, 4: 2}), (3, 4), explosions=2)

        level_zero = {1: 25, 2: 25}
        level_one = [{4: 5, 5: 5}, {5: 10, 6: 10}]  # 3 + roll / 4 + roll
        level_two = [
            {7: 1, 8: 1, 9: 1, 10: 2},  # 3 + 3 + roll
            {8: 2, 9: 2, 10: 2, 11: 4},  # 3 + 4 + roll
            {8: 2, 9: 2, 10: 2, 11: 4},  # 4 + 3 + roll
            {9: 4, 10: 4, 11: 4, 12: 8},
        ]  # 4 + 4 + roll
        answer = level_zero.copy()
        for sub_dict in level_one + level_two:
            answer = add_dicts(answer, sub_dict)
        self.assertEqual(
            answer, {1: 25, 2: 25, 4: 5, 5: 15, 6: 10, 7: 1, 8: 5, 9: 9, 10: 10, 11: 12, 12: 8}
        )
        self.assertEqual(answer, die.get_dict())

    def test_ExplodingOn_get_dict_WeightedDie_two(self):
        die = ExplodingOn(WeightedDie({1: 1, 2: 1, 3: 2, 4: 3}), (3, 4), explosions=2)

        level_zero = {1: 49, 2: 49}
        level_one = [{4: 14, 5: 14}, {5: 21, 6: 21}]  # 3 + roll / 4 + roll
        level_two = [
            {7: 4, 8: 4, 9: 8, 10: 12},  # 3 + 3 + roll
            {8: 6, 9: 6, 10: 12, 11: 18},  # 3 + 4 + roll
            {8: 6, 9: 6, 10: 12, 11: 18},  # 4 + 3 + roll
            {9: 9, 10: 9, 11: 18, 12: 27},
        ]  # 4 + 4 + roll
        answer = level_zero.copy()
        for sub_dict in level_one + level_two:
            answer = add_dicts(answer, sub_dict)

        self.assertEqual(
            answer, {1: 49, 2: 49, 4: 14, 5: 35, 6: 21, 7: 4, 8: 16, 9: 29, 10: 45, 11: 54, 12: 27}
        )
        self.assertEqual(answer, die.get_dict())

    def test_ExplodingOn_get_dict_WeightedDie_set_explosions(self):
        die = ExplodingOn(WeightedDie({1: 1, 2: 2, 3: 3}), (2, 3), explosions=3)

        level_zero = {1: 216}
        level_one = [{3: 36 * 2}, {4: 36 * 3}]  # 2+roll / 3+roll
        level_two = [
            {5: 4 * 6},  # 2 + 2 + roll
            {6: 6 * 6},  # 2 + 3 + roll
            {6: 6 * 6},  # 3 + 2 + roll
            {7: 9 * 6},
        ]  # 3 + 3 + roll
        level_three = [
            {7: 8, 8: 8 * 2, 9: 8 * 3},  # 2+2+2+roll
            {8: 12, 9: 12 * 2, 10: 12 * 3},  # 2+2+3+roll
            {8: 12, 9: 12 * 2, 10: 12 * 3},  # 2+3+2+roll
            {9: 18, 10: 18 * 2, 11: 18 * 3},  # 2+3+3+roll
            {8: 12, 9: 12 * 2, 10: 12 * 3},  # 3+2+2+roll
            {9: 18, 10: 18 * 2, 11: 18 * 3},  # 3+2+3+roll
            {9: 18, 10: 18 * 2, 11: 18 * 3},  # 3+3+2+roll
            {10: 27, 11: 27 * 2, 12: 27 * 3},
        ]  # 3+3+3+roll
        answer = level_zero.copy()
        for sub_dict in level_one + level_two + level_three:
            answer = add_dicts(answer, sub_dict)

        self.assertEqual(
            answer,
            {
                1: 216,
                3: 72,
                4: 108,
                5: 24,
                6: 72,
                7: 62,
                8: 16 + 12 * 3,
                9: 24 * 4 + 18 * 3,
                10: 36 * 6 + 27,
                11: 162 + 54,
                12: 81,
            },
        )
        self.assertEqual(answer, die.get_dict())

    def test_ExplodingOn_get_dict_edge_case_empty_explodes_on(self):
        die = ExplodingOn(Die(3), ())
        self.assertEqual(die.get_dict(), {1: 9, 2: 9, 3: 9})
        die = ExplodingOn(Die(3), (), explosions=2)
        self.assertEqual(die.get_dict(), {1: 9, 2: 9, 3: 9})

    def test_ExplodingOn_get_dict_edge_case_no_explosions(self):
        die = ExplodingOn(Die(3), (1, 2), 0)
        self.assertEqual(die.get_dict(), {1: 1, 2: 1, 3: 1})

    def test_ExplodingOn_get_dict_edge_case_explodes_on_all_values(self):
        die = ExplodingOn(Die(3), (1, 2, 3), 1)
        self.assertEqual(die.get_dict(), {2: 1, 3: 2, 4: 3, 5: 2, 6: 1})

    def test_ExplodingOn_get_dict_edge_case_explodes_on_duplicate_values(self):
        die = ExplodingOn(Die(3), (1, 2, 1, 2, 3, 1), 1)
        self.assertEqual(die.get_dict(), {2: 1, 3: 2, 4: 3, 5: 2, 6: 1})

    def test_ExplodingOn_get_size(self):
        dice = [
            Die(3),
            ModDie(3, 1),
            WeightedDie({1: 2, 2: 4}),
            ModWeightedDie({1: 2, 3: 4}, -1),
            StrongDie(Die(4), 2),
        ]
        for die in dice:
            self.assertEqual(ExplodingOn(die, (2,), 3).get_size(), die.get_size())

    def test_ExplodingOn_get_weight_changes_according_to_len_explodes_on(self):
        weight_zero = Die(6)
        weight_six = WeightedDie(dict.fromkeys([1, 2, 3, 4, 5, 6], 1))
        self.assertEqual(weight_zero.get_weight(), 0)
        self.assertEqual(weight_six.get_weight(), 6)

        self.assertEqual(ExplodingOn(weight_zero, (1,)).get_weight(), 1)
        self.assertEqual(ExplodingOn(weight_zero, (1, 2)).get_weight(), 2)
        self.assertEqual(ExplodingOn(weight_zero, (1, 3, 5)).get_weight(), 3)

        self.assertEqual(ExplodingOn(weight_six, (1,)).get_weight(), 7)
        self.assertEqual(ExplodingOn(weight_six, (1, 2)).get_weight(), 8)
        self.assertEqual(ExplodingOn(weight_six, (1, 3, 5)).get_weight(), 9)

    def test_ExplodingOn_get_input_die(self):
        dice = [
            Die(3),
            ModDie(3, 1),
            WeightedDie({1: 2, 2: 4}),
            ModWeightedDie({1: 2, 3: 4}, -1),
            StrongDie(Die(4), 2),
        ]
        for die in dice:
            self.assertEqual(ExplodingOn(die, (2,), 3).get_input_die(), die)

    def test_ExplodingOn_get_explosions(self):
        two = ExplodingOn(Modifier(1), (1,))
        five = ExplodingOn(Modifier(1), (1,), 5)
        self.assertEqual(two.get_explosions(), 2)
        self.assertEqual(five.get_explosions(), 5)

    def test_ExplodingOn_get_explodes_on(self):
        self.assertEqual(ExplodingOn(Die(3), ()).get_explodes_on(), ())
        self.assertEqual(ExplodingOn(Die(3), (1,)).get_explodes_on(), (1,))
        self.assertEqual(ExplodingOn(Die(3), (1, 2)).get_explodes_on(), (1, 2))

    def test_ExplodingOn_get_explodes_on_duplicate_values(self):
        self.assertEqual(ExplodingOn(Die(3), (1, 1)).get_explodes_on(), (1,))
        self.assertEqual(ExplodingOn(Die(3), (1, 1, 2, 1, 2, 3, 2)).get_explodes_on(), (1, 2, 3))

    def test_ExplodingOn__str__(self):
        self.assertEqual(ExplodingOn(Die(6), (1, 2), 3).__str__(), "D6: Explosions=3 On: 1, 2")
        self.assertEqual(
            ExplodingOn(ModWeightedDie({1: 1, 2: 2}, -2), (0,), 1).__str__(),
            "D2-2  W:3: Explosions=1 On: 0",
        )

    def test_ExplodingOn_multiply_str(self):
        self.assertEqual(
            ExplodingOn(Die(6), (1, 2), 3).multiply_str(3), "3(D6: Explosions=3 On: 1, 2)"
        )
        self.assertEqual(
            ExplodingOn(ModWeightedDie({1: 1, 2: 2}, -2), (0,), 1).multiply_str(5),
            "5(D2-2  W:3: Explosions=1 On: 0)",
        )

    def test_ExplodingOn_weight_info(self):
        self.assertEqual(
            ExplodingOn(Die(6), (1, 5)).weight_info(),
            "D6: Explosions=2 On: 1, 5\n    No weights\nExploding on 2 values adds weight: 2",
        )
        self.assertEqual(
            ExplodingOn(ModWeightedDie({1: 1, 2: 2}, -2), (0,), 1).weight_info(),
            (
                "D2-2  W:3: Explosions=1 On: 0\n"
                + "    a roll of 1 has a weight of 1\n"
                + "    a roll of 2 has a weight of 2\n"
                + "Exploding on 1 value adds weight: 1"
            ),
        )

    def test_ExplodingOn_repr(self):
        self.assertEqual(repr(ExplodingOn(Die(6), (1,))), "ExplodingOn(Die(6), (1,), 2)")
        self.assertEqual(
            repr(ExplodingOn(StrongDie(Die(6), 3), (3, 6), explosions=10)),
            "ExplodingOn(StrongDie(Die(6), 3), (3, 6), 10)",
        )

    def test_ExplodingOn_all_relevant_methods_ignore_duplicate_explodes_on_values(self):
        die = ExplodingOn(Die(2), (1, 1, 1), explosions=1)
        self.assertEqual(str(die), "D2: Explosions=1 On: 1")
        self.assertEqual(repr(die), "ExplodingOn(Die(2), (1,), 1)")
        self.assertEqual(die.multiply_str(2), "2(D2: Explosions=1 On: 1)")
        self.assertEqual(die.get_weight(), 1)
        self.assertEqual(
            die.weight_info(),
            "D2: Explosions=1 On: 1\n    No weights\nExploding on 1 value adds weight: 1",
        )
        self.assertEqual(die, ExplodingOn(Die(2), (1,), 1))


if __name__ == "__main__":
    unittest.main()
