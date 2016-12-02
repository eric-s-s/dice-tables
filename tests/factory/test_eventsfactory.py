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
from dicetables.factory.factoryerrorhandler import EventsFactoryError
from dicetables.factory.factorywarninghandler import EventsFactoryWarning


class Dummy(object):
    factory_keys = ('number', 'dice', 'dictionary')
    new_keys = [('number', 'get_num', 0)]

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


class NewDiceTableSameInitNoUpdate(DiceTable):
    def __init__(self, event_dic, dice):
        super(NewDiceTableSameInitNoUpdate, self).__init__(event_dic, dice)


class NewDiceTableSameInitUpdate(DiceTable):
    factory_keys = ('dictionary', 'dice')

    def __init__(self, event_dic, dice):
        super(NewDiceTableSameInitUpdate, self).__init__(event_dic, dice)


class NewDiceTableNewInitNoUpdate(DiceTable):
    def __init__(self, event_dic, dice, number):
        self.number = number
        super(NewDiceTableNewInitNoUpdate, self).__init__(event_dic, dice)


class NewDiceTableNewInitUpdate(DiceTable):
    factory_keys = ('dictionary', 'dice', 'number')
    new_keys = [('number', 'number', 0, 'property')]

    def __init__(self, event_dic, dice, number):
        self.number = number
        super(NewDiceTableNewInitUpdate, self).__init__(event_dic, dice)


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

    def test_Getter_eq_true(self):
        getter1 = Getter('get_num', 0)
        getter2 = Getter('get_num', 0)
        self.assertTrue(getter1 == getter2)

    def test_Getter_eq_false_by_default(self):
        getter1 = Getter('get_num', 0)
        getter2 = Getter('get_num', '0')
        self.assertFalse(getter1 == getter2)

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

    def test_EventsFactory_has_class_true(self):
        EventsFactory.reset()
        self.assertTrue(EventsFactory.has_class(AdditiveEvents))

    def test_EventsFactory_has_class_false(self):
        EventsFactory.reset()
        self.assertFalse(EventsFactory.has_class(float))

    def test_EventsFactory_has_getter_true(self):
        EventsFactory.reset()
        self.assertTrue(EventsFactory.has_getter('dictionary'))

    def test_EventsFactory_has_getter_false(self):
        EventsFactory.reset()
        self.assertFalse(EventsFactory.has_getter('not_there'))

    def test_EventsFactory_get_class_params(self):
        self.assertEqual(EventsFactory.get_class_params(AdditiveEvents), ('dictionary', ))

    def test_EventsFactory_get_class_raises_KeyError(self):
        class NoClass(object):
            pass

        self.assertRaises(KeyError, EventsFactory.get_class_params, NoClass)

    def test_EventsFactory_get_getter_string(self):
        get_dict = 'method: "get_dict", default: {0: 1}'
        self.assertEqual(EventsFactory.get_getter_string('dictionary'), get_dict)

    def test_EventsFactory_get_getter_string_raises_KeyError(self):
        self.assertRaises(KeyError, EventsFactory.get_getter_string, 'no_getter')

    def test_EventsFactory_reset(self):
        EventsFactory.reset()
        EventsFactory.add_class(Dummy, ('dictionary',))
        EventsFactory.add_getter('number', 'get_num', 0)
        self.assertTrue(EventsFactory.has_class(Dummy))
        self.assertTrue(EventsFactory.has_getter('number'))

        EventsFactory.reset()
        not_there = [Dummy, NewDiceTableSameInitNoUpdate, NewDiceTableSameInitUpdate,
                     NewDiceTableNewInitNoUpdate, NewDiceTableNewInitUpdate]
        for absent_class in not_there:
            self.assertFalse(EventsFactory.has_class(absent_class))

        self.assertFalse(EventsFactory.has_getter('number'))
        for preset in [AdditiveEvents, DiceTable, RichDiceTable]:
            self.assertTrue(EventsFactory.has_class(preset))
        for getter_key in ['dictionary', 'dice', 'calc_bool']:
            self.assertTrue(EventsFactory.has_getter(getter_key))

    def test_EventsFactory_add_class(self):
        class Bob(object):
            pass

        EventsFactory.reset()
        EventsFactory.add_class(Bob, ('dictionary',))
        self.assertTrue(EventsFactory.has_class(Bob))
        self.assertEqual(EventsFactory.get_class_params(Bob), ('dictionary',))

    def test_EventsFactory_add_class_already_has_class_does_not_change(self):
        self.assertTrue(EventsFactory.has_class(AdditiveEvents))
        self.assertEqual(EventsFactory.get_class_params(AdditiveEvents), ('dictionary', ))
        EventsFactory.add_class(AdditiveEvents, ('dictionary',))
        self.assertTrue(EventsFactory.has_class(AdditiveEvents))
        self.assertEqual(EventsFactory.get_class_params(AdditiveEvents), ('dictionary',))

    def test_EventsFactory_add_class_already_has_class_raises_EventsFactoryError(self):
        self.assertRaises(EventsFactoryError, EventsFactory.add_class, AdditiveEvents, ('dice', ))

    def test_EventsFactory_add_class_factory_missing_getter_raises_EventsFactoryError(self):
        class Bob(object):
            pass

        EventsFactory.reset()
        self.assertRaises(EventsFactoryError, EventsFactory.add_class, Bob, ('not_there', ))

    def test_EventsFactory_add_getter_new_method(self):
        EventsFactory.reset()
        EventsFactory.add_getter('number', 'get_num', 0)
        self.assertEqual(EventsFactory.get_getter_string('number'), 'method: "get_num", default: 0')

    def test_EventsFactory_add_getter_new_property(self):
        EventsFactory.reset()
        EventsFactory.add_getter('number', 'get_num', 0, type_str='property')
        self.assertEqual(EventsFactory.get_getter_string('number'), 'property: "get_num", default: 0')

    def test_EventsFactory_add_getter_already_there_does_nothing(self):
        EventsFactory.reset()
        EventsFactory.add_getter('dictionary', 'get_dict', {0: 1})
        self.assertEqual(EventsFactory.get_getter_string('dictionary'), 'method: "get_dict", default: {0: 1}')

    def test_EventsFactory_add_getter_already_not_equal_raises_error(self):
        EventsFactory.reset()
        self.assertRaises(EventsFactoryError, EventsFactory.add_getter, 'dictionary', 'get_dict', {1: 1})

    def test_EventsFactory_check_no_errors_or_warnings(self):
        self.assert_no_warning(EventsFactory.check, AdditiveEvents)

    def test_EventsFactory_check_no_errors_or_warnings_because_load(self):
        EventsFactory.reset()
        self.assert_no_warning(EventsFactory.check, NewDiceTableSameInitUpdate)
        self.assertTrue(EventsFactory.has_class(NewDiceTableSameInitUpdate))

    def test_EventsFactory_check_raises_warning(self):
        msg = ("factory: <class 'dicetables.factory.eventsfactory.EventsFactory'>, " +
               "code: CHECK, params: ['NewDiceTableNewInitNoUpdate']")
        self.assert_warning(EventsFactoryWarning, msg, EventsFactory.check, NewDiceTableNewInitNoUpdate)

    def test_EventsFactory_check_error(self):
        class Bob(object):
            factory_keys = ('dice', )
        EventsFactory.reset()
        EventsFactory.add_class(Bob, ('dictionary', ))
        self.assertRaises(EventsFactoryError, EventsFactory.check(Bob))

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

    def test_EventsFactory_new_has_update_info(self):
        EventsFactory.reset()
        self.assert_no_warning(EventsFactory.new, NewDiceTableSameInitUpdate)
        new = EventsFactory.new(NewDiceTableSameInitUpdate)
        self.assertEqual(new.__class__, NewDiceTableSameInitUpdate)
        self.assertEqual(new.get_dict(), {0: 1})
        self.assertEqual(new.get_list(), [])

# TODO here
    def test_warning(self):
        NewDiceTableSameInitNoUpdate({1: 1}, [])

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

