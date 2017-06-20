# pylint: disable=missing-docstring, invalid-name, too-many-public-methods
from __future__ import absolute_import

import unittest
import ast
import sys

from dicetables.dieevents import Die, ModDie, WeightedDie, ModWeightedDie, StrongDie, Modifier, Exploding, ExplodingOn

from dicetables.parser import Parser, ParseError, make_int, make_int_dict, make_int_tuple


class TestParser(unittest.TestCase):
    def test_init_default(self):
        self.assertFalse(Parser().ignore_case)

    def test_init_setting_ignore_case(self):
        self.assertFalse(Parser(False).ignore_case)
        self.assertTrue(Parser(True).ignore_case)

    def test_get_param_types(self):
        the_parser = Parser()
        answer = {'int': make_int, 'int_dict': make_int_dict,
                  'die': the_parser.make_die, 'int_tuple': make_int_tuple}

        self.assertEqual(the_parser.get_param_types(), answer)
        self.assertIsNot(the_parser.get_param_types(), answer)
        self.assertNotEqual(Parser().get_param_types(), answer)

    def test_get_param_types_is_specific_to_each_instance_due_to_value_at_die(self):
        the_parser = Parser()
        answer = {'int': make_int, 'int_dict': make_int_dict,
                  'die': the_parser.make_die, 'int_tuple': make_int_tuple}

        self.assertNotEqual(Parser().get_param_types(), answer)

    def test_get_classes(self):
        answer = {Die: ('int',), ModDie: ('int', 'int'), Modifier: ('int',), ModWeightedDie: ('int_dict', 'int'),
                  WeightedDie: ('int_dict',), StrongDie: ('die', 'int'), Exploding: ('die', 'int'),
                  ExplodingOn: ('die', 'int_tuple', 'int')}
        self.assertEqual(answer, Parser().get_classes())
        self.assertIsNot(answer, Parser().get_classes())

    def test_make_int(self):
        self.assertEqual(make_int(ast.Num(n=3)), 3)
        self.assertEqual(make_int(ast.Num(n=-3)), -3)
        self.assertEqual(make_int(ast.Num(n=0)), 0)

    def test_make_int_with_unary_operation_node_python_3_vs_2(self):
        unary_operation = ast.parse('- 2').body[0].value
        if sys.version_info[0] > 2:
            self.assertEqual(ast.dump(unary_operation), 'UnaryOp(op=USub(), operand=Num(n=2))')
            self.assertIsInstance(unary_operation, ast.UnaryOp)
        else:
            self.assertEqual(ast.dump(unary_operation), 'Num(n=-2)')
            self.assertIsInstance(unary_operation, ast.Num)

        self.assertEqual(make_int(unary_operation), -2)

    def test_make_int_tuple(self):
        self.assertEqual(make_int_tuple(ast.Tuple(elts=[])), ())
        self.assertEqual(make_int_tuple(ast.Tuple(elts=[ast.Num(n=-2)])), (-2,))
        self.assertEqual(make_int_tuple(ast.Tuple(elts=[ast.Num(n=2), ast.Num(n=0), ast.Num(n=-2)])), (2, 0, -2))

    def test_make_int_tuple_with_unary_operation_node_python_3_vs_2(self):
        tuple_node = ast.parse('(-2,)').body[0].value
        if sys.version_info[0] > 2:
            self.assertIsInstance(tuple_node.elts[0], ast.UnaryOp)
            self.assertEqual(ast.dump(tuple_node), 'Tuple(elts=[UnaryOp(op=USub(), operand=Num(n=2))], ctx=Load())')
        else:
            self.assertIsInstance(tuple_node.elts[0], ast.Num)
            self.assertEqual(ast.dump(tuple_node), 'Tuple(elts=[Num(n=-2)], ctx=Load())')

        self.assertEqual(make_int_tuple(tuple_node), (-2,))

    def test_make_int_dict(self):
        self.assertEqual(
            make_int_dict(
                ast.Dict(keys=[ast.Num(n=-1), ast.Num(n=0), ast.Num(n=1)],
                         values=[ast.Num(n=1), ast.Num(n=0), ast.Num(n=-1)])
            ),
            {-1: 1, 0: 0, 1: -1})
        self.assertEqual(
            make_int_dict(
                ast.Dict(keys=[],
                         values=[])
            ),
            {})

    def test_make_int_dict_with_unary_operation_nodes_python_3_vs_2(self):
        dict_node = ast.parse('{-2: -2}').body[0].value
        if sys.version_info[0] > 2:
            self.assertIsInstance(dict_node.keys[0], ast.UnaryOp)
            self.assertIsInstance(dict_node.values[0], ast.UnaryOp)
            self.assertEqual(
                ast.dump(dict_node),
                'Dict(keys=[UnaryOp(op=USub(), operand=Num(n=2))], values=[UnaryOp(op=USub(), operand=Num(n=2))])'
            )
        else:
            self.assertIsInstance(dict_node.keys[0], ast.Num)
            self.assertIsInstance(dict_node.values[0], ast.Num)
            self.assertEqual(
                ast.dump(dict_node),
                'Dict(keys=[Num(n=-2)], values=[Num(n=-2)])'
            )

        self.assertEqual(make_int_dict(dict_node), {-2: -2})

    def test_make_die_raises_error_on_function_call_not_in_parser(self):
        die = ast.parse('NotThere()').body[0].value
        with self.assertRaises(ParseError) as cm:
            Parser().make_die(die)
        self.assertEqual(cm.exception.args[0], 'Die class: <NotThere> not recognized by parser.')

    def test_make_die_raises_error_on_die_with_bad_param_types(self):
        class StupidDie(Die):
            def __init__(self, name, size):
                self.name = name
                super(StupidDie, self).__init__(size)

        parser = Parser()
        parser.add_class(StupidDie, ('string', 'int'))

        die = ast.parse('StupidDie("Ishmael", 6)').body[0].value
        with self.assertRaises(ParseError) as cm:
            parser.make_die(die)
        self.assertEqual(
            cm.exception.args[0], (
                "Failed to create die: <StupidDie> with param types: ('string', 'int'). " +
                "One or more param types not recognized."
            )
        )

    def test_make_die_on_simple_die(self):
        die = ast.parse('Die(6)').body[0].value
        self.assertEqual(Parser().make_die(die), Die(6))

    def test_make_die_on_multi_param(self):
        die = ast.parse('ModWeightedDie({1: 2}, 6)').body[0].value
        self.assertEqual(Parser().make_die(die), ModWeightedDie({1: 2}, 6))

    def test_make_die_on_die_with_recursive_call(self):
        die = ast.parse('ExplodingOn(Die(4), (1, 2))').body[0].value
        self.assertEqual(Parser().make_die(die), ExplodingOn(Die(4), (1, 2)))

    def test_make_die_default_values_do_not_need_to_be_included(self):
        die = ast.parse('Exploding(Die(6))').body[0].value
        self.assertEqual(Parser().make_die(die), Exploding(Die(6), explosions=2))

        same_die = ast.parse('Exploding(Die(6), 2)').body[0].value
        self.assertEqual(Parser().make_die(same_die), Exploding(Die(6), explosions=2))

    def test_make_die_ignore_case_true_basic_die(self):
        die = ast.parse('dIe(6)').body[0].value
        self.assertEqual(Parser(ignore_case=True).make_die(die), Die(6))

        die = ast.parse('Die(6)').body[0].value
        self.assertEqual(Parser(ignore_case=True).make_die(die), Die(6))

    def test_make_die_ignore_case_true_recursive_call(self):
        die = ast.parse('strONgdIE(diE(6), 3)').body[0].value
        self.assertEqual(Parser(ignore_case=True).make_die(die), StrongDie(Die(6), 3))

        die = ast.parse('StrongDie(Die(6), 3)').body[0].value
        self.assertEqual(Parser(ignore_case=True).make_die(die), StrongDie(Die(6), 3))

    def test_make_die_ignore_case_false_basic_die(self):
        with self.assertRaises(ParseError):
            die = ast.parse('dIe(6)').body[0].value
            self.assertEqual(Parser(ignore_case=False).make_die(die), Die(6))

        die = ast.parse('Die(6)').body[0].value
        self.assertEqual(Parser(ignore_case=False).make_die(die), Die(6))

    def test_make_die_ignore_case_false_recursive_call(self):
        with self.assertRaises(ParseError):
            die = ast.parse('strONgdIE(diE(6), 3)').body[0].value
            self.assertEqual(Parser(ignore_case=False).make_die(die), StrongDie(Die(6), 3))

        die = ast.parse('StrongDie(Die(6), 3)').body[0].value
        self.assertEqual(Parser(ignore_case=False).make_die(die), StrongDie(Die(6), 3))

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

    def test_add_class(self):
        class Thing(object):
            pass

        parser = Parser()
        parser.add_class(Thing, ('bogus', 'lame'))

        answer = {Die: ('int',), ModDie: ('int', 'int'), Modifier: ('int',), ModWeightedDie: ('int_dict', 'int'),
                  WeightedDie: ('int_dict',), StrongDie: ('die', 'int'), Exploding: ('die', 'int'),
                  ExplodingOn: ('die', 'int_tuple', 'int'), Thing: ('bogus', 'lame')}

        self.assertEqual(answer, parser.get_classes())

    def test_add_param_type(self):
        def a_func(x):
            return x

        parser = Parser()
        parser.add_param_type('make_funkiness', a_func)

        answer = {'int': make_int, 'int_dict': make_int_dict, 'make_funkiness': a_func,
                  'die': parser.make_die, 'int_tuple': make_int_tuple}
        self.assertEqual(answer, parser.get_param_types())

    def test_add_class_override_key(self):
        new_parser = Parser()
        new_parser.add_class(Die, ('nonsense',))

        self.assertEqual(new_parser.get_classes()[Die], ('nonsense',))

    def test_add_param_type_override_key(self):
        new_parser = Parser()
        new_parser.add_param_type('int', int)

        self.assertEqual(new_parser.get_param_types()['int'], int)

    def test_an_instance_of_parser_with_a_new_die(self):
        class StupidDie(Die):
            def __init__(self, name, size):
                self.name = name
                super(StupidDie, self).__init__(size)

            def __eq__(self, other):
                return super(StupidDie, self).__eq__(other) and self.name == other.name

        new_parser = Parser()
        new_parser.add_param_type('string', lambda str_node: str_node.s)
        new_parser.add_class(StupidDie, ('string', 'int'))

        self.assertEqual(new_parser.parse_die('StupidDie("hello", 3)'), StupidDie("hello", 3))
        self.assertEqual(new_parser.parse_die('Die(3)'), Die(3))

    def test_new_parser_class_with_new_die(self):
        class StupidDie(Die):
            def __init__(self, name, size):
                self.name = name
                super(StupidDie, self).__init__(size)

            def __eq__(self, other):
                return super(StupidDie, self).__eq__(other) and self.name == other.name

        def make_string(str_node):
            return str_node.s

        class NewParser(Parser):
            def __init__(self, ignore_case=False):
                super(NewParser, self).__init__(ignore_case=ignore_case)
                self.add_class(StupidDie, ('string', 'int'))
                self.add_param_type('string', make_string)

        self.assertEqual(NewParser().parse_die('StupidDie("hello", 3)'), StupidDie("hello", 3))
        self.assertEqual(NewParser().parse_die('Die(3)'), Die(3))

    def test_new_parser_class_with_new_die_that_calls_die(self):
        class DoubleDie(Die):
            def __init__(self, die, size):
                self.die = die
                super(DoubleDie, self).__init__(size)

            def __eq__(self, other):
                return super(DoubleDie, self).__eq__(other) and self.die == other.die

        class NewParser(Parser):
            def __init__(self, ignore_case=False):
                super(NewParser, self).__init__(ignore_case=ignore_case)
                self.add_class(DoubleDie, ('die', 'int'))

        self.assertEqual(NewParser().parse_die('DoubleDie(DoubleDie(Die(2), 4), 3)'),
                         DoubleDie(DoubleDie(Die(2), 4), 3))
        self.assertEqual(NewParser().parse_die('Die(3)'), Die(3))


if __name__ == '__main__':
    unittest.main()
