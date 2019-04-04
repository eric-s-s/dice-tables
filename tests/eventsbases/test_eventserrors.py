from __future__ import absolute_import

import unittest

from dicetables.eventsbases.eventerrors import InvalidEventsError, DiceRecordError


class TestEventsErrors(unittest.TestCase):
    def test_InvalidEventsError_empty(self):
        error = InvalidEventsError()
        self.assertEqual(str(error), '')
        self.assertEqual(error.args[0], '')

    def test_InvalidEventsError_non_empty(self):
        error = InvalidEventsError('message')
        self.assertEqual(str(error), 'message')
        self.assertEqual(error.args[0], 'message')

    def test_DiceRecordError_message(self):
        error = DiceRecordError('oops')
        self.assertEqual(error.args[0], 'oops')
        self.assertEqual(str(error), 'oops')

    def test_DiceRecordError_no_message(self):
        error = DiceRecordError()
        self.assertEqual(error.args[0], '')


if __name__ == '__main__':
    unittest.main()
