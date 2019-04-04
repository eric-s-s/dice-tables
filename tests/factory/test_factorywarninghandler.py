# pylint: disable=missing-docstring, invalid-name, too-many-public-methods
from __future__ import absolute_import

import unittest
import warnings

from dicetables.additiveevents import AdditiveEvents
from dicetables.dicetable import DiceTable
from dicetables.factory.eventsfactory import EventsFactory
from dicetables.factory.warninghandler import EventsFactoryWarning, EventsFactoryWarningHandler


class TestEventsFactoryWarningHandler(unittest.TestCase):
    def setUp(self):
        EventsFactory.reset()

    def assert_warning(self, warning, msg, func, *args):
        with warnings.catch_warnings(record=True) as cm:
            warnings.simplefilter("always")
            func(*args)
        if len(cm) != 1:
            self.fail('Warning not raised or too many warnings')
        else:
            self.assertEqual(msg, str(cm[0].message))
            self.assertEqual(warning, cm[0].category)

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

    def test_create_message_header(self):
        expected = (
                '\n' +
                'factory: <class \'dicetables.factory.eventsfactory.EventsFactory\'>\n' +
                'Warning code: CHECK\n' +
                'Failed to find/add the following class to the EventsFactory - \n' +
                'class: <class \'dicetables.factory.warninghandler.EventsFactoryWarningHandler\'>\n'
        )
        self.assertEqual(create_message_header('CHECK', EventsFactory, EventsFactoryWarningHandler), expected)

    def test_create_error_code_body_CONSTRUCT(self):
        expected = (
                '\n' +
                'Class found in factory: <class \'dicetables.additiveevents.AdditiveEvents\'>\n' +
                'attempted object construction using its signature. tried to return instance of original class.\n' +
                'If that had failed, returned instance of the class found in EventsFactory.\n' +
                '\n'
        )
        self.assertEqual(create_error_code_body((EventsFactoryWarningHandler, AdditiveEvents), 'CONSTRUCT'),
                         expected)

    def test_create_error_code_body_CHECK(self):
        expected = '\nWarning raised while performing check at instantiation\n\n'
        self.assertEqual(create_error_code_body((EventsFactoryWarningHandler, AdditiveEvents), 'CHECK'),
                         expected)

    def test_create_instructions(self):
        self.maxDiff = None
        expected = (
                'SOLUTION:\n' +
                '  class variable: factory_keys = (getter method/property names)\n'
                '  current factory keys are: [\'calc_includes_zeroes\', \'dice_data\', \'get_dict\']\n' +
                '  class variable: new_keys = [(info for each key not already in factory)]\n' +
                '  Each tuple in "new_keys" is (getter_name, default_value, "property"/"method")\n' +
                'ex:\n' +
                '  NewClass(Something):\n' +
                '      factory_keys = ("dice_data", "get_dict", "get_thingy", "label")\n' +
                '      new_keys = [("get_thingy", 0, "method"),\n' +
                '                  ("label", "", "property")]\n' +
                '\n' +
                '      def __init__(self, events_dict, dice_list, new_thingy, label):\n' +
                '          ....\n'
        )
        self.assertEqual(create_instructions(EventsFactory), expected)

    def test_create_warning_message(self):
        EventsFactory.reset()
        factory = EventsFactory
        code = 'CHECK'
        failed_class = EventsFactoryWarningHandler
        found_class = AdditiveEvents

        start = create_message_header(code, factory, failed_class)
        middle = create_error_code_body((failed_class, found_class), code)
        end = create_instructions(factory)
        self.assertEqual(create_warning_message(factory, code, failed_class, found_class), start + middle + end)

    def test_FactoryWarningHandler_warning_by_CHECK(self):
        msg = create_warning_message(EventsFactory, 'CHECK', DiceTable, AdditiveEvents)
        self.assert_warning(EventsFactoryWarning, msg, EventsFactoryWarningHandler(EventsFactory).raise_warning,
                            'CHECK', DiceTable, AdditiveEvents)

    def test_FactoryWarningHandler_warning_by_CONSTRUCT(self):
        msg = create_warning_message(EventsFactory, 'CONSTRUCT', DiceTable, AdditiveEvents)
        self.assert_warning(EventsFactoryWarning, msg, EventsFactoryWarningHandler(EventsFactory).raise_warning,
                            'CONSTRUCT', DiceTable, AdditiveEvents)


def create_warning_message(factory, code, *classes):
    failed_class = classes[0]

    intro = create_message_header(code, factory, failed_class)
    middle = create_error_code_body(classes, code)

    instructions = create_instructions(factory)
    return intro + middle + instructions


def create_message_header(code, factory, failed_class):
    intro = (
            '\nfactory: {}\n'.format(factory) +
            'Warning code: {}\n'.format(code) +
            'Failed to find/add the following class to the EventsFactory - \n' +
            'class: {}\n'.format(failed_class)
    )
    return intro


def create_error_code_body(classes, code):
    if code == 'CONSTRUCT':
        in_factory = classes[1]
        middle = (
                '\nClass found in factory: {}\n'.format(in_factory) +
                'attempted object construction using its signature. tried to return instance of original class.\n' +
                'If that had failed, returned instance of the class found in EventsFactory.\n\n'
        )
    else:
        middle = '\nWarning raised while performing check at instantiation\n\n'
    return middle


def create_instructions(factory):
    instructions = (
            'SOLUTION:\n' +
            '  class variable: factory_keys = (getter method/property names)\n'
            '  current factory keys are: {}\n'.format(factory.get_keys()[1]) +
            '  class variable: new_keys = [(info for each key not already in factory)]\n' +
            '  Each tuple in "new_keys" is (getter_name, default_value, "property"/"method")\n'
            'ex:\n' +
            '  NewClass(Something):\n' +
            '      factory_keys = ("dice_data", "get_dict", "get_thingy", "label")\n' +
            '      new_keys = [("get_thingy", 0, "method"),\n' +
            '                  ("label", "", "property")]\n\n' +
            '      def __init__(self, events_dict, dice_list, new_thingy, label):\n' +
            '          ....\n'
    )
    return instructions


if __name__ == '__main__':
    unittest.main()
