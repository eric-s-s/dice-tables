# pylint: disable=missing-docstring, invalid-name, too-many-public-methods


import ast
from typing import Dict, Iterable

import pytest

from dicetables.bestworstmid import (
    BestOfDicePool,
    WorstOfDicePool,
    UpperMidOfDicePool,
    LowerMidOfDicePool,
)
from dicetables.dieevents import (
    Die,
    ModDie,
    WeightedDie,
    ModWeightedDie,
    StrongDie,
    Modifier,
    Exploding,
    ExplodingOn,
)
from dicetables.eventsbases.protodie import ProtoDie
from dicetables.parser import (
    ParseError,
)
from dicetables.new_parser import (
    NewParser,
    make_int,
    make_int_dict,
    make_int_tuple,
)
from dicetables.tools.limit_checker import LimitsError


def test_init_setting_ignore_case():
    assert not NewParser(False).ignore_case
    assert NewParser(True).ignore_case


def test_classes_property():
    parser = NewParser()
    assert parser.classes == {Die, Modifier, ModDie, WeightedDie, ModWeightedDie, StrongDie, Exploding, ExplodingOn,
                              BestOfDicePool, WorstOfDicePool, UpperMidOfDicePool, LowerMidOfDicePool}
    assert parser.classes is not parser.classes


@pytest.mark.parametrize("input_value", ["2", "-2", "0"])
def test_make_int(input_value):
    assert make_int(ast.parse(input_value).body[0].value) == int(input_value)


def test_make_int_error():
    with pytest.raises(ValueError):
        make_int(ast.parse("'a'").body[0].value)


@pytest.mark.parametrize("tuple_value", [(), (2,), (-2, 2, 0)])
def test_make_int_tuple(tuple_value):
    node = ast.parse(str(tuple_value)).body[0].value
    assert make_int_tuple(node) == tuple_value


def test_make_int_tuple_error():
    with pytest.raises(ValueError):
        make_int_tuple(ast.parse("('a', 1, 2)").body[0].value)


@pytest.mark.parametrize("dict_value", [dict(), {-1: -2, 0: 0, 3: 4}])
def test_make_int_dict(dict_value):
    node = ast.parse(str(dict_value)).body[0].value
    assert make_int_dict(node) == dict_value


def test_make_int_dict_error():
    with pytest.raises(ValueError):
        make_int_dict(ast.parse("{'a': 'b'}").body[0].value)


def test_param_types():
    the_parser = NewParser()
    answer = {
        int: make_int,
        Dict[int, int]: make_int_dict,
        ProtoDie: the_parser.make_die,
        Iterable[int]: make_int_tuple,
    }

    assert the_parser.param_types == answer
    assert the_parser.param_types is not answer


def test_param_types_is_specific_to_each_instance():
    parser = NewParser()
    assert NewParser().param_types != parser.param_types


def test_make_die_raises_error_on_function_call_not_in_parser():
    die_node = ast.parse("NotThere()").body[0].value
    with pytest.raises(ParseError) as cm:
        NewParser().make_die(die_node)
    assert cm.value.args[0] == "Die class: <NotThere> not recognized by parser."


def test_make_die_on_die_with_bad_param_values():
    die_node = ast.parse('WeightedDie({"K":2})').body[0].value
    with pytest.raises(ValueError):
        NewParser().make_die(die_node)

    die_node = ast.parse("Die(12.00)").body[0].value
    with pytest.raises(ValueError):
        NewParser().make_die(die_node)


def test_make_die_on_simple_die():
    die_node = ast.parse("Die(6)").body[0].value
    assert NewParser().make_die(die_node) == Die(6)


def test_make_die_on_multi_param():
    die_node = ast.parse("ModWeightedDie({1: 2}, 6)").body[0].value
    assert NewParser().make_die(die_node) == ModWeightedDie({1: 2}, 6)


def test_make_die_on_die_with_recursive_call():
    die_node = ast.parse("ExplodingOn(Die(4), (1, 2))").body[0].value
    assert NewParser().make_die(die_node) == ExplodingOn(Die(4), (1, 2))


def test_make_die_default_values_do_not_need_to_be_included():
    die_node = ast.parse("Exploding(Die(6))").body[0].value
    assert NewParser().make_die(die_node) == Exploding(Die(6), explosions=2)

    same_die = ast.parse("Exploding(Die(6), 2)").body[0].value
    assert NewParser().make_die(same_die) == Exploding(Die(6), explosions=2)


def test_make_die_ignore_case_true_basic_die():
    die_node = ast.parse("dIe(6)").body[0].value
    assert NewParser(ignore_case=True).make_die(die_node) == Die(6)

    die_node = ast.parse("Die(6)").body[0].value
    assert NewParser(ignore_case=True).make_die(die_node) == Die(6)


def test_make_die_ignore_case_true_recursive_call():
    die_node = ast.parse("strONgdIE(diE(6), 3)").body[0].value
    assert NewParser(ignore_case=True).make_die(die_node) == StrongDie(Die(6), 3)

    die_node = ast.parse("StrongDie(Die(6), 3)").body[0].value
    assert NewParser(ignore_case=True).make_die(die_node) == StrongDie(Die(6), 3)


def test_make_die_ignore_case_false_basic_die():
    die_node = ast.parse("dIe(6)").body[0].value
    with pytest.raises(ParseError):
        NewParser(ignore_case=False).make_die(die_node)

    die_node = ast.parse("Die(6)").body[0].value
    assert NewParser(ignore_case=False).make_die(die_node) == Die(6)


def test_make_die_ignore_case_false_recursive_call():
    die_node = ast.parse("strONgdIE(diE(6), 3)").body[0].value
    with pytest.raises(ParseError):
        NewParser(ignore_case=False).make_die(die_node)

    die_node = ast.parse("StrongDie(Die(6), 3)").body[0].value
    assert NewParser(ignore_case=False).make_die(die_node) == StrongDie(Die(6), 3)


def test_make_die_all_kwargs():
    die_node = ast.parse("ModDie(die_size=6, modifier=-1)").body[0].value
    assert NewParser().make_die(die_node) == ModDie(6, -1)


def test_make_die_some_kwargs():
    die_node = ast.parse("ModDie(6, modifier=-1)").body[0].value
    assert NewParser().make_die(die_node) == ModDie(6, -1)


def test_make_die_kwargs_in_recursive_call():
    die_node = (
        ast.parse("StrongDie(ModDie(6, modifier=-1), multiplier=3)").body[0].value
    )
    assert NewParser().make_die(die_node) == StrongDie(ModDie(6, -1), 3)


def test_make_die_kwargs_in_recursive_call_all_kwargs_in_outer_die():
    die_node = (
        ast.parse("StrongDie(input_die=ModDie(6, modifier=-1), multiplier=3)")
        .body[0]
        .value
    )
    assert NewParser().make_die(die_node) == StrongDie(ModDie(6, -1), 3)


def test_make_die_incorrect_kwargs():
    die_node = ast.parse("ModDie(die_size=6, MODIFIER=-1)").body[0].value
    msg = r"The keyword: MODIFIER is not in the die signature: \(die_size: ?int, modifier: ?int\)"
    with pytest.raises(ParseError, match=msg):
        NewParser().make_die(die_node), ModDie(6, -1)


def test_make_die_ignore_case_applies_to_kwargs():
    die_node = ast.parse("MODDIE(DIE_SIZE=6, MODIFIER=-1)").body[0].value
    assert NewParser(ignore_case=True).make_die(die_node) == ModDie(6, -1)


def test_parse_arbitrary_spacing():
    assert NewParser().parse_die("   Die  ( 5  )  ") == Die(5)
    assert NewParser().parse_die("   Die  ( die_size = 5  )  ") == Die(5)
    assert NewParser().parse_die(
        "   Exploding ( Die  ( die_size = 5  ) ,  1 ) "
    ) == Exploding(Die(5), 1)


def test_walk_dice_calls():
    parser = NewParser()
    multiplier = 20
    die_string = ("StrongDie(" * multiplier) + "Die(6)" + (", 3)" * multiplier)
    result = parser.walk_dice_calls(ast.parse(die_string).body[0].value)
    expected_die = 1
    expected_strong_die = multiplier
    result_list = list(result)
    assert result_list.count(Die) == expected_die
    assert result_list.count(StrongDie) == expected_strong_die
    assert len(result_list) == expected_die + expected_strong_die


def test_walk_dice_calls_complex():
    die = "Die"
    strong_die = "StrongDie"
    mod_die = "ModDie"
    parser = NewParser()
    die_string = f"{die}({strong_die}(), {mod_die}(3, {die}({strong_die}(3))))"
    result = parser.walk_dice_calls(ast.parse(die_string).body[0].value)
    expected_die = 2
    expected_strong_die = 2
    expected_mod_die = 1
    result_list = list(result)
    assert result_list.count(Die) == expected_die
    assert result_list.count(StrongDie) == expected_strong_die
    assert result_list.count(ModDie) == expected_mod_die
    assert len(result_list) == expected_die + expected_strong_die + expected_mod_die


def test_walk_dice_calls_bad_value():
    parser = NewParser()
    result = parser.walk_dice_calls(ast.parse("Die(Oops(3))").body[0].value)
    with pytest.raises(ParseError):
        list(result)


class TestParserWithLimits(object):
    def test_parse_within_limits_max_size_int(self):
        assert NewParser.with_limits().parse_die("Die(500)") == Die(500)
        with pytest.raises(LimitsError):
            NewParser.with_limits().parse_die("Die(501)")

    def test_parse_within_limits_max_size_dict(self):
        assert NewParser.with_limits().parse_die("WeightedDie({500:1})") == WeightedDie(
            {500: 1}
        )
        with pytest.raises(LimitsError):
            NewParser.with_limits().parse_die("WeightedDie({501: 1})")

    def test_parse_within_limits_max_explosions_only_explosions(self):
        assert NewParser.with_limits().parse_die("Exploding(Die(6),  10)") == Exploding(
            Die(6), 10
        )
        with pytest.raises(LimitsError):
            NewParser.with_limits().parse_die("Exploding(Die(6), 11)")

    def test_parse_within_limits_max_explosions_explosions_and_explodes_on(self):
        actual = NewParser.with_limits().parse_die("ExplodingOn(Die(6), (1, 2, 3), 7)")
        assert actual == ExplodingOn(Die(6), (1, 2, 3), 7)
        with pytest.raises(LimitsError):
            NewParser.with_limits().parse_die("ExplodingOn(Die(6), (1, 2, 3), 8)")

    def test_parse_within_limits_dice_pool_passes_and_fails(self):
        actual = NewParser.with_limits().parse_die("BestOfDicePool(Die(3), 5, 1)")
        assert actual == BestOfDicePool(Die(3), 5, 1)
        with pytest.raises(LimitsError):
            NewParser.with_limits().parse_die("BestOfDicePool(Die(3), 600, 1)")

        actual = NewParser.with_limits().parse_die("WorstOfDicePool(Die(3), 5, 1)")
        assert actual == WorstOfDicePool(Die(3), 5, 1)
        with pytest.raises(LimitsError):
            NewParser.with_limits().parse_die("WorstOfDicePool(Die(3), 600, 1)")

        actual = NewParser.with_limits().parse_die("UpperMidOfDicePool(Die(3), 5, 1)")
        assert actual == UpperMidOfDicePool(Die(3), 5, 1)
        with pytest.raises(LimitsError):
            NewParser.with_limits().parse_die("UpperMidOfDicePool(Die(3), 600, 1)")

        actual = NewParser.with_limits().parse_die("LowerMidOfDicePool(Die(3), 5, 1)")
        assert actual == LowerMidOfDicePool(Die(3), 5, 1)
        with pytest.raises(LimitsError):
            NewParser.with_limits().parse_die("LowerMidOfDicePool(Die(3), 600, 1)")

    def test_parse_within_limits_max_nested_dice(self):
        parser = NewParser.with_limits(max_dice=4)
        depth_4 = StrongDie(StrongDie(StrongDie(Die(4), 2), 2), 2)
        depth_5 = StrongDie(StrongDie(StrongDie(StrongDie(Die(4), 2), 2), 2), 2)

        assert parser.parse_die(repr(depth_4)) == depth_4
        with pytest.raises(LimitsError):
            parser.parse_die(repr(depth_5))


@pytest.mark.parametrize(
    "die",
    [
        Die(6),
        ModDie(6, 2),
        ModDie(6, 0),
        ModDie(6, -2),
        WeightedDie({1: 2, 3: 4}),
        ModWeightedDie({1: 2, 3: 4}, 2),
        ModWeightedDie({1: 2, 3: 4}, 0),
        ModWeightedDie({1: 2, 3: 4}, -2),
        StrongDie(Die(6), 2),
        StrongDie(Die(6), 0),
        StrongDie(Die(6), -2),
        Modifier(4),
        Modifier(0),
        Modifier(-4),
        Exploding(Die(6), 3),
        Exploding(Die(6), 0),
        Exploding(Die(6)),
        ExplodingOn(Die(6), (2, 6), 3),
        ExplodingOn(Die(6), (2, 6), 0),
        ExplodingOn(Die(6), (2,)),
        ExplodingOn(Die(6), ()),
        BestOfDicePool(Die(2), 5, 2),
        BestOfDicePool(Die(2), 5, 5),
        BestOfDicePool(Die(2), 5, 0),
        WorstOfDicePool(Die(2), 5, 2),
        UpperMidOfDicePool(Die(2), 5, 2),
        LowerMidOfDicePool(Die(2), 5, 2),
    ],
    ids=lambda el: repr(el),
)
def test_parse_die(die):
    assert NewParser().parse_die(repr(die)) == die


def test_die_with_kwargs():
    assert NewParser().parse_die("Die(die_size=6)") == Die(6)


def test_mod_die_with_kwargs():
    assert NewParser().parse_die("ModDie(die_size=6, modifier=-2)") == ModDie(6, -2)


def test_weighted_die_with_kwargs():
    assert NewParser().parse_die(
        "WeightedDie(dictionary_input={1: 2, 3: 4})"
    ) == WeightedDie({1: 2, 3: 4})


def test_mod_weighted_die_with_kwargs():
    actual = NewParser().parse_die(
        "ModWeightedDie(dictionary_input={1: 2, 3: 4}, modifier=-3)"
    )
    assert actual == ModWeightedDie({1: 2, 3: 4}, -3)


def test_strong_die_with_kwargs():
    assert NewParser().parse_die(
        "StrongDie(input_die=Die(6), multiplier=-2)"
    ) == StrongDie(Die(6), -2)


def test_modifier_with_kwargs():
    assert NewParser().parse_die("Modifier(modifier=-6)") == Modifier(-6)


def test_exploding_with_kwargs():
    assert NewParser().parse_die(
        "Exploding(input_die=Die(6), explosions=0)"
    ) == Exploding(Die(6), 0)
    assert NewParser().parse_die("Exploding(input_die=Die(6))") == Exploding(Die(6))


def test_exploding_on_with_kwargs():
    actual = NewParser().parse_die(
        "ExplodingOn(input_die=Die(6), explodes_on=(2, 6), explosions=0)"
    )
    assert actual == ExplodingOn(Die(6), (2, 6), 0)
    assert NewParser().parse_die(
        "ExplodingOn(Die(6), explodes_on=(2,))"
    ) == ExplodingOn(Die(6), (2,))


def test_best_of_dice_pool_with_kwargs():
    actual = NewParser().parse_die(
        "BestOfDicePool(input_die=Die(2), pool_size=5, select=2)"
    )
    assert actual == BestOfDicePool(Die(2), 5, 2)


def test_worst_of_dice_pool_with_kwargs():
    actual = NewParser().parse_die(
        "WorstOfDicePool(input_die=Die(2), pool_size=5, select=2)"
    )
    assert actual == WorstOfDicePool(Die(2), 5, 2)


def test_upper_mid_of_dice_pool_with_kwargs():
    actual = NewParser().parse_die(
        "UpperMidOfDicePool(input_die=Die(2), pool_size=5, select=2)"
    )
    assert actual == UpperMidOfDicePool(Die(2), 5, 2)


def test_lower_mid_of_dice_pool_with_kwargs():
    actual = NewParser().parse_die(
        "LowerMidOfDicePool(input_die=Die(2), pool_size=5, select=2)"
    )
    assert actual == LowerMidOfDicePool(Die(2), 5, 2)


def test_nested_dice():
    actual = NewParser().parse_die(
        "Exploding(StrongDie(WeightedDie({1: 2, 3: 4}), 3), 4)"
    )
    assert actual == Exploding(StrongDie(WeightedDie({1: 2, 3: 4}), 3), 4)


def test_add_class_un_recognized_param_types_raises_error():
    class StupidDie(Die):
        def __init__(self, name: str, size: int):
            self.name = name
            super(StupidDie, self).__init__(size)

    parser = NewParser()
    msg = r"The signature: \(name: ?str, size: ?int\) has one or more un-recognized param types"
    with pytest.raises(ParseError, match=msg):
        parser.add_class(StupidDie)


def test_add_class_missing_type_hint_raises_error():
    class StupidDie(Die):
        def __init__(self, name, size: int):
            self.name = name
            super(StupidDie, self).__init__(size)

    parser = NewParser()
    msg = r"The signature: \(name, size: ?int\) is missing type annotations"
    with pytest.raises(ParseError, match=msg):
        parser.add_class(StupidDie)


def test_add_class_auto_detect_kwargs():
    class Thing(object):
        def __init__(self, num: int):
            self.num = num

        def __eq__(self, other):
            return self.num == other.num

    parser = NewParser()
    parser.add_class(Thing)
    actual = parser.parse_die("Thing(num=3)")
    other_actual = parser.parse_die("Thing(3)")
    expected = Thing(3)
    assert actual == expected
    assert other_actual == expected


def test_add_class_okay_if_init_parameters():
    class Thing(object):
        pass

    NewParser().add_class(Thing)


def test_add_class_raises_error_if_no_type_hinting():
    class Thing(object):
        def __init__(self, num):
            self.num = num

    with pytest.raises(ParseError):
        NewParser().add_class(Thing)


def test_add_param_type():
    def a_func(x):
        return x

    parser = NewParser()
    parser.add_param_type(str, a_func)

    answer = {
        int: make_int,
        Dict[int, int]: make_int_dict,
        str: a_func,
        ProtoDie: parser.make_die,
        Iterable[int]: make_int_tuple,
    }
    assert answer == parser.param_types


def test_new_parser_class_with_new_die():
    class StupidDie(Die):
        def __init__(self, name: str, size: int):
            self.name = name
            super(StupidDie, self).__init__(size)

        def __eq__(self, other):
            return super(StupidDie, self).__eq__(other) and self.name == other.name

    def make_string(str_node):
        return str_node.s

    class NewNewParser(NewParser):
        def __init__(self, *args, **kwargs):
            super(NewNewParser, self).__init__(*args, **kwargs)
            self.add_param_type(str, make_string)
            self.add_class(StupidDie)

    assert NewNewParser().parse_die('StupidDie("hello", 3)') == StupidDie("hello", 3)
    assert NewNewParser().parse_die('StupidDie(name="hello", size=3)') == StupidDie(
        "hello", 3
    )
    assert NewNewParser().parse_die("Die(3)") == Die(3)


def test_new_parser_class_with_new_die_that_calls_die():
    class DoubleDie(Die):
        def __init__(self, die: ProtoDie, size: int):
            self.die = die
            super(DoubleDie, self).__init__(size)

        def __eq__(self, other):
            return super(DoubleDie, self).__eq__(other) and self.die == other.die

    class NewNewParser(NewParser):
        def __init__(self, *args, **kwargs):
            super(NewNewParser, self).__init__(*args, **kwargs)
            self.add_class(DoubleDie)

    assert NewNewParser().parse_die("DoubleDie(DoubleDie(Die(2), 4), 3)") == DoubleDie(
        DoubleDie(Die(2), 4), 3
    )
    assert NewNewParser().parse_die("Die(3)") == Die(3)


def test_parser_with_limits_fails_to_check_size_with_new_key_word():
    class NewDie(Die):
        def __init__(self, kwazy_size: int):
            super(NewDie, self).__init__(kwazy_size)

    parser = NewParser.with_limits(max_size=5)
    parser.add_class(NewDie)

    with pytest.raises(LimitsError):
        parser.parse_die("Die(6)")

    parser.parse_die("NewDie(6)")
