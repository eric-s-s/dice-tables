# pylint: disable=missing-docstring, invalid-name, too-many-public-methods
from __future__ import absolute_import

import unittest

from dicetables.additiveevents import AdditiveEvents
from dicetables.dicerecord import DiceRecord
from dicetables.dicetable import DetailedDiceTable
from dicetables.factory.factorytools import StaticDict, Getter


class TestFactoryTools(unittest.TestCase):
    def test_StaticDict_init_empty(self):
        empty = StaticDict({})
        self.assertEqual(empty.items(), {}.items())

    def test_StaticDict_init_non_empty_items(self):
        new = StaticDict({1: 2, 3: 4})
        self.assertEqual(new.items(), {1: 2, 3: 4}.items())

    def test_StaticDict_init_is_not_original(self):
        input_dict = {1: 2, 3: 4}
        new = StaticDict(input_dict)
        input_dict[1] = 'a'
        self.assertEqual(new.items(), {1: 2, 3: 4}.items())

    def test_StaticDict_keys_empty(self):
        empty = StaticDict({})
        self.assertEqual(empty.keys(), {}.keys())

    def test_StaticDict_keys(self):
        new = StaticDict({1: 2, 3: 4})
        self.assertEqual(tuple(new.keys()), (1, 3))

    def test_StaticDict_values_empty(self):
        empty = StaticDict({})
        self.assertEqual(empty.keys(), {}.keys())

    def test_StaticDict_values(self):
        new = StaticDict({1: 2, 3: 4})
        self.assertEqual(tuple(new.values()), (2, 4))

    def test_StaticDict_copy_empty(self):
        new = StaticDict({})
        cpy = new.copy()
        self.assertIsNot(cpy, new)
        self.assertEqual(cpy.items(), {}.items())

    def test_StaticDict_copy(self):
        new = StaticDict({1: 2, 3: 4})
        cpy = new.copy()
        self.assertEqual(cpy.items(), new.items())

    def test_StaticDict_copy_returns_correct_type(self):
        new = StaticDict({})
        self.assertIs(type(new.copy()), StaticDict)

    def test_StaticDict_get_not_there_default_not_set(self):
        new = StaticDict({1: 2, 3: 4})
        answer = new.get(2)
        self.assertIsNone(answer)

    def test_StaticDict_get_not_there_default_set(self):
        new = StaticDict({1: 2, 3: 4})
        answer = new.get(2, 'a')
        self.assertEqual(answer, 'a')

    def test_StaticDict_get_returns_correct_value(self):
        new = StaticDict({1: 2, 3: 4})
        self.assertEqual(new.get(1), 2)

    def test_StaticDict_set_new_key(self):
        new = StaticDict({1: 2, 3: 4})
        new = new.set(4, 5)
        self.assertEqual(tuple(new.items()), ((1, 2), (3, 4), (4, 5)))

    def test_StaticDict_set_present_key(self):
        new = StaticDict({1: 2, 3: 4})
        new = new.set(3, 5)
        self.assertEqual(tuple(new.items()), ((1, 2), (3, 5)))

    def test_StaticDict_set_returns_correct_type(self):
        new = StaticDict({})
        self.assertIs(type(new.set(1, 2)), StaticDict)

    def test_StaticDict_delete_key_not_present_raises_key_error(self):
        new = StaticDict({1: 2, 3: 4})
        self.assertRaises(KeyError, new.delete, 5)

    def test_StaticDict_delete(self):
        new = StaticDict({1: 2, 3: 4})
        new = new.delete(3)
        self.assertEqual(tuple(new.items()), ((1, 2),))

    def test_StaticDict_delete_returns_correct_type(self):
        new = StaticDict({1: 2})
        self.assertIs(type(new.delete(1)), StaticDict)

    def test_Getter_init_copies_if_possible(self):
        new = {}
        getter = Getter('hi', new)
        new[1] = 2
        self.assertEqual(getter.get_default(), {})

    def test_Getter_get_default(self):
        self.assertEqual(Getter('get_dict', {0: 1}).get_default(), {0: 1})

    def test_Getter_get_default_does_not_copy_if_no_copy_method(self):
        self.assertEqual(Getter('a', 5).get_default(), 5)

    def test_Getter_get_default_copies_if_possible(self):
        dic = {0: 1}
        getter = Getter('get_dict', dic)
        default = getter.get_default()
        default[1] = 5
        dic[2] = 7
        self.assertEqual(getter.get_default(), {0: 1})

    def test_Getter_get_from__object_has_getter_method(self):
        events = AdditiveEvents({1: 1})
        self.assertEqual(Getter('get_dict', {0: 1}).get_from(events), {1: 1})

    def test_Getter_get_from__object_has_getter_property(self):
        events = DetailedDiceTable({1: 1}, DiceRecord.new(), calc_includes_zeroes=False)
        getter = Getter('calc_includes_zeroes', True, is_property=True)
        self.assertEqual(getter.get_from(events), False)

    def test_Getter_get_bool_true(self):
        self.assertTrue(Getter('a', 1, is_property=True).get_bool())

    def test_Getter_get_bool_false(self):
        self.assertFalse(Getter('a', 1, is_property=False).get_bool())

    def test_Getter_get_name(self):
        self.assertEqual(Getter('a', 1).get_name(), 'a')

    def test_Getter_str_method_property(self):
        expected_string = 'property: "calc_includes_zeroes", default: True'
        self.assertEqual(str(Getter('calc_includes_zeroes', True, is_property=True)), expected_string)

    def test_Getter_str_method_method(self):
        expected_string = 'method: "calc_includes_zeroes", default: True'
        self.assertEqual(str(Getter('calc_includes_zeroes', True)), expected_string)

    def test_Getter_eq_true(self):
        getter1 = Getter('get_num', 0)
        getter2 = Getter('get_num', 0)
        self.assertTrue(getter1 == getter2)

    def test_Getter_eq_false_by_default(self):
        getter1 = Getter('get_num', 0)
        getter2 = Getter('get_num', '0')
        self.assertFalse(getter1 == getter2)

    def test_Getter_eq_false_by_incomparable_defaults(self):
        class Bob(object):
            number = 5

            def __eq__(self, other):
                return self.number == other.number

        class Frank(object):
            letter = 'a'

            def __eq__(self, other):
                return self.letter == other.letter

        self.assertRaises(AttributeError, Bob().__eq__, Frank())
        self.assertFalse(Getter('a', Bob()) == Getter('a', Frank()))

    def test_Getter_eq_false_by_defaults_object_has_no_eq_method_two_instances(self):
        class Bob(object):
            number = 5

        bob1 = Bob()
        bob2 = Bob()
        self.assertFalse(Getter('a', bob1) == Getter('a', bob2))

    def test_Getter_eq_false_by_property_bool(self):
        getter1 = Getter('get_num', 0, is_property=True)
        getter2 = Getter('get_num', 0, is_property=False)
        self.assertFalse(getter1 == getter2)

    def test_Getter_eq_false_by_name(self):
        getter1 = Getter('get_number', 0)
        getter2 = Getter('get_num', 0)
        self.assertFalse(getter1 == getter2)

    def test_Getter_ne_false(self):
        getter1 = Getter('get_num', 0)
        getter2 = Getter('get_num', 0)
        self.assertFalse(getter1 != getter2)

    def test_Getter_ne_true(self):
        getter1 = Getter('get_number', 0)
        getter2 = Getter('get_num', 0)
        self.assertTrue(getter1 != getter2)


if __name__ == '__main__':
    unittest.main()
