# pylint: disable=missing-docstring, invalid-name, too-many-public-methods
from __future__ import absolute_import

import unittest

from dicetables.dieevents import Die, ModDie, WeightedDie, ModWeightedDie, StrongDie, Modifier, Exploding, ExplodingOn

from dicetables.parser import NodeCreator, Parser, FunctionCall, StringPrep


class TestStringPrep(unittest.TestCase):

    def test_find_end_of_first_group_list(self):
        self.assertEqual(StringPrep.find_end_of_first_group('[1, 2], 1'), 5)

    def test_find_end_of_first_group_set(self):
        self.assertEqual(StringPrep.find_end_of_first_group('{1, 2}, 1'), 5)

    def test_find_end_of_first_group_tuple(self):
        self.assertEqual(StringPrep.find_end_of_first_group('(1, 2), 1'), 5)

    def test_find_end_of_first_group_dict(self):
        self.assertEqual(len('{1: 3, 2: 4}'), 12)
        self.assertEqual(StringPrep.find_end_of_first_group('{1: 3, 2: 4}, 1'), 11)

    def test_find_end_of_first_group_raises_value_error(self):
        self.assertRaises(ValueError, StringPrep.find_end_of_first_group, ' [1, 2]')
        self.assertRaises(ValueError, StringPrep.find_end_of_first_group, ', [1, 2]')
        self.assertRaises(ValueError, StringPrep.find_end_of_first_group, '1, [1, 2]')
        self.assertRaises(ValueError, StringPrep.find_end_of_first_group, '[1, 2, 3)')

    def test_find_end_of_first_group_mixed_elements(self):
        self.assertEqual(len('[1, [2, 3], (4, 5), {6, 7}]'), 27)
        self.assertEqual(StringPrep.find_end_of_first_group('[1, [2, 3], (4, 5), {6, 7}], [1, 2]'), 26)


    # @unittest.skip
    def test_thing_singleton(self):
        answer = StringPrep.get_params('"ab", "c"')
        self.assertEqual(answer, ['"ab"', '"c"'])

        answer = StringPrep.get_params('12, 34')
        self.assertEqual(answer, ['12', '34'])

    # @unittest.skip
    def test_thing_list(self):
        answer = StringPrep.get_params('[1, 2, 3]')
        self.assertEqual(answer, ['[1, 2, 3]'])

    # @unittest.skip
    def test_thing_list2(self):
        answer = StringPrep.get_params('[1, 2, 3], [4, 5, 6]')
        self.assertEqual(answer, ['[1, 2, 3]', '[4, 5, 6]'])

    # @unittest.skip
    def test_thing_list3(self):
        answer = StringPrep.get_params('[[1, 2], [3]], [[1, 2], [3]]')
        self.assertEqual(answer, ['[[1, 2], [3]]', '[[1, 2], [3]]'])

    # @unittest.skip
    def test_node_creator(self):
        creator = StringPrep.get_params('ExplodingOn(StrongDie(WeightedDie({1: 2, 3: 4}), 3), (1, 3), 4)')
        self.assertEqual(creator,
                         [FunctionCall(
                             func='ExplodingOn',
                             params=[
                                 FunctionCall(
                                     func='StrongDie',
                                     params=[
                                         FunctionCall(
                                             func='WeightedDie',
                                             params=['{1: 2, 3: 4}']
                                         ),
                                         '3'
                                     ]
                                 ),
                                 '(1, 3)',
                                 '4'
                             ]
                         )]
                         )


class TestParser(unittest.TestCase):
    def setUp(self):
        self.parser = Parser

    @unittest.skip
    def test_Die(self):
        self.assertEqual(self.parser.parse('Die(6)'), Die(6))

    @unittest.skip
    def test_ModDie(self):
        self.assertEqual(self.parser.parse('ModDie(6, -2)'), ModDie(6, -2))

    @unittest.skip
    def test_WeightedDie(self):
        self.assertEqual(self.parser.parse('WeightedDie({1: 2, 3: 4})'), WeightedDie({1: 2, 3: 4}))

    @unittest.skip
    def test_ModWeightedDie(self):
        self.assertEqual(self.parser.parse('ModWeightedDie({1: 2, 3: 4}, 3)'), ModWeightedDie({1: 2, 3: 4}, 3))

    @unittest.skip
    def test_StrongDie(self):
        self.assertEqual(self.parser.parse('StrongDie(Die(6), -2)'), StrongDie(Die(6), -2))

    @unittest.skip
    def test_Modifier(self):
        self.assertEqual(self.parser.parse('Modifier(6)'), Modifier(6))

    @unittest.skip
    def test_Exploding(self):
        self.assertEqual(self.parser.parse('Exploding(Die(6), 3)'), Exploding(Die(6), 3))

    @unittest.skip
    def test_composite(self):
        self.assertEqual(self.parser.parse('Exploding(StrongDie(Die(6), 3), 4)'),
                         Exploding(
                             StrongDie(Die(6), 3), 4
                         )
                         )

    @unittest.skip
    def test_composite2(self):
        self.assertEqual(self.parser.parse('Exploding(StrongDie(WeightedDie({1: 2, 3: 4}), 3), 4)'),
                         Exploding(
                             StrongDie(WeightedDie({1: 2, 3: 4}), 3), 4
                         )
                         )

    @unittest.skip
    def test_ExplodingOn(self):
        self.assertEqual(self.parser.parse('ExplodingOn(Die(6), (2, 6), 3)'), ExplodingOn(Die(6), (2, 6), 3))
