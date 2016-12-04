# pylint: disable=missing-docstring, invalid-name, too-many-public-methods
"""tests for the baseevents.py module"""
from __future__ import absolute_import

import unittest

from dicetables.factory.factoryerrorhandler import EventsFactoryError, EventsFactoryErrorHandler
from dicetables.dicetable import DiceTable
from dicetables.dieevents import Die
from dicetables.factory.eventsfactory import EventsFactory, Getter


class TestEventsFactoryErrorHandler(unittest.TestCase):
    def assert_my_regex(self, error_type, regex, func, *args):
        with self.assertRaises(error_type) as cm:
            func(*args)
        error_msg = cm.exception.args[0]
        self.assertEqual(error_msg, regex)

    def test_assert_my_regex(self):
        self.assert_my_regex(ValueError, "invalid literal for int() with base 10: 'a'", int, 'a')

    def test_create_header_with_param_class(self):
        expected = (
            'Error Code: CLASS OVERWRITE\n' +
            'Factory:    <class \'dicetables.factory.eventsfactory.EventsFactory\'>\n' +
            'Error At:   <class \'dicetables.dicetable.DiceTable\'>\n'
        )
        self.assertEqual(expected, create_header('CLASS OVERWRITE', EventsFactory, DiceTable))

    def test_create_header_with_error_code_GETTER_OVERWRITE(self):
        expected = (
            'Error Code: GETTER OVERWRITE\n' +
            'Factory:    <class \'dicetables.factory.eventsfactory.EventsFactory\'>\n' +
            'Error At:   Factory Getter Key: \'oops\'\n'
        )
        print(expected)
        self.assertEqual(expected, create_header('GETTER OVERWRITE', EventsFactory, 'oops'))

    def test_create_error_body_CLASS_OVERWRITE(self):
        expected = (
            '\nAttempted to add class already in factory but used different factory keys.\n' +
            'Class: <class \'dicetables.dicetable.DiceTable\'>\n' +
            'Current Factory Keys: (\'dictionary\', \'dice\')\n' +
            'Keys Passed In:       (\'dice\',)\n'
        )
        self.assertEqual(expected, create_error_body('CLASS OVERWRITE', EventsFactory, DiceTable, ('dice',)))

    def test_create_error_body_MISSING_GETTER(self):
        """missing getter = events_class, getter key"""
        expected = (
            '\nAttempted to add class with a getter key not in the factory.\n' +
            'Class: <class \'dicetables.dicetable.DiceTable\'>\n' +
            'Current Factory Keys: [\'calc_bool\', \'dice\', \'dictionary\']\n' +
            'Key Passed In:        \'foo\'\n'
        )
        self.assertEqual(expected, create_error_body('MISSING GETTER', EventsFactory, DiceTable, 'foo'))

    def test_create_error_body_GETTER_OVERWRITE(self):
        """getter overwrite = getter key, new getter object"""
        expected = (
            '\nAttempted to add getter key already in factory but used different parameters.\n' +
            'Key: \'dice\'\n' +
            'Factory Parameter:    method: "get_dice_items", default: []\n' +
            'Passed In Parameters: method: "get_dice", default: [(2, Die(6))]\n'
        )
        self.assertEqual(expected, create_error_body('GETTER OVERWRITE', EventsFactory, 'dice',
                                                     Getter('get_dice', [(2, Die(6))])))

    def test_create_error_body_SIGNATURES_DIFFERENT(self):
        """signatures different = events_class"""
        expected = (
            '\nAttempted to construct a class already present in factory, but with a different signature.\n' +
            'Class: <class \'dicetables.dicetable.DiceTable\'>\n' +
            'Signature In Factory: (\'dictionary\', \'dice\')\n' +
            'To reset the factory to its base state, use EventsFactory.reset()\n'
        )
        self.assertEqual(expected, create_error_body('SIGNATURES DIFFERENT', EventsFactory, DiceTable))

    def test_create_error_body_WTF(self):
        """wtf = events"""
        expected = (
            '\nAttempted to construct a class unrelated, in any way, to any class in the factory.\n' +
            'EventsFactory can currently construct the following classes:\n' +
            '[\'AdditiveEvents\', \'DiceTable\', \'RichDiceTable\']\n' +
            'EventsFactory searched the MRO of <class \'dicetables.dicetable.DiceTable\'>,\n' +
            'and found no matches to the classes in the factory.\n'
        )
        self.assertEqual(expected, create_error_body('WTF', EventsFactory, DiceTable))


def create_header(error_code, factory, bad_param):
    msg_start = 'Error Code: {}\nFactory:    {}\nError At:   '.format(error_code, factory)
    if error_code == 'GETTER OVERWRITE':
        msg_end = 'Factory Getter Key: {!r}\n'.format(bad_param)
    else:
        msg_end = '{}\n'.format(bad_param)

    return msg_start + msg_end


def create_error_body(error_code, factory, *bad_params):
    explanation = ''
    params_record = ''
    if error_code == 'CLASS OVERWRITE':
        explanation = '\nAttempted to add class already in factory but used different factory keys.\n'
        params_record = (
            'Class: {}\n'.format(bad_params[0]) +
            'Current Factory Keys: {}\n'.format(factory.get_class_params(bad_params[0])) +
            'Keys Passed In:       {}\n'.format(bad_params[1])
        )
    elif error_code == 'MISSING GETTER':
        explanation = '\nAttempted to add class with a getter key not in the factory.\n'
        params_record = (
            'Class: {}\n'.format(bad_params[0]) +
            'Current Factory Keys: {}\n'.format(factory.get_keys()[1]) +
            'Key Passed In:        {!r}\n'.format(bad_params[1])
        )
    elif error_code == 'GETTER OVERWRITE':
        explanation = '\nAttempted to add getter key already in factory but used different parameters.\n'
        params_record = (
            'Key: {!r}\n'.format(bad_params[0]) +
            'Factory Parameter:    {}\n'.format(factory.get_getter_string(bad_params[0])) +
            'Passed In Parameters: {}\n'.format(bad_params[1])
        )
    elif error_code == 'SIGNATURES DIFFERENT':
        explanation = '\nAttempted to construct a class already present in factory, but with a different signature.\n'
        params_record = (
            'Class: {}\n'.format(bad_params[0]) +
            'Signature In Factory: {}\n'.format(factory.get_class_params(bad_params[0])) +
            'To reset the factory to its base state, use EventsFactory.reset()\n'
        )
    elif error_code == 'WTF':
        explanation = '\nAttempted to construct a class unrelated, in any way, to any class in the factory.\n'
        params_record = (
            'EventsFactory can currently construct the following classes:\n' +
            '{}\n'.format(factory.get_keys()[0]) +
            'EventsFactory searched the MRO of {},\n'.format(bad_params[0]) +
            'and found no matches to the classes in the factory.\n'
        )
    return explanation + params_record

if __name__ == '__main__':
    unittest.main()

