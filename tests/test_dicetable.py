# pylint: disable=missing-docstring, invalid-name, too-many-public-methods
"""unittests for dicetable.py"""
from __future__ import absolute_import

import unittest
from dicetables.dieevents import Die, ModWeightedDie, ModDie, StrongDie
from dicetables.dicetable import DiceTable, DiceRecord, DiceRecordError, RichDiceTable
from dicetables.baseevents import InvalidEventsError


class NewDiceTable(DiceTable):
    def __init__(self, events_dic, dice):
        super(NewDiceTable, self).__init__(events_dic, dice)


class NumberedDiceTable(DiceTable):
    def __init__(self, events_dic, dice, number):
        super(NumberedDiceTable, self).__init__(events_dic, dice)
        self.number = number


class TestDiceStats(unittest.TestCase):

    def assert_my_regex(self, error_type, regex, func, *args):
        with self.assertRaises(error_type) as cm:
            func(*args)
        error_msg = str(cm.exception)
        self.assertEqual(error_msg, regex)

    def test_assert_my_regex(self):
        self.assert_my_regex(ValueError, "invalid literal for int() with base 10: 'a'", int, 'a')

    def test_DiceRecordError_message(self):
        error = DiceRecordError('oops')
        self.assertEqual(error.args[0], 'oops')
        self.assertEqual(str(error), 'oops')

    def test_DiceRecordError_no_message(self):
        error = DiceRecordError()
        self.assertEqual(error.args[0], '')

    def test_DiceRecord_init_empty_iterator(self):
        self.assertEqual(DiceRecord({}.items()).get_record(), {})

    def test_DiceRecord_init_different_empty_iterator(self):
        self.assertEqual(DiceRecord([]).get_record(), {})

    def test_DiceRecord_init_list_with_negative_number_raises_error(self):
        self.assertRaises(DiceRecordError, DiceRecord, {Die(1): -2}.items())

    def test_DiceRecord_init_error_message(self):
        self.assert_my_regex(DiceRecordError, 'DiceRecord may not have negative dice. Error at (Die(1), -2)',
                             DiceRecord, {Die(1): -2}.items())

    def test_DiceRecord_init_does_not_add_zero_values(self):
        self.assertEqual(DiceRecord({Die(1): 0}.items()).get_record(), {})

    def test_DiceRecord_init_works_items_iterator(self):
        self.assertEqual(DiceRecord({Die(1): 2, Die(2): 2}.items()).get_record(), {Die(1): 2, Die(2): 2})

    def test_DiceRecord_init_works_list_iterator(self):
        self.assertEqual(DiceRecord(iter([(Die(1), 2), (Die(2), 2)])).get_record(), {Die(1): 2, Die(2): 2})

    def test_DiceRecord_init_works_list(self):
        self.assertEqual(DiceRecord([(Die(1), 2), (Die(2), 2)]).get_record(), {Die(1): 2, Die(2): 2})

    def test_DiceRecord_get_record_returns_dictionary(self):
        self.assertEqual(DiceRecord({Die(3): 4, Die(2): 1}.items()).get_record(), {Die(2): 1, Die(3): 4})

    def test_DiceRecord_get_record_does_not_mutate_original(self):
        record = DiceRecord({Die(3): 4, Die(2): 1}.items())
        dictionary = record.get_record()
        dictionary[Die(3)] = 10
        self.assertEqual(record.get_record(), {Die(2): 1, Die(3): 4})

    def test_DiceRecord_get_items_empty(self):
        self.assertEqual(DiceRecord([]).get_items(), {}.items())

    def test_DiceRecord_get_list(self):
        the_items = {Die(3): 4, Die(2): 1}.items()
        record = DiceRecord(the_items)
        self.assertEqual(record.get_items(), the_items)

    def test_DiceRecord_get_number_no_die_returns_zero(self):
        record = DiceRecord({Die(3): 4, Die(2): 1}.items())
        self.assertEqual(record.get_number(Die(5)), 0)

    def test_DiceRecord_get_number_returns_correct_number(self):
        record = DiceRecord({Die(3): 4, Die(2): 1}.items())
        self.assertEqual(record.get_number(Die(3)), 4)

    def test_DiceRecord_add_die_raises_error_for_negative_add(self):
        self.assertRaises(DiceRecordError, DiceRecord([]).add_die, -5, Die(1))

    def test_DiceRecord_add_die_error_message(self):
        self.assert_my_regex(DiceRecordError, 'May not add negative dice to DiceRecord. Error at (Die(1), -5)',
                             DiceRecord([]).add_die, -5, Die(1))

    def test_DiceRecord_add_die_returns_new_record_with_die_added_to_die_already_there(self):
        record = DiceRecord({Die(1): 2}.items())
        new_record = record.add_die(3, Die(1))
        self.assertEqual(new_record.get_record(), {Die(1): 5})

    def test_DiceRecord_add_die_returns_new_record_with_new_die_added(self):
        record = DiceRecord({Die(1): 2}.items())
        new_record = record.add_die(3, Die(2))
        self.assertEqual(new_record.get_record(), {Die(1): 2, Die(2): 3})

    def test_DiceRecord_remove_die_raises_error_for_negative_add(self):
        self.assertRaises(DiceRecordError, DiceRecord([]).remove_die, -5, Die(1))

    def test_DiceRecord_remove_die_error_message(self):
        self.assert_my_regex(DiceRecordError, 'May not remove negative dice from DiceRecord. Error at (Die(1), -5)',
                             DiceRecord([]).remove_die, -5, Die(1))

    def test_DiceRecord_remove_die_returns_correct_new_record(self):
        record = DiceRecord({Die(1): 2, Die(2): 5}.items())
        new_record = record.remove_die(3, Die(2))
        self.assertEqual(new_record.get_record(), {Die(1): 2, Die(2): 2})

    def test_DiceRecord_remove_die_returns_correct_new_record_all_dice_removed_from_list(self):
        record = DiceRecord({Die(1): 2, Die(2): 5}.items())
        new_record = record.remove_die(5, Die(2))
        self.assertEqual(new_record.get_record(), {Die(1): 2})

    def test_DiceRecord_remove_die_raises_error_when_too_many_dice_removed_from_list(self):
        record = DiceRecord({Die(1): 2, Die(2): 5}.items())
        self.assert_my_regex(DiceRecordError, 'Removed too many dice from DiceRecord. Error at (Die(2), -12)',
                             record.remove_die, 17, Die(2))

    def test_DiceRecord_remove_die_raises_error_when_dice_not_in_record_removed_from_list(self):
        record = DiceRecord({Die(1): 2}.items())
        self.assert_my_regex(DiceRecordError, 'Removed too many dice from DiceRecord. Error at (Die(2), -17)',
                             record.remove_die, 17, Die(2))

    def test_DiceTable_init_raises_InvalidEventsError(self):
        self.assertRaises(InvalidEventsError, DiceTable, {1: 0}, [])

    def test_DiceTable_init_raises_DiceRecordError_for_negative_dice_numbers(self):
        self.assertRaises(DiceRecordError, DiceTable, {1: 1}, [(Die(2), -1)])

    def test_DiceTable_init_works_as_expected(self):
        table = DiceTable({1: 2, 3: 4}, [(Die(1), 2), (Die(3), 4)])
        self.assertEqual(table.get_list(), [(Die(1), 2), (Die(3), 4)])
        self.assertEqual(table.get_dict(), {1: 2, 3: 4})

    def test_DiceTable_class_method__new_returns_DiceTable_with_identity_dict_empty_dice_list(self):
        table = DiceTable.new()
        self.assertEqual(table.get_dict(), {0: 1})
        self.assertEqual(table.get_list(), [])

    def test_DiceTable_get_dict_removes_zeros_from_dict(self):
        table = DiceTable({1: 2, 3: 4, 5: 0, 10: 0}, [(Die(1), 2), (Die(3), 4)])
        self.assertEqual(table.get_list(), [(Die(1), 2), (Die(3), 4)])
        self.assertEqual(table.get_dict(), {1: 2, 3: 4})

    def test_DiceTable_get_dice_items(self):
        dice_items = {Die(1): 1, Die(2): 2}.items()
        self.assertEqual(DiceTable({1: 1}, dice_items).get_dice_items(), dice_items)

    def test_DiceTable_get_list_empty_record(self):
        table = DiceTable({1: 1}, [])
        self.assertEqual(table.get_list(), [])

    def test_DiceTable_get_list_non_empty_record(self):
        table = DiceTable({1: 1}, [(Die(1), 2)])
        self.assertEqual(table.get_list(), [(Die(1), 2)])

    def test_DiceTable_get_list_is_sorted(self):
        table = DiceTable({1: 1}, [(Die(3), 2), (Die(2), 100), (Die(1), 2)])
        self.assertEqual(table.get_list(), [(Die(1), 2), (Die(2), 100), (Die(3), 2)])

    def test_DiceTable_number_of_dice_reports_correctly(self):
        table = DiceTable({1: 1}, [(Die(4), 5)])
        self.assertEqual(table.number_of_dice(Die(4)), 5)

    def test_DiceTable_number_of_dice_reports_zero_when_dice_not_there(self):
        table = DiceTable.new()
        self.assertEqual(table.number_of_dice(Die(4)), 0)

    def test_DiceTable_weights_info_returns_empty_str_for_empty_table(self):
        table = DiceTable.new()
        self.assertEqual(table.weights_info(), '')

    def test_DiceTable_weights_info_returns_appropriate_string(self):
        table = DiceTable({1: 1}, [(Die(4), 2), (ModWeightedDie({1: 10, 4: 0}, 2), 5)])
        w_info = ('2D4\n' +
                  '    No weights\n\n' +
                  '5D4+10  W:10\n' +
                  '    a roll of 1 has a weight of 10\n' +
                  '    a roll of 2 has a weight of 0\n' +
                  '    a roll of 3 has a weight of 0\n' +
                  '    a roll of 4 has a weight of 0')
        self.assertEqual(table.weights_info(), w_info)

    def test_DiceTable_str_is_empty_for_empty_table(self):
        table = DiceTable.new()
        self.assertEqual(str(table), '')

    def test_DiceTable_str_one_element(self):
        self.assertEqual(DiceTable({1: 1}, [(Die(1), 2)]).__str__(), '2D1')

    def test_DiceTable_str_many_elements_note_they_are_sorted(self):
        dice_list = [(ModDie(4, -2), 2), (Die(10), 3), (ModWeightedDie({4: 10}, 2), 5)]
        table = DiceTable({1: 1}, dice_list)
        table_str = ('2D4-4\n' +
                     '5D4+10  W:10\n' +
                     '3D10')
        self.assertEqual(str(table), table_str)

    def test_DiceTable_add_die_raise_error_for_negative_add(self):
        table = DiceTable.new()
        self.assertRaises(DiceRecordError, table.add_die, -2, Die(5))

    def test_DiceTable_add_die_doesnt_add_zero_dice(self):
        table = DiceTable.new()
        new = table.add_die(0, Die(4))
        self.assertEqual(new.get_list(), [])
        self.assertEqual(new.get_dict(), {0: 1})

    def test_DiceTable_add_die_updates_list_same_dice(self):
        table = DiceTable({1: 1}, [(Die(2), 10)])
        new = table.add_die(2, Die(2))
        self.assertEqual(new.get_list(), [(Die(2), 12)])

    def test_DiceTable_add_die_updates_list_different_dice(self):
        table = DiceTable({1: 1}, [(Die(2), 10)])
        new = table.add_die(2, Die(1))
        self.assertEqual(new.get_list(), [(Die(1), 2), (Die(2), 10)])

    def test_DiceTable_add_die_adds_correct_dice(self):
        table = DiceTable.new()
        new = table.add_die(2, Die(4))
        self.assertEqual(new.get_list(), [(Die(4), 2)])
        events_dict = {2: 1, 3: 2, 4: 3, 5: 4, 6: 3, 7: 2, 8: 1}
        self.assertEqual(new.get_dict(), events_dict)

    def test_DiceTable_remove_die_raise_error_for_negative_add(self):
        table = DiceTable.new()
        self.assertRaises(DiceRecordError, table.remove_die, -2, Die(5))

    def test_DiceTable_remove_die_removes_correct_dice(self):
        table = DiceTable.new()
        five_d_four = table.add_die(5, Die(4))
        two_d_four = five_d_four.remove_die(3, Die(4))
        self.assertEqual(two_d_four.get_list(), [(Die(4), 2)])
        events_dict = {2: 1, 3: 2, 4: 3, 5: 4, 6: 3, 7: 2, 8: 1}
        self.assertEqual(two_d_four.get_dict(), events_dict)

    def test_DiceTable_remove_die_can_remove_all_the_dice(self):
        table = DiceTable.new()
        two_d_four = table.add_die(2, Die(4))
        no_dice = two_d_four.remove_die(2, Die(4))
        self.assertEqual(no_dice.get_list(), [])
        self.assertEqual(no_dice.get_dict(), {0: 1})

    def test_DiceTable_remove_die_raises_error_if_Die_not_in_table(self):
        self.assertRaises(DiceRecordError, DiceTable.new().remove_die, 1, Die(4))

    def test_DiceTable_remove_die_raises_error_if_too_many_dice_removed(self):
        table = DiceTable.new()
        three_d_four = table.add_die(3, Die(4))
        self.assertRaises(DiceRecordError, three_d_four.remove_die, 4, Die(4))

    def test_DiceTable_combine(self):
        table = DiceTable.new()
        new = table.combine(1, Die(2))
        self.assertEqual(new.get_dict(), {1: 1, 2: 1})
        self.assertEqual(new.get_list(), [])

    def test_DiceTable_combine_by_dictionary(self):
        table = DiceTable.new()
        new = table.combine_by_dictionary(1, Die(2))
        self.assertEqual(new.get_dict(), {1: 1, 2: 1})
        self.assertEqual(new.get_list(), [])

    def test_DiceTable_combine_by_flattened_list(self):
        table = DiceTable.new()
        new = table.combine_by_flattened_list(1, Die(2))
        self.assertEqual(new.get_dict(), {1: 1, 2: 1})
        self.assertEqual(new.get_list(), [])

    def test_DiceTable_combine_by_indexed_values(self):
        table = DiceTable.new()
        new = table.combine_by_indexed_values(1, Die(2))
        self.assertEqual(new.get_dict(), {1: 1, 2: 1})
        self.assertEqual(new.get_list(), [])

    def test_DiceTable_remove(self):
        table = DiceTable({1: 1, 2: 1}, [(Die(2), 1)])
        new = table.remove(1, Die(2))
        self.assertEqual(new.get_dict(), {0: 1})
        self.assertEqual(new.get_list(), [(Die(2), 1)])

    def test_RichDiceTable_init_does_DiceTable_init(self):
        table = RichDiceTable({1: 1}, [], True)
        self.assertEqual(table.get_dict(), {1: 1})
        self.assertEqual(table.get_list(), [])

    def test_RichDiceTable_init_calc_includes_zeroes_defaults_True(self):
        table = RichDiceTable({1: 1}, [])
        self.assertTrue(table.calc_includes_zeroes)

    def test_RichDiceTable_init_calc_includes_zeroes_set_to_False(self):
        table = RichDiceTable({1: 1}, [], calc_includes_zeroes=False)
        self.assertFalse(table.calc_includes_zeroes)

    def test_RichDiceTable_init_does_has_correct_calc(self):
        table = RichDiceTable({1: 1}, [])
        self.assertEqual(table.calc.percentage_points(), [(1, 100.0)])

    def test_RichDiceTable_calc_defaults_to_include_zeros(self):
        table = RichDiceTable({1: 1}, [])
        self.assertTrue(table.calc.include_zeroes)

    def test_RichDiceTable_init_calc_includes_zeros_false(self):
        table = RichDiceTable({1: 1}, [], calc_includes_zeroes=False)
        self.assertFalse(table.calc.include_zeroes)

    def test_RichDiceTable_update_resets_calc(self):
        table = RichDiceTable({1: 1}, [])
        new = table.add_die(1, Die(2))
        self.assertEqual(new.calc.percentage_points(), [(2, 50.0), (3, 50.0)])

    def test_RichDiceTable_update_keeps_include_zeroes_info_true(self):
        table = RichDiceTable({1: 1}, [], calc_includes_zeroes=True)
        new = table.add_die(1, Die(2))
        self.assertTrue(new.calc.include_zeroes)

    def test_RichDiceTable_update_keeps_include_zeroes_info_false(self):
        table = RichDiceTable({1: 1}, [], calc_includes_zeroes=False)
        new = table.add_die(1, Die(2))
        self.assertFalse(new.calc.include_zeroes)

    def test_RichDiceTable_info_property(self):
        table = RichDiceTable({1: 1}, [], calc_includes_zeroes=False)
        self.assertEqual(table.info.all_events(), [(1, 1)])
        self.assertEqual(table.info.events_range(), (1, 1))

    def test_RichDiceTable_info_property_updates(self):
        table = RichDiceTable({1: 1}, [], calc_includes_zeroes=False)
        self.assertEqual(table.info.all_events(), [(1, 1)])
        new = table.add_die(1, Die(2))
        self.assertEqual(new.info.all_events(), [(2, 1), (3, 1)])

    def test_RichDiceTable_class_method__new_get_dict(self):
        table = RichDiceTable.new()
        self.assertEqual(table.get_dict(), {0: 1})

    def test_RichDiceTable_class_method__new_get_list(self):
        table = RichDiceTable.new()
        self.assertEqual(table.get_list(), [])

    def test_RichDiceTable_class_method__new_has_calc_and_info(self):
        table = RichDiceTable.new()
        self.assertEqual(table.info.all_events(), [(0, 1)])
        self.assertEqual(table.calc.percentage_points(), [(0, 100.0)])

    def test_RichDiceTable_class_method__new_calc_includes_zeroes_is_True(self):
        table = RichDiceTable.new()
        self.assertTrue(table.calc_includes_zeroes)

    def test_RichDiceTable_switch_boolean_switches_calc_includes_zeros(self):
        table = RichDiceTable({5: 1}, [(Die(5), 100)], calc_includes_zeroes=True)
        is_false = table.switch_boolean()
        is_true = is_false.switch_boolean()
        self.assertFalse(is_false.calc_includes_zeroes)
        self.assertTrue(is_true.calc_includes_zeroes)

    def test_RichDiceTable_switch_boolean_keeps_events_and_dice_record(self):
        table = RichDiceTable({5: 1}, [(Die(5), 100)], calc_includes_zeroes=True)
        is_false = table.switch_boolean()
        is_true = is_false.switch_boolean()

        self.assertEqual(table.get_list(), is_true.get_list())
        self.assertEqual(table.get_list(), is_false.get_list())
        self.assertEqual(table.get_dict(), is_true.get_dict())
        self.assertEqual(table.get_dict(), is_false.get_dict())

    def test_RichDiceTable_add_die(self):
        table = RichDiceTable.new()
        table = table.switch_boolean()
        new = table.add_die(1, StrongDie(Die(2), 2))
        self.assertEqual(new.info.all_events(), [(2, 1), (4, 1)])
        self.assertEqual(new.calc.percentage_points(), [(2, 50.0), (4, 50.0)])
        self.assertEqual(new.get_list(), [(StrongDie(Die(2), 2), 1)])

    def test_RichDiceTable_combine_updates_calc_and_info(self):
        table = RichDiceTable.new()
        table = table.switch_boolean()
        new = table.combine(1, StrongDie(Die(2), 2))
        self.assertEqual(new.info.all_events(), [(2, 1), (4, 1)])
        self.assertEqual(new.calc.percentage_points(), [(2, 50.0), (4, 50.0)])
        self.assertEqual(new.get_list(), [])

    def test_RichDiceTable_combine_by_dictionary(self):
        table = RichDiceTable.new()
        table = table.switch_boolean()
        new = table.combine_by_dictionary(1, StrongDie(Die(2), 2))
        self.assertEqual(new.info.all_events(), [(2, 1), (4, 1)])
        self.assertEqual(new.calc.percentage_points(), [(2, 50.0), (4, 50.0)])
        self.assertEqual(new.get_list(), [])

    def test_RichDiceTable_combine_by_flattened_list(self):
        table = RichDiceTable.new()
        table = table.switch_boolean()
        new = table.combine_by_flattened_list(1, StrongDie(Die(2), 2))
        self.assertEqual(new.info.all_events(), [(2, 1), (4, 1)])
        self.assertEqual(new.calc.percentage_points(), [(2, 50.0), (4, 50.0)])
        self.assertEqual(new.get_list(), [])

    def test_RichDiceTable_combine_by_indexed_values(self):
        table = RichDiceTable.new()
        table = table.switch_boolean()
        new = table.combine_by_indexed_values(1, StrongDie(Die(2), 2))
        self.assertEqual(new.info.all_events(), [(2, 1), (4, 1)])
        self.assertEqual(new.calc.percentage_points(), [(2, 50.0), (4, 50.0)])
        self.assertEqual(new.get_list(), [])

    def test_RichDiceTable_remove_die_updates_calc_and_info(self):
        table = RichDiceTable({2: 1, 4: 1}, [(StrongDie(Die(2), 2), 1)], False)
        new = table.remove_die(1, StrongDie(Die(2), 2))
        self.assertEqual(new.info.all_events(), [(0, 1)])
        self.assertEqual(new.calc.percentage_points(), [(0, 100.0)])
        self.assertEqual(new.get_list(), [])
        self.assertFalse(new.calc_includes_zeroes)

    def test_RichDiceTable_remove(self):
        table = RichDiceTable({2: 1, 4: 1}, [(StrongDie(Die(2), 2), 1)], False)
        new = table.remove(1, StrongDie(Die(2), 2))
        self.assertEqual(new.info.all_events(), [(0, 1)])
        self.assertEqual(new.calc.percentage_points(), [(0, 100.0)])
        self.assertEqual(new.get_list(), [(StrongDie(Die(2), 2), 1)])
        self.assertFalse(new.calc_includes_zeroes)


if __name__ == '__main__':
    unittest.main()
