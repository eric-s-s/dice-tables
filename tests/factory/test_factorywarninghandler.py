# pylint: disable=missing-docstring, invalid-name, too-many-public-methods
"""tests for the baseevents.py module"""
from __future__ import absolute_import

import unittest
import warnings

from dicetables.factory.factorywarninghandler import EventsFactoryWarning, EventsFactoryWarningHandler
from dicetables.factory.eventsfactory import EventsFactory
from dicetables.baseevents import AdditiveEvents
from dicetables.dicetable import DiceTable, RichDiceTable


class TestEventsFactoryWarningHandler(unittest.TestCase):
    def setUp(self):
        EventsFactory.reset()

    def assert_my_regex(self, error_type, regex, func, *args):
        with self.assertRaises(error_type) as cm:
            func(*args)
        error_msg = cm.exception.args[0]
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
            warnings.warn('msg', EventsFactoryWarning, stacklevel=2)
            return number
        self.assert_warning(EventsFactoryWarning, 'msg', func, 5)

    def test_assert_warning_with_no_warning(self):
        def func(number):
            return number
        with self.assertRaises(AssertionError) as cm:
            self.assert_warning(EventsFactoryWarning, 'hi', func, 5)
        self.assertEqual(cm.exception.args[0], 'Warning not raised or too many warnings')

    def test_assert_warning_with_too_many_warnings(self):
        def func(number):
            warnings.warn('msg', EventsFactoryWarning, stacklevel=2)
            warnings.warn('msg', Warning, stacklevel=2)
            return number
        with self.assertRaises(AssertionError) as cm:
            self.assert_warning(EventsFactoryWarning, 'hi', func, 5)
        self.assertEqual(cm.exception.args[0], 'Warning not raised or too many warnings')

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

    def test_create_warning_message(self):
        EventsFactory.reset()
        factory = EventsFactory
        code = 'CONSTRUCT'
        action = 'construction'
        failed_class = EventsFactoryWarningHandler
        in_factory = AdditiveEvents

        expected = (
            "\nfactory:  <class 'dicetables.factory.eventsfactory.EventsFactory'>" +
            'Warning code: CONSTRUCT\n' +
            'Failed to find/add the following class to the EventsFactory - \n' +
            'class: {} to the EventsFactory.\n'.format(failed_class) +
            'closest class is {}.\n'.format(in_factory) +
            'Will attempt all object construction using its signature\n' +
            'To rectify this, add a tuple of parameters as a class level variable named "factory_keys"\n'
            'current factory keywords are: {}\n'.format(factory.get_keys()[1]) +
            'add new factory keywords as a class level list of tuples named "new_keys"\n' +
            'Each tuple in "new_keys" is (key_name, getter_name, default_value, "property"/"method")\n'
            'ex: NewClass(Something):\n' +
            '        factory_keys = ("dictionary", "dice", "thingy", "other")\n' +
            '        new_keys = [("thingy", "get_thingy", 0, "method"),\n' +
            '                    ("other", "label", "", "property")]\n' +
            '        def __init__(self, ........\n'

        )
        print(expected)
        self.assertEqual(create_warning_message(factory, code, failed_class, in_factory), expected)

    def test_FactoryWarningHandler_warning_by_CHECK(self):
        msg = create_warning_message(EventsFactory, 'CHECK', DiceTable, AdditiveEvents)
        self.assert_warning(EventsFactoryWarning, msg, EventsFactoryWarningHandler(EventsFactory).raise_warning,
                            'CHECK', DiceTable, AdditiveEvents)


def create_warning_message(factory, code, *classes):
    failed_class = classes[0]

    intro = (
        '\nfactory: {}\n'.format(factory) +
        'Warning code: {}\n'.format(code) +
        'Failed to find/add the following class to the EventsFactory - \n' +
        'class: {}\n'.format(failed_class)
    )
    if code == 'CONSTRUCT':
        in_factory = classes[1]
        middle = (
            '\nClass found in factory: {}\n'.format(in_factory) +
            'attempted object construction using its signature. tried to return instance of original class.\n' +
            'If that had failed, returned instance of the class found in EventsFactory.\n\n'
        )
    else:
        middle = '\nWarning raised while performing check at instantiation\n\n'

    instructions = (
        'SOLUTION:\n' +
        '  class variable: factory_keys = (names of factory keys for getters)\n'
        '  current factory keys are: {}\n'.format(factory.get_keys()[1]) +
        '  class variable: new_keys = [(info for each key not already in factory)]\n' +
        '  Each tuple in "new_keys" is (key_name, getter_name, default_value, "property"/"method")\n'
        '  ex:\n' +
        '  NewClass(Something):\n' +
        '      factory_keys = ("dictionary", "dice", "thingy", "other")\n' +
        '      new_keys = [("thingy", "get_thingy", 0, "method"),\n' +
        '                  ("other", "label", "", "property")]\n\n' +
        '      def __init__(self, events_dict, dice_list, new_thingy, label):\n' +
        '          ....\n'
    )
    return intro + middle + instructions


if __name__ == '__main__':
    unittest.main()

