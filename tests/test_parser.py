# pylint: disable=missing-docstring, invalid-name, too-many-public-methods
from __future__ import absolute_import

import unittest
import ast
import sys

from dicetables.dieevents import Die, ModDie, WeightedDie, ModWeightedDie, StrongDie, Modifier, Exploding, ExplodingOn

from dicetables.parser import Parser, ParseError, ParserLimitsError, make_int, make_int_dict, make_int_tuple


class TestParser(unittest.TestCase):
    def test_init_default(self):
        self.assertFalse(Parser().ignore_case)
        self.assertFalse(Parser().disable_kwargs)

        self.assertEqual(Parser().max_nested_dice, 5)
        self.assertEqual(Parser().max_size, 500)
        self.assertEqual(Parser().max_explosions, 10)

    def test_init_setting_ignore_case(self):
        self.assertFalse(Parser(False).ignore_case)
        self.assertTrue(Parser(True).ignore_case)

    def test_init_setting_disable_kwargs(self):
        self.assertFalse(Parser(disable_kwargs=False).disable_kwargs)
        self.assertTrue(Parser(disable_kwargs=True).disable_kwargs)

    def test_init_setting_limits(self):
        self.assertEqual(Parser(max_nested_dice=10).max_nested_dice, 10)
        self.assertEqual(Parser(max_explosions=100).max_explosions, 100)
        self.assertEqual(Parser(max_size=100).max_size, 100)

    def test_make_int(self):
        self.assertEqual(make_int(ast.parse('3').body[0].value), 3)
        self.assertEqual(make_int(ast.parse('-3').body[0].value), -3)
        self.assertEqual(make_int(ast.parse('0').body[0].value), 0)

    def test_make_int_with_unary_operation_node_python_3_vs_2(self):
        unary_operation = ast.parse('-2').body[0].value
        if sys.version_info[0] > 2:
            self.assertEqual(ast.dump(unary_operation), 'UnaryOp(op=USub(), operand=Num(n=2))')
            self.assertIsInstance(unary_operation, ast.UnaryOp)
        else:
            self.assertEqual(ast.dump(unary_operation), 'Num(n=-2)')
            self.assertIsInstance(unary_operation, ast.Num)

        self.assertEqual(make_int(unary_operation), -2)

    def test_make_int_tuple(self):
        empty_node = ast.parse('()').body[0].value
        self.assertEqual(make_int_tuple(empty_node), ())

        tuple_node = ast.parse('(-2,)').body[0].value
        self.assertEqual(make_int_tuple(tuple_node), (-2,))

        tuple_node = ast.parse('(-2, 2, 0)').body[0].value
        self.assertEqual(make_int_tuple(tuple_node), (-2, 2, 0))

    def test_make_int_dict(self):
        dict_node = ast.parse('{-1: 1, 0: 0, 1: -1}').body[0].value
        self.assertEqual(make_int_dict(dict_node), {-1: 1, 0: 0, 1: -1})

        empty_dict_node = ast.parse('{}').body[0].value
        self.assertEqual(make_int_dict(empty_dict_node), {})

    def test_param_types(self):
        the_parser = Parser()
        answer = {'int': make_int, 'int_dict': make_int_dict,
                  'die': the_parser.make_die, 'int_tuple': make_int_tuple}

        self.assertEqual(the_parser.param_types, answer)
        self.assertIsNot(the_parser.param_types, answer)
        self.assertNotEqual(Parser().param_types, answer)

    def test_param_types_is_specific_to_each_instance_due_to_value_at_die(self):
        the_parser = Parser()
        answer = {'int': make_int, 'int_dict': make_int_dict,
                  'die': the_parser.make_die, 'int_tuple': make_int_tuple}

        self.assertNotEqual(Parser().param_types, answer)

    def test_classes(self):
        answer = {Die: ('int',), ModDie: ('int', 'int'), Modifier: ('int',), ModWeightedDie: ('int_dict', 'int'),
                  WeightedDie: ('int_dict',), StrongDie: ('die', 'int'), Exploding: ('die', 'int'),
                  ExplodingOn: ('die', 'int_tuple', 'int')}
        self.assertEqual(answer, Parser().classes)
        self.assertIsNot(answer, Parser().classes)

    def test_kwargs(self):
        answer = {Die: ('die_size',), ModDie: ('die_size', 'modifier'), Modifier: ('modifier',),
                  ModWeightedDie: ('dictionary_input', 'modifier'), WeightedDie: ('dictionary_input',),
                  StrongDie: ('input_die', 'multiplier'), Exploding: ('input_die', 'explosions'),
                  ExplodingOn: ('input_die', 'explodes_on', 'explosions')}
        self.assertEqual(answer, Parser().kwargs)
        self.assertIsNot(answer, Parser().kwargs)

    def test_limits_kwargs(self):
        answer = {'size': [('die_size', None), ('dictionary_input', None)],
                  'explosions': [('explosions', 2), ('explodes_on', None)]}
        self.assertEqual(Parser().limits_kwargs, answer)

    def test_make_die_raises_error_on_function_call_not_in_parser(self):
        die_node = ast.parse('NotThere()').body[0].value
        with self.assertRaises(ParseError) as cm:
            Parser().make_die(die_node)
        self.assertEqual(cm.exception.args[0], 'Die class: <NotThere> not recognized by parser.')

    def test_make_die_raises_error_on_die_with_bad_param_types(self):
        class StupidDie(Die):
            def __init__(self, name, size):
                self.name = name
                super(StupidDie, self).__init__(size)

        parser = Parser()
        parser.add_class(StupidDie, ('string', 'int'))

        die_node = ast.parse('StupidDie("Ishmael", 6)').body[0].value
        with self.assertRaises(ParseError) as cm:
            parser.make_die(die_node)
        self.assertEqual(
            cm.exception.args[0], (
                "Failed to create die: <StupidDie> with param types: ('string', 'int'). " +
                "One or more param types not recognized."
            )
        )

    def test_make_die_on_die_with_bad_param_values(self):
        die_node = ast.parse('WeightedDie({"K":2})').body[0].value
        self.assertRaises((AttributeError, TypeError), Parser().make_die, die_node)

        die_node = ast.parse('Die(12.00)').body[0].value
        self.assertRaises((AttributeError, TypeError), Parser().make_die, die_node)

    def test_make_die_on_simple_die(self):
        die_node = ast.parse('Die(6)').body[0].value
        self.assertEqual(Parser().make_die(die_node), Die(6))

    def test_make_die_on_multi_param(self):
        die_node = ast.parse('ModWeightedDie({1: 2}, 6)').body[0].value
        self.assertEqual(Parser().make_die(die_node), ModWeightedDie({1: 2}, 6))

    def test_make_die_on_die_with_recursive_call(self):
        die_node = ast.parse('ExplodingOn(Die(4), (1, 2))').body[0].value
        self.assertEqual(Parser().make_die(die_node), ExplodingOn(Die(4), (1, 2)))

    def test_make_die_default_values_do_not_need_to_be_included(self):
        die_node = ast.parse('Exploding(Die(6))').body[0].value
        self.assertEqual(Parser().make_die(die_node), Exploding(Die(6), explosions=2))

        same_die = ast.parse('Exploding(Die(6), 2)').body[0].value
        self.assertEqual(Parser().make_die(same_die), Exploding(Die(6), explosions=2))

    def test_make_die_ignore_case_true_basic_die(self):
        die_node = ast.parse('dIe(6)').body[0].value
        self.assertEqual(Parser(ignore_case=True).make_die(die_node), Die(6))

        die_node = ast.parse('Die(6)').body[0].value
        self.assertEqual(Parser(ignore_case=True).make_die(die_node), Die(6))

    def test_make_die_ignore_case_true_recursive_call(self):
        die_node = ast.parse('strONgdIE(diE(6), 3)').body[0].value
        self.assertEqual(Parser(ignore_case=True).make_die(die_node), StrongDie(Die(6), 3))

        die_node = ast.parse('StrongDie(Die(6), 3)').body[0].value
        self.assertEqual(Parser(ignore_case=True).make_die(die_node), StrongDie(Die(6), 3))

    def test_make_die_ignore_case_false_basic_die(self):
        with self.assertRaises(ParseError) as e:
            die_node = ast.parse('dIe(6)').body[0].value
            Parser(ignore_case=False).make_die(die_node)
        self.assertEqual(e.exception.args[0], 'Die class: <dIe> not recognized by parser.')

        die_node = ast.parse('dIe(6)').body[0].value
        self.assertRaises(ParseError, Parser(ignore_case=False).make_die, die_node)

        die_node = ast.parse('Die(6)').body[0].value
        self.assertEqual(Parser(ignore_case=False).make_die(die_node), Die(6))

    def test_make_die_ignore_case_false_recursive_call(self):
        with self.assertRaises(ParseError):
            die_node = ast.parse('strONgdIE(diE(6), 3)').body[0].value
            Parser(ignore_case=False).make_die(die_node)

        die_node = ast.parse('StrongDie(Die(6), 3)').body[0].value
        self.assertEqual(Parser(ignore_case=False).make_die(die_node), StrongDie(Die(6), 3))

    def test_make_die_all_kwargs(self):
        die_node = ast.parse('ModDie(die_size=6, modifier=-1)').body[0].value
        self.assertEqual(Parser().make_die(die_node), ModDie(6, -1))

    def test_make_die_some_kwargs(self):
        die_node = ast.parse('ModDie(6, modifier=-1)').body[0].value
        self.assertEqual(Parser().make_die(die_node), ModDie(6, -1))

    def test_make_die_kwargs_in_recursive_call(self):
        die_node = ast.parse('StrongDie(ModDie(6, modifier=-1), multiplier=3)').body[0].value
        self.assertEqual(Parser().make_die(die_node), StrongDie(ModDie(6, -1), 3))

    def test_make_die_kwargs_in_recursive_call_all_kwargs_in_outer_die(self):
        die_node = ast.parse('StrongDie(input_die=ModDie(6, modifier=-1), multiplier=3)').body[0].value
        self.assertEqual(Parser().make_die(die_node), StrongDie(ModDie(6, -1), 3))

    def test_make_die_incorrect_kwargs(self):
        die_node = ast.parse('ModDie(die_size=6, MODIFIER=-1)').body[0].value
        with self.assertRaises(ParseError) as cm:
            Parser().make_die(die_node), ModDie(6, -1)
        self.assertEqual(cm.exception.args[0],
                         "One or more kwargs not in kwarg_list: ('die_size', 'modifier') for die: <ModDie>")

    def test_make_die_ignore_case_applies_to_kwargs(self):
        die_node = ast.parse('MODDIE(DIE_SIZE=6, MODIFIER=-1)').body[0].value
        self.assertEqual(Parser(ignore_case=True).make_die(die_node), ModDie(6, -1))

    def test_make_die_ignore_case_applies_to_kwargs_with_mixed_case(self):
        class OddDie(Die):
            def __init__(self, dIe_SiZE):
                super(OddDie, self).__init__(dIe_SiZE)

        parser = Parser(ignore_case=True)
        parser.add_class(OddDie, ('int',))
        self.assertEqual(parser.kwargs[OddDie], ('dIe_SiZE',))

        die_node = ast.parse('ODDDIE(DIE_SIZE=6)').body[0].value
        self.assertEqual(parser.make_die(die_node), OddDie(6))

    def test_make_die_disable_kwargs(self):
        die_node = ast.parse('Die(6)').body[0].value
        self.assertEqual(Parser(disable_kwargs=True).make_die(die_node), Die(6))

    def test_make_die_disable_kwargs_raises_error(self):
        die_node = ast.parse('Die(die_size=6)').body[0].value
        with self.assertRaises(ParseError) as cm:
            Parser(disable_kwargs=True).make_die(die_node)
        self.assertEqual(cm.exception.args[0], 'Tried to use kwargs on a Parser with disable_kwargs=True')

    def test_parse_within_limits_max_size_int(self):
        self.assertEqual(Parser().parse_die_within_limits('Die(500)'), Die(500))
        self.assertRaises(ParserLimitsError, Parser().parse_die_within_limits, 'Die(501)')

    def test_parse_within_limits_max_size_dict(self):
        self.assertEqual(Parser().parse_die_within_limits('WeightedDie({500:1})'), WeightedDie({500: 1}))
        self.assertRaises(ParserLimitsError, Parser().parse_die_within_limits, 'WeightedDie({501: 1})')

    def test_parse_within_limits_max_explosions_only_explosions(self):
        self.assertEqual(Parser().parse_die_within_limits('Exploding(Die(6), 10)'), Exploding(Die(6), 10))
        self.assertRaises(ParserLimitsError, Parser().parse_die_within_limits, 'Exploding(Die(6), 11)')

    def test_parse_within_limits_max_explosions_explosions_and_explodes_on(self):
        self.assertEqual(Parser().parse_die_within_limits('ExplodingOn(Die(6), (1, 2, 3), 7)'),
                         ExplodingOn(Die(6), (1, 2, 3), 7))
        self.assertRaises(ParserLimitsError, Parser().parse_die_within_limits, 'ExplodingOn(Die(6), (1, 2, 3), 8)')

    def test_parse_within_limits_max_nested_dice(self):
        parser = Parser(max_nested_dice=3)
        depth_3 = StrongDie(StrongDie(StrongDie(Die(4), 2), 2), 2)
        depth_4 = StrongDie(StrongDie(StrongDie(StrongDie(Die(4), 2), 2), 2), 2)

        self.assertEqual(parser.parse_die_within_limits(repr(depth_3)), depth_3)
        self.assertRaises(ParserLimitsError, parser.parse_die_within_limits, repr(depth_4))

    def test_parse_die_within_limits_resets_nested_dice_counter_each_time(self):
        parser = Parser(max_nested_dice=3)
        depth_3 = StrongDie(StrongDie(StrongDie(Die(4), 2), 2), 2)
        depth_4 = StrongDie(StrongDie(StrongDie(StrongDie(Die(4), 2), 2), 2), 2)

        self.assertEqual(parser.parse_die_within_limits(repr(depth_3)), depth_3)
        self.assertEqual(parser.parse_die_within_limits(repr(depth_3)), depth_3)
        self.assertRaises(ParserLimitsError, parser.parse_die_within_limits, repr(depth_4))
        self.assertEqual(parser.parse_die_within_limits(repr(depth_3)), depth_3)

    def test_parse_within_limits_catches_violation_on_nested_call(self):
        exploding_on_error = 'StrongDie(ExplodingOn(Exploding(Die(500), 3), (1, 2), 9), 5)'
        with self.assertRaises(ParserLimitsError) as e:
            Parser().parse_die_within_limits(exploding_on_error)

        self.assertEqual(e.exception.args[0], 'Max number of explosions + len(explodes_on): 10')

    def test_parse_within_limits_does_not_catch_non_hardcoded_kwargs(self):
        class NewDie(Die):
            def __init__(self, funky_new_die_size):
                super(NewDie, self).__init__(funky_new_die_size)

        parser = Parser()
        parser.add_class(NewDie, ('int',))

        self.assertRaises(ParserLimitsError, parser.parse_die_within_limits, 'Die(5000)')
        self.assertEqual(NewDie(5000), parser.parse_die_within_limits('NewDie(5000)'))

    def test_parse_within_limits_unfilled_default_value(self):
        self.assertEqual(Parser().parse_die_within_limits('Exploding(Die(5))'), Exploding(Die(5)))
        self.assertEqual(Parser().parse_die_within_limits('ExplodingOn(Die(10), (1, 2, 3))'),
                         ExplodingOn(Die(10), (1, 2, 3)))

        self.assertRaises(ParserLimitsError, Parser().parse_die_within_limits,
                          'ExplodingOn(Die(10), (1, 2, 3, 4, 5, 6, 7, 8, 9))')

    def test_parse_within_limits_unfilled_default_value_can_pass_limiter_and_fails_elsewhere(self):
        self.assertRaises(TypeError, Parser().parse_die_within_limits, 'Die()')
        self.assertRaises(TypeError, Parser().parse_die_within_limits, 'WeightedDie()')
        self.assertRaises(TypeError, Parser().parse_die_within_limits, 'ExplodingOn(Die(6))')

    def test_parse_within_limits_error_message_nested_calls(self):
        parser = Parser(max_nested_dice=1)
        with self.assertRaises(ParserLimitsError) as e:
            parser.parse_die_within_limits('StrongDie(StrongDie(Die(6), 2), 2)')
        self.assertEqual(e.exception.args[0], 'Max number of nested dice: 1')

    def test_parse_within_limits_error_message_max_size(self):
        parser = Parser(max_size=10)
        with self.assertRaises(ParserLimitsError) as e:
            parser.parse_die_within_limits('Die(11)')
        self.assertEqual(e.exception.args[0], 'Max die_size: 10')

    def test_parse_within_limits_error_message_max_explosions(self):
        parser = Parser(max_explosions=2)
        with self.assertRaises(ParserLimitsError) as e:
            parser.parse_die_within_limits('Exploding(Die(5), 3)')
        self.assertEqual(e.exception.args[0], 'Max number of explosions + len(explodes_on): 2')

    def test_Die(self):
        self.assertEqual(Parser().parse_die('Die(6)'), Die(6))
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

    def test_Die_with_kwargs(self):
        self.assertEqual(Parser().parse_die('Die(die_size=6)'), Die(6))

    def test_ModDie_with_kwargs(self):
        self.assertEqual(Parser().parse_die('ModDie(die_size=6, modifier=-2)'), ModDie(6, -2))

    def test_WeightedDie_with_kwargs(self):
        self.assertEqual(Parser().parse_die('WeightedDie(dictionary_input={1: 2, 3: 4})'), WeightedDie({1: 2, 3: 4}))

    def test_ModWeightedDie_with_kwargs(self):
        self.assertEqual(Parser().parse_die('ModWeightedDie(dictionary_input={1: 2, 3: 4}, modifier=-3)'),
                         ModWeightedDie({1: 2, 3: 4}, -3))

    def test_StrongDie_with_kwargs(self):
        self.assertEqual(Parser().parse_die('StrongDie(input_die=Die(6), multiplier=-2)'), StrongDie(Die(6), -2))

    def test_Modifier_with_kwargs(self):
        self.assertEqual(Parser().parse_die('Modifier(modifier=-6)'), Modifier(-6))

    def test_Exploding_with_kwargs(self):
        self.assertEqual(Parser().parse_die('Exploding(input_die=Die(6), explosions=0)'), Exploding(Die(6), 0))
        self.assertEqual(Parser().parse_die('Exploding(input_die=Die(6))'), Exploding(Die(6)))

    def test_ExplodingOn_with_kwargs(self):
        self.assertEqual(Parser().parse_die('ExplodingOn(input_die=Die(6), explodes_on=(2, 6), explosions=0)'),
                         ExplodingOn(Die(6), (2, 6), 0))
        self.assertEqual(Parser().parse_die('ExplodingOn(Die(6), explodes_on=(2,))'),
                         ExplodingOn(Die(6), (2,)))

    def test_nested_dice(self):
        self.assertEqual(Parser().parse_die('Exploding(StrongDie(WeightedDie({1: 2, 3: 4}), 3), 4)'),
                         Exploding(StrongDie(WeightedDie({1: 2, 3: 4}), 3), 4))

    def test_add_class_no_auto_detect_kwargs_no_manual_kwargs(self):
        class Thing(object):
            pass

        parser = Parser()
        parser.add_class(Thing, ('bogus', 'lame'), auto_detect_kwargs=False)

        classes = {Die: ('int',), ModDie: ('int', 'int'), Modifier: ('int',), ModWeightedDie: ('int_dict', 'int'),
                   WeightedDie: ('int_dict',), StrongDie: ('die', 'int'), Exploding: ('die', 'int'),
                   ExplodingOn: ('die', 'int_tuple', 'int'), Thing: ('bogus', 'lame')}
        self.assertEqual(classes, parser.classes)

        kwargs = {Die: ('die_size',), ModDie: ('die_size', 'modifier'), Modifier: ('modifier',),
                  ModWeightedDie: ('dictionary_input', 'modifier'), WeightedDie: ('dictionary_input',),
                  StrongDie: ('input_die', 'multiplier'), Exploding: ('input_die', 'explosions'),
                  ExplodingOn: ('input_die', 'explodes_on', 'explosions'), Thing: ()}
        self.assertEqual(kwargs, parser.kwargs)

    def test_add_class_auto_detect_kwargs(self):
        class Thing(object):
            def __init__(self, num):
                self.num = num

        parser = Parser()
        parser.add_class(Thing, ('int',), auto_detect_kwargs=True)
        self.assertEqual(parser.classes[Thing], ('int',))
        self.assertEqual(parser.kwargs[Thing], ('num',))

    def test_add_class_auto_detect_kwargs_overrides_manual(self):
        class Thing(object):
            def __init__(self, num):
                self.num = num

        parser = Parser()
        parser.add_class(Thing, ('int',), auto_detect_kwargs=True, kwargs=('bite', 'my', 'shiny', 'metal', 'ass'))
        self.assertEqual(parser.classes[Thing], ('int',))
        self.assertEqual(parser.kwargs[Thing], ('num',))

    def test_add_class_manual_kwargs(self):
        class Thing(object):
            def __init__(self, num):
                self.num = num

        kwargs = ('some', 'made', 'up', 'nonsense')
        parser = Parser()
        parser.add_class(Thing, ('int',), auto_detect_kwargs=False, kwargs=kwargs)
        self.assertEqual(parser.classes[Thing], ('int',))
        self.assertEqual(parser.kwargs[Thing], kwargs)

    def test_add_class_auto_detect_raises_error_if_no_init_code(self):
        class Thing(object):
            @classmethod
            def do_stuff(cls, x):
                return cls.__name__ + x

        with self.assertRaises(AttributeError):
            Parser().add_class(Thing.do_stuff, ('str',))

        with self.assertRaises(AttributeError) as cm:
            Parser().add_class(Thing, ('str',))

        self.assertEqual(cm.exception.args[0],
                         'could not find the code for __init__ function at class_.__init__.__code__')

    def test_add_param_type(self):
        def a_func(x):
            return x

        parser = Parser()
        parser.add_param_type('make_funkiness', a_func)

        answer = {'int': make_int, 'int_dict': make_int_dict, 'make_funkiness': a_func,
                  'die': parser.make_die, 'int_tuple': make_int_tuple}
        self.assertEqual(answer, parser.param_types)

    def test_add_class_override_key(self):
        new_parser = Parser()
        new_parser.add_class(Die, ('nonsense',))

        self.assertEqual(new_parser.classes[Die], ('nonsense',))

    def test_add_param_type_override_key(self):
        new_parser = Parser()
        new_parser.add_param_type('int', int)

        self.assertEqual(new_parser.param_types['int'], int)

    def test_add_die_size_limit_kwarg_no_default_value(self):
        defaults = {'size': [('die_size', None), ('dictionary_input', None)],
                    'explosions': [('explosions', 2), ('explodes_on', None)]}
        parser = Parser()
        self.assertEqual(parser.limits_kwargs, defaults)

        parser.add_die_size_limit_kwarg('new_size_kwarg')
        answer = {'size': [('die_size', None), ('dictionary_input', None), ('new_size_kwarg', None)],
                  'explosions': [('explosions', 2), ('explodes_on', None)]}
        self.assertEqual(parser.limits_kwargs, answer)

    def test_add_die_size_limit_kwarg_with_default_value(self):
        defaults = {'size': [('die_size', None), ('dictionary_input', None)],
                    'explosions': [('explosions', 2), ('explodes_on', None)]}
        parser = Parser()
        self.assertEqual(parser.limits_kwargs, defaults)

        parser.add_die_size_limit_kwarg('new_size_kwarg', 11)
        answer = {'size': [('die_size', None), ('dictionary_input', None), ('new_size_kwarg', 11)],
                  'explosions': [('explosions', 2), ('explodes_on', None)]}
        self.assertEqual(parser.limits_kwargs, answer)

    def test_add_explosions_limit_kwarg_no_default_value(self):
        defaults = {'size': [('die_size', None), ('dictionary_input', None)],
                    'explosions': [('explosions', 2), ('explodes_on', None)]}
        parser = Parser()
        self.assertEqual(parser.limits_kwargs, defaults)

        parser.add_explosions_limit_kwarg('new_explosions_kwarg')
        answer = {'size': [('die_size', None), ('dictionary_input', None)],
                  'explosions': [('explosions', 2), ('explodes_on', None), ('new_explosions_kwarg', None)]}
        self.assertEqual(parser.limits_kwargs, answer)

    def test_add_explosions_limit_kwarg_with_default_value(self):
        defaults = {'size': [('die_size', None), ('dictionary_input', None)],
                    'explosions': [('explosions', 2), ('explodes_on', None)]}
        parser = Parser()
        self.assertEqual(parser.limits_kwargs, defaults)

        parser.add_explosions_limit_kwarg('new_explosions_kwarg', 100)
        answer = {'size': [('die_size', None), ('dictionary_input', None)],
                  'explosions': [('explosions', 2), ('explodes_on', None), ('new_explosions_kwarg', 100)]}
        self.assertEqual(parser.limits_kwargs, answer)

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
            def __init__(self, ignore_case=False, disable_kwargs=False):
                super(NewParser, self).__init__(ignore_case=ignore_case, disable_kwargs=disable_kwargs)
                self.add_class(StupidDie, ('string', 'int'))
                self.add_param_type('string', make_string)

        self.assertEqual(NewParser().parse_die('StupidDie("hello", 3)'), StupidDie("hello", 3))
        self.assertEqual(NewParser().parse_die('Die(3)'), Die(3))

    def test_new_parser_class_with_new_die_and_kwargs(self):
        class StupidDie(Die):
            def __init__(self, name, size):
                self.name = name
                super(StupidDie, self).__init__(size)

            def __eq__(self, other):
                return super(StupidDie, self).__eq__(other) and self.name == other.name

        def make_string(str_node):
            return str_node.s

        class NewParser(Parser):
            def __init__(self, ignore_case=False, disable_kwargs=False):
                super(NewParser, self).__init__(ignore_case=ignore_case, disable_kwargs=disable_kwargs)
                self.add_class(StupidDie, ('string', 'int'), kwargs=('name', 'size'))
                self.add_param_type('string', make_string)

        self.assertEqual(NewParser().parse_die('StupidDie(name="hello", size=3)'), StupidDie("hello", 3))
        self.assertEqual(NewParser().parse_die('Die(3)'), Die(3))

    def test_new_parser_class_with_new_die_that_calls_die(self):
        class DoubleDie(Die):
            def __init__(self, die, size):
                self.die = die
                super(DoubleDie, self).__init__(size)

            def __eq__(self, other):
                return super(DoubleDie, self).__eq__(other) and self.die == other.die

        class NewParser(Parser):
            def __init__(self, ignore_case=False, disable_kwargs=False):
                super(NewParser, self).__init__(ignore_case=ignore_case, disable_kwargs=disable_kwargs)
                self.add_class(DoubleDie, ('die', 'int'))

        self.assertEqual(NewParser().parse_die('DoubleDie(DoubleDie(Die(2), 4), 3)'),
                         DoubleDie(DoubleDie(Die(2), 4), 3))
        self.assertEqual(NewParser().parse_die('Die(3)'), Die(3))

    # parse_within_limits_new_die
    def test_parse_within_limits_new_die_size_kwarg_int(self):
        class NewDie(Die):
            def __init__(self, funky_new_die_size):
                super(NewDie, self).__init__(funky_new_die_size)

        parser = Parser()
        parser.add_class(NewDie, ('int',))
        parser.add_die_size_limit_kwarg('funky_new_die_size')
        self.assertRaises(ParserLimitsError, parser.parse_die_within_limits, 'NewDie(5000)')
        self.assertRaises(ParserLimitsError, parser.parse_die_within_limits, 'Die(5000)')

    def test_parse_within_limits_new_die_size_kwarg_dict(self):
        class NewDie(WeightedDie):
            def __init__(self, funky_new_die_dict):
                super(NewDie, self).__init__(funky_new_die_dict)

        parser = Parser()
        parser.add_class(NewDie, ('int_dict',))
        parser.add_die_size_limit_kwarg('funky_new_die_dict')
        self.assertRaises(ParserLimitsError, parser.parse_die_within_limits, 'NewDie({5000: 1})')
        self.assertRaises(ParserLimitsError, parser.parse_die_within_limits, 'WeightedDie({5000: 1})')

    def test_parse_within_limits_new_die_size_kwarg_error(self):
        class NewDie(Die):
            def __init__(self, size_int_as_str):
                super(NewDie, self).__init__(int(size_int_as_str))

        def make_string(str_node):
            return str_node.s

        parser = Parser()
        parser.add_param_type('string', make_string)
        parser.add_class(NewDie, ('string',))
        parser.add_die_size_limit_kwarg('size_int_as_str')

        self.assertEqual(parser.parse_die('NewDie("5")'), NewDie("5"))

        with self.assertRaises(ValueError) as e:
            parser.parse_die_within_limits('NewDie("5")')
        self.assertEqual(e.exception.args[0],
                         'A kwarg declared as a "die size limit" is neither an int nor a dict of ints.')

        self.assertRaises(ParserLimitsError, parser.parse_die_within_limits, 'WeightedDie({5000: 1})')

    def test_parse_within_limits_new_explosions_kwarg_int(self):
        class NewDie(ExplodingOn):
            def __init__(self, input_die, explodes_on, biiiiig_booooooms=2):
                super(NewDie, self).__init__(input_die, explodes_on, biiiiig_booooooms)

        parser = Parser()
        parser.add_class(NewDie, ('die', 'int_tuple', 'int'))
        parser.add_explosions_limit_kwarg('biiiiig_booooooms')
        self.assertRaises(ParserLimitsError, parser.parse_die_within_limits, 'NewDie(Die(5), (1, 2), 9)')
        self.assertRaises(ParserLimitsError, parser.parse_die_within_limits, 'ExplodingOn(Die(5), (1, 2), 9)')

    def test_parse_within_limits_new_explosions_kwarg_int_tuple(self):
        class NewDie(ExplodingOn):
            def __init__(self, input_die, boom_points, explosions=2):
                super(NewDie, self).__init__(input_die, boom_points, explosions)

        parser = Parser()
        parser.add_class(NewDie, ('die', 'int_tuple', 'int'))
        parser.add_explosions_limit_kwarg('boom_points')
        self.assertRaises(ParserLimitsError, parser.parse_die_within_limits, 'NewDie(Die(5), (1, 2), 9)')
        self.assertRaises(ParserLimitsError, parser.parse_die_within_limits, 'ExplodingOn(Die(5), (1, 2), 9)')

    def test_parse_within_limits_new_explosions_kwarg_error(self):
        class NewDie(ExplodingOn):
            def __init__(self, input_die, explodes_on, str_splosions="2"):
                super(NewDie, self).__init__(input_die, explodes_on, int(str_splosions))

        def make_string(str_node):
            return str_node.s

        parser = Parser()
        parser.add_param_type('string', make_string)
        parser.add_class(NewDie, ('die', 'int_tuple', 'string'))
        parser.add_explosions_limit_kwarg('str_splosions')

        self.assertEqual(parser.parse_die('NewDie(Die(5), (1, 2), "5")'), NewDie(Die(5), (1, 2), "5"))

        with self.assertRaises(ValueError) as e:
            parser.parse_die_within_limits('NewDie(Die(5), (1, 2), "9")')
        self.assertEqual(e.exception.args[0],
                         'A kwarg declared as an "explosions limit" is neither an int nor a tuple/list of ints.')

        self.assertRaises(ParserLimitsError, parser.parse_die_within_limits, 'ExplodingOn(Die(5), (1, 2), 9)')

    def test_parse_wihtin_limits_new_size_kwarg_with_defualts(self):
        class NewDie(Die):
            def __init__(self, funky_new_die_size=5000):
                super(NewDie, self).__init__(funky_new_die_size)

        parser = Parser()
        parser.add_class(NewDie, ('int',))
        parser.add_die_size_limit_kwarg('funky_new_die_size', 5000)
        self.assertEqual(parser.parse_die('NewDie()'), NewDie())
        self.assertRaises(ParserLimitsError, parser.parse_die_within_limits, 'NewDie()')

    def test_parse_within_limits_new_explosions_kwarg_with_defaults(self):
        class NewDie(ExplodingOn):
            def __init__(self, input_die, explodes_on, biiiiig_booooooms=11):
                super(NewDie, self).__init__(input_die, explodes_on, biiiiig_booooooms)

        parser = Parser()
        parser.add_class(NewDie, ('die', 'int_tuple', 'int'))
        parser.add_explosions_limit_kwarg('biiiiig_booooooms', 11)
        self.assertEqual(parser.parse_die('NewDie(Die(5), (1, 2))'), NewDie(Die(5), (1, 2)))
        self.assertRaises(ParserLimitsError, parser.parse_die_within_limits, 'NewDie(Die(5), (1, 2))')

    def test_parse_within_limits_kwarg_with_defaults_beyond_scope_ignoring_limits(self):
        class NewDie(Die):
            def __init__(self, funky_new_die_size=5000):
                super(NewDie, self).__init__(funky_new_die_size)

        parser = Parser()
        parser.add_class(NewDie, ('int',))
        parser.add_die_size_limit_kwarg('funky_new_die_size', 5)
        self.assertEqual(parser.parse_die('NewDie()'), NewDie(5000))
        self.assertEqual(parser.parse_die_within_limits('NewDie()'), NewDie(5000))

    def test_parse_within_limits_kwarg_with_defaults_beyond_scope_catching_false_limits(self):
        class NewDie(Die):
            def __init__(self, funky_new_die_size=5):
                super(NewDie, self).__init__(funky_new_die_size)

        parser = Parser()
        parser.add_class(NewDie, ('int',))
        parser.add_die_size_limit_kwarg('funky_new_die_size', 5000)
        self.assertEqual(parser.parse_die('NewDie()'), NewDie(5))
        self.assertRaises(ParserLimitsError, parser.parse_die_within_limits, 'NewDie()')


if __name__ == '__main__':
    unittest.main()
