# pylint: disable=missing-docstring, invalid-name, too-many-public-methods
'''unittests for dicestats.py'''
import unittest
import dicestats as ds

#todo get rid of these and use simpler test fixtures
#ie WeightedDie({5:1}) is just fine
D4 = ds.Die(4)
D4W4 = ds.WeightedDie(dict((x, 1) for x in range(1, 5)))
D10 = ds.Die(10)
D4PLUS2 = ds.ModDie(4, 2)
D4MINUS2 = ds.ModDie(4, -2)
D4W10 = ds.WeightedDie(dict((x, 5-x) for x in range(1, 5)))
D4W10PLUS2 = ds.ModWeightedDie(dict((x, 5-x) for x in range(1, 5)), 2)
D4W10MINUS2 = ds.ModWeightedDie(dict((x, 5-x) for x in range(1, 5)), -2)

class TestDiceStats(unittest.TestCase):
    def setUp(self):
        self.table = ds.DiceTable()
    def tearDown(self):
        del self.table

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

#todo don't use D4 constant
    def test_die_moddie_eq(self):
        self.assertEqual(D4 == ds.ModDie(4, 0), True)
        self.assertEqual(ds.ModDie(4, 1) == D4, False)
        self.assertEqual(D4 == ds.ModDie(4, -1), False)
    def test_die_moddie_lt(self):
        self.assertEqual(D4 < ds.ModDie(4, 0), False)
        self.assertEqual(D4 < ds.ModDie(4, 1), True)
        self.assertEqual(D4 < ds.ModDie(4, -1), False)
#todo make consistent with old stuff
    def test_WeightedDie_eq(self):
        dic = {1:1, 2:2}
        self.assertEqual(ds.WeightedDie(dic), ds.WeightedDie(dic))
        self.assertNotEqual(ds.WeightedDie(dic), ds.WeightedDie({2:2}))
    def test_WeightedDie_not_equal_Die_with_same_dictionary(self):
        self.assertNotEqual(D4, D4W4)
    def test_WeightedDie_lt_by_size(self):
        D5W1 = ds.WeightedDie({5:1})
        self.assertTrue(D4W10 < D5W1)
    def test_WeightedDie_lt_by_weight(self):
        self.assertTrue(D4W4 < D4W10)
    def test_WeightedDie_lt_by_tuple_list(self):
        smaller_weight_ten = dict((x, x) for x in range(1, 5))
        self.assertTrue(ds.WeightedDie(smaller_weight_ten) < D4W10)
#todo update test name to be more explicit edge case
    def test_WeightedDie_eq_lt_gt_strange_case(self):
        die1 = ds.WeightedDie({2:0})
        die2 = ds.WeightedDie({1:2})
        self.assertFalse(die1 == die2)
        self.assertFalse(die1.get_size() == die2.get_size())
        self.assertTrue(die1 > die2)
        self.assertTrue(die2 < die1)


    def test_die_get_size(self):
        self.assertEqual(ds.Die(6).get_size(), 6)
    def test_die_get_weight(self):
        self.assertEqual(ds.Die(10).get_weight(), 0)
    def test_die_tuple_list(self):
        self.assertEqual(ds.Die(100).tuple_list(),
                         [(x, 1) for x in range(1, 101)])
    def test_die_weight_info(self):
        self.assertEqual(ds.Die(10000).weight_info(), 'D10000\n    No weights')
    def test_die_str(self):
        self.assertEqual(str(ds.Die(1234)), 'D1234')
    def test_die_multiply_str(self):
        self.assertEqual(ds.Die(5).multiply_str(-2.3e-20), '-2.3e-20D5')
        
    def test_ModDie_get_modifier(self):
        self.assertEqual(ds.ModDie(7, 33).get_modifier(), 33)
    def test_ModDie_tuple_list(self):
        self.assertEqual(ds.ModDie(3, 2).tuple_list(), [(3, 1), (4, 1), (5, 1)])
#todo this belongs in dice equality        
    def test_modDie_with_zero_mod_is_Die(self):
        self.assertEqual(ds.ModDie(10, 0), ds.Die(10))
    def test_modDie_string(self):
        self.assertEqual(str(ds.ModDie(10, 0)), 'D10+0')
    def test_ModDie_multiply_str_pos_mod(self):
        self.assertEqual(ds.ModDie(5, 3).multiply_str(1.5), '1.5D5+4.5')
    def test_ModDie_multiply_str_neg_mod(self):
        self.assertEqual(ds.ModDie(5, -3).multiply_str(1.5), '1.5D5-4.5')

    def test_WeightedDie_get_size(self):
        self.assertEqual(ds.WeightedDie({5:2, 2:5}).get_size(), 5)
#todo KIS for next 3
    def test_WeightedDie_get_weight(self):
        dic = dict((x, 2*x) for x in range(1, 6))
        self.assertEqual(ds.WeightedDie(dic).get_weight(), 2*(1+2+3+4+5))
    def test_WeightedDie_tuple_list(self):
        tuples = [(x, x**2) for x in range(1, 5)]
        self.assertEqual(ds.WeightedDie(dict(tuples)).tuple_list(), tuples)
    def test_WeightedDie_tuple_list_doesnt_return_zero_frequencies(self):
        tuples = [(x, x*(x%2)) for x in range(1, 7)]
        tuples_no_zeros = [(1, 1), (3, 3), (5, 5)]
        self.assertEqual(ds.WeightedDie(dict(tuples)).tuple_list(),
                         tuples_no_zeros)
    def test_WeightedDie_weight_info(self):
        dic = dict((x, x+1) for x in range(1, 6, 2))
        weights_str = ('D5  W:12\n'+
                       '    a roll of 1 has a weight of 2\n' +
                       '    a roll of 2 has a weight of 0\n' +
                       '    a roll of 3 has a weight of 4\n' +
                       '    a roll of 4 has a weight of 0\n' +
                       '    a roll of 5 has a weight of 6')
        self.assertEqual(ds.WeightedDie(dic).weight_info(), weights_str)
    def test_WeightedDie_str(self):
        self.assertEqual(str(D4W10), 'D4  W:10')
    def test_WeightedDie_multiply_str(self):
        self.assertEqual(D4W10.multiply_str(10), '10D4  W:10')
    
    def test_ModWeightedDie_get_mod(self):
        self.assertEqual(D4W10PLUS2.get_modifier(), 2)
    def test_ModWeightedDie_tuple_list(self):
        self.assertEqual(D4W10MINUS2.tuple_list(), [(-1, 4), (0, 3), (1, 2), (2, 1)])
    def test_ModWeightedDie_string(self):
        self.assertEqual(str(D4W10MINUS2), 'D4-2  W:10')
    def test_ModWeightedDie_zero_mod_equals_non_mod(self):
        dic = dict((x, 2+x) for x in range(1, 6))
        self.assertEqual(ds.WeightedDie(dic), ds.ModWeightedDie(dic, 0))
    def test_ModWeigtedDie_multiply_str(self):
        self.assertEqual(D4W10PLUS2.multiply_str(5), '5D4+10  W:10')

    def test_DiceTable_inits_empty(self):
        self.assertEqual(self.table.frequency_all(), [(0, 1)])
        self.assertEqual(self.table.get_list(), [])
    def test_DiceTable_update_list_adds_same_die_to_die_already_in_table(self):
        self.table.update_list(3, D4)
        self.table.update_list(2, D4)
        self.assertIn((D4, 5), self.table.get_list())
    def test_DiceTable_update_list_doesnt_combine_similar_dice(self):
        self.table.update_list(3, D4)
        self.table.update_list(2, D4W4)
        self.assertIn((D4W4, 2), self.table.get_list())
        self.assertIn((D4, 3), self.table.get_list())
    def test_DiceTable_updates_list_removes_die_with_zero_amount(self):
        self.table.update_list(2, D4)
        self.assertIn((D4, 2), self.table.get_list())
        self.table.update_list(-2, D4)
        self.assertEqual([], self.table.get_list())
    def test_DiceTable_number_of_dice_reports_correctly(self):
        self.table.update_list(5, D4)
        self.assertEqual(self.table.number_of_dice(D4), 5)
    def test_DiceTable_number_of_dice_reports_zero_when_dice_not_there(self):
        self.assertEqual(self.table.number_of_dice(D4), 0)
    def test_weights_info_returns_empty_str_for_empty_table(self):
        self.assertEqual(self.table.weights_info(), '')
    def test_weights_info_returns_appropriate_string(self):
        self.table.update_list(2, D4)
        self.table.update_list(5, D4W10PLUS2)
        w_info = ('2D4\n    No weights\n\n5D4+10  W:10\n'+
                  '    a roll of 1 has a weight of 4\n'+
                  '    a roll of 2 has a weight of 3\n'+
                  '    a roll of 3 has a weight of 2\n'+
                  '    a roll of 4 has a weight of 1')
        self.assertEqual(self.table.weights_info(), w_info)
    def test_str_is_empty_for_empty_table(self):
        self.assertEqual(str(self.table), '')
    def test_str_returns_appropriate_value(self):
        self.table.update_list(2, D4MINUS2)
        self.table.update_list(3, D10)
        self.table.update_list(5, D4W10PLUS2)
        table_str = '2D4-4\n5D4+10  W:10\n3D10'
        self.assertEqual(str(self.table), table_str)

    def test_add_doesnt_add_zero_dice(self):
        self.table.add_die(0, D4)
        self.assertEqual(self.table.get_list(), [])
        self.assertEqual(self.table.frequency_all(), [(0, 1)])
    def test_add_adds_correct_dice(self):
        self.table.add_die(2, D4)
        self.assertEqual(self.table.get_list(), [(D4, 2)])
        freq_all = [(2, 1), (3, 2), (4, 3), (5, 4), (6, 3), (7, 2), (8, 1)]
        self.assertEqual(self.table.frequency_all(), freq_all)
    def test_remove_die_removes_correct_dice(self):
        self.table.add_die(5, D4)
        self.table.remove_die(3, D4)
        self.assertEqual(self.table.get_list(), [(D4, 2)])
        freq_all = [(2, 1), (3, 2), (4, 3), (5, 4), (6, 3), (7, 2), (8, 1)]
        self.assertEqual(self.table.frequency_all(), freq_all)
    def test_remove_die_can_remove_all_the_dice(self):
        self.table.add_die(2, D4)
        self.table.remove_die(2, D4)
        self.assertEqual(self.table.get_list(), [])
        self.assertEqual(self.table.frequency_all(), [(0, 1)])
    def test_remove_die_raises_error_if_die_not_in_table(self):
        self.assertRaisesRegexp(ValueError,
                                'dice not in table, or removed too many dice',
                                self.table.remove_die, 1, D4)
    def test_remove_die_raises_error_if_too_many_dice_removed(self):
        self.table.add_die(3, D4)
        self.assertRaisesRegexp(ValueError,
                                'dice not in table, or removed too many dice',
                                self.table.remove_die, 4, D4)

if __name__ == '__main__':
    unittest.main()

