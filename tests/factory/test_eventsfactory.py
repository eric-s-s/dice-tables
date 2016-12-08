# pylint: disable=missing-docstring, invalid-name, too-many-public-methods
from __future__ import absolute_import

import unittest
import warnings
from sys import version_info
from itertools import cycle

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

    def assert_EventsFactoryError_code(self, error_code, func, *args):
        with self.assertRaises(EventsFactoryError) as cm:
            func(*args)
        error_msg = cm.exception.args[0]
        self.assertIn(error_code, error_msg)

    def test_assert_EventsFactoryError_code(self):
        def raise_events_factory_error(msg):
            raise EventsFactoryError(msg)
        self.assert_EventsFactoryError_code('RAISED', raise_events_factory_error, 'code: RAISED')

    @unittest.expectedFailure
    def test_assert_EventsFactoryError_code_wrong_code(self):
        def raise_events_factory_error(msg):
            raise EventsFactoryError(msg)
        self.assert_EventsFactoryError_code('wrong', raise_events_factory_error, 'code: RAISED')

    def assert_EventsFactoryWarning_code(self, code_list, func, *args):
        with warnings.catch_warnings(record=True) as cm:
            warnings.simplefilter("always")
            func(*args)
        self.assertEqual(len(cm), len(code_list))
        for caught in cm:
            self.assertEqual(caught.category, EventsFactoryWarning)
            msg = str(caught.message)
            self.assertTrue(any(code in msg for code in code_list))

    def assert_no_warning(self, func, *args):
        with warnings.catch_warnings(record=True) as cm:
            warnings.simplefilter("always")
            func(*args)
        if len(cm) != 0:
            self.fail('number of warnings: {}'.format(len(cm)))

    def test_assert_EventsFactoryWarning_code(self):
        def func(number):
            warnings.warn('msg\ncode: TEST', EventsFactoryWarning, stacklevel=2)
            return number
        self.assert_EventsFactoryWarning_code(['TEST'], func, 5)

    def test_assert_EventsFactoryWarning_code_multiple(self):
        def func(number):
            warnings.warn('msg\ncode: TEST', EventsFactoryWarning, stacklevel=2)
            warnings.warn('other\ncode: TEST2', EventsFactoryWarning, stacklevel=2)
            return number
        self.assert_EventsFactoryWarning_code(['TEST', 'TEST2'], func, 5)

    @unittest.expectedFailure
    def test_assert_EventsFactoryWarning_code_with_no_warning(self):
        def func(number):
            return number

        self.assert_EventsFactoryWarning_code(['TEST'], func, 5)

    @unittest.expectedFailure
    def test_assert_EventsFactoryWarning_code_with_too_many_warnings(self):
        def func(number):
            warnings.warn('code: TEST', EventsFactoryWarning, stacklevel=2)
            warnings.warn('code: OTHER', Warning, stacklevel=2)
            return number
        self.assert_EventsFactoryWarning_code(['TEST'], func, 5)

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
        class BadByClassPresentButDifferent(object):
            factory_keys = ('dice', )
        EventsFactory.add_class(BadByClassPresentButDifferent, ('dictionary',))

        class BadByBadKeyName(object):
            factory_keys = ('so very very wrong', )

        self.assert_EventsFactoryError_code('CLASS OVERWRITE',
                                            Loader(EventsFactory).load, BadByClassPresentButDifferent)
        self.assert_EventsFactoryError_code('MISSING GETTER',
                                            Loader(EventsFactory).load, BadByBadKeyName)

    def test_Loader_bad_new_keys_raises_EventsFactoryError(self):
        class Bob(object):
            factory_keys = ('dice',)
            new_keys = [('dice', 'get_dice', [1])]
        self.assert_EventsFactoryError_code('GETTER OVERWRITE', Loader(EventsFactory).load, Bob)

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

    def test_EventsFactory_get_class_params_raises_KeyError(self):
        class NoClass(object):
            pass
        self.assertRaises(KeyError, EventsFactory.get_class_params, NoClass)

    def test_EventsFactory_get_getter_string(self):
        get_dict = 'method: "get_dict", default: {0: 1}'
        self.assertEqual(EventsFactory.get_getter_string('dictionary'), get_dict)

    def test_EventsFactory_get_getter_string_raises_KeyError(self):
        self.assertRaises(KeyError, EventsFactory.get_getter_string, 'no_getter')

    def test_EventsFactory_get_keys(self):
        class X(object):
            pass
        classes = ['AdditiveEvents', 'DiceTable', 'RichDiceTable']
        getters = ['calc_bool', 'dice', 'dictionary']
        self.assertEqual(EventsFactory.get_keys(), (classes, getters))

        EventsFactory.add_class(X, ('dice', ))
        EventsFactory.add_getter('z', 'get', 0)
        classes.append('X')
        getters.append('z')
        self.assertEqual(EventsFactory.get_keys(), (classes, getters))

    def test_EventsFactory_reset(self):
        class Bob(object):
            pass
        EventsFactory.add_class(Bob, ('dictionary',))
        EventsFactory.add_getter('number', 'get_num', 0)
        self.assertTrue(EventsFactory.has_class(Bob))
        self.assertTrue(EventsFactory.has_getter('number'))
        EventsFactory.reset()
        default_classes = ['AdditiveEvents', 'DiceTable', 'RichDiceTable']
        default_getters = ['calc_bool', 'dice', 'dictionary']
        self.assertEqual(EventsFactory.get_keys(), (default_classes, default_getters))

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
        self.assert_EventsFactoryError_code('CLASS OVERWRITE', EventsFactory.add_class, AdditiveEvents, ('dice', ))

    def test_EventsFactory_add_class_factory_missing_getter_raises_EventsFactoryError(self):
        class Bob(object):
            pass
        self.assert_EventsFactoryError_code('MISSING GETTER', EventsFactory.add_class, Bob, ('not_there', ))

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
        self.assert_EventsFactoryError_code('GETTER OVERWRITE',
                                            EventsFactory.add_getter, 'dictionary', 'get_dict', {1: 1})
        self.assert_EventsFactoryError_code('GETTER OVERWRITE',
                                            EventsFactory.add_getter, 'dictionary', 'oops', {0: 1})

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
        self.assert_EventsFactoryWarning_code(['CHECK'], EventsFactory.check, NewDiceTableNewInitNoUpdate)

    def test_EventsFactory_check_error(self):
        class Bob(object):
            factory_keys = ('oops', )
        self.assert_EventsFactoryError_code('MISSING GETTER', EventsFactory.check, Bob)

    def test_EventsFactory_check_never_runs_loader_if_class_found(self):
        class Bob(object):
            factory_keys = ('will cause error', )
        EventsFactory.add_class(Bob, ('dice', ))
        self.assert_no_warning(EventsFactory.check, Bob)

    def test_EventsFactory_check_only_issues_warning_for_totally_unrelated_class(self):
        class Bob(object):
            pass
        self.assert_EventsFactoryWarning_code(['CHECK'], EventsFactory.check, Bob)

    def test_EventFactory_construction__class_in_defaults(self):
        self.assert_no_warning(EventsFactory.new, AdditiveEvents)
        test = EventsFactory.new(AdditiveEvents)
        self.assertIs(type(test), AdditiveEvents)
        self.assertEqual(test.get_dict(), {0: 1})

    def test_EventFactory_construction__new_class_added_and_called(self):
        class Bob(AdditiveEvents):
            pass
        EventsFactory.add_class(Bob, ('dictionary', ))
        self.assert_no_warning(EventsFactory.new, Bob)
        test = EventsFactory.new(Bob)
        self.assertIs(type(test), Bob)
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
        self.assert_EventsFactoryWarning_code(['CHECK', 'CONSTRUCT'], EventsFactory.new, NewDiceTableSameInitNoUpdate)
        test = EventsFactory.new(NewDiceTableSameInitNoUpdate)
        self.assertIs(type(test), NewDiceTableSameInitNoUpdate)
        self.assertEqual(test.get_dict(), {0: 1})

    def test_EventsFactory_construction__new_class_has_no_update_info_init_did_change(self):
        self.assert_EventsFactoryWarning_code(['CONSTRUCT'], EventsFactory.new, NewDiceTableNewInitNoUpdate)
        test = EventsFactory.new(NewDiceTableNewInitNoUpdate)
        self.assertIs(type(test), DiceTable)
        self.assertEqual(test.get_dict(), {0: 1})

    def test_EventsFactory_construction__bad_loader_info_ignored_if_class_already_in_factory(self):
        class Bob(object):
            factory_keys = ('whoopsy-doodle', )
            new_keys = [('wrong', ), ('very wrong', )]

            def __init__(self, num):
                self.num = num
        EventsFactory.add_getter('number', 'num', -5, 'property')
        EventsFactory.add_class(Bob, ('number', ))
        self.assert_no_warning(EventsFactory.new, Bob)
        test = EventsFactory.new(Bob)
        self.assertIs(type(test), Bob)
        self.assertEqual(test.num, -5)

    def test_EventsFactory_construction__totally_unrelated_object_with_no_loader_raises_EventsFactoryError(self):
        class Bob(object):
            pass
        self.assert_EventsFactoryError_code('WTF', EventsFactory.new, Bob)

    def test_EventsFactory_construction__new_class_bad_factory_keys_raises_EventsFactoryError(self):
        class BadLoaderKeys(AdditiveEvents):
            factory_keys = ('bad and wrong', )
        self.assert_EventsFactoryError_code('MISSING GETTER', EventsFactory.new, BadLoaderKeys)

    def test_EventsFactory_construction__new_class_bad_new_keys_raises_EventsFactoryError(self):
        class BadLoaderKeys(AdditiveEvents):
            factory_keys = ('dice', )
            new_keys = [('dice', 'get_dice', 5)]
        self.assert_EventsFactoryError_code('GETTER OVERWRITE', EventsFactory.new, BadLoaderKeys)

    def test_EventsFactory_construction__class_present_wrong_signature_wrong_param_EventsFactoryError(self):
        class Bob(AdditiveEvents):
            pass
        EventsFactory.add_class(Bob, ('dice', ))
        self.assert_EventsFactoryError_code('SIGNATURES DIFFERENT', EventsFactory.new, Bob)

    def test_EventsFactory_construction__class_present_different_signature_too_many_params_EventsFactoryError(self):
        class Bob(AdditiveEvents):
            pass
        EventsFactory.add_class(Bob, ('dictionary', 'dice'))
        self.assert_EventsFactoryError_code('SIGNATURES DIFFERENT', EventsFactory.new, Bob)

    def test_EventsFactory_construction__class_present_different_signature_too_few_params_EventsFactoryError(self):
        class Bob(DiceTable):
            pass
        EventsFactory.add_class(Bob, ('dictionary', ))
        self.assert_EventsFactoryError_code('SIGNATURES DIFFERENT', EventsFactory.new, Bob)

    def test_EventsFactory_construction__class_present_wrong_signature_wrong_order_EventsFactoryError(self):
        class Bob(DiceTable):
            pass
        EventsFactory.add_class(Bob, ('dice', 'dictionary'))
        self.assert_EventsFactoryError_code('SIGNATURES DIFFERENT', EventsFactory.new, Bob)

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

    def test_EventsFactory_from_dict_and_dice_RichDiceTable(self):
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

    def test_Events_Factory_warning_correct_message_raised_CHECK(self):
        will_warn_insert = 'TestEventsFactory.test_Events_Factory_warning_correct_message_raised_CHECK.<locals>.'
        if version_info[0] < 3:
            will_warn_insert = ''
        will_warn = 'tests.factory.test_eventsfactory.{}WillWarn'.format(will_warn_insert)
        expected = (
            'factory: <class \'dicetables.factory.eventsfactory.EventsFactory\'>\n' +
            'Warning code: CHECK\n' +
            'Failed to find/add the following class to the EventsFactory - \n' +
            'class: <class \'{}\'>\n'
            '\n' +
            'Warning raised while performing check at instantiation\n' +
            '\n' +
            'SOLUTION:\n' +
            '  class variable: factory_keys = (names of factory keys for getters)\n'
            '  current factory keys are: [\'calc_bool\', \'dice\', \'dictionary\']\n'
        )

        class WillWarn(DiceTable):
            pass
        self.assert_EventsFactoryWarning_code([expected.format(will_warn)], EventsFactory.check, WillWarn)

    def test_Events_Factory_warning_correct_message_CONSTRUCT(self):
        will_warn_insert = 'TestEventsFactory.test_Events_Factory_warning_correct_message_CONSTRUCT.<locals>.'
        if version_info[0] < 3:
            will_warn_insert = ''
        will_warn = 'tests.factory.test_eventsfactory.{}WillWarn'.format(will_warn_insert)

        expected = (
            'factory: <class \'dicetables.factory.eventsfactory.EventsFactory\'>\n' +
            'Warning code: CONSTRUCT\n' +
            'Failed to find/add the following class to the EventsFactory - \n' +
            'class: <class \'{}\'>\n' +
            '\n' +
            'Class found in factory: <class \'dicetables.dicetable.DiceTable\'>\n'
        )

        class WillWarn(DiceTable):
            pass
        self.assert_EventsFactoryWarning_code([expected.format(will_warn), 'CHECK'], EventsFactory.new, WillWarn)

    def test_Events_Factory_error_correct_message_CLASS_OVERWRITE(self):
        expected = (
            'Error Code: CLASS OVERWRITE\n' +
            'Factory:    <class \'dicetables.factory.eventsfactory.EventsFactory\'>\n' +
            'Error At:   <class \'dicetables.dicetable.DiceTable\'>\n' +
            '\n' +
            'Attempted to add class already in factory but used different factory keys.\n' +
            'Class: <class \'dicetables.dicetable.DiceTable\'>\n' +
            'Current Factory Keys: (\'dictionary\', \'dice\')\n' +
            'Keys Passed In:       (\'dice\',)\n'
        )
        self.assert_EventsFactoryError_code(expected, EventsFactory.add_class, DiceTable, ('dice',))

    def test_Events_Factory_error_correct_message_GETTER_OVERWRITE(self):
        expected = (
            'Error Code: GETTER OVERWRITE\n' +
            'Factory:    <class \'dicetables.factory.eventsfactory.EventsFactory\'>\n' +
            'Error At:   Factory Getter Key: \'dice\'\n' +
            '\n' +
            'Attempted to add getter key already in factory but used different parameters.\n' +
            'Key: \'dice\'\n' +
            'Factory Parameter:    method: "get_dice_items", default: []\n' +
            'Passed In Parameters: method: "get_dice", default: [(2, Die(6))]\n'
        )

        class Bob(object):
            factory_keys = ('dice', )
            new_keys = [('dice', 'get_dice', [(2, Die(6))], 'method')]
        self.assert_EventsFactoryError_code(expected, EventsFactory.new, Bob)

    def test_Events_Factory_error_correct_message_MISSING_GETTER(self):
        bob_insert = 'TestEventsFactory.test_Events_Factory_error_correct_message_MISSING_GETTER.<locals>.'
        if version_info[0] < 3:
            bob_insert = ''
        bob = 'tests.factory.test_eventsfactory.{}Bob'.format(bob_insert)
        expected = (
            'Error Code: MISSING GETTER\n' +
            'Factory:    <class \'dicetables.factory.eventsfactory.EventsFactory\'>\n' +
            'Error At:   <class \'{bob}\'>\n' +
            '\n' +
            'Attempted to add class with a getter key not in the factory.\n' +
            'Class: <class \'{bob}\'>\n' +
            'Current Factory Keys: [\'calc_bool\', \'dice\', \'dictionary\']\n' +
            'Key Passed In:        \'foo\'\n'
        )

        class Bob(object):
            factory_keys = ('dice', 'foo')
        self.assert_EventsFactoryError_code(expected.format(bob=bob), EventsFactory.new, Bob)

    def test_Events_Factory_error_correct_message_SIGNATURES_DIFFERENT(self):
        bob_insert = 'TestEventsFactory.test_Events_Factory_error_correct_message_SIGNATURES_DIFFERENT.<locals>.'
        if version_info[0] < 3:
            bob_insert = ''
        bob = 'tests.factory.test_eventsfactory.{}Bob'.format(bob_insert)
        expected = (
            'Error Code: SIGNATURES DIFFERENT\n' +
            'Factory:    <class \'dicetables.factory.eventsfactory.EventsFactory\'>\n' +
            'Error At:   <class \'{bob}\'>\n' +
            '\n' +
            'Attempted to construct a class already present in factory, but with a different signature.\n' +
            'Class: <class \'{bob}\'>\n' +
            'Signature In Factory: (\'dictionary\', \'dice\')\n' +
            'To reset the factory to its base state, use EventsFactory.reset()\n'
        )

        class Bob(object):
            def __init__(self, num):
                self.num = num
        EventsFactory.add_class(Bob, ('dictionary', 'dice'))
        self.assert_EventsFactoryError_code(expected.format(bob=bob), EventsFactory.new, Bob)

    def test_Events_Factory_error_correct_message_WTF(self):
        bob_insert = 'TestEventsFactory.test_Events_Factory_error_correct_message_WTF.<locals>.'
        if version_info[0] < 3:
            bob_insert = ''
        bob = 'tests.factory.test_eventsfactory.{}Bob'.format(bob_insert)
        expected = (
            'Error Code: WTF\n' +
            'Factory:    <class \'dicetables.factory.eventsfactory.EventsFactory\'>\n' +
            'Error At:   <class \'{bob}\'>\n' +
            '\n' +
            'Attempted to construct a class unrelated, in any way, to any class in the factory.\n' +
            'EventsFactory can currently construct the following classes:\n' +
            '[\'AdditiveEvents\', \'DiceTable\', \'RichDiceTable\']\n' +
            'EventsFactory searched the MRO of <class \'{bob}\'>,\n'
            + 'and found no matches to the classes in the factory.\n'
        )

        class Bob(object):
            pass
        self.assert_EventsFactoryError_code(expected.format(bob=bob), EventsFactory.new, Bob)

    def test_object_of_astonishing_idiocy(self):

        class DoubleTable(DiceTable):
            factory_keys = ('dictionary', 'second_dic', 'dice', 'dice_first')
            new_keys = [('second_dic', 'get_dict_alt', {0: 1}, 'method'),
                        ('dice_first', 'init_dice_first', True, 'method')]

            def __init__(self, dic1, dic2, dice, init_dice_first):
                if init_dice_first:
                    dice_dic = dic1
                    additive = dic2
                else:
                    dice_dic = dic2
                    additive = dic1
                self._dice_first = True
                self._additive = AdditiveEvents(additive)
                super(DoubleTable, self).__init__(dice_dic, dice)

            def get_dict(self):
                if not self._dice_first:
                    return self._additive.get_dict()
                return super(DoubleTable, self).get_dict()

            def get_dict_alt(self):
                if not self._dice_first:
                    return super(DoubleTable, self).get_dict()
                return self._additive.get_dict()

            def get_dict_items(self):
                return super(DoubleTable, self).get_dice_items()

            def init_dice_first(self):
                answer = self._dice_first
                self._dice_first = True
                return answer

            def combine(self, times, events):
                self._dice_first = False
                return super(DoubleTable, self).combine(times, events)

            def remove(self, times, events):
                self._dice_first = False
                return super(DoubleTable, self).remove(times, events)

        new = DoubleTable.new()
        d1 = new.add_die(1, Die(2))
        self.assertTrue(d1._dice_first)
        self.assertEqual(d1.get_dict(), {1: 1, 2: 1})
        self.assertEqual(d1.get_dict_alt(), {0: 1})
        d1_plus = d1.combine(1, Die(3))
        self.assertTrue(d1_plus._dice_first)
        self.assertEqual(d1_plus.get_dict(), {1: 1, 2: 1})
        self.assertEqual(d1_plus.get_dict_alt(), {1: 1, 2: 1, 3: 1})

    def test_deep_depths_of_dumbness(self):
        class DetachableDiceTable(DiceTable):
            factory_keys = ('dictionary', 'dice')
            lyrics = cycle((
                'I woke up this morning with a bad hangover and my {} was missing again.',
                'I can leave it home, when I think it\'s gonna get me in trouble,',
                'I really don\'t like being without my {} for too long. It makes me feel like less of a man,',
                'I saw my {} lying on a blanket next to a broken toaster oven. Some guy was selling it.',
                'I had to buy it off him. He wanted twenty-two bucks, but I talked him down to seventeen.',
                'People sometimes tell me I should get it permanently attached, but I don\'t know.',
                'Even though sometimes it\'s a pain in the ass, I like having a detachable {}.'
            ))

            def __init__(self, events_dict, dice_list):
                super(DetachableDiceTable, self).__init__(events_dict, dice_list)

            def detach(self, die):
                awesome_lyric = next(self.__class__.lyrics).format(die)
                times = self.number_of_dice(die)
                less_of_a_table = self.remove_die(times, die)
                detached = self.new().add_die(times, die)
                return awesome_lyric, detached, less_of_a_table

        new = DetachableDiceTable.new()
        two_d3 = new.add_die(2, Die(3))
        two_d3_three_d4 = two_d3.add_die(3, Die(4))
        two_d3_three_d4_four_d5 = two_d3_three_d4.add_die(4, Die(5))
        msg, detached_1, left = two_d3_three_d4_four_d5.detach(Die(5))
        self.assertEqual(msg, 'I woke up this morning with a bad hangover and my D5 was missing again.')
        self.assertIsInstance(detached_1, DetachableDiceTable)
        self.assertEqual(detached_1.get_dict(), DiceTable.new().add_die(4, Die(5)).get_dict())
        self.assertEqual(left.get_dict(), two_d3_three_d4.get_dict())
        msg2, empty, detached_2 = detached_1.detach(Die(100))
        self.assertEqual(msg2, 'I can leave it home, when I think it\'s gonna get me in trouble,')
        self.assertIsInstance(detached_2, DetachableDiceTable)
        self.assertEqual(detached_1.get_dict(), detached_2.get_dict())
        self.assertEqual(str(detached_1), '4D5')
        self.assertEqual(empty.get_dict(), {0: 1})

    def test_dangerous_inheritance(self):
        class NewFactory(EventsFactory):
            pass

        class Bob(object):
            pass

        NewFactory.add_class(Bob, ('dice', ))
        self.assertTrue(EventsFactory.has_class(Bob))

if __name__ == '__main__':
    unittest.main()
