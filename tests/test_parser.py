# pylint: disable=missing-docstring, invalid-name, too-many-public-methods
from __future__ import absolute_import

import unittest

from dicetables.dieevents import Die, ModDie, WeightedDie, ModWeightedDie, StrongDie, Modifier, Exploding, ExplodingOn

from dicetables.parser import (StringToParams, FunctionCall, Value, Group, Parser,
                               make_int, make_int_dict, make_int_tuple)


class TestStringToParams(unittest.TestCase):

    def test_starts_with_function_call_true(self):
        self.assertTrue(StringToParams.starts_with_function_call(' int(1), 2, 3'))
        self.assertTrue(StringToParams.starts_with_function_call('UpperCaseFunc(1), 2, 3'))
        self.assertTrue(StringToParams.starts_with_function_call('underscore_func(1), 2, 3'))
        self.assertTrue(StringToParams.starts_with_function_call('_private_func(1), 2, 3'))
        self.assertTrue(StringToParams.starts_with_function_call('numbered2(1), 2, 3'))
        self.assertTrue(StringToParams.starts_with_function_call('A(1), 2, 3'))

    def test_starts_with_function_call_false(self):
        self.assertFalse(StringToParams.starts_with_function_call(' [int(1), 2, 3]'))
        self.assertFalse(StringToParams.starts_with_function_call('1, UpperCaseFunc(1), 2, 3'))
        self.assertFalse(StringToParams.starts_with_function_call('1, UpperCaseFunc(1), 2, 3'))
        self.assertFalse(StringToParams.starts_with_function_call('-UpperCaseFunc(1), 2, 3'))
        self.assertFalse(StringToParams.starts_with_function_call('&UpperCaseFunc(1), 2, 3'))

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

    def test_get_param_elements_with_other_characters(self):
        params = '-1'
        self.assertEqual(StringToParams.get_param(params), ('-1', ''))

        for char in '!@#$%^&*_+=':
            self.assertEqual(StringToParams.get_param(char), (char, ''))

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
    # TODO re-order, add tests for: init, (get_params, get_die_class), bad class to parse, bad added class at parse,
    # TODO calling with ignore case, and also nested ignore case.
    def test_make_die_on_die(self):
        die = FunctionCall('Die', [Value('6')])
        self.assertEqual(Parser().make_die(die), Die(6))

    def test_make_die_on_modweighteddie(self):
        die = FunctionCall('ModWeightedDie', [Group('{1: 2}'), Value('6')])
        self.assertEqual(Parser().make_die(die), ModWeightedDie({1: 2}, 6))

    def test_make_die_on_explodingon(self):
        die = FunctionCall('ExplodingOn', [FunctionCall('Die', [Value('4')]), Group('(1, 2)')])
        self.assertEqual(Parser().make_die(die), ExplodingOn(Die(4), (1, 2)))

    def test_make_int(self):
        self.assertEqual(make_int(Value('3')), 3)
        self.assertEqual(make_int(Value('-3')), -3)
        self.assertEqual(make_int(Value('0')), 0)

    def test_make_int_tuple(self):
        self.assertEqual(make_int_tuple(Group('()')), ())
        self.assertEqual(make_int_tuple(Group('(-2,)')), (-2,))
        self.assertEqual(make_int_tuple(Group('(2, 0, -2)')), (2, 0, -2))

    def test_make_int_dict(self):
        self.assertEqual(make_int_dict(Group('{}')), {})
        self.assertEqual(make_int_dict(Group('{-1: 1, 0: 0, 1: -1}')), {-1: 1, 0: 0, 1: -1})

    def test_Die(self):
        self.assertEqual(Parser().parse_die('Die(6)'), Die(6))

    def test_ModDie(self):
        self.assertEqual(Parser().parse_die('ModDie(6, 2)'), ModDie(6, 2))
        self.assertEqual(Parser().parse_die('ModDie(6, -2)'), ModDie(6, -2))
        self.assertEqual(Parser().parse_die('ModDie(6, 0)'), ModDie(6, 0))

    def test_WeightedDie(self):
        self.assertEqual(Parser().parse_die('WeightedDie({1: 2, 3: 4})'), WeightedDie({1: 2, 3: 4}))

    def test_ModWeightedDie(self):
        self.assertEqual(Parser().parse_die('ModWeightedDie({1: 2, 3: 4}, 3)'), ModWeightedDie({1: 2, 3: 4}, 3))
        self.assertEqual(Parser().parse_die('ModWeightedDie({1: 2, 3: 4}, -3)'), ModWeightedDie({1: 2, 3: 4}, -3))
        self.assertEqual(Parser().parse_die('ModWeightedDie({1: 2, 3: 4}, 0)'), ModWeightedDie({1: 2, 3: 4}, 0))

    def test_StrongDie(self):
        self.assertEqual(Parser().parse_die('StrongDie(Die(6), 2)'), StrongDie(Die(6), 2))
        self.assertEqual(Parser().parse_die('StrongDie(Die(6), -2)'), StrongDie(Die(6), -2))
        self.assertEqual(Parser().parse_die('StrongDie(Die(6), 0)'), StrongDie(Die(6), 0))

    def test_Modifier(self):
        self.assertEqual(Parser().parse_die('Modifier(6)'), Modifier(6))
        self.assertEqual(Parser().parse_die('Modifier(-6)'), Modifier(-6))
        self.assertEqual(Parser().parse_die('Modifier(0)'), Modifier(0))

    def test_Exploding(self):
        self.assertEqual(Parser().parse_die('Exploding(Die(6), 3)'), Exploding(Die(6), 3))
        self.assertEqual(Parser().parse_die('Exploding(Die(6), 0)'), Exploding(Die(6), 0))
        self.assertEqual(Parser().parse_die('Exploding(Die(6))'), Exploding(Die(6)))

    def test_ExplodingOn(self):
        self.assertEqual(Parser().parse_die('ExplodingOn(Die(6), (2, 6), 3)'), ExplodingOn(Die(6), (2, 6), 3))
        self.assertEqual(Parser().parse_die('ExplodingOn(Die(6), (2, 6), 0)'), ExplodingOn(Die(6), (2, 6), 0))
        self.assertEqual(Parser().parse_die('ExplodingOn(Die(6), (2,))'), ExplodingOn(Die(6), (2,)))
        self.assertEqual(Parser().parse_die('ExplodingOn(Die(6), ())'), ExplodingOn(Die(6), ()))

    def test_nested_dice(self):
        self.assertEqual(Parser().parse_die('Exploding(StrongDie(WeightedDie({1: 2, 3: 4}), 3), 4)'),
                         Exploding(
                             StrongDie(
                                 WeightedDie({1: 2, 3: 4}),
                                 3
                             ),
                             4
                         )
                         )

    def test_get_methods(self):
        the_parser = Parser()
        answer = {'int': make_int, 'int_dict': make_int_dict,
                  'die': the_parser.make_die, 'int_tuple': make_int_tuple}

        self.assertEqual(the_parser.get_methods(), answer)
        self.assertIsNot(the_parser.get_methods(), answer)
        self.assertNotEqual(Parser().get_methods(), answer)

    def test_get_methods_is_specific_to_each_instance_due_to_value_at_die(self):
        the_parser = Parser()
        answer = {'int': make_int, 'int_dict': make_int_dict,
                  'die': the_parser.make_die, 'int_tuple': make_int_tuple}

        self.assertNotEqual(Parser().get_methods(), answer)

    def test_get_classes(self):
        answer = {Die: ('int',), ModDie: ('int', 'int'), Modifier: ('int',), ModWeightedDie: ('int_dict', 'int'),
                  WeightedDie: ('int_dict',), StrongDie: ('die', 'int'), Exploding: ('die', 'int'),
                  ExplodingOn: ('die', 'int_tuple', 'int')}
        self.assertEqual(answer, Parser().get_classes())
        self.assertIsNot(answer, Parser().get_classes())

    def test_add_class(self):
        class Thing(object):
            pass

        parser = Parser()
        parser.add_class(Thing, ('bogus', 'lame'))

        answer = {Die: ('int',), ModDie: ('int', 'int'), Modifier: ('int',), ModWeightedDie: ('int_dict', 'int'),
                  WeightedDie: ('int_dict',), StrongDie: ('die', 'int'), Exploding: ('die', 'int'),
                  ExplodingOn: ('die', 'int_tuple', 'int'), Thing: ('bogus', 'lame')}

        self.assertEqual(answer, parser.get_classes())

    def test_add_method(self):
        a_func = lambda x: x
        parser = Parser()
        parser.add_method('make_funkiness', a_func)

        answer = {'int': make_int, 'int_dict': make_int_dict, 'make_funkiness': a_func,
                  'die': parser.make_die, 'int_tuple': make_int_tuple}
        self.assertEqual(answer, parser.get_methods())

    def test_add_class_key_override_raises_error(self):
        self.assertRaises(KeyError, Parser().add_class, Die, ('int',))

    def test_add_method_key_override_raises_error(self):
        self.assertRaises(KeyError, Parser().add_method, 'int', make_int)

    def test_reset_with_methods(self):
        a_func = lambda x: x
        parser = Parser()
        parser.add_method('make_funkiness', a_func)

        answer = {'int': make_int, 'int_dict': make_int_dict,
                  'die': parser.make_die, 'int_tuple': make_int_tuple}
        parser.reset()
        self.assertEqual(answer, parser.get_methods())

    def test_reset_with_class(self):
        class Thing(object):
            pass

        parser = Parser()
        parser.add_class(Thing, ('bogus', 'lame'))

        answer = {Die: ('int',), ModDie: ('int', 'int'), Modifier: ('int',), ModWeightedDie: ('int_dict', 'int'),
                  WeightedDie: ('int_dict',), StrongDie: ('die', 'int'), Exploding: ('die', 'int'),
                  ExplodingOn: ('die', 'int_tuple', 'int')}
        parser.reset()

        self.assertEqual(answer, parser.get_classes())

    def test_an_instance_of_parser_with_a_new_die(self):
        class StupidDie(Die):
            def __init__(self, name, size):
                self.name = name
                super(StupidDie, self).__init__(size)

            def __repr__(self):
                return 'StupidDie({!r}, {})'.format(self.name, self.get_size())

        new_parser = Parser()
        new_parser.add_method('name', lambda val_tuple: val_tuple.value[1: -1])
        new_parser.add_class(StupidDie, ('name', 'int'))

        self.assertEqual(new_parser.parse_die('StupidDie("hello", 3)'), StupidDie("hello", 3))
        self.assertEqual(new_parser.parse_die('Die(3)'), Die(3))

    def test_new_parser_class_with_new_die(self):
        class StupidDie(Die):
            def __init__(self, name, size):
                self.name = name
                super(StupidDie, self).__init__(size)

            def __repr__(self):
                return 'StupidDie({!r}, {})'.format(self.name, self.get_size())

        def make_name(value_tuple):
            return value_tuple.value[1: -1]

        class NewParser(Parser):
            def reset(self):
                super(NewParser, self).reset()
                self.add_class(StupidDie, ('name', 'int'))
                self.add_method('name', make_name)

        self.assertEqual(NewParser().parse_die('StupidDie("hello", 3)'), StupidDie("hello", 3))
        self.assertEqual(NewParser().parse_die('Die(3)'), Die(3))

    def test_new_parser_class_with_new_die_that_calls_die(self):
        class DoubleDie(Die):
            def __init__(self, die, size):
                self.die = die
                super(DoubleDie, self).__init__(size)

            def __repr__(self):
                return 'DoubleDie({!r}, {})'.format(self.die, self.get_size())

        class NewParser(Parser):
            def reset(self):
                super(NewParser, self).reset()
                self.add_class(DoubleDie, ('die', 'int'))

        self.assertEqual(NewParser().parse_die('DoubleDie(DoubleDie(Die(2), 4), 3)'),
                         DoubleDie(DoubleDie(Die(2), 4), 3))
        self.assertEqual(NewParser().parse_die('Die(3)'), Die(3))
