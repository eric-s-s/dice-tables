# pylint: disable=missing-docstring, invalid-name, too-many-public-methods


import unittest

from dicetables.dicerecord import DiceRecord
from dicetables.dieevents import Die
from dicetables.eventsbases.eventerrors import DiceRecordError


class TestDiceRecord(unittest.TestCase):
    def assert_my_regex(self, error_type, regex, func, *args):
        with self.assertRaises(error_type) as cm:
            func(*args)
        error_msg = cm.exception.args[0]
        self.assertEqual(error_msg, regex)

    def test_assert_my_regex(self):
        self.assert_my_regex(ValueError, "invalid literal for int() with base 10: 'a'", int, "a")

    def test_DiceRecord_init_empty(self):
        self.assertEqual(DiceRecord({}).get_dict(), {})

    def test_DiceRecord_init_dict_with_non_die_raises_error(self):
        self.assertRaises(DiceRecordError, DiceRecord, {"a": 2})

    def test_DiceRecord_init_dict_with_non_int_raises_error(self):
        self.assertRaises(DiceRecordError, DiceRecord, {Die(1): 2.0})

    def test_DiceRecord_init_dict_with_negative_number_raises_error(self):
        self.assertRaises(DiceRecordError, DiceRecord, {Die(1): -2})

    def test_DiceRecord_init_error_message_negative(self):
        self.assert_my_regex(
            DiceRecordError,
            "Tried to create a DiceRecord with a negative value at Die(1): -2",
            DiceRecord,
            {Die(1): -2},
        )

    def test_DiceRecord_init_error_message_type(self):
        self.assert_my_regex(
            DiceRecordError, "input must be {ProtoDie: int, ...}", DiceRecord, {Die(1): "a"}
        )

    def test_DiceRecord_init_does_not_add_zero_values(self):
        self.assertEqual(DiceRecord({Die(1): 0}).get_dict(), {})

    def test_DiceRecord_init_non_emtpy(self):
        self.assertEqual(DiceRecord({Die(1): 2, Die(2): 2}).get_dict(), {Die(1): 2, Die(2): 2})

    def test_DiceRecord_init_non_emtpy_does_not_mutate(self):
        dice_dict = {Die(1): 2, Die(2): 2}
        record = DiceRecord(dice_dict)
        dice_dict[Die(1)] = "a"
        self.assertEqual(record.get_dict(), {Die(1): 2, Die(2): 2})

    def test_DiceRecord_new(self):
        record = DiceRecord.new()
        self.assertEqual(record.get_dict(), {})

    def test_DiceRecord_get_dict_empty(self):
        self.assertEqual(DiceRecord({}).get_dict(), {})

    def test_DiceRecord_get_dict(self):
        dice_dict = {Die(3): 4, Die(2): 1}
        record = DiceRecord(dice_dict)
        self.assertEqual(record.get_dict(), dice_dict)

    def test_DiceRecord_get_dict_cannot_mutate_DiceRecord(self):
        record = DiceRecord({Die(3): 4, Die(2): 1})
        dice_dict = record.get_dict()
        dice_dict[Die(3)] = "oh nos!"
        self.assertEqual(record.get_dict(), {Die(3): 4, Die(2): 1})

    def test_DiceRecord_get_number_no_die_returns_zero(self):
        record = DiceRecord({Die(3): 4, Die(2): 1})
        self.assertEqual(record.get_number(Die(5)), 0)

    def test_DiceRecord_get_number_returns_correct_number(self):
        record = DiceRecord({Die(3): 4, Die(2): 1})
        self.assertEqual(record.get_number(Die(3)), 4)

    def test_DiceRecord_add_die_raises_error_for_negative_add(self):
        self.assertRaises(DiceRecordError, DiceRecord({}).add_die, Die(1), -5)

    def test_DiceRecord_add_die_error_message(self):
        self.assert_my_regex(
            DiceRecordError,
            "Tried to add_die or remove_die with a negative number.",
            DiceRecord({}).add_die,
            Die(1),
            -5,
        )

    def test_DiceRecord_add_die_returns_new_record_with_die_added_to_die_already_there(self):
        record = DiceRecord({Die(1): 2})
        new_record = record.add_die(Die(1), 3)
        self.assertEqual(new_record.get_dict(), {Die(1): 5})

    def test_DiceRecord_add_die_returns_new_record_with_new_die_added(self):
        record = DiceRecord({Die(1): 2})
        new_record = record.add_die(Die(2), 3)
        self.assertEqual(new_record.get_dict(), {Die(1): 2, Die(2): 3})

    def test_DiceRecord_add_die_zero_times_returns_identical_record(self):
        record = DiceRecord({Die(1): 2})
        new_record = record.add_die(Die(2), 0)
        self.assertEqual(record, new_record)
        self.assertIsNot(record, new_record)

    def test_DiceRecord_remove_die_raises_error_for_negative_remove(self):
        self.assertRaises(DiceRecordError, DiceRecord({}).remove_die, Die(1), -5)

    def test_DiceRecord_remove_die_error_message(self):
        self.assert_my_regex(
            DiceRecordError,
            "Tried to add_die or remove_die with a negative number.",
            DiceRecord({}).remove_die,
            Die(1),
            -5,
        )

    def test_DiceRecord_remove_die_returns_correct_new_record(self):
        record = DiceRecord({Die(1): 2, Die(2): 5})
        new_record = record.remove_die(Die(2), 3)
        self.assertEqual(new_record.get_dict(), {Die(1): 2, Die(2): 2})

    def test_DiceRecord_remove_die_returns_correct_new_record_all_dice_removed_from_list(self):
        record = DiceRecord({Die(1): 2, Die(2): 5})
        new_record = record.remove_die(Die(2), 5)
        self.assertEqual(new_record.get_dict(), {Die(1): 2})

    def test_DiceRecord_remove_die_raises_error_when_too_many_dice_removed_from_list(self):
        record = DiceRecord({Die(1): 2, Die(2): 5})
        self.assertRaises(DiceRecordError, record.remove_die, Die(2), 17)

    def test_DiceRecord_remove_die_raises_error_when_too_many_dice_removed_msg(self):
        record = DiceRecord({Die(1): 2, Die(2): 5})
        self.assert_my_regex(
            DiceRecordError,
            "Tried to create a DiceRecord with a negative value at Die(2): -12",
            record.remove_die,
            Die(2),
            17,
        )

    def test_DiceRecord_remove_die_raises_error_when_dice_not_in_record_removed_from_list(self):
        record = DiceRecord({Die(1): 2})
        self.assertRaises(DiceRecordError, record.remove_die, Die(2), 17)

    def test_DiceRecord_remove_die_raises_error_when_dice_not_in_record_removed_msg(self):
        record = DiceRecord({Die(1): 2})
        self.assert_my_regex(
            DiceRecordError,
            "Tried to create a DiceRecord with a negative value at Die(2): -17",
            record.remove_die,
            Die(2),
            17,
        )

    def test_DiceRecord_remove_die_works_when_zero_dice_that_are_not_in_list_are_removed(self):
        record = DiceRecord({Die(1): 2})
        new = record.remove_die(Die(100), 0)
        self.assertEqual(new.get_dict(), {Die(1): 2})

    def test_DiceRecord__eq__true(self):
        record_1 = DiceRecord({Die(1): 2, Die(3): 5})
        record_2 = DiceRecord({Die(1): 2, Die(3): 5})
        self.assertTrue(record_1.__eq__(record_2))

    def test_DiceRecord__eq__false_wrong_type(self):
        record_1 = DiceRecord({Die(1): 2, Die(3): 5})
        record_2 = {Die(1): 2, Die(3): 5}
        self.assertFalse(record_1.__eq__(record_2))

    def test_DiceRecord__eq__false_wrong_number(self):
        record_1 = DiceRecord({Die(1): 1, Die(3): 5})
        record_2 = DiceRecord({Die(1): 2, Die(3): 5})
        self.assertFalse(record_1.__eq__(record_2))

    def test_DiceRecord__eq__false_wrong_die(self):
        record_1 = DiceRecord({Die(2): 2, Die(3): 5})
        record_2 = DiceRecord({Die(1): 2, Die(3): 5})
        self.assertFalse(record_1.__eq__(record_2))

    def test_DiceRecord__ne__true(self):
        record_1 = DiceRecord({Die(2): 2, Die(3): 5})
        record_2 = DiceRecord({Die(1): 2, Die(3): 5})
        self.assertTrue(record_1.__ne__(record_2))

    def test_DiceRecord__ne__false(self):
        record_1 = DiceRecord({Die(2): 2, Die(3): 5})
        record_2 = DiceRecord({Die(2): 2, Die(3): 5})
        self.assertFalse(record_1.__ne__(record_2))

    def test_DiceRecord__repr__(self):
        record = DiceRecord({Die(2): 2, Die(3): 5})
        possible_reprs = (
            "DiceRecord({Die(2): 2, Die(3): 5})",
            "DiceRecord({Die(3): 5, Die(2): 2})",
        )
        self.assertIn(repr(record), possible_reprs)


if __name__ == "__main__":
    unittest.main()
