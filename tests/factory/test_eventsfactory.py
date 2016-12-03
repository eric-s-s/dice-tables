# pylint: disable=missing-docstring, invalid-name, too-many-public-methods
"""tests for the baseevents.py module"""
from __future__ import absolute_import

import unittest
import warnings
from sys import version_info

from dicetables.baseevents import AdditiveEvents
from dicetables.dicetable import DiceTable, RichDiceTable
from dicetables.dieevents import Die
from dicetables.factory.eventsfactory import EventsFactory, Getter, Loader, LoaderError
from dicetables.factory.factoryerrorhandler import EventsFactoryError
from dicetables.factory.factorywarninghandler import EventsFactoryWarning


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
    def setUp(self):
        EventsFactory.reset()

    def assert_my_regex(self, error_type, regex, func, *args):
        with self.assertRaises(error_type) as cm:
            func(*args)
        error_msg = str(cm.exception)
        self.assertEqual(error_msg, regex)

    def test_assert_my_regex(self):
        self.assert_my_regex(ValueError, "invalid literal for int() with base 10: 'a'", int, 'a')

    def assert_warning(self, warning_list, msg_list, func, *args):
        with warnings.catch_warnings(record=True) as cm:
            warnings.simplefilter("always")
            func(*args)
        for warn in cm:
            print(warn.message)
        if len(cm) != len(warning_list):
            self.fail('Wrong number of warnings: {}'.format(len(cm)))
        else:
            for caught in cm:
                self.assertIn(caught.category, warning_list)
                self.assertIn(str(caught.message), msg_list)

    def assert_no_warning(self, func, *args):
        with warnings.catch_warnings(record=True) as cm:
            warnings.simplefilter("always")
            func(*args)
        if len(cm) != 0:
            self.fail('number of warnings: {}'.format(len(cm)))

    def test_assert_warning(self):
        def func(number):
            warnings.warn('msg', EventsFactoryWarning, stacklevel=2)
            return number
        self.assert_warning([EventsFactoryWarning], ['msg'], func, 5)

    def test_assert_warning_multiple(self):
        def func(number):
            warnings.warn('msg', EventsFactoryWarning, stacklevel=2)
            warnings.warn('other', SyntaxWarning, stacklevel=2)
            return number
        self.assert_warning([EventsFactoryWarning, SyntaxWarning], ['msg', 'other'], func, 5)

    def test_assert_warning_with_no_warning(self):
        def func(number):
            return number
        with self.assertRaises(AssertionError) as cm:
            self.assert_warning([EventsFactoryWarning], ['hi'], func, 5)
        self.assertEqual(cm.exception.args[0], 'Wrong number of warnings: 0')

    def test_assert_warning_with_too_many_warnings(self):
        def func(number):
            warnings.warn('msg', EventsFactoryWarning, stacklevel=2)
            warnings.warn('msg', Warning, stacklevel=2)
            return number
        with self.assertRaises(AssertionError) as cm:
            self.assert_warning([EventsFactoryWarning], ['hi'], func, 5)
        self.assertEqual(cm.exception.args[0], 'Wrong number of warnings: 2')

    def test_assert_no_warning_with_no_warning(self):
        def func(number):
            return number
        self.assert_no_warning(func, 5)

    @unittest.expectedFailure
    def test_assert_no_warning_with_warning(self):
        def func(number):
            warnings.warn('msg', EventsFactoryWarning, stacklevel=2)
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

    def test_Loader_no_factory_keys_raises_LoaderError(self):
        self.assertRaises(LoaderError, Loader(EventsFactory).load, NewDiceTableSameInitNoUpdate)

    def test_Loader_bad_factory_keys_raises_EventsFactoryError(self):
        class Bob(object):
            factory_keys = ('dice', )
        EventsFactory.add_class(Bob, ('dictionary', ))
        self.assertRaises(EventsFactoryError, Loader(EventsFactory).load, Bob)

    def test_Loader_bad_new_keys_raises_EventsFactoryError(self):
        class Bob(object):
            factory_keys = ('dice',)
            new_keys = [('dice', 'get_dice', [1])]

        self.assertRaises(EventsFactoryError, Loader(EventsFactory).load, Bob)

    def test_Loader_class_already_present(self):
        class Bob(object):
            factory_keys = ('dice',)
        EventsFactory.add_class(Bob, ('dice', ))
        self.assertTrue(EventsFactory.has_class(Bob))
        self.assertIsNone(Loader(EventsFactory).load(Bob))
        self.assertTrue(EventsFactory.has_class(Bob))

    def test_Loader_no_new_keys(self):
        class Bob(object):
            factory_keys = ('dice',)
        self.assertFalse(EventsFactory.has_class(Bob))
        Loader(EventsFactory).load(Bob)
        self.assertTrue(EventsFactory.has_class(Bob))

    def test_Loader_new_keys(self):
        class Bob(object):
            factory_keys = ('my_method', 'my_property')
            new_keys = [('my_method', 'get_method', 5), ('my_property', 'my_property', 'a', 'property')]
        Loader(EventsFactory).load(Bob)
        self.assertTrue(EventsFactory.get_class_params(Bob), ('my_method', 'my_property'))
        self.assertEqual(EventsFactory.get_getter_string('my_method'), 'method: "get_method", default: 5')
        self.assertEqual(EventsFactory.get_getter_string('my_property'), 'property: "my_property", default: \'a\'')

    def test_EventsFactory_has_class_true(self):
        self.assertTrue(EventsFactory.has_class(AdditiveEvents))

    def test_EventsFactory_has_class_false(self):
        self.assertFalse(EventsFactory.has_class(float))

    def test_EventsFactory_has_getter_true(self):
        self.assertTrue(EventsFactory.has_getter('dictionary'))

    def test_EventsFactory_has_getter_false(self):
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
        class Bob(object):
            pass
        EventsFactory.add_class(Bob, ('dictionary',))
        EventsFactory.add_getter('number', 'get_num', 0)
        self.assertTrue(EventsFactory.has_class(Bob))
        self.assertTrue(EventsFactory.has_getter('number'))

        EventsFactory.reset()
        not_there = [Bob, NewDiceTableSameInitNoUpdate, NewDiceTableSameInitUpdate,
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

        self.assertRaises(EventsFactoryError, EventsFactory.add_class, Bob, ('not_there', ))

    def test_EventsFactory_add_getter_new_method(self):
        EventsFactory.add_getter('number', 'get_num', 0)
        self.assertEqual(EventsFactory.get_getter_string('number'), 'method: "get_num", default: 0')

    def test_EventsFactory_add_getter_new_property(self):
        EventsFactory.add_getter('number', 'get_num', 0, type_str='property')
        self.assertEqual(EventsFactory.get_getter_string('number'), 'property: "get_num", default: 0')

    def test_EventsFactory_add_getter_already_there_does_nothing(self):
        EventsFactory.add_getter('dictionary', 'get_dict', {0: 1})
        self.assertEqual(EventsFactory.get_getter_string('dictionary'), 'method: "get_dict", default: {0: 1}')

    def test_EventsFactory_add_getter_already_not_equal_raises_error(self):
        self.assertRaises(EventsFactoryError, EventsFactory.add_getter, 'dictionary', 'get_dict', {1: 1})

    def test_EventsFactory_check_no_errors_or_warnings(self):
        self.assert_no_warning(EventsFactory.check, AdditiveEvents)

    def test_EventsFactory_check_no_errors_or_warnings_because_load(self):
        self.assert_no_warning(EventsFactory.check, NewDiceTableSameInitUpdate)

    def test_EventsFactory_check_no_errors_or_warnings_because_load_new_init(self):
        self.assert_no_warning(EventsFactory.check, NewDiceTableNewInitUpdate)

    def test_EventsFactory_check_adds_class_to_factory(self):
        self.assertFalse(EventsFactory.has_class(NewDiceTableNewInitUpdate))
        self.assert_no_warning(EventsFactory.check, NewDiceTableNewInitUpdate)
        self.assertTrue(EventsFactory.has_class(NewDiceTableNewInitUpdate))

    def test_EventsFactory_check_raises_warning(self):
        msg = ("factory: <class 'dicetables.factory.eventsfactory.EventsFactory'>, " +
               "code: CHECK, params: ['NewDiceTableNewInitNoUpdate']")
        self.assert_warning([EventsFactoryWarning], [msg], EventsFactory.check, NewDiceTableNewInitNoUpdate)

    def test_EventsFactory_check_error(self):
        class Bob(object):
            factory_keys = ('oops', )
        self.assertRaises(EventsFactoryError, EventsFactory.check, Bob)

    def test_EventsFactory_check_never_runs_loader_if_class_found(self):
        class Bob(object):
            factory_keys = ('will cause error', )
        EventsFactory.add_class(Bob, ('dice', ))
        self.assert_no_warning(EventsFactory.check, Bob)

    def test_EventsFactory_check_only_issues_warning_for_totally_unrelated_class(self):
        class Bob(object):
            pass
        msg = ("factory: <class 'dicetables.factory.eventsfactory.EventsFactory'>, " +
               "code: CHECK, params: ['Bob']")
        self.assert_warning([EventsFactoryWarning], [msg], EventsFactory.check, Bob)

    def test_EventFactory_construction__class_in_defaults(self):
        self.assert_no_warning(EventsFactory.new, AdditiveEvents)
        test = EventsFactory.new(AdditiveEvents)
        self.assertIs(type(test), AdditiveEvents)
        self.assertEqual(test.get_dict(), {0: 1})

    def test_EventsFactory_construction__new_class_has_update_info_init_did_not_change(self):
        self.assert_no_warning(EventsFactory.new, NewDiceTableSameInitUpdate)
        test = EventsFactory.new(NewDiceTableSameInitUpdate)
        self.assertIs(type(test), NewDiceTableSameInitUpdate)
        self.assertEqual(test.get_dict(), {0: 1})
        self.assertEqual(test.get_list(), [])

    def test_EventsFactory_construction__new_class_has_update_info_init_did_change(self):
        self.assert_no_warning(EventsFactory.new, NewDiceTableNewInitUpdate)
        test = EventsFactory.new(NewDiceTableNewInitUpdate)
        self.assertIs(type(test), NewDiceTableNewInitUpdate)
        self.assertEqual(test.get_dict(), {0: 1})
        self.assertEqual(test.get_list(), [])
        self.assertEqual(test.number, 0)

    def test_EventsFactory_construction__new_class_has_no_update_info_init_did_not_change(self):
        msg1 = ("factory: <class 'dicetables.factory.eventsfactory.EventsFactory'>, code: CONSTRUCT, " +
                "params: ['NewDiceTableSameInitNoUpdate', 'DiceTable']")
        msg2 = ("factory: <class 'dicetables.factory.eventsfactory.EventsFactory'>, " +
                "code: CHECK, params: ['NewDiceTableSameInitNoUpdate']")
        self.assert_warning([EventsFactoryWarning, EventsFactoryWarning], [msg1, msg2],
                            EventsFactory.new, NewDiceTableSameInitNoUpdate)
        test = EventsFactory.new(NewDiceTableSameInitNoUpdate)
        self.assertIs(type(test), NewDiceTableSameInitNoUpdate)
        self.assertEqual(test.get_dict(), {0: 1})

    def test_EventsFactory_construction__new_class_has_no_update_info_init_did_change(self):
        msg1 = ("factory: <class 'dicetables.factory.eventsfactory.EventsFactory'>, code: CONSTRUCT, " +
                "params: ['NewDiceTableNewInitNoUpdate', 'DiceTable']")
        self.assert_warning([EventsFactoryWarning], [msg1],
                            EventsFactory.new, NewDiceTableNewInitNoUpdate)
        test = EventsFactory.new(NewDiceTableNewInitNoUpdate)
        self.assertIs(type(test), DiceTable)
        self.assertEqual(test.get_dict(), {0: 1})

    def test_EventsFactory_construction__bad_loader_ignored_if_class_already_in_factory(self):
        class Bob(object):
            factory_keys = ('whoopsy-doodle', )

            def __init__(self, num):
                self.num = num
        EventsFactory.add_getter('number', 'num', -5, 'property')
        EventsFactory.add_class(Bob, ('number', ))
        self.assert_no_warning(EventsFactory.new, Bob)
        test = EventsFactory.new(Bob)
        self.assertIs(type(test), Bob)
        self.assertEqual(test.num, -5)

    def test_EventsFactory_construction__raises_error_for_totally_unrelated_object_with_no_loader(self):
        class Bob(object):
            pass
        self.assertRaises(EventsFactoryError, EventsFactory.new, Bob)

    def test_EventsFactory_construction__raises_error_for_class_not_in_factory_and_bad_loader_keys(self):
        class BadLoaderKeys(AdditiveEvents):
            factory_keys = ('bad and wrong', )
        self.assertRaises(EventsFactoryError, EventsFactory.new, BadLoaderKeys)

    def test_EventsFactory_construction__raises_error_for_class_not_in_factory_and_bad_new_keys(self):
        class BadLoaderKeys(AdditiveEvents):
            factory_keys = ('dice', )
            new_keys = [('dice', 'get_dice', 5)]
        self.assertRaises(EventsFactoryError, EventsFactory.new, BadLoaderKeys)

#TODO HERE

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

    def test_EventsFactory_from_params(self):
        start_dict = {2: 2}
        new_dict = {1: 1}
        start_dice = [(Die(2), 1)]
        new_dice = [(Die(3), 3)]
        start_num = 5
        new_num = 10

        start = NewDiceTableNewInitUpdate(start_dict, start_dice, start_num)
        new_events1 = EventsFactory.from_params(start, {'number': new_num, 'dice': new_dice})
        self.assertEqual(new_events1.get_dict(), start_dict)
        self.assertEqual(new_events1.get_list(), new_dice)
        self.assertEqual(new_events1.number, new_num)

        new_events2 = EventsFactory.from_params(start, {'dictionary': new_dict})
        self.assertEqual(new_events2.get_dict(), new_dict)
        self.assertEqual(new_events2.get_list(), start_dice)
        self.assertEqual(new_events2.number, start_num)

        self.assertIs(type(new_events1), NewDiceTableNewInitUpdate)
        self.assertIs(type(new_events2), NewDiceTableNewInitUpdate)


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

