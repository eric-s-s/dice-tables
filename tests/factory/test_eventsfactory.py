# pylint: disable=missing-docstring, invalid-name, too-many-public-methods
"""tests for the baseevents.py module"""
from __future__ import absolute_import

import unittest
import warnings
from sys import version_info

from dicetables.baseevents import AdditiveEvents
from dicetables.dicetable import DiceTable, RichDiceTable
from dicetables.dieevents import Die
from dicetables.factory.eventsfactory import EventsFactory, ClassNotInFactoryWarning, Getter


class Dummy(object):
    class_args = ('number', 'dice', 'dictionary')
    new_args = ('number', 'get_num', 0)

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
    class_args = ('dictionary', 'dice')

    def __init__(self, event_dic, dice):
        super(NewDiceTableSameInitFactoryUpdate, self).__init__(event_dic, dice)


class NewDiceTableNewInitNoFactoryUpdate(DiceTable):
    def __init__(self, event_dic, dice, number):
        self.number = number
        super(NewDiceTableNewInitNoFactoryUpdate, self).__init__(event_dic, dice)


class NewDiceTableNewInitFactoryUpdate(DiceTable):
    class_args = ('dictionary', 'dice', 'number')
    new_args = [('number', 'number', 0, 'property')]

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
        if len(cm) != 0:
            self.fail('number of warnings: {}'.format(len(cm)))

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

    def test_create_factory_string_no_adds(self):
        expected = ("CLASSES:\n" +
                    "    AdditiveEvents: ('dictionary',)\n" +
                    "    DiceTable: ('dictionary', 'dice')\n" +
                    "    RichDiceTable: ('dictionary', 'dice', 'calc_bool')\n" +
                    "GETTERS:\n" +
                    '    calc_bool: property: "calc_includes_zeroes", default: True\n' +
                    '    dice: method: "get_dice_items", default: []\n' +
                    '    dictionary: method: "get_dict", default: {0: 1}')
        self.assertEqual(expected, create_factory_string())

    def test_create_factory_string_adds(self):
        expected = ("CLASSES:\n" +
                    "    AdditiveEvents: ('dictionary',)\n" +
                    "    B: ('cb',)\n"
                    "    C: ('dice',)\n" +
                    "    DiceTable: ('dictionary', 'dice')\n" +
                    "    RichDiceTable: ('dictionary', 'dice', 'calc_bool')\n" +
                    "GETTERS:\n" +
                    '    calc_bool: property: "calc_includes_zeroes", default: True\n' +
                    '    cb: method: "get", default: 0\n' +
                    '    dice: method: "get_dice_items", default: []\n' +
                    '    dictionary: method: "get_dict", default: {0: 1}')
        new_classes = (("B", ('cb', )), ("C", ('dice', )))
        new_getters = (('cb', Getter('get', 0)), )
        self.assertEqual(expected, create_factory_string(new_classes, new_getters))

    def test_Getter_get_default(self):
        self.assertEqual(Getter('get_dict', {0: 1}).get_default(), {0: 1})

    def test_Getter_get__object_has_getter_method(self):
        events = AdditiveEvents({1: 1})
        self.assertEqual(Getter('get_dict', {0: 1}).get(events), {1: 1})

    def test_Getter_get__object_has_getter_property(self):
        events = RichDiceTable({1: 1}, [], calc_includes_zeroes=False)
        getter = Getter('calc_includes_zeroes', True, is_property=True)
        self.assertEqual(getter.get(events), False)

    def test_Getter_str_method_property(self):
        expected_string = 'property: "calc_includes_zeroes", default: True'
        self.assertEqual(str(Getter('calc_includes_zeroes', True, is_property=True)), expected_string)

    def test_Getter_str_method_method(self):
        expected_string = 'method: "calc_includes_zeroes", default: True'
        self.assertEqual(str(Getter('calc_includes_zeroes', True)), expected_string)

    def test_EventsFactory_currents_state(self):
        EventsFactory.reset()
        self.assertEqual(EventsFactory.current_state(), create_factory_string())

    def test_EventsFactory_has_class_true(self):
        EventsFactory.reset()
        self.assertTrue(EventsFactory.has_class(AdditiveEvents))

    def test_EventsFactory_has_class_false(self):
        EventsFactory.reset()
        self.assertFalse(EventsFactory.has_class(float))

    def test_EventsFactory_has_getter_key_true(self):
        EventsFactory.reset()
        self.assertTrue(EventsFactory.has_getter_key(('dictionary', 'calc_bool')))

    def test_EventsFactory_has_getter_key_false(self):
        EventsFactory.reset()
        self.assertFalse(EventsFactory.has_getter_key(('dictionary', 'calc_bool', 'not_there')))

    def test_EventsFactory_update_class(self):
        EventsFactory.reset()
        EventsFactory.update_class('bob', ('dictionary',))
        status = create_factory_string(new_classes=(('bob', ('dictionary',)), ))
        self.assertEqual(EventsFactory.current_state(), status)

    def test_EventsFactory_reset(self):
        EventsFactory.reset()
        EventsFactory.update_class('Dummy', ('dictionary',))
        EventsFactory.update_getter_key('number', 'get_num', 0)
        self.assertTrue(EventsFactory.has_class(Dummy))
        self.assertTrue(EventsFactory.has_getter_key(('number', )))

        EventsFactory.reset()
        self.assertFalse(EventsFactory.has_class(Dummy))
        self.assertFalse(EventsFactory.has_getter_key(('number', )))
        for preset in [AdditiveEvents, DiceTable, RichDiceTable]:
            self.assertTrue(EventsFactory.has_class(preset))
        self.assertTrue(EventsFactory.has_getter_key(['dictionary', 'dice', 'calc_bool']))
    #
    # def test_EventsFactory_update_class_raises_AttributeError(self):
    #     EventsFactory.reset()
    #     expected_msg = ('in {}\nin method "add_class"\n' +
    #                     "one or more args not in list: ['calc_bool', 'dice', 'dictionary']\n" +
    #                     "add missing args and getters with update_getter_key method")
    #     with self.assertRaises(AttributeError) as cm:
    #         expected_msg = expected_msg.format(EventsFactory)
    #         EventsFactory.update_class('bob', ('poop',))
    #     msg = cm.exception.args[0]
    #     self.assertEqual(msg, expected_msg)

    def test_EventsFactory_update_getter_key_not_property_default_val(self):
        EventsFactory.update_getter_key('number', 'get_num', 0)
        EventsFactory.update_class('Dummy', ('number', 'dice', 'dictionary'))
        new = EventsFactory.new(Dummy)
        self.assertEqual(new.get_num(), 0)

    def test_EventsFactory_update_getter_key_not_property_held_val(self):
        EventsFactory.update_getter_key('number', 'get_num', 0)
        EventsFactory.update_class('Dummy', ('number', 'dice', 'dictionary'))
        number_five = Dummy(5, [(Die(1), 1)], {1: 1})
        new = EventsFactory.from_dictionary(number_five, {1: 1})
        self.assertEqual(new.get_num(), 5)

    def test_EventsFactory_update_getter_key_is_property_default_val(self):
        EventsFactory.update_getter_key('number', 'num', 0, is_property=True)
        EventsFactory.update_class('Dummy', ('number', 'dice', 'dictionary'))
        new = EventsFactory.new(Dummy)
        self.assertEqual(new.num, 0)

    def test_EventsFactory_update_getter_key_is_property_held_val(self):
        EventsFactory.update_getter_key('number', 'num', 0, is_property=True)
        EventsFactory.update_class('Dummy', ('number', 'dice', 'dictionary'))
        number_five = Dummy(5, [(Die(1), 1)], {1: 1})
        new = EventsFactory.from_dictionary(number_five, {1: 1})
        self.assertEqual(new.num, 5)

    def test_mro(self):
        print(Dummy.mro())
        print(NewDiceTableNewInitFactoryUpdate.mro())

    @unittest.skip('a long way away')
    def test_inheritance_no_change_to_factory(self):
        msg = create_warning_message(NewDiceTableSameInitNoFactoryUpdate)
        self.assert_warning(ClassNotInFactoryWarning, msg, EventsFactory.raise_warning,
                            NewDiceTableSameInitNoFactoryUpdate)

    @unittest.skip('waiting for change to API')
    def test_inheritance_with_change_to_factory(self):
        self.assert_no_warning(EventsFactory.raise_warning,
                               NewDiceTableSameInitFactoryUpdate)

    def test_EventsFactory_new_AdditiveEvents(self):
        new = EventsFactory.new(AdditiveEvents)
        self.assertIs(type(new), AdditiveEvents)
        self.assertEqual(new.get_dict(), {0: 1})

    def test_EventsFactory_new_DiceTable(self):
        new = EventsFactory.new(DiceTable)
        self.assertIs(type(new), DiceTable)
        self.assertEqual(new.get_dict(), {0: 1})
        self.assertEqual(new.get_list(), [])

    def test_EventsFactory_new_RichDiceTable(self):
        new = EventsFactory.new(RichDiceTable)
        self.assertIs(type(new), RichDiceTable)
        self.assertEqual(new.get_dict(), {0: 1})
        self.assertEqual(new.get_list(), [])
        self.assertTrue(new.calc_includes_zeroes)

    def test_EventsFactory_from_dict_AdditiveEvents(self):
        events = AdditiveEvents.new()
        new_events = EventsFactory.from_dictionary(events, {1: 1})
        self.assertIs(type(new_events), AdditiveEvents)
        self.assertEqual(new_events.get_dict(), {1: 1})

    def test_EventsFactory_from_dict_DiceTable(self):
        events = DiceTable.new()
        new_events = EventsFactory.from_dictionary(events, {1: 1})
        self.assertIs(type(new_events), DiceTable)
        self.assertEqual(new_events.get_dict(), {1: 1})
        self.assertEqual(new_events.get_list(), [])

    def test_EventsFactory_from_dict_RichDiceTable(self):
        events = RichDiceTable.new()
        new_events = EventsFactory.from_dictionary(events, {1: 1})
        self.assertIs(type(new_events), RichDiceTable)
        self.assertEqual(new_events.get_dict(), {1: 1})
        self.assertEqual(new_events.get_list(), [])
        self.assertTrue(new_events.calc_includes_zeroes)

    def test_EventsFactory_from_dict_and_dice_DiceTable(self):
        events = DiceTable.new()
        new_events = EventsFactory.from_dictionary_and_dice(events, {1: 1}, [(Die(2), 2)])
        self.assertIs(type(new_events), DiceTable)
        self.assertEqual(new_events.get_dict(), {1: 1})
        self.assertEqual(new_events.get_list(), [(Die(2), 2)])

    def test_EventsFactory_from_dict__and_dice_RichDiceTable(self):
        events = RichDiceTable({2: 2}, [], False)
        new_events = EventsFactory.from_dictionary_and_dice(events, {1: 1}, [(Die(2), 2)])
        self.assertIs(type(new_events), RichDiceTable)
        self.assertEqual(new_events.get_dict(), {1: 1})
        self.assertEqual(new_events.get_list(), [(Die(2), 2)])
        self.assertFalse(new_events.calc_includes_zeroes)


def create_factory_string(new_classes=(), new_getters=()):
    getters = {'dictionary': Getter('get_dict', {0: 1}),
               'dice': Getter('get_dice_items', []),
               'calc_bool': Getter('calc_includes_zeroes', True, is_property=True)}

    classes = {'AdditiveEvents': ('dictionary',),
               'DiceTable': ('dictionary', 'dice'),
               'RichDiceTable': ('dictionary', 'dice', 'calc_bool')}
    for class_name, params in new_classes:
        classes[class_name] = params
    for param_name, getter in new_getters:
        getters[param_name] = getter
    indent = '    '
    out_str = 'CLASSES:\n'
    for key in sorted(classes.keys()):
        out_str += '{}{}: {}\n'.format(indent, key, classes[key])
    out_str += 'GETTERS:\n'
    for key in sorted(getters.keys()):
        out_str += '{}{}: {}\n'.format(indent, key, getters[key])
    return out_str.rstrip('\n')


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

