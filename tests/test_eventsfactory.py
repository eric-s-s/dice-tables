# pylint: disable=missing-docstring, invalid-name, too-many-public-methods
"""tests for the baseevents.py module"""
from __future__ import absolute_import
import unittest
import warnings
from sys import version_info
from dicetables.eventsfactory import EventsFactory, ClassNotInFactoryWarning, Getter
from dicetables.baseevents import AdditiveEvents
from dicetables.dicetable import DiceTable, RichDiceTable
from dicetables.dieevents import Die


class Dummy(object):
    def __init__(self, num, dice, dictionary):
        self.num = num
        self.dice = dice
        self.dictionary = dictionary

    def get_num(self):
        return self.num

    def get_dict(self):
        return self.dictionary

    def get_dice_items(self):
        return self.dice


class NewDiceTableSameInitNoFactoryUpdate(DiceTable):
    def __init__(self, event_dic, dice):
        super(NewDiceTableSameInitNoFactoryUpdate, self).__init__(event_dic, dice)


class NewDiceTableSameInitFactoryUpdate(DiceTable):
    DiceTable.factory.add_class('NewDiceTableSameInitFactoryUpdate', ('dictionary', 'dice'))

    def __init__(self, event_dic, dice):
        super(NewDiceTableSameInitFactoryUpdate, self).__init__(event_dic, dice)


class NewDiceTableNewInitNoFactoryUpdate(DiceTable):
    def __init__(self, event_dic, dice, number):
        self.number = number
        super(NewDiceTableNewInitNoFactoryUpdate, self).__init__(event_dic, dice)


class NewDiceTableNewInitFactoryUpdate(DiceTable):
    DiceTable.factory.add_arg('number', 'number', 0)
    DiceTable.factory.add_class('NewDiceTableSameInitFactoryUpdate', ('dictionary', 'dice', 'number'))

    def __init__(self, event_dic, dice, number):
        self.number = number
        super(NewDiceTableNewInitFactoryUpdate, self).__init__(event_dic, dice)


class TestEventsFactory(unittest.TestCase):
    def assert_my_regex(self, error_type, regex, func, *args):
        with self.assertRaises(error_type) as cm:
            func(*args)
        error_msg = str(cm.exception)
        self.assertEqual(error_msg, regex)

    def test_assert_my_regex(self):
        self.assert_my_regex(ValueError, "invalid literal for int() with base 10: 'a'", int, 'a')

    def assert_warning(self, warning, msg, func, *args):
        with warnings.catch_warnings(record=True) as cm:
            warnings.simplefilter("always")
            func(*args)
        if len(cm) != 1:
            self.fail('Warning not raised or too many warnings')
        else:
            self.assertEqual(msg, str(cm[0].message))
            self.assertEqual(warning, cm[0].category)

    def assert_no_warning(self, func, *args):
        with warnings.catch_warnings(record=True) as cm:
            warnings.simplefilter("always")
            func(*args)
        self.assertEqual(len(cm), 0)

    def test_assert_warning(self):
        def func(number):
            warnings.warn('msg', ClassNotInFactoryWarning, stacklevel=2)
            return number
        self.assert_warning(ClassNotInFactoryWarning, 'msg', func, 5)

    def test_assert_warning_with_no_warning(self):
        def func(number):
            return number
        with self.assertRaises(AssertionError) as cm:
            self.assert_warning(ClassNotInFactoryWarning, 'hi', func, 5)
        self.assertEqual(cm.exception.args[0], 'Warning not raised or too many warnings')

    def test_assert_warning_with_too_many_warnings(self):
        def func(number):
            warnings.warn('msg', ClassNotInFactoryWarning, stacklevel=2)
            warnings.warn('msg', Warning, stacklevel=2)
            return number
        with self.assertRaises(AssertionError) as cm:
            self.assert_warning(ClassNotInFactoryWarning, 'hi', func, 5)
        self.assertEqual(cm.exception.args[0], 'Warning not raised or too many warnings')

    def test_assert_no_warning_with_no_warning(self):
        def func(number):
            return number
        self.assert_no_warning(func, 5)

    @unittest.expectedFailure
    def test_assert_no_warning_with_warning(self):
        def func(number):
            warnings.warn('msg', ClassNotInFactoryWarning, stacklevel=2)
            return number
        self.assert_no_warning(func, 5)

    def test_Getter_get_default(self):
        self.assertEqual(Getter('get_dict', {0: 1}).get_default(), {0: 1})

    def test_Getter_get__object_has_getter_method(self):
        events = AdditiveEvents({1: 1})
        self.assertEqual(Getter('get_dict', {0: 1}).get(events), {1: 1})

    def test_Getter_get__object_has_getter_property(self):
        events = RichDiceTable({1: 1}, [], calc_includes_zeroes=False)
        getter = Getter('calc_includes_zeroes', True, is_property=True)
        self.assertEqual(getter.get(events), False)

    def test_EventsFactory_has_class_true(self):
        self.assertTrue(EventsFactory().has_class(AdditiveEvents))

    def test_EventsFactory_has_class_false(self):
        self.assertFalse(EventsFactory().has_class(float))

    def test_EventsFactory_raise_warning_no_warning(self):
        self.assert_no_warning(EventsFactory().raise_warning, AdditiveEvents)

    def test_EventsFactory_raise_warning(self):
        msg = create_warning_message(float)
        self.assert_warning(ClassNotInFactoryWarning, msg, EventsFactory().raise_warning, float)

    def test_EventsFactory_add_class(self):
        factory = EventsFactory()
        factory.add_class('bob', ('dictionary', ))
        self.assertEqual(factory.class_args['bob'], ('dictionary',))

    def test_EventsFactory_add_class_raises_AttributeError(self):
        expected_msg = ('in {}\nin method "add_class"\n' +
                        "one or more args not in list: ['calc_bool', 'dice', 'dictionary']\n" +
                        "add missing args and getters with add_arg method")
        with self.assertRaises(AttributeError) as cm:
            factory = EventsFactory()
            expected_msg = expected_msg.format(factory)
            factory.add_class('bob', ('poop',))
        msg = cm.exception.args[0]
        self.assertEqual(msg, expected_msg)

    def test_EventsFactory_add_arg_not_property_default_val(self):
        factory = EventsFactory()
        factory.add_arg('number', 'get_num', 0)
        factory.add_class('Dummy', ('number', 'dice', 'dictionary'))
        new = factory.new(Dummy)
        self.assertEqual(new.get_num(), 0)

    def test_EventsFactory_add_arg_not_property_held_val(self):
        factory = EventsFactory()
        factory.add_arg('number', 'get_num', 0)
        factory.add_class('Dummy', ('number', 'dice', 'dictionary'))
        number_five = Dummy(5, [(Die(1), 1)], {1: 1})
        new = factory.from_dictionary(number_five, {1: 1})
        self.assertEqual(new.get_num(), 5)

    def test_EventsFactory_add_arg_is_property_default_val(self):
        factory = EventsFactory()
        factory.add_arg('number', 'num', 0, is_property=True)
        factory.add_class('Dummy', ('number', 'dice', 'dictionary'))
        new = factory.new(Dummy)
        self.assertEqual(new.num, 0)

    def test_EventsFactory_add_arg_is_property_held_val(self):
        factory = EventsFactory()
        factory.add_arg('number', 'num', 0, is_property=True)
        factory.add_class('Dummy', ('number', 'dice', 'dictionary'))
        number_five = Dummy(5, [(Die(1), 1)], {1: 1})
        new = factory.from_dictionary(number_five, {1: 1})
        self.assertEqual(new.num, 5)

    def test_mro(self):
        print(Dummy.mro())
        print(NewDiceTableNewInitFactoryUpdate.mro())

    def test_inheritance_no_change_to_factory(self):
        msg = create_warning_message(NewDiceTableSameInitNoFactoryUpdate)
        self.assert_warning(ClassNotInFactoryWarning, msg, EventsFactory().raise_warning,
                            NewDiceTableSameInitNoFactoryUpdate)

    def test_inheritance_with_change_to_factory(self):
        self.assert_no_warning(NewDiceTableSameInitFactoryUpdate.factory.raise_warning,
                               NewDiceTableSameInitFactoryUpdate)

    def test_EventsFactory_new_AdditiveEvents(self):
        new = EventsFactory().new(AdditiveEvents)
        self.assertIs(type(new), AdditiveEvents)
        self.assertEqual(new.get_dict(), {0: 1})

    def test_EventsFactory_new_DiceTable(self):
        new = EventsFactory().new(DiceTable)
        self.assertIs(type(new), DiceTable)
        self.assertEqual(new.get_dict(), {0: 1})
        self.assertEqual(new.get_list(), [])

    def test_EventsFactory_new_RichDiceTable(self):
        new = EventsFactory().new(RichDiceTable)
        self.assertIs(type(new), RichDiceTable)
        self.assertEqual(new.get_dict(), {0: 1})
        self.assertEqual(new.get_list(), [])
        self.assertTrue(new.calc_includes_zeroes)

    def test_EventsFactory_from_dict_AdditiveEvents(self):
        events = AdditiveEvents.new()
        new_events = EventsFactory().from_dictionary(events, {1: 1})
        self.assertIs(type(new_events), AdditiveEvents)
        self.assertEqual(new_events.get_dict(), {1: 1})

    def test_EventsFactory_from_dict_DiceTable(self):
        events = DiceTable.new()
        new_events = EventsFactory().from_dictionary(events, {1: 1})
        self.assertIs(type(new_events), DiceTable)
        self.assertEqual(new_events.get_dict(), {1: 1})
        self.assertEqual(new_events.get_list(), [])

    def test_EventsFactory_from_dict_RichDiceTable(self):
        events = RichDiceTable.new()
        new_events = EventsFactory().from_dictionary(events, {1: 1})
        self.assertIs(type(new_events), RichDiceTable)
        self.assertEqual(new_events.get_dict(), {1: 1})
        self.assertEqual(new_events.get_list(), [])
        self.assertTrue(new_events.calc_includes_zeroes)

    def test_EventsFactory_from_dict_and_dice_DiceTable(self):
        events = DiceTable.new()
        new_events = EventsFactory().from_dictionary_and_dice(events, {1: 1}, [(Die(2), 2)])
        self.assertIs(type(new_events), DiceTable)
        self.assertEqual(new_events.get_dict(), {1: 1})
        self.assertEqual(new_events.get_list(), [(Die(2), 2)])

    def test_EventsFactory_from_dict__and_dice_RichDiceTable(self):
        events = RichDiceTable({2: 2}, [], False)
        new_events = EventsFactory().from_dictionary_and_dice(events, {1: 1}, [(Die(2), 2)])
        self.assertIs(type(new_events), RichDiceTable)
        self.assertEqual(new_events.get_dict(), {1: 1})
        self.assertEqual(new_events.get_list(), [(Die(2), 2)])
        self.assertFalse(new_events.calc_includes_zeroes)


def create_warning_message(the_class):
    msg = ('{} not in Factory.  Will attempt to use parent class.\n'.format(the_class) +
           'At the class level, please do -\n' +
           '<parent class>.factory.add_class("CurrentClass", ("parameter kw 1", "parameter kw 2", ..)\n' +
           'or see documentation at https://github.com/eric-s-s/dice-tables')
    if version_info[0] < 3:
        msg = msg.replace('Type', 'Class')
    return msg


if __name__ == '__main__':
    unittest.main()
