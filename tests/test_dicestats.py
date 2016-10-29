# pylint: disable=missing-docstring, invalid-name, too-many-public-methods
"""unittests for dicestats.py"""
from __future__ import absolute_import

import unittest
import dicetables as dt


class TestDiceStats(unittest.TestCase):

    # rich comparison testing
    def test_Die_equal(self):
        self.assertEqual(dt.Die(3) == dt.Die(3), True)
        self.assertEqual(dt.Die(1) == dt.Die(5), False)

    def test_Die_not_equal(self):
        self.assertEqual(dt.Die(3) != dt.Die(10), True)
        self.assertEqual(dt.Die(5) != dt.Die(5), False)

    def test_Die_lt(self):
        self.assertEqual(dt.Die(4) < dt.Die(5), True)
        self.assertEqual(dt.Die(4) < dt.Die(4), False)
        self.assertEqual(dt.Die(4) < dt.Die(3), False)

    def test_Die_le(self):
        self.assertEqual(dt.Die(4) <= dt.Die(5), True)
        self.assertEqual(dt.Die(4) <= dt.Die(4), True)
        self.assertEqual(dt.Die(4) <= dt.Die(3), False)

    def test_Die_gt(self):
        self.assertEqual(dt.Die(7) > dt.Die(7), False)
        self.assertEqual(dt.Die(7) > dt.Die(1), True)
        self.assertEqual(dt.Die(8) > dt.Die(7), True)

    def test_Die_ge(self):
        self.assertEqual(dt.Die(4) >= dt.Die(5), False)
        self.assertEqual(dt.Die(4) >= dt.Die(4), True)
        self.assertEqual(dt.Die(4) >= dt.Die(3), True)

    def test_Die_ModDie_eq(self):
        self.assertEqual(dt.ModDie(4, 1) == dt.Die(4), False)
        self.assertEqual(dt.Die(4) == dt.ModDie(4, -1), False)

    def test_Die_ModDie_lt(self):
        self.assertEqual(dt.Die(4) < dt.ModDie(4, 1), True)
        self.assertEqual(dt.Die(4) < dt.ModDie(4, -1), False)

    def test_ModDie_with_zero_mod_not_equal_Die_due_to_repr(self):
        self.assertEqual(dt.ModDie(10, 0) != dt.Die(10), True)

    def test_WeightedDie_eq(self):
        self.assertEqual(dt.WeightedDie({1: 1}) == dt.WeightedDie({1: 1}), True)
        self.assertEqual(dt.WeightedDie({1: 1}) == dt.WeightedDie({2: 2}), False)

    def test_WeightedDie_not_equal_Die_with_same_dictionary(self):
        self.assertEqual(dt.WeightedDie({1: 1, 2: 1}) == dt.Die(2), False)

    def test_WeightedDie_lt_by_size(self):
        self.assertEqual(dt.WeightedDie({2: 2}) < dt.WeightedDie({3: 2}), True)

    def test_WeightedDie_lt_by_weight(self):
        self.assertEqual(dt.WeightedDie({2: 2}) < dt.WeightedDie({2: 3}), True)

    def test_WeightedDie_lt_by_tuple_list(self):
        self.assertEqual(dt.WeightedDie({1: 1, 2: 2}) < dt.WeightedDie({1: 2, 2: 1}), True)

    def test_Die_lt_by_repr(self):
        self.assertEqual(dt.WeightedDie({1: 1}) > dt.ModWeightedDie({1: 1}, 0), True)

    def test_ModWeightedDie_with_zero_mod_not_equal_WeightedDie(self):
        self.assertEqual(dt.WeightedDie({1: 2}) == dt.ModWeightedDie({1: 2}, 0), False)

    def test_StrongDie_with_one_multiplier_not_equal_Die(self):
        self.assertNotEqual(dt.Die(1), dt.StrongDie(dt.Die(1), 1))

    def test_StrongDie_gt_same_size_lt_larger(self):
        self.assertGreater(dt.StrongDie(dt.Die(1), 2), dt.Die(1))
        self.assertLess(dt.StrongDie(dt.Die(1), 5), dt.Die(2))

    #  Die tests
    def test_Die_get_size(self):
        self.assertEqual(dt.Die(6).get_size(), 6)

    def test_Die_get_weight(self):
        self.assertEqual(dt.Die(10).get_weight(), 0)

    def test_Die_tuple_list(self):
        self.assertEqual(dt.Die(3).get_dict(), {1: 1, 2: 1, 3: 1})

    def test_Die_weight_info(self):
        self.assertEqual(dt.Die(10000).weight_info(), 'D10000\n    No weights')

    def test_Die_str(self):
        self.assertEqual(str(dt.Die(1234)), 'D1234')

    def test_Die_repr(self):
        self.assertEqual(repr(dt.Die(123)), 'Die(123)')

    def test_Die_multiply_str(self):
        self.assertEqual(dt.Die(5).multiply_str(101), '101D5')

    #  ModDie tests
    def test_ModDie_get_modifier(self):
        self.assertEqual(dt.ModDie(7, 33).get_modifier(), 33)

    def test_ModDie_tuple_list(self):
        self.assertEqual(dt.ModDie(2, 5).get_dict(), {6: 1, 7: 1})

    def test_ModDie_string(self):
        self.assertEqual(str(dt.ModDie(10, 0)), 'D10+0')

    def test_ModDie_repr(self):
        self.assertEqual(repr(dt.ModDie(5, -1)), 'ModDie(5, -1)')

    def test_ModDie_multiply_str_pos_mod(self):
        self.assertEqual(dt.ModDie(5, 3).multiply_str(2), '2D5+6')

    def test_ModDie_multiply_str_neg_mod(self):
        self.assertEqual(dt.ModDie(5, -3).multiply_str(2), '2D5-6')

    #  WeightedDie tests
    def test_WeightedDie_get_size(self):
        self.assertEqual(dt.WeightedDie({5: 2, 2: 5}).get_size(), 5)

    def test_WeightedDie_get_weight(self):
        self.assertEqual(dt.WeightedDie({1: 2, 3: 5}).get_weight(), 7)

    def test_WeightedDie_tuple_list(self):
        self.assertEqual(dt.WeightedDie({1: 2, 3: 4}).get_dict(), {1: 2, 3: 4})

    def test_WeightedDie_tuple_list_doesnt_return_zero_frequencies(self):
        self.assertEqual(dt.WeightedDie({1: 2, 3: 0}).get_dict(), {1: 2})

    def test_WeightedDie_weight_info(self):
        dic = dict((x, x + 1) for x in range(1, 6, 2))
        weights_str = ('D5  W:12\n' +
                       '    a roll of 1 has a weight of 2\n' +
                       '    a roll of 2 has a weight of 0\n' +
                       '    a roll of 3 has a weight of 4\n' +
                       '    a roll of 4 has a weight of 0\n' +
                       '    a roll of 5 has a weight of 6')
        self.assertEqual(dt.WeightedDie(dic).weight_info(), weights_str)

    def test_WeightedDie_weight_info_formatting_large_num(self):
        dic = dict((x, x + 1) for x in range(1, 12, 2))
        weights_str = ('D11  W:42\n' +
                       '    a roll of  1 has a weight of 2\n' +
                       '    a roll of  2 has a weight of 0\n' +
                       '    a roll of  3 has a weight of 4\n' +
                       '    a roll of  4 has a weight of 0\n' +
                       '    a roll of  5 has a weight of 6\n' +
                       '    a roll of  6 has a weight of 0\n' +
                       '    a roll of  7 has a weight of 8\n' +
                       '    a roll of  8 has a weight of 0\n' +
                       '    a roll of  9 has a weight of 10\n' +
                       '    a roll of 10 has a weight of 0\n' +
                       '    a roll of 11 has a weight of 12')
        self.assertEqual(dt.WeightedDie(dic).weight_info(), weights_str)

    def test_WeightedDie_str(self):
        self.assertEqual(str(dt.WeightedDie({1: 1, 5: 3})), 'D5  W:4')

    def test_WeightedDie_repr(self):
        self.assertEqual(repr(dt.WeightedDie({1: 1, 2: 3})),
                         'WeightedDie({1: 1, 2: 3})')

    def test_WeightedDie_repr_edge_case(self):
        die1 = dt.WeightedDie({1: 1, 3: 0})
        die2 = dt.WeightedDie({1: 1, 2: 0, 3: 0})
        the_repr = 'WeightedDie({1: 1, 2: 0, 3: 0})'
        self.assertEqual(repr(die1), the_repr)
        self.assertEqual(repr(die2), the_repr)
        self.assertEqual(die1, die2)

    def test_WeightedDie_multiply_str(self):
        self.assertEqual(dt.WeightedDie({1: 1, 5: 3}).multiply_str(2), '2D5  W:4')

    #  ModWeightedDie tests
    def test_ModWeightedDie_get_mod(self):
        self.assertEqual(dt.ModWeightedDie({1: 2}, 3).get_modifier(), 3)

    def test_ModWeightedDie_tuple_list(self):
        self.assertEqual(dt.ModWeightedDie({1: 2, 3: 4}, -2).get_dict(),
                         {1 - 2: 2, 3 - 2: 4})

    def test_ModWeightedDie_string_for_positive_mod(self):
        self.assertEqual(str(dt.ModWeightedDie({1: 2}, 3)), 'D1+3  W:2')

    def test_ModWeightedDie_string_for_negative_mod(self):
        self.assertEqual(str(dt.ModWeightedDie({1: 2}, -3)), 'D1-3  W:2')

    def test_ModWeightedDie_repr(self):
        self.assertEqual(repr(dt.ModWeightedDie({1: 2}, -3)),
                         'ModWeightedDie({1: 2}, -3)')

    def test_ModWeightedDie_multiply_str_for_positive_mod(self):
        self.assertEqual(dt.ModWeightedDie({1: 2}, 3).multiply_str(5), '5D1+15  W:2')

    def test_ModWeightedDie_multiply_str_for_negative_mod(self):
        self.assertEqual(dt.ModWeightedDie({1: 2}, -3).multiply_str(5), '5D1-15  W:2')

    #  StrongDie tests
    # TODO tests *-1, *0
    def test_StrongDie_get_size(self):
        orig = dt.ModWeightedDie({1: 2}, -3)
        self.assertEqual(dt.StrongDie(orig, 100).get_size(), orig.get_size())

    def test_StrongDie_get_weight(self):
        orig = dt.ModWeightedDie({1: 2}, -3)
        self.assertEqual(dt.StrongDie(orig, 100).get_weight(), orig.get_weight())

    def test_StrongDie_get_multiplier(self):
        self.assertEqual(dt.StrongDie(dt.Die(3), 5).get_multiplier(), 5)

    def test_StrongDie_get_original(self):
        self.assertEqual(dt.StrongDie(dt.Die(3), 5).get_input_die(), dt.Die(3))

    def test_StrongDie_tuple_list(self):
        orig = dt.ModWeightedDie({1: 2, 2: 1}, 1)
        self.assertEqual(dt.StrongDie(orig, 100).get_dict(),
                         {200: 2, 300: 1})

    def test_StrongDie_weight_info(self):
        dic = dict((x, x + 1) for x in range(1, 6, 2))
        weights_str = ('(D5  W:12)X(10)\n' +
                       '    a roll of 1 has a weight of 2\n' +
                       '    a roll of 2 has a weight of 0\n' +
                       '    a roll of 3 has a weight of 4\n' +
                       '    a roll of 4 has a weight of 0\n' +
                       '    a roll of 5 has a weight of 6')
        self.assertEqual(dt.StrongDie(dt.WeightedDie(dic), 10).weight_info(),
                         weights_str)

    def test_StrongDie_multiply_str(self):
        orig = dt.ModWeightedDie({1: 2}, -3)
        expected = '(5D1-15  W:2)X(100)'
        self.assertEqual(dt.StrongDie(orig, 100).multiply_str(5), expected)

    def test_StrongDie_str(self):
        self.assertEqual(str(dt.StrongDie(dt.Die(7), 5)), '(D7)X(5)')

    def test_StrongDie_repr(self):
        self.assertEqual(repr(dt.StrongDie(dt.Die(7), 5)), 'StrongDie(Die(7), 5)')

    def test_StrongDie_expected_lt_cases_positive_tuple_list(self):
        die = dt.Die(5)
        self.assertEqual(die < dt.StrongDie(die, 2), True)

    def test_StrongDie_expected_lt_cases_zero_tuple_list(self):
        die = dt.ModDie(5, -1)
        self.assertEqual(die < dt.StrongDie(die, 2), True)

    def test_StrongDie_expected_lt_cases_negative_tuple_list(self):
        die = dt.ModDie(5, -3)
        self.assertEqual(die < dt.StrongDie(die, 2), False)

    def test_StrongDie_edge_StrongDie_of_StrongDie_size(self):
        die = dt.StrongDie(dt.Die(5), 2)
        self.assertEqual(dt.StrongDie(die, 3).get_size(), 5)

    def test_StrongDie_edge_StrongDie_of_StrongDie_weight(self):
        die = dt.StrongDie(dt.WeightedDie({1: 5}), 2)
        self.assertEqual(dt.StrongDie(die, 3).get_weight(), 5)

    def test_StrongDie_edge_StrongDie_of_StrongDie_tuple_list(self):
        die = dt.StrongDie(dt.ModDie(3, 1), 2)
        expected_tuple = dict([(roll * 6, 1) for roll in [2, 3, 4]])
        self.assertEqual(dt.StrongDie(die, 3).get_dict(), expected_tuple)

    def test_StrongDie_edge_StrongDie_of_StrongDie_get_multiplier(self):
        die = dt.StrongDie(dt.ModDie(3, 1), 2)
        self.assertEqual(dt.StrongDie(die, 3).get_multiplier(), 3)

    def test_StrongDie_edge_StrongDie_of_StrongDie_get_original(self):
        die = dt.StrongDie(dt.ModDie(3, 1), 2)
        self.assertEqual(dt.StrongDie(die, 3).get_input_die(), die)

    def test_StrongDie_edge_StrongDie_of_StrongDie_str(self):
        die = dt.StrongDie(dt.ModDie(3, 1), 2)
        self.assertEqual(dt.StrongDie(die, 3).__str__(), '((D3+1)X(2))X(3)')

    def test_StrongDie_edge_StrongDie_of_StrongDie_repr(self):
        die = dt.StrongDie(dt.ModDie(3, 1), 2)
        self.assertEqual(dt.StrongDie(die, 3).__repr__(), 'StrongDie(StrongDie(ModDie(3, 1), 2), 3)')

    def test_StrongDie_edge_StrongDie_of_StrongDie_multiply_str(self):
        die = dt.StrongDie(dt.ModDie(3, 1), 2)
        self.assertEqual(dt.StrongDie(die, 3).multiply_str(5), '((5D3+5)X(2))X(3)')

    def test_StrongDie_edge_StrongDie_of_StrongDie_weight_info(self):
        die = dt.StrongDie(dt.ModWeightedDie({1: 4}, 1), 2)
        self.assertEqual(dt.StrongDie(die, 3).weight_info(), '((D1+1  W:4)X(2))X(3)\n    a roll of 1 has a weight of 4')

    #  ProtoDie __hash__

    def test_ProtoDie_hash_with_Die(self):
        one_a = dt.Die(1)
        one_b = dt.Die(1)
        self.assertEqual(hash(one_a), hash(one_b))
        self.assertNotEqual(hash(one_a), hash(dt.Die(2)))

    def test_ProtoDie_hash_with_Die_and_ModDie(self):
        one_a = dt.ModDie(1, 0)
        one_b = dt.ModDie(1, 0)
        not_same_a = dt.Die(1)
        not_same_b = dt.ModDie(2, 0)
        not_same_c = dt.ModDie(1, 1)
        self.assertEqual(hash(one_a), hash(one_b))
        self.assertNotEqual(hash(one_a), hash(not_same_a))
        self.assertNotEqual(hash(one_a), hash(not_same_b))
        self.assertNotEqual(hash(one_a), hash(not_same_c))

    #  DiceTable tests
    def test_DiceTable_inits_empty(self):
        table = dt.DiceTable()
        self.assertEqual(table.get_dict(), {0: 1})
        self.assertEqual(table.get_list(), [])

    def test_DiceTable_update_list_adds_same_Die_to_Die_already_in_table(self):
        table = dt.DiceTable()
        table.update_list(3, dt.Die(4))
        table.update_list(2, dt.Die(4))
        self.assertIn((dt.Die(4), 5), table.get_list())

    def test_DiceTable_update_list_doesnt_combine_similar_dice(self):
        table = dt.DiceTable()
        table.update_list(3, dt.Die(3))
        table.update_list(2, dt.WeightedDie({1: 1, 2: 1, 3: 1}))
        self.assertIn((dt.WeightedDie({1: 1, 2: 1, 3: 1}), 2), table.get_list())
        self.assertIn((dt.Die(3), 3), table.get_list())

    def test_DiceTable_updates_list_removes_Die_with_zero_amount(self):
        table = dt.DiceTable()
        table.update_list(2, dt.Die(4))
        self.assertIn((dt.Die(4), 2), table.get_list())
        table.update_list(-2, dt.Die(4))
        self.assertEqual([], table.get_list())

    def test_DiceTable_number_of_dice_reports_correctly(self):
        table = dt.DiceTable()
        table.update_list(5, dt.Die(4))
        self.assertEqual(table.number_of_dice(dt.Die(4)), 5)

    def test_DiceTable_number_of_dice_reports_zero_when_dice_not_there(self):
        table = dt.DiceTable()
        self.assertEqual(table.number_of_dice(dt.Die(4)), 0)

    def test_DiceTable_weights_info_returns_empty_str_for_empty_table(self):
        table = dt.DiceTable()
        self.assertEqual(table.weights_info(), '')

    def test_DiceTable_weights_info_returns_appropriate_string(self):
        table = dt.DiceTable()
        table.update_list(2, dt.Die(4))
        table.update_list(5, dt.ModWeightedDie({1: 10, 4: 0}, 2))
        w_info = ('2D4\n    No weights\n\n5D4+10  W:10\n' +
                  '    a roll of 1 has a weight of 10\n' +
                  '    a roll of 2 has a weight of 0\n' +
                  '    a roll of 3 has a weight of 0\n' +
                  '    a roll of 4 has a weight of 0')
        self.assertEqual(table.weights_info(), w_info)

    def test_DiceTable_str_is_empty_for_empty_table(self):
        table = dt.DiceTable()
        self.assertEqual(str(table), '')

    def test_DiceTable_str_returns_appropriate_value(self):
        table = dt.DiceTable()
        table.update_list(2, dt.ModDie(4, -2))
        table.update_list(3, dt.Die(10))
        table.update_list(5, dt.ModWeightedDie({4: 10}, 2))
        table_str = '2D4-4\n5D4+10  W:10\n3D10'
        self.assertEqual(str(table), table_str)

    def test_DiceTable_add_die_doesnt_add_zero_dice(self):
        table = dt.DiceTable()
        table.add_die(0, dt.Die(4))
        self.assertEqual(table.get_list(), [])
        self.assertEqual(table.get_dict(), {0: 1})

    def test_DiceTable_add_die_adds_correct_dice(self):
        table = dt.DiceTable()
        table.add_die(2, dt.Die(4))
        self.assertEqual(table.get_list(), [(dt.Die(4), 2)])
        freq_all = dict([(2, 1), (3, 2), (4, 3), (5, 4), (6, 3), (7, 2), (8, 1)])
        self.assertEqual(table.get_dict(), freq_all)

    def test_DiceTable_remove_die_removes_correct_dice(self):
        table = dt.DiceTable()
        table.add_die(5, dt.Die(4))
        table.remove_die(3, dt.Die(4))
        self.assertEqual(table.get_list(), [(dt.Die(4), 2)])
        freq_all = dict([(2, 1), (3, 2), (4, 3), (5, 4), (6, 3), (7, 2), (8, 1)])
        self.assertEqual(table.get_dict(), freq_all)

    def test_DiceTable_remove_die_can_remove_all_the_dice(self):
        table = dt.DiceTable()
        table.add_die(2, dt.Die(4))
        table.remove_die(2, dt.Die(4))
        self.assertEqual(table.get_list(), [])
        self.assertEqual(table.get_dict(), {0: 1})

    def test_DiceTable_remove_die_raises_error_if_Die_not_in_table(self):
        with self.assertRaises(ValueError) as cm:
            dt.DiceTable().remove_die(1, dt.Die(4))
        self.assertEqual(cm.exception.args[0],
                         'dice not in table, or removed too many dice')

    def test_DiceTable_remove_die_raises_error_if_too_many_dice_removed(self):
        table = dt.DiceTable()
        table.add_die(3, dt.Die(4))
        with self.assertRaises(ValueError) as cm:
            table.remove_die(4, dt.Die(4))
        self.assertEqual(cm.exception.args[0],
                         'dice not in table, or removed too many dice')


if __name__ == '__main__':
    unittest.main()
