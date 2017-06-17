# pylint: disable=missing-docstring, invalid-name, too-many-public-methods
from __future__ import absolute_import

import unittest

from dicetables.dieevents import Die, ModDie, WeightedDie, ModWeightedDie, StrongDie, Modifier, Exploding, ExplodingOn

from dicetables.parser import Parser, FunctionCall, Value, Group, StringToParams


class TestStringToParams(unittest.TestCase):

    def test_starts_with_function_call_true(self):
        self.assertTrue(StringToParams.starts_with_function_call(' int(1), 2, 3'))
        self.assertTrue(StringToParams.starts_with_function_call('UpperCaseFunc(1), 2, 3'))
        self.assertTrue(StringToParams.starts_with_function_call('underscore_func(1), 2, 3'))
        self.assertTrue(StringToParams.starts_with_function_call('_private_func(1), 2, 3'))
        self.assertTrue(StringToParams.starts_with_function_call('numbered2(1), 2, 3'))

    def test_starts_with_function_call_false(self):
        self.assertFalse(StringToParams.starts_with_function_call(' [int(1), 2, 3]'))
        self.assertFalse(StringToParams.starts_with_function_call('1, UpperCaseFunc(1), 2, 3'))
        self.assertFalse(StringToParams.starts_with_function_call('1, UpperCaseFunc(1), 2, 3'))

    def test_starts_with_group_true(self):
        self.assertTrue(StringToParams.starts_with_group(' [[1, 2'))
        self.assertTrue(StringToParams.starts_with_group('{[1, 2'))
        self.assertTrue(StringToParams.starts_with_group(' ([1, 2'))

    def test_starts_with_group_false(self):
        self.assertFalse(StringToParams.starts_with_group(', [[1, 2'))
        self.assertFalse(StringToParams.starts_with_group('"a", {[1, 2'))
        self.assertFalse(StringToParams.starts_with_group('function([1, 2'))

    def test_find_end_of_first_group_list(self):
        self.assertEqual(StringToParams.find_end_of_first_group('[1, 2], 1'), 5)

    def test_find_end_of_first_group_set(self):
        self.assertEqual(StringToParams.find_end_of_first_group('{1, 2}, 1'), 5)

    def test_find_end_of_first_group_tuple(self):
        self.assertEqual(StringToParams.find_end_of_first_group('(1, 2), 1'), 5)

    def test_find_end_of_first_group_dict(self):
        self.assertEqual(len('{1: 3, 2: 4}'), 12)
        self.assertEqual(StringToParams.find_end_of_first_group('{1: 3, 2: 4}, 1'), 11)

    def test_find_end_of_first_group_raises_value_error(self):
        self.assertRaises(ValueError, StringToParams.find_end_of_first_group, ' [1, 2]')
        self.assertRaises(ValueError, StringToParams.find_end_of_first_group, ', [1, 2]')
        self.assertRaises(ValueError, StringToParams.find_end_of_first_group, '1, [1, 2]')
        self.assertRaises(ValueError, StringToParams.find_end_of_first_group, '[1, 2, 3)')

    def test_find_end_of_first_group_mixed_elements(self):
        self.assertEqual(len('[1, [2, 3], (4, 5), {6, 7}]'), 27)
        self.assertEqual(StringToParams.find_end_of_first_group('[1, [2, 3], (4, 5), {6, 7}], [1, 2]'), 26)

    def test_get_param_multi_elements(self):
        params = '"a",function(x),(2, 3)'
        self.assertEqual(StringToParams.get_param(params), ('"a"', 'function(x),(2, 3)'))

    def test_get_param_removes_extraneous_whitespace(self):
        params = '  "a"  ,   function(x), (2, 3)   '
        self.assertEqual(StringToParams.get_param(params), ('"a"', 'function(x), (2, 3)'))

    def test_get_param_singleton(self):
        params = '  "a"        '
        self.assertEqual(StringToParams.get_param(params), ('"a"', ''))

    def test_get_group_multi_elements(self):
        params = '[[1, 2, 3]], [1], 2'
        self.assertEqual(StringToParams.get_group(params), ('[[1, 2, 3]]', '[1], 2'))

    def test_get_group_multi_elements_extraneous_whitespace(self):
        params = '  [[1, 2, 3]]  ,   [1], 2'
        self.assertEqual(StringToParams.get_group(params), ('[[1, 2, 3]]', '[1], 2'))

    def test_get_group_singleton(self):
        params = '  [[1, 2, 3]]  '
        self.assertEqual(StringToParams.get_group(params), ('[[1, 2, 3]]', ''))

    def test_get_group_other_groups(self):
        params = '  (([1, 2, 3]))  '
        self.assertEqual(StringToParams.get_group(params), ('(([1, 2, 3]))', ''))

        params = '  {{[1, 2, 3]}}  '
        self.assertEqual(StringToParams.get_group(params), ('{{[1, 2, 3]}}', ''))

        params = '{1: {2: 3}}'
        self.assertEqual(StringToParams.get_group(params), ('{1: {2: 3}}', ''))

    def test_get_function_call_multi_elements(self):
        params = 'function(x), [1], 2'
        self.assertEqual(StringToParams.get_function_call(params),
                         ('function', 'x', '[1], 2'))

    def test_get_function_call_multi_elements_extra_whitespace(self):
        params = '   function(x)   ,    [1], 2'
        self.assertEqual(StringToParams.get_function_call(params),
                         ('function', 'x', '[1], 2'))

    def test_get_function_call_singleton(self):
        params = 'function(x)'
        self.assertEqual(StringToParams.get_function_call(params),
                         ('function', 'x', ''))

    def test_get_function_call_many_function_params(self):
        params = 'function("a", (1, 2), {1: 2})'
        self.assertEqual(StringToParams.get_function_call(params),
                         ('function', '"a", (1, 2), {1: 2}', ''))

    def test_get_function_call_with_function_call_in_params(self):
        params = 'function("a", (1, 2), {1: 2}, funky_func([1, 2]))'
        self.assertEqual(StringToParams.get_function_call(params),
                         ('function', '"a", (1, 2), {1: 2}, funky_func([1, 2])', ''))

    def test_get_call_structure_singleton(self):
        answer = StringToParams.get_call_structure('"ab"')
        self.assertEqual(answer, [Value('"ab"')])

        answer = StringToParams.get_call_structure('1234')
        self.assertEqual(answer, [Value('1234')])

    def test_get_call_structure_comma_separated_elements(self):
        answer = StringToParams.get_call_structure('"ab", 1234, [1, 2], {1: (2,)}')
        self.assertEqual(answer, [Value('"ab"'), Value('1234'), Group('[1, 2]'), Group('{1: (2,)}')])

    def test_get_call_structure_simple_function_call(self):
        answer = StringToParams.get_call_structure('ACoolClass(1, (2, 3), "a")')
        self.assertEqual(answer, [FunctionCall(func='ACoolClass',
                                               params=[Value('1'), Group('(2, 3)'), Value('"a"')]
                                               )
                                  ]
                         )

    def test_get_call_structure_nested_function_calls(self):
        creator = StringToParams.get_call_structure('ExplodingOn(StrongDie(WeightedDie({1: 2, 3: 4}), 3), (1, 3), 4)')
        self.assertEqual(creator,
                         [FunctionCall(
                             func='ExplodingOn',
                             params=[
                                 FunctionCall(
                                     func='StrongDie',
                                     params=[
                                         FunctionCall(
                                             func='WeightedDie',
                                             params=[Group('{1: 2, 3: 4}')]
                                         ),
                                         Value('3')
                                     ]
                                 ),
                                 Group('(1, 3)'),
                                 Value('4')
                             ]
                         )]
                         )


class TestParser(unittest.TestCase):

    # @unittest.skip
    def test_Die(self):
        self.assertEqual(Parser.parse_die('Die(6)'), Die(6))

    # @unittest.skip
    def test_ModDie(self):
        self.assertEqual(Parser.parse_die('ModDie(6, -2)'), ModDie(6, -2))

    # @unittest.skip
    def test_WeightedDie(self):
        self.assertEqual(Parser.parse_die('WeightedDie({1: 2, 3: 4})'), WeightedDie({1: 2, 3: 4}))

    # @unittest.skip
    def test_ModWeightedDie(self):
        self.assertEqual(Parser.parse_die('ModWeightedDie({1: 2, 3: 4}, 3)'), ModWeightedDie({1: 2, 3: 4}, 3))

    # @unittest.skip
    def test_StrongDie(self):
        self.assertEqual(Parser.parse_die('StrongDie(Die(6), -2)'), StrongDie(Die(6), -2))

    # @unittest.skip
    def test_Modifier(self):
        self.assertEqual(Parser.parse_die('Modifier(6)'), Modifier(6))

    # @unittest.skip
    def test_Exploding(self):
        self.assertEqual(Parser.parse_die('Exploding(Die(6), 3)'), Exploding(Die(6), 3))

    # @unittest.skip
    def test_composite(self):
        self.assertEqual(Parser.parse_die('Exploding(StrongDie(Die(6), 3), 4)'),
                         Exploding(
                             StrongDie(Die(6), 3), 4
                         )
                         )

    # @unittest.skip
    def test_composite2(self):
        self.assertEqual(Parser.parse_die('Exploding(StrongDie(WeightedDie({1: 2, 3: 4}), 3), 4)'),
                         Exploding(
                             StrongDie(WeightedDie({1: 2, 3: 4}), 3), 4
                         )
                         )

    # @unittest.skip
    def test_ExplodingOn(self):
        self.assertEqual(Parser.parse_die('ExplodingOn(Die(6), (2, 6), 3)'), ExplodingOn(Die(6), (2, 6), 3))
