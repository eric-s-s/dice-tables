# pylint: disable=missing-docstring, invalid-name, too-many-public-methods
"""tests for the baseevents.py module"""
from __future__ import absolute_import
import unittest
from dicetables.eventsfactory import EventsFactory
from dicetables.baseevents import AdditiveEvents
from dicetables.dicetable import DiceTable, RichDiceTable


class TestEventsFactory(unittest.TestCase):
    # def assert_my_regex(self, error_type, regex, func, *args):
    #     with self.assertRaises(error_type) as cm:
    #         func(*args)
    #     error_msg = str(cm.exception)
    #     self.assertEqual(error_msg, regex)
    #
    # def test_assert_my_regex(self):
    #     self.assert_my_regex(ValueError, "invalid literal for int() with base 10: 'a'", int, 'a')
    #
    # def test_EventsFactory_add_class(self):
    #     factory = EventsFactory()
    #     factory.add_class('bob', ('dictionary', ))
    #     self.assertEqual(factory.init_args['bob'], ('dictionary',))
    #
    # def test_EventsFactory_add_class_raises_AttributeError(self):
    #     msg_start = "arg not in list: ["
    #     msg_end = "]. add arg and getter with add_arg method"
    #     msg_contains = ['calc_bool', 'dice', 'dictionary']
    #     with self.assertRaises(AttributeError) as cm:
    #         EventsFactory().add_class('bob', ('poop',))
    #     msg = cm.exception.args[0]
    #     self.assertTrue(msg.startswith(msg_start))
    #     self.assertTrue(msg.endswith(msg_end))
    #     for value in msg_contains:
    #         self.assertIn(value, msg)
    #
    # def test_EventsFactory_add_arg(self):
    #     factory = EventsFactory()
    #     factory.add_arg('number', 'get_num', 0)
    #     self.assertEqual(factory.getters['number'], 'get_num')
    #     self.assertEqual(factory.empty_args['number'], 0)

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


if __name__ == '__main__':
    unittest.main()
