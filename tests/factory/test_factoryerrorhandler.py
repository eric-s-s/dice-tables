# pylint: disable=missing-docstring, invalid-name, too-many-public-methods
from __future__ import absolute_import

import unittest

from dicetables.dicetable import DiceTable
from dicetables.dieevents import Die
from dicetables.factory.errorhandler import EventsFactoryError, EventsFactoryErrorHandler
from dicetables.factory.eventsfactory import EventsFactory, Getter


class StandInForBadClass(object):
    pass


class TestEventsFactoryErrorHandler(unittest.TestCase):
    def setUp(self):
        EventsFactory.reset()

    def assert_events_factory_error_message(self, msg, func, *args):
        with self.assertRaises(EventsFactoryError) as cm:
            func(*args)
        error_msg = cm.exception.args[0]
        self.assertEqual(error_msg, msg)

    def test_assert_events_factory_error_message(self):
        def my_func():
            raise EventsFactoryError('hello')

        self.assert_events_factory_error_message('hello', my_func)

    def test_EventsFactoryErrorHandler_CLASS_OVERWRITE(self):
        expected = (
                'Error Code: CLASS OVERWRITE\n' +
                'Factory:    <class \'dicetables.factory.eventsfactory.EventsFactory\'>\n' +
                'Error At:   <class \'dicetables.dicetable.DiceTable\'>\n' +
                '\n' +
                'Attempted to add class already in factory but used different factory keys.\n' +
                'Class: <class \'dicetables.dicetable.DiceTable\'>\n' +
                'Current Factory Keys: (\'get_dict\', \'dice_data\')\n' +
                'Keys Passed In:       (\'dice_data\',)\n'
        )
        self.assert_events_factory_error_message(expected,
                                                 EventsFactoryErrorHandler(EventsFactory).raise_error,
                                                 'CLASS OVERWRITE',
                                                 DiceTable,
                                                 ('dice_data',))

    def test_EventsFactoryErrorHandler_GETTER_OVERWRITE(self):
        expected = (
                'Error Code: GETTER OVERWRITE\n' +
                'Factory:    <class \'dicetables.factory.eventsfactory.EventsFactory\'>\n' +
                'Error At:   Factory Getter Key: \'dice_data\'\n' +
                '\n' +
                'Attempted to add getter key already in factory but used different parameters.\n' +
                'Key: \'dice_data\'\n' +
                'Factory Parameter:    method: "dice_data", default: DiceRecord({})\n' +
                'Passed In Parameters: method: "get_dice", default: [(2, Die(6))]\n'
        )
        self.assert_events_factory_error_message(expected,
                                                 EventsFactoryErrorHandler(EventsFactory).raise_error,
                                                 'GETTER OVERWRITE',
                                                 'dice_data',
                                                 Getter('get_dice', [(2, Die(6))]))

    def test_EventsFactoryErrorHandler_MISSING_GETTER(self):
        expected = (
                'Error Code: MISSING GETTER\n' +
                'Factory:    <class \'dicetables.factory.eventsfactory.EventsFactory\'>\n' +
                'Error At:   <class \'tests.factory.test_factoryerrorhandler.StandInForBadClass\'>\n' +
                '\n' +
                'Attempted to add class with a getter key not in the factory.\n' +
                'Class: <class \'tests.factory.test_factoryerrorhandler.StandInForBadClass\'>\n' +
                'Current Factory Keys: [\'calc_includes_zeroes\', \'dice_data\', \'get_dict\']\n' +
                'Key Passed In:        \'foo\'\n'
        )
        self.assert_events_factory_error_message(expected,
                                                 EventsFactoryErrorHandler(EventsFactory).raise_error,
                                                 'MISSING GETTER',
                                                 StandInForBadClass,
                                                 'foo')

    def test_EventsFactoryErrorHandler_SIGNATURES_DIFFERENT(self):
        expected = (
                'Error Code: SIGNATURES DIFFERENT\n' +
                'Factory:    <class \'dicetables.factory.eventsfactory.EventsFactory\'>\n' +
                'Error At:   <class \'dicetables.dicetable.DiceTable\'>\n' +
                '\n' +
                'Attempted to construct a class already present in factory, but with a different signature.\n' +
                'Class: <class \'dicetables.dicetable.DiceTable\'>\n' +
                'Signature In Factory: (\'get_dict\', \'dice_data\')\n' +
                'To reset the factory to its base state, use EventsFactory.reset()\n'
        )
        self.assert_events_factory_error_message(expected,
                                                 EventsFactoryErrorHandler(EventsFactory).raise_error,
                                                 'SIGNATURES DIFFERENT',
                                                 DiceTable)

    def test_EventsFactoryErrorHandler_WTF(self):
        expected = (
                'Error Code: WTF\n' +
                'Factory:    <class \'dicetables.factory.eventsfactory.EventsFactory\'>\n' +
                'Error At:   <class \'tests.factory.test_factoryerrorhandler.StandInForBadClass\'>\n' +
                '\n' +
                'Attempted to construct a class unrelated, in any way, to any class in the factory.\n' +
                'EventsFactory can currently construct the following classes:\n' +
                '[\'AdditiveEvents\', \'DetailedDiceTable\', \'DiceTable\']\n' +
                'EventsFactory searched the MRO of <class \'tests.factory.test_factoryerrorhandler.StandInForBadClass\'>,\n'
                + 'and found no matches to the classes in the factory.\n'
        )
        self.assert_events_factory_error_message(expected,
                                                 EventsFactoryErrorHandler(EventsFactory).raise_error,
                                                 'WTF',
                                                 StandInForBadClass)


if __name__ == '__main__':
    unittest.main()
