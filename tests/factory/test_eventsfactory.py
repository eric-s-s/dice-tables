# pylint: disable=missing-docstring, invalid-name, too-many-public-methods
from __future__ import absolute_import

import unittest
import warnings
from itertools import cycle
from sys import version_info

from dicetables.additiveevents import AdditiveEvents
from dicetables.dicerecord import DiceRecord
from dicetables.dicetable import DiceTable, DetailedDiceTable
from dicetables.dieevents import Die
from dicetables.factory.errorhandler import EventsFactoryError
from dicetables.factory.eventsfactory import EventsFactory, Loader, LoaderError
from dicetables.factory.warninghandler import EventsFactoryWarning
from dicetables.tools.dictcombiner import DictCombiner


class NewDiceTableSameInitNoUpdate(DiceTable):
    def __init__(self, event_dic, dice):
        super(NewDiceTableSameInitNoUpdate, self).__init__(event_dic, dice)


class NewDiceTableSameInitUpdate(DiceTable):
    factory_keys = ('get_dict', 'dice_data')

    def __init__(self, event_dic, dice):
        super(NewDiceTableSameInitUpdate, self).__init__(event_dic, dice)


class NewDiceTableNewInitNoUpdate(DiceTable):
    def __init__(self, event_dic, dice, number):
        self.number = number
        super(NewDiceTableNewInitNoUpdate, self).__init__(event_dic, dice)


class NewDiceTableNewInitUpdate(DiceTable):
    factory_keys = ('get_dict', 'dice_data', 'number')
    new_keys = [('number', 0, 'property')]

    def __init__(self, event_dic, dice, number):
        self.number = number
        super(NewDiceTableNewInitUpdate, self).__init__(event_dic, dice)


class TestEventsFactory(unittest.TestCase):
    def setUp(self):
        EventsFactory.reset()

    def assert_EventsFactoryError_contains(self, phrases_tuple, func, *args):
        with self.assertRaises(EventsFactoryError) as cm:
            func(*args)
        error_msg = cm.exception.args[0]
        for phrase in phrases_tuple:
            self.assertIn(phrase, error_msg)

    def assert_EventsFactoryError_code(self, error_code, func, *args):
        self.assert_EventsFactoryError_contains((error_code,), func, *args)

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

    def test_assert_EventsFactoryError_contains(self):
        def raise_events_factory_error(msg):
            raise EventsFactoryError(msg)

        self.assert_EventsFactoryError_contains(('a', 'b', 'c'), raise_events_factory_error, 'abcd')

    @unittest.expectedFailure
    def test_assert_EventsFactoryError_contains_fail(self):
        def raise_events_factory_error(msg):
            raise EventsFactoryError(msg)

        self.assert_EventsFactoryError_contains(('a', 'b', 'e'), raise_events_factory_error, 'abcd')

    def test_assert_EventsFactoryError_code(self):
        def raise_events_factory_error(msg):
            raise EventsFactoryError(msg)

        self.assert_EventsFactoryError_code('RAISED', raise_events_factory_error, 'code: RAISED')

    @unittest.expectedFailure
    def test_assert_EventsFactoryError_code_wrong_code(self):
        def raise_events_factory_error(msg):
            raise EventsFactoryError(msg)

        self.assert_EventsFactoryError_code('wrong', raise_events_factory_error, 'code: RAISED')

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

    def test_Loader_no_factory_keys_raises_LoaderError(self):
        self.assertRaises(LoaderError, Loader(EventsFactory).load, NewDiceTableSameInitNoUpdate)

    def test_Loader_bad_factory_keys_raises_EventsFactoryError(self):
        class BadByClassPresentButDifferent(object):
            factory_keys = ('dice_data',)

        EventsFactory.add_class(BadByClassPresentButDifferent, ('get_dict',))

        class BadByBadKeyName(object):
            factory_keys = ('so very very wrong',)

        self.assert_EventsFactoryError_code('CLASS OVERWRITE',
                                            Loader(EventsFactory).load, BadByClassPresentButDifferent)
        self.assert_EventsFactoryError_code('MISSING GETTER',
                                            Loader(EventsFactory).load, BadByBadKeyName)

    def test_Loader_bad_new_keys_raises_EventsFactoryError(self):
        class Bob(object):
            factory_keys = ('dice_data',)
            new_keys = [('dice_data', 'get_dice', [1])]

        self.assert_EventsFactoryError_code('GETTER OVERWRITE', Loader(EventsFactory).load, Bob)

    def test_Loader_class_already_present(self):
        class Bob(object):
            factory_keys = ('dice_data',)

        EventsFactory.add_class(Bob, ('dice_data',))
        self.assertTrue(EventsFactory.has_class(Bob))
        self.assertIsNone(Loader(EventsFactory).load(Bob))
        self.assertTrue(EventsFactory.has_class(Bob))

    def test_Loader_no_new_keys(self):
        class Bob(object):
            factory_keys = ('dice_data',)

        self.assertFalse(EventsFactory.has_class(Bob))
        Loader(EventsFactory).load(Bob)
        self.assertTrue(EventsFactory.has_class(Bob))

    def test_Loader_new_keys(self):
        class Bob(object):
            factory_keys = ('my_method', 'my_property')
            new_keys = [('my_method', 5), ('my_property', 'a', 'property')]

        Loader(EventsFactory).load(Bob)
        self.assertTrue(EventsFactory.get_class_params(Bob), ('my_method', 'my_property'))
        self.assertEqual(EventsFactory.get_getter_string('my_method'), 'method: "my_method", default: 5')
        self.assertEqual(EventsFactory.get_getter_string('my_property'), 'property: "my_property", default: \'a\'')

    def test_EventsFactory_has_class_true(self):
        self.assertTrue(EventsFactory.has_class(AdditiveEvents))

    def test_EventsFactory_has_class_false(self):
        self.assertFalse(EventsFactory.has_class(float))

    def test_EventsFactory_has_getter_true(self):
        self.assertTrue(EventsFactory.has_getter('get_dict'))

    def test_EventsFactory_has_getter_false(self):
        self.assertFalse(EventsFactory.has_getter('not_there'))

    def test_EventsFactory_get_class_params(self):
        self.assertEqual(EventsFactory.get_class_params(AdditiveEvents), ('get_dict',))

    def test_EventsFactory_get_class_params_no_class(self):
        self.assertIsNone(EventsFactory.get_class_params(int))

    def test_EventsFactory_get_getter_string(self):
        get_dict = 'method: "get_dict", default: {0: 1}'
        self.assertEqual(EventsFactory.get_getter_string('get_dict'), get_dict)

    def test_EventsFactory_get_getter_string_no_getters(self):
        self.assertEqual(EventsFactory.get_getter_string('not_there'), 'None')

    def test_EventsFactory_get_keys(self):
        class X(object):
            pass

        classes = ['AdditiveEvents', 'DetailedDiceTable', 'DiceTable']
        getters = ['calc_includes_zeroes', 'dice_data', 'get_dict']
        self.assertEqual(EventsFactory.get_keys(), (classes, getters))

        EventsFactory.add_class(X, ('dice_data',))
        EventsFactory.add_getter('z', 'get', 0)
        classes.append('X')
        getters.append('z')
        self.assertEqual(EventsFactory.get_keys(), (classes, getters))

    def test_EventsFactory_reset(self):
        class Bob(object):
            pass

        EventsFactory.add_class(Bob, ('get_dict',))
        EventsFactory.add_getter('number', 'get_num', 0)
        self.assertTrue(EventsFactory.has_class(Bob))
        self.assertTrue(EventsFactory.has_getter('number'))
        EventsFactory.reset()
        default_classes = ['AdditiveEvents', 'DetailedDiceTable', 'DiceTable']
        default_getters = ['calc_includes_zeroes', 'dice_data', 'get_dict']
        self.assertEqual(EventsFactory.get_keys(), (default_classes, default_getters))

    def test_EventsFactory_add_class(self):
        class Bob(object):
            pass

        self.assertFalse(EventsFactory.has_class(Bob))
        EventsFactory.add_class(Bob, ('get_dict',))
        self.assertTrue(EventsFactory.has_class(Bob))
        self.assertEqual(EventsFactory.get_class_params(Bob), ('get_dict',))

    def test_EventsFactory_add_class_already_has_class_does_not_change(self):
        self.assertTrue(EventsFactory.has_class(AdditiveEvents))
        self.assertEqual(EventsFactory.get_class_params(AdditiveEvents), ('get_dict',))
        EventsFactory.add_class(AdditiveEvents, ('get_dict',))
        self.assertTrue(EventsFactory.has_class(AdditiveEvents))
        self.assertEqual(EventsFactory.get_class_params(AdditiveEvents), ('get_dict',))

    def test_EventsFactory_add_class_already_has_class_raises_EventsFactoryError(self):
        self.assert_EventsFactoryError_code('CLASS OVERWRITE', EventsFactory.add_class, AdditiveEvents, ('dice_data',))

    def test_EventsFactory_add_class_factory_missing_getter_raises_EventsFactoryError(self):
        class Bob(object):
            pass

        self.assert_EventsFactoryError_code('MISSING GETTER', EventsFactory.add_class, Bob, ('not_there',))

    def test_EventsFactory_add_getter_new_method(self):
        EventsFactory.add_getter('get_num', 0)
        self.assertEqual(EventsFactory.get_getter_string('get_num'), 'method: "get_num", default: 0')

    def test_EventsFactory_add_getter_new_property(self):
        EventsFactory.add_getter('get_num', 0, type_str='property')
        self.assertEqual(EventsFactory.get_getter_string('get_num'), 'property: "get_num", default: 0')

    def test_EventsFactory_add_getter_already_there_does_nothing(self):
        EventsFactory.add_getter('get_dict', {0: 1})
        self.assertEqual(EventsFactory.get_getter_string('get_dict'), 'method: "get_dict", default: {0: 1}')

    def test_EventsFactory_add_getter_already_not_equal_raises_error(self):
        self.assert_EventsFactoryError_code('GETTER OVERWRITE',
                                            EventsFactory.add_getter, 'get_dict', {1: 1})
        self.assert_EventsFactoryError_code('GETTER OVERWRITE',
                                            EventsFactory.add_getter, 'get_dict', {0: 1}, 'property')

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
            factory_keys = ('oops',)

        self.assert_EventsFactoryError_code('MISSING GETTER', EventsFactory.check, Bob)

    def test_EventsFactory_check_never_runs_loader_if_class_found(self):
        class Bob(object):
            factory_keys = ('will cause error',)

        EventsFactory.add_class(Bob, ('dice_data',))
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

        EventsFactory.add_class(Bob, ('get_dict',))
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
            factory_keys = ('whoopsy-doodle',)
            new_keys = [('wrong',), ('very wrong',)]

            def __init__(self, num):
                self.num = num

        EventsFactory.add_getter('num', -5, 'property')
        EventsFactory.add_class(Bob, ('num',))
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
            factory_keys = ('bad and wrong',)

        self.assert_EventsFactoryError_code('MISSING GETTER', EventsFactory.new, BadLoaderKeys)

    def test_EventsFactory_construction__new_class_bad_new_keys_raises_EventsFactoryError(self):
        class BadLoaderKeys(AdditiveEvents):
            factory_keys = ('dice_data',)
            new_keys = [('dice_data', 5)]

        self.assert_EventsFactoryError_code('GETTER OVERWRITE', EventsFactory.new, BadLoaderKeys)

    def test_EventsFactory_construction__class_present_wrong_signature_wrong_param_EventsFactoryError(self):
        class Bob(AdditiveEvents):
            pass

        EventsFactory.add_class(Bob, ('dice_data',))
        self.assert_EventsFactoryError_code('SIGNATURES DIFFERENT', EventsFactory.new, Bob)

    def test_EventsFactory_construction__class_present_different_signature_too_many_params_EventsFactoryError(self):
        class Bob(AdditiveEvents):
            pass

        EventsFactory.add_class(Bob, ('get_dict', 'dice_data'))
        self.assert_EventsFactoryError_code('SIGNATURES DIFFERENT', EventsFactory.new, Bob)

    def test_EventsFactory_construction__class_present_different_signature_too_few_params_EventsFactoryError(self):
        class Bob(DiceTable):
            pass

        EventsFactory.add_class(Bob, ('get_dict',))
        self.assert_EventsFactoryError_code('SIGNATURES DIFFERENT', EventsFactory.new, Bob)

    def test_EventsFactory_construction__class_present_wrong_signature_wrong_order_EventsFactoryError(self):
        class Bob(DiceTable):
            pass

        EventsFactory.add_class(Bob, ('dice_data', 'get_dict'))
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

    def test_EventsFactory_new_DetailedDiceTable(self):
        new = EventsFactory.new(DetailedDiceTable)
        self.assertIs(type(new), DetailedDiceTable)
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

    def test_EventsFactory_from_dict_DetailedDiceTable(self):
        events = DetailedDiceTable.new()
        new_events = EventsFactory.from_dictionary(events, {1: 1})
        self.assertIs(type(new_events), DetailedDiceTable)
        self.assertEqual(new_events.get_dict(), {1: 1})
        self.assertEqual(new_events.get_list(), [])
        self.assertTrue(new_events.calc_includes_zeroes)

    def test_EventsFactory_from_dict_and_dice_DiceTable(self):
        events = DiceTable.new()
        new_events = EventsFactory.from_dictionary_and_dice(events, {1: 1}, DiceRecord({Die(2): 2}))
        self.assertIs(type(new_events), DiceTable)
        self.assertEqual(new_events.get_dict(), {1: 1})
        self.assertEqual(new_events.get_list(), [(Die(2), 2)])

    def test_EventsFactory_from_dict_and_dice_DetailedDiceTable(self):
        events = DetailedDiceTable({2: 2}, DiceRecord.new(), False)
        new_events = EventsFactory.from_dictionary_and_dice(events, {1: 1}, DiceRecord({Die(2): 2}))
        self.assertIs(type(new_events), DetailedDiceTable)
        self.assertEqual(new_events.get_dict(), {1: 1})
        self.assertEqual(new_events.get_list(), [(Die(2), 2)])
        self.assertFalse(new_events.calc_includes_zeroes)

    def test_EventsFactory_from_params(self):
        start_dict = {2: 2}
        new_dict = {1: 1}

        start_dice = DiceRecord({Die(2): 1})
        new_dice = DiceRecord({Die(3): 3})

        start_num = 5
        new_num = 10

        start = NewDiceTableNewInitUpdate(start_dict, start_dice, start_num)

        new_events1 = EventsFactory.from_params(start, {'number': new_num, 'dice_data': new_dice})
        self.assertEqual(new_events1.get_dict(), start_dict)
        self.assertEqual(new_events1.dice_data(), new_dice)
        self.assertEqual(new_events1.number, new_num)

        new_events2 = EventsFactory.from_params(start, {'get_dict': new_dict})
        self.assertEqual(new_events2.get_dict(), new_dict)
        self.assertEqual(new_events2.dice_data(), start_dice)
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
                '  class variable: factory_keys = (getter method/property names)\n'
                '  current factory keys are: [\'calc_includes_zeroes\', \'dice_data\', \'get_dict\']\n'
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
        factory_name = '<class \'dicetables.factory.eventsfactory.EventsFactory\'>'
        class_name = '<class \'dicetables.dicetable.DiceTable\'>'
        current_keys = '(\'get_dict\', \'dice_data\')'
        passed_keys = '(\'dice_data\',)'
        expected = (factory_name, class_name, current_keys, passed_keys)
        self.assert_EventsFactoryError_contains(expected, EventsFactory.add_class, DiceTable, ('dice_data',))

    def test_Events_Factory_error_correct_message_GETTER_OVERWRITE(self):
        factory_name = '<class \'dicetables.factory.eventsfactory.EventsFactory\'>'
        getter_key = '\'dice_data\''
        getter_string = 'method: "dice_data", default: DiceRecord({})'
        new_getter_string = 'method: "dice_data", default: [(2, Die(6))]'
        expected = (factory_name, getter_key, getter_string, new_getter_string)

        class Bob(object):
            factory_keys = ('dice_data',)
            new_keys = [('dice_data', [(2, Die(6))], 'method')]

        self.assert_EventsFactoryError_contains(expected, EventsFactory.new, Bob)

    def test_Events_Factory_error_correct_message_MISSING_GETTER(self):
        bob_insert = 'TestEventsFactory.test_Events_Factory_error_correct_message_MISSING_GETTER.<locals>.'
        if version_info[0] < 3:
            bob_insert = ''
        bob = 'tests.factory.test_eventsfactory.{}Bob'.format(bob_insert)
        factory_name = '<class \'dicetables.factory.eventsfactory.EventsFactory\'>'
        factory_keys = '[\'calc_includes_zeroes\', \'dice_data\', \'get_dict\']'
        missing_key = '\'foo\''
        expected = (bob, factory_name, factory_keys, missing_key)

        class Bob(object):
            factory_keys = ('dice_data', 'foo')

        self.assert_EventsFactoryError_contains(expected, EventsFactory.new, Bob)

    def test_Events_Factory_error_correct_message_SIGNATURES_DIFFERENT(self):
        bob_insert = 'TestEventsFactory.test_Events_Factory_error_correct_message_SIGNATURES_DIFFERENT.<locals>.'
        if version_info[0] < 3:
            bob_insert = ''
        bob = 'tests.factory.test_eventsfactory.{}Bob'.format(bob_insert)
        factory_name = '<class \'dicetables.factory.eventsfactory.EventsFactory\'>'
        signature = '(\'get_dict\', \'dice_data\')'
        expected = (bob, factory_name, signature)

        class Bob(object):
            def __init__(self, num):
                self.num = num

        EventsFactory.add_class(Bob, ('get_dict', 'dice_data'))
        self.assert_EventsFactoryError_contains(expected, EventsFactory.new, Bob)

    def test_Events_Factory_error_correct_message_WTF(self):
        bob_insert = 'TestEventsFactory.test_Events_Factory_error_correct_message_WTF.<locals>.'
        if version_info[0] < 3:
            bob_insert = ''
        bob = 'tests.factory.test_eventsfactory.{}Bob'.format(bob_insert)
        factory_name = '<class \'dicetables.factory.eventsfactory.EventsFactory\'>'
        factory_classes = '[\'AdditiveEvents\', \'DetailedDiceTable\', \'DiceTable\']'
        expected = (bob, factory_name, factory_classes)

        class Bob(object):
            pass

        self.assert_EventsFactoryError_contains(expected, EventsFactory.new, Bob)

    def test_BUG_inheritance_issue_RESOLVED_as_best_as_can_be_without_metaclass(self):
        """
        Each class variable of a child class points to its parent class's class variable
        So when parent is re-assigned, child gets re-assigned.  When child get re-assigned, then they no
        longer point to same thing.
        so B(A).  A.num = 5 changes B.num to 5.  B.num = 7 does not change A.num.  A.num = 3 no longer changes B.num
        because it was re-assigned.
        I used StaticDict with EventsFactory so that changes to child dict do not
        mutate parent dict.
        """

        class A(EventsFactory):
            pass

        class B(A):
            pass

        class C(B):
            pass

        self.assertIs(EventsFactory._class_args, C._class_args)
        self.assertIs(B._getters, A._getters)
        B.add_class(int, ('dice_data',))
        self.assertEqual(EventsFactory.get_keys()[0], ['AdditiveEvents', 'DetailedDiceTable', 'DiceTable'])
        self.assertEqual(C.get_keys()[0], ['AdditiveEvents', 'DetailedDiceTable', 'DiceTable', 'int'])
        EventsFactory.reset()
        self.assertIs(EventsFactory._getters, A._getters)
        A.reset()
        self.assertIsNot(EventsFactory._getters, A._getters)
        self.assertEqual(B.get_keys()[0], ['AdditiveEvents', 'DetailedDiceTable', 'DiceTable', 'int'])
        C.reset()
        self.assertIsNot(B._getters, C._getters)

    def test_object_of_astonishing_idiocy(self):
        class DoubleTable(DiceTable):
            """
            TWO TABLES IN ONE!!!
            add_die/remove_die affect primary table.
            combine/remove affect secondary table.
            demonstrates factory method and EventsDictCreator
            """
            factory_keys = ('get_dict', 'get_dict_alt', 'dice_data')
            new_keys = [('get_dict_alt', {0: 1}, 'method')]

            def __init__(self, dict_for_add_die, dict_for_combine, dice_record):
                self._additive = AdditiveEvents(dict_for_combine)
                super(DoubleTable, self).__init__(dict_for_add_die, dice_record)

            def get_dict_alt(self):
                return self._additive.get_dict()

            def combine(self, events, times=1):
                new_alt_dict = DictCombiner(self._additive.get_dict()).combine_by_fastest(events.get_dict(), times)
                return EventsFactory.from_params(self, {'get_dict_alt': new_alt_dict})

            def remove(self, events, times=1):
                new_alt_dict = DictCombiner(self._additive.get_dict()).remove_by_tuple_list(events.get_dict(), times)
                return EventsFactory.from_params(self, {'get_dict_alt': new_alt_dict})

        new = DoubleTable.new()
        d1 = new.add_die(Die(2), 1)
        self.assertEqual(d1.get_dict(), {1: 1, 2: 1})
        self.assertEqual(d1.get_dict_alt(), {0: 1})
        d1_plus = d1.combine(Die(3), 1)
        self.assertEqual(d1_plus.get_dict(), {1: 1, 2: 1})
        self.assertEqual(d1_plus.get_dict_alt(), {1: 1, 2: 1, 3: 1})

    def test_deep_depths_of_dumbness(self):
        class DetachableDiceTable(DiceTable):
            factory_keys = ('get_dict', 'dice_data')
            lyrics = cycle((
                'I woke up this morning with a bad hangover and my {} was missing again.',
                'I can leave it home, when I think it\'s gonna get me in trouble,',
                'I really don\'t like being without my {} for too long. It makes me feel like less of a man,',
                'I saw my {} lying on a blanket next to a broken toaster oven. Some guy was selling it.',
                'I had to buy it off him. He wanted twenty-two bucks, but I talked him down to seventeen.',
                'People sometimes tell me I should get it permanently attached, but I don\'t know.',
                'Even though sometimes it\'s a pain in the ass, I like having a detachable {}.'
            ))

            def __init__(self, events_dict, dice_record):
                super(DetachableDiceTable, self).__init__(events_dict, dice_record)

            def detach(self, die):
                awesome_lyric = next(self.__class__.lyrics).format(die)
                times = self.number_of_dice(die)
                less_of_a_table = self.remove_die(die, times)
                detached = self.new().add_die(die, times)
                return awesome_lyric, detached, less_of_a_table

        new = DetachableDiceTable.new()
        two_d3 = new.add_die(Die(3), 2)
        two_d3_three_d4 = two_d3.add_die(Die(4), 3)
        two_d3_three_d4_four_d5 = two_d3_three_d4.add_die(Die(5), 4)
        msg, detached_1, remainder = two_d3_three_d4_four_d5.detach(Die(5))
        self.assertEqual(msg, 'I woke up this morning with a bad hangover and my D5 was missing again.')
        self.assertIsInstance(detached_1, DetachableDiceTable)
        self.assertEqual(detached_1, DetachableDiceTable.new().add_die(Die(5), 4))
        self.assertEqual(remainder, two_d3_three_d4)
        msg2, empty, detached_2 = detached_1.detach(Die(100))
        self.assertEqual(msg2, 'I can leave it home, when I think it\'s gonna get me in trouble,')
        self.assertEqual(detached_1, detached_2)
        self.assertEqual(str(detached_1), '4D5')
        self.assertEqual(empty.get_dict(), {0: 1})

    def test_a_silly_example_to_show_EventsDictCreator_and_EventsFactory_from_params(self):
        """
        combine events with a single event that occurs once. simply shifts the values of all events.

        AdditiveEvents({1: 2, 3: 4}).combine(AdditiveEvents({10: 1})).get_dict()
        {11: 2, 13: 4}
        AdditiveEvents({1: 2, 3: 4}).combine(AdditiveEvents({100: 1})).get_dict()
        {101: 2, 103: 4}
        """

        class ModifierTable(DiceTable):
            factory_keys = ('get_dict', 'dice_data', 'modifier')
            new_keys = [('modifier', 0, 'property')]

            def __init__(self, events_dict, dice_record, modifier):
                self._mod = modifier
                super(ModifierTable, self).__init__(events_dict, dice_record)

            def __str__(self):
                return '{}\n{:+}'.format(super(ModifierTable, self).__str__(), self._mod)

            @property
            def modifier(self):
                return self._mod

            def change_mod(self, new_modifier):
                change = new_modifier - self._mod
                change_events = AdditiveEvents({change: 1})
                new_dict = DictCombiner(self.get_dict()).combine_by_dictionary(change_events.get_dict(), 1)
                return EventsFactory.from_params(self, {'get_dict': new_dict, 'modifier': new_modifier})

        to_test = ModifierTable.new()
        to_test = to_test.add_die(Die(2), 2)
        self.assertEqual(to_test.get_dict(), {2: 1, 3: 2, 4: 1})
        self.assertEqual(str(to_test), '2D2\n+0')
        to_test = to_test.change_mod(10)
        self.assertEqual(to_test.get_dict(), {12: 1, 13: 2, 14: 1})
        self.assertEqual(str(to_test), '2D2\n+10')
        to_test = to_test.change_mod(-14)
        self.assertEqual(to_test.get_dict(), {-12: 1, -11: 2, -10: 1})
        self.assertEqual(str(to_test), '2D2\n-14')


if __name__ == '__main__':
    unittest.main()
