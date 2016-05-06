# pylint: disable=missing-docstring, invalid-name, too-many-public-methods
'''unittests for dicestats.py'''
from __future__ import absolute_import


import unittest
import dicetables.dicestats as ds

class TestDiceStats(unittest.TestCase):
    def test_die_equal(self):
        self.assertEqual(ds.Die(3) == ds.Die(3), True)
        self.assertEqual(ds.Die(0) == ds.Die(5), False)
    def test_die_not_equal(self):
        self.assertEqual(ds.Die(3) != ds.Die(10), True)
        self.assertEqual(ds.Die(5) != ds.Die(5), False)
    def test_die_lt(self):
        self.assertEqual(ds.Die(4) < ds.Die(5), True)
        self.assertEqual(ds.Die(4) < ds.Die(4), False)
        self.assertEqual(ds.Die(4) < ds.Die(3), False)
    def test_die_le(self):
        self.assertEqual(ds.Die(4) <= ds.Die(5), True)
        self.assertEqual(ds.Die(4) <= ds.Die(4), True)
        self.assertEqual(ds.Die(4) <= ds.Die(3), False)
    def test_die_gt(self):
        self.assertEqual(ds.Die(7) > ds.Die(7), False)
        self.assertEqual(ds.Die(7) > ds.Die(0), True)
        self.assertEqual(ds.Die(8) > ds.Die(7), True)
    def test_die_ge(self):
        self.assertEqual(ds.Die(4) >= ds.Die(5), False)
        self.assertEqual(ds.Die(4) >= ds.Die(4), True)
        self.assertEqual(ds.Die(4) >= ds.Die(3), True)
    def test_die_moddie_eq(self):
        self.assertEqual(ds.ModDie(4, 1) == ds.Die(4), False)
        self.assertEqual(ds.Die(4) == ds.ModDie(4, -1), False)
    def test_die_moddie_lt(self):
        self.assertEqual(ds.Die(4) < ds.ModDie(4, 1), True)
        self.assertEqual(ds.Die(4) < ds.ModDie(4, -1), False)
    def test_moddie_with_zero_mod_not_equal_die_due_to_repr(self):
        self.assertEqual(ds.ModDie(10, 0) != ds.Die(10), True)

    def test_weighteddie_eq(self):
        self.assertEqual(ds.WeightedDie({1:1}) == ds.WeightedDie({1:1}), True)
        self.assertEqual(ds.WeightedDie({1:1}) == ds.WeightedDie({2:2}), False)
    def test_weighteddie_not_equal_die_with_same_dictionary(self):
        self.assertEqual(ds.WeightedDie({1:1, 2:1}) == ds.Die(2), False)
    def test_weighteddie_lt_by_size(self):
        self.assertEqual(ds.WeightedDie({2:2}) < ds.WeightedDie({3:2}), True)
    def test_weighteddie_lt_by_weight(self):
        self.assertEqual(ds.WeightedDie({2:2}) < ds.WeightedDie({2:3}), True)
    def test_weighteddie_lt_by_tuple_list(self):
        self.assertEqual(ds.WeightedDie({1:1, 2:2}) < ds.WeightedDie({1:2, 2:1}), True)
    def test_die_lt_by_repr(self):
        self.assertEqual(ds.WeightedDie({1:1}) > ds.ModWeightedDie({1:1}, 0), True)

    def test_modweighteddie_with_zero_mod_not_equal_weighteddie(self):
        self.assertEqual(ds.WeightedDie({1:2}) == ds.ModWeightedDie({1:2}, 0), False)


    def test_die_get_size(self):
        self.assertEqual(ds.Die(6).get_size(), 6)
    def test_die_get_weight(self):
        self.assertEqual(ds.Die(10).get_weight(), 0)
    def test_die_tuple_list(self):
        self.assertEqual(ds.Die(3).tuple_list(), [(1, 1), (2, 1), (3, 1)])
    def test_die_weight_info(self):
        self.assertEqual(ds.Die(10000).weight_info(), 'D10000\n    No weights')
    def test_die_str(self):
        self.assertEqual(str(ds.Die(1234)), 'D1234')
    def test_die_repr(self):
        self.assertEqual(repr(ds.Die(123)), 'Die(123)')
    def test_die_multiply_str(self):
        self.assertEqual(ds.Die(5).multiply_str(101), '101D5')

    def test_moddie_get_modifier(self):
        self.assertEqual(ds.ModDie(7, 33).get_modifier(), 33)
    def test_moddie_tuple_list(self):
        self.assertEqual(ds.ModDie(2, 5).tuple_list(), [(1+5, 1), (2+5, 1)])
    def test_moddie_string(self):
        self.assertEqual(str(ds.ModDie(10, 0)), 'D10+0')
    def test_moddie_repr(self):
        self.assertEqual(repr(ds.ModDie(5, -1)), 'ModDie(5, -1)')
    def test_moddie_multiply_str_pos_mod(self):
        self.assertEqual(ds.ModDie(5, 3).multiply_str(2), '2D5+6')
    def test_moddie_multiply_str_neg_mod(self):
        self.assertEqual(ds.ModDie(5, -3).multiply_str(2), '2D5-6')

    def test_weighteddie_get_size(self):
        self.assertEqual(ds.WeightedDie({5:2, 2:5}).get_size(), 5)
    def test_weighteddie_get_weight(self):
        self.assertEqual(ds.WeightedDie({1:2, 3:5}).get_weight(), 7)
    def test_weighteddie_tuple_list(self):
        self.assertEqual(ds.WeightedDie({1:2, 3:4}).tuple_list(), [(1, 2), (3, 4)])
    def test_weighteddie_tuple_list_doesnt_return_zero_frequencies(self):
        self.assertEqual(ds.WeightedDie({1:2, 3:0}).tuple_list(), [(1, 2)])
    def test_weighteddie_weight_info(self):
        dic = dict((x, x+1) for x in range(1, 6, 2))
        weights_str = ('D5  W:12\n'+
                       '    a roll of 1 has a weight of 2\n' +
                       '    a roll of 2 has a weight of 0\n' +
                       '    a roll of 3 has a weight of 4\n' +
                       '    a roll of 4 has a weight of 0\n' +
                       '    a roll of 5 has a weight of 6')
        self.assertEqual(ds.WeightedDie(dic).weight_info(), weights_str)
    def test_weighteddie_str(self):
        self.assertEqual(str(ds.WeightedDie({1:1, 5:3})), 'D5  W:4')
    def test_weighteddie_repr(self):
        self.assertEqual(repr(ds.WeightedDie({1:1, 2:3})),
                         'WeightedDie({1: 1, 2: 3})')
    def test_weighteddie_repr_edge_case(self):
        die1 = ds.WeightedDie({1:1, 3:0})
        die2 = ds.WeightedDie({1:1, 2:0, 3:0})
        the_repr = 'WeightedDie({1: 1, 2: 0, 3: 0})'
        self.assertEqual(repr(die1), the_repr)
        self.assertEqual(repr(die2), the_repr)
        self.assertEqual(die1, die2)
    def test_weighteddie_multiply_str(self):
        self.assertEqual(ds.WeightedDie({1:1, 5:3}).multiply_str(2), '2D5  W:4')

    def test_modweighteddie_get_mod(self):
        self.assertEqual(ds.ModWeightedDie({1:2}, 3).get_modifier(), 3)
    def test_modweighteddie_tuple_list(self):
        self.assertEqual(ds.ModWeightedDie({1:2, 3:4}, -2).tuple_list(),
                         [(1-2, 2), (3-2, 4)])
    def test_modweighteddie_string_for_positive_mod(self):
        self.assertEqual(str(ds.ModWeightedDie({1:2}, 3)), 'D1+3  W:2')
    def test_modweighteddie_string_for_negative_mod(self):
        self.assertEqual(str(ds.ModWeightedDie({1:2}, -3)), 'D1-3  W:2')
    def test_modweighteddie_repr(self):
        self.assertEqual(repr(ds.ModWeightedDie({1:2}, -3)),
                         'ModWeightedDie({1: 2}, -3)')
    def test_modweighteddie_multiply_str_for_positive_mod(self):
        self.assertEqual(ds.ModWeightedDie({1:2}, 3).multiply_str(5), '5D1+15  W:2')
    def test_modweighteddie_multiply_str_for_negative_mod(self):
        self.assertEqual(ds.ModWeightedDie({1:2}, -3).multiply_str(5), '5D1-15  W:2')

    def test_dicetable_inits_empty(self):
        table = ds.DiceTable()
        self.assertEqual(table.frequency_all(), [(0, 1)])
        self.assertEqual(table.get_list(), [])
    def test_dicetable_update_list_adds_same_die_to_die_already_in_table(self):
        table = ds.DiceTable()
        table.update_list(3, ds.Die(4))
        table.update_list(2, ds.Die(4))
        self.assertIn((ds.Die(4), 5), table.get_list())
    def test_dicetable_update_list_doesnt_combine_similar_dice(self):
        table = ds.DiceTable()
        table.update_list(3, ds.Die(3))
        table.update_list(2, ds.WeightedDie({1:1, 2:1, 3:1}))
        self.assertIn((ds.WeightedDie({1:1, 2:1, 3:1}), 2), table.get_list())
        self.assertIn((ds.Die(3), 3), table.get_list())
    def test_dicetable_updates_list_removes_die_with_zero_amount(self):
        table = ds.DiceTable()
        table.update_list(2, ds.Die(4))
        self.assertIn((ds.Die(4), 2), table.get_list())
        table.update_list(-2, ds.Die(4))
        self.assertEqual([], table.get_list())
    def test_dicetable_number_of_dice_reports_correctly(self):
        table = ds.DiceTable()
        table.update_list(5, ds.Die(4))
        self.assertEqual(table.number_of_dice(ds.Die(4)), 5)
    def test_dicetable_number_of_dice_reports_zero_when_dice_not_there(self):
        table = ds.DiceTable()
        self.assertEqual(table.number_of_dice(ds.Die(4)), 0)
    def test_weights_info_returns_empty_str_for_empty_table(self):
        table = ds.DiceTable()
        self.assertEqual(table.weights_info(), '')
    def test_weights_info_returns_appropriate_string(self):
        table = ds.DiceTable()
        table.update_list(2, ds.Die(4))
        table.update_list(5, ds.ModWeightedDie({1:10, 4:0}, 2))
        w_info = ('2D4\n    No weights\n\n5D4+10  W:10\n'+
                  '    a roll of 1 has a weight of 10\n'+
                  '    a roll of 2 has a weight of 0\n'+
                  '    a roll of 3 has a weight of 0\n'+
                  '    a roll of 4 has a weight of 0')
        self.assertEqual(table.weights_info(), w_info)
    def test_str_is_empty_for_empty_table(self):
        table = ds.DiceTable()
        self.assertEqual(str(table), '')
    def test_str_returns_appropriate_value(self):
        table = ds.DiceTable()
        table.update_list(2, ds.ModDie(4, -2))
        table.update_list(3, ds.Die(10))
        table.update_list(5, ds.ModWeightedDie({4:10}, 2))
        table_str = '2D4-4\n5D4+10  W:10\n3D10'
        self.assertEqual(str(table), table_str)

    def test_add_doesnt_add_zero_dice(self):
        table = ds.DiceTable()
        table.add_die(0, ds.Die(4))
        self.assertEqual(table.get_list(), [])
        self.assertEqual(table.frequency_all(), [(0, 1)])
    def test_add_adds_correct_dice(self):
        table = ds.DiceTable()
        table.add_die(2, ds.Die(4))
        self.assertEqual(table.get_list(), [(ds.Die(4), 2)])
        freq_all = [(2, 1), (3, 2), (4, 3), (5, 4), (6, 3), (7, 2), (8, 1)]
        self.assertEqual(table.frequency_all(), freq_all)
    def test_remove_die_removes_correct_dice(self):
        table = ds.DiceTable()
        table.add_die(5, ds.Die(4))
        table.remove_die(3, ds.Die(4))
        self.assertEqual(table.get_list(), [(ds.Die(4), 2)])
        freq_all = [(2, 1), (3, 2), (4, 3), (5, 4), (6, 3), (7, 2), (8, 1)]
        self.assertEqual(table.frequency_all(), freq_all)
    def test_remove_die_can_remove_all_the_dice(self):
        table = ds.DiceTable()
        table.add_die(2, ds.Die(4))
        table.remove_die(2, ds.Die(4))
        self.assertEqual(table.get_list(), [])
        self.assertEqual(table.frequency_all(), [(0, 1)])
    def test_remove_die_raises_error_if_die_not_in_table(self):
        table = ds.DiceTable()
        with self.assertRaises(ValueError) as cm:
            table.remove_die(1, ds.Die(4))
        self.assertEqual(cm.exception.args[0],
                         'dice not in table, or removed too many dice')
    def test_remove_die_raises_error_if_too_many_dice_removed(self):
        table = ds.DiceTable()
        table.add_die(3, ds.Die(4))
        with self.assertRaises(ValueError) as cm:
            table.remove_die(4, ds.Die(4))
        self.assertEqual(cm.exception.args[0],
                         'dice not in table, or removed too many dice')

if __name__ == '__main__':
    unittest.main()

