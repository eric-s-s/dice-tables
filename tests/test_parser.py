# pylint: disable=missing-docstring, invalid-name, too-many-public-methods
from __future__ import absolute_import

import unittest

from dicetables.dieevents import Die, ModDie, WeightedDie, ModWeightedDie, StrongDie, Modifier, Exploding, ExplodingOn

from dicetables.parser import NodeCreator, Parser


class TestParser(unittest.TestCase):
    def setUp(self):
        self.parser = Parser

    def test_node_creator(self):
        creator = NodeCreator('ExplodingOn(StrongDie(WeightedDie({1: 2, 3: 4}), 3), (1, 3), 4)')
        self.assertEqual(creator.to_dict(),
                         {
                             'ExplodingOn': [
                                 {
                                     'StrongDie': [
                                         {
                                             'WeightedDie': [
                                                 '{1: 2, 3: 4}'
                                             ]
                                         },
                                         '3'
                                     ]
                                 },
                                 '(1, 3)',
                                 '4'
                             ]
                         }
                         )

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
