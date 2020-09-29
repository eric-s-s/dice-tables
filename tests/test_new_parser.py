# pylint: disable=missing-docstring, invalid-name, too-many-public-methods


import ast
import re
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
    LimitsError,
)
from dicetables.new_parser import (
    NewParser,
    make_int,
    make_int_dict,
    make_int_tuple,
)
from dicetables.tools.orderedcombinations import count_unique_combination_keys


def test_init_default():
    assert not NewParser().ignore_case

    assert NewParser().max_nested_dice == 5
    assert NewParser().max_size == 500
    assert NewParser().max_explosions == 10


def test_init_setting_ignore_case():
    assert not NewParser(False).ignore_case
    assert NewParser(True).ignore_case


def test_init_setting_limits():
    assert NewParser(max_nested_dice=10).max_nested_dice == 10
    assert NewParser(max_explosions=100).max_explosions == 100
    assert NewParser(max_size=100).max_size == 100


@pytest.mark.parametrize('input_value', ["2", "-2", "0"])
def test_make_int(input_value):
    assert make_int(ast.parse(input_value).body[0].value) == int(input_value)


def test_make_int_error():
    with pytest.raises(ValueError):
        make_int(ast.parse("'a'").body[0].value)


@pytest.mark.parametrize('tuple_value', [(), (2,), (-2, 2, 0)])
def test_make_int_tuple(tuple_value):
    node = ast.parse(str(tuple_value)).body[0].value
    assert make_int_tuple(node) == tuple_value


def test_make_int_tuple_error():
    with pytest.raises(ValueError):
        make_int_tuple(ast.parse("('a', 1, 2)").body[0].value)


@pytest.mark.parametrize('dict_value', [dict(), {-1: -2, 0: 0, 3: 4}])
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
    die_string = ('StrongDie(' * multiplier) + 'Die(6)' + (', 3)' * multiplier)
    result = parser.walk_dice_calls(ast.parse(die_string).body[0].value)
    expected_die = 1
    expected_strong_die = multiplier
    result_list = list(result)
    assert result_list.count(Die) == expected_die
    assert result_list.count(StrongDie) == expected_strong_die
    assert len(result_list) == expected_die + expected_strong_die


def test_walk_dice_calls_complex():
    die = 'Die'
    strong_die = 'StrongDie'
    mod_die = 'ModDie'
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
    result = parser.walk_dice_calls(ast.parse('Die(Oops(3))').body[0].value)
    with pytest.raises(ParseError):
        list(result)


def test_parse_within_limits_max_size_int():
    assert NewParser().parse_die_within_limits("Die(500)") == Die(500)
    with pytest.raises(LimitsError):
        NewParser().parse_die_within_limits("Die(501)")


def test_parse_within_limits_and_then_regular_parse():
    parser = NewParser()
    parser.parse_die_within_limits('Die(500)')
    expected = parser.parse_die('Die(501)')
    assert expected == Die(501)


def test_parse_within_limits_max_size_dict():
    assert NewParser().parse_die_within_limits("WeightedDie({500:1})") == WeightedDie(
        {500: 1}
    )
    with pytest.raises(LimitsError):
        NewParser().parse_die_within_limits("WeightedDie({501: 1})")


def test_parse_within_limits_max_explosions_only_explosions():
    assert NewParser().parse_die_within_limits("Exploding(Die(6),  10)") == Exploding(
        Die(6), 10
    )
    with pytest.raises(LimitsError):
        NewParser().parse_die_within_limits("Exploding(Die(6), 11)")


def test_parse_within_limits_max_explosions_explosions_and_explodes_on():
    actual = NewParser().parse_die_within_limits("ExplodingOn(Die(6), (1, 2, 3), 7)")
    assert actual == ExplodingOn(Die(6), (1, 2, 3), 7)
    with pytest.raises(LimitsError):
        NewParser().parse_die_within_limits("ExplodingOn(Die(6), (1, 2, 3), 8)")


def test_parse_within_limits_dice_pool_passes_and_fails():
    actual = NewParser().parse_die_within_limits("BestOfDicePool(Die(3), 5, 1)")
    assert actual == BestOfDicePool(Die(3), 5, 1)
    with pytest.raises(LimitsError):
        NewParser().parse_die_within_limits("BestOfDicePool(Die(3), 600, 1)")

    actual = NewParser().parse_die_within_limits("WorstOfDicePool(Die(3), 5, 1)")
    assert actual == WorstOfDicePool(Die(3), 5, 1)
    with pytest.raises(LimitsError):
        NewParser().parse_die_within_limits("WorstOfDicePool(Die(3), 600, 1)")

    actual = NewParser().parse_die_within_limits("UpperMidOfDicePool(Die(3), 5, 1)")
    assert actual == UpperMidOfDicePool(Die(3), 5, 1)
    with pytest.raises(LimitsError):
        NewParser().parse_die_within_limits("UpperMidOfDicePool(Die(3), 600, 1)")

    actual = NewParser().parse_die_within_limits("LowerMidOfDicePool(Die(3), 5, 1)")
    assert actual == LowerMidOfDicePool(Die(3), 5, 1)
    with pytest.raises(LimitsError):
        NewParser().parse_die_within_limits("LowerMidOfDicePool(Die(3), 600, 1)")


def test_parse_within_limits_white_box_test_of_dice_pool():
    assert NewParser()._check_dice_pool(Die(3), 5) is None
    with pytest.raises(LimitsError):
        NewParser()._check_dice_pool(Die(3), 131)


def test_parse_within_limits_white_box_test_of_dice_pool_uses_dict_size_not_dice_size():
    die = WeightedDie({1: 2, 2: 1, 100: 2})
    assert die.get_size() == 100
    assert len(die.get_dict()) == 3

    assert NewParser()._check_dice_pool(die, 130) is None
    with pytest.raises(LimitsError):
        NewParser()._check_dice_pool(die, 131)

    die = Exploding(Die(6))
    assert die.get_size() == 6
    assert len(die.get_dict()) == 16

    assert NewParser()._check_dice_pool(die, 7) is None
    with pytest.raises(LimitsError):
        NewParser()._check_dice_pool(die, 8)


@pytest.mark.parametrize(
    "die_size,die_pool,max_combinations",
    [
        (2, 599, 600),
        (3, 130, 8700),
        (4, 54, 30000),
        (5, 31, 55000),
        (6, 21, 70000),
        (7, 16, 100000),
        (12, 9, 200000),
        (30, 4, 250000),
        (100, 3, 250000),
    ],
)
def test_parse_within_limits_white_box_test_dice_pool_each_dictionary_limit(
        die_size, die_pool, max_combinations
):
    """
    self.max_dice_pool_combinations_per_dict_size = {
        2: 600, 3: 8700, 4: 30000, 5: 55000, 6: 70000,
        7: 100000, 12: 200000, 30: 250000
    }
    """
    with pytest.raises(LimitsError):
        NewParser().parse_die_within_limits("BestOfDicePool(Die(1), 1, 1)")

    assert count_unique_combination_keys(Die(die_size), die_pool) <= max_combinations
    assert count_unique_combination_keys(Die(die_size), die_pool + 1) > max_combinations
    assert NewParser()._check_dice_pool(Die(die_size), die_pool) is None
    with pytest.raises(LimitsError):
        NewParser()._check_dice_pool(Die(die_size), die_pool + 1)


def test_parse_within_limits_max_nested_dice():
    parser = NewParser(max_nested_dice=3)
    depth_3 = StrongDie(StrongDie(StrongDie(Die(4), 2), 2), 2)
    depth_4 = StrongDie(StrongDie(StrongDie(StrongDie(Die(4), 2), 2), 2), 2)

    assert parser.parse_die_within_limits(repr(depth_3)) == depth_3
    with pytest.raises(LimitsError):
        parser.parse_die_within_limits(repr(depth_4))
    # Can be parsed if no limits.
    assert parser.parse_die(repr(depth_4)) == depth_4


def test_parse_die_within_limits_resets_nested_dice_counter_each_time():
    parser = NewParser(max_nested_dice=3)
    depth_3 = StrongDie(StrongDie(StrongDie(Die(4), 2), 2), 2)
    depth_4 = StrongDie(StrongDie(StrongDie(StrongDie(Die(4), 2), 2), 2), 2)

    assert parser.parse_die_within_limits(repr(depth_3)) == depth_3
    assert parser.parse_die_within_limits(repr(depth_3)) == depth_3
    with pytest.raises(LimitsError):
        parser.parse_die_within_limits(repr(depth_4))
    assert parser.parse_die_within_limits(repr(depth_3)) == depth_3


def test_parse_within_limits_max_dice_pool_calls():
    parser = NewParser(max_nested_dice=3)
    two_calls = BestOfDicePool(WorstOfDicePool(Die(2), 3, 2), 3, 2)
    two_calls_alt = UpperMidOfDicePool(LowerMidOfDicePool(Die(2), 3, 2), 3, 2)
    two_pools_three_nested_dice = BestOfDicePool(
        StrongDie(WorstOfDicePool(Die(2), 3, 2), 2), 3, 2
    )
    three_calls = BestOfDicePool(
        BestOfDicePool(WorstOfDicePool(Die(2), 3, 2), 3, 2), 3, 2
    )

    assert parser.parse_die_within_limits(repr(two_calls)) == two_calls
    assert parser.parse_die_within_limits(repr(two_calls_alt)) == two_calls_alt
    assert (
            parser.parse_die_within_limits(repr(two_pools_three_nested_dice))
            == two_pools_three_nested_dice
    )
    with pytest.raises(LimitsError):
        parser.parse_die_within_limits(repr(three_calls))
    # Can be parsed if no limits.
    assert parser.parse_die(repr(three_calls)) == three_calls


def test_parse_within_limits_dice_pool_calls_are_still_nested_die_calls():
    parser = NewParser(max_nested_dice=3)
    depth_4 = BestOfDicePool(StrongDie(StrongDie(StrongDie(Die(2), 2), 2), 2), 2, 2)
    with pytest.raises(LimitsError):
        parser.parse_die_within_limits(repr(depth_4))


def test_parse_die_within_limits_resets_dice_pool_counter_each_time():
    parser = NewParser(max_nested_dice=3)
    two_calls = BestOfDicePool(WorstOfDicePool(Die(2), 3, 2), 3, 2)
    three_calls = BestOfDicePool(
        BestOfDicePool(WorstOfDicePool(Die(2), 3, 2), 3, 2), 3, 2
    )

    assert parser.parse_die_within_limits(repr(two_calls)) == two_calls
    assert parser.parse_die_within_limits(repr(two_calls)) == two_calls
    with pytest.raises(LimitsError):
        parser.parse_die_within_limits(repr(three_calls))
    assert parser.parse_die_within_limits(repr(two_calls)) == two_calls


def test_parse_within_limits_catches_violation_on_nested_call():
    exploding_on_error = "StrongDie(ExplodingOn(Exploding(Die(500), 3), (1, 2), 9), 5)"
    msg = re.escape("Max number of explosions + len(explodes_on): 10")
    with pytest.raises(LimitsError, match=msg):
        NewParser().parse_die_within_limits(exploding_on_error)


def test_parse_within_limits_does_not_catch_non_hardcoded_kwargs():
    class NewDie(Die):
        def __init__(self, funky_new_die_size):
            super(NewDie, self).__init__(funky_new_die_size)

    parser = NewParser()
    parser.add_class(NewDie)

    with pytest.raises(LimitsError):
        parser.parse_die_within_limits("Die(5000)")
    assert NewDie(5000) == parser.parse_die_within_limits("NewDie(5000)")


def test_parse_within_limits_white_box_test_non_hardcoded_kwargs_for_dicepool():
    """This could be run as a regular blackbox test, but it would take 0.5s for this single test."""

    class IgnoresLimits(BestOfDicePool):
        def __init__(self, a_die, pool_size, select):
            super(IgnoresLimits, self).__init__(a_die, pool_size, select)

    class AlsoIgnoresLimits(BestOfDicePool):
        def __init__(self, input_die, poolio, select):
            super(AlsoIgnoresLimits, self).__init__(input_die, poolio, select)

    class CatchesLimits(BestOfDicePool):
        def __init__(self, input_die, pool_size, selection):
            super(CatchesLimits, self).__init__(input_die, pool_size, selection)

    parser = NewParser()
    parser.add_class(IgnoresLimits, ("die", "int", "int"))
    parser.add_class(AlsoIgnoresLimits, ("die", "int", "int"))
    parser.add_class(CatchesLimits, ("die", "int", "int"))

    assert parser._dice_pool_counter == 0
    assert parser._check_limits(IgnoresLimits, (Die(6), 1000, 900), ()) is None
    assert parser._dice_pool_counter == 1  # It checked Limits for DicePool and passed

    parser._dice_pool_counter = 0
    assert parser._check_limits(AlsoIgnoresLimits, (Die(6), 1000, 900), ()) is None
    assert parser._dice_pool_counter == 1  # It checked Limits for DicePool and passed

    parser._dice_pool_counter = 0
    with pytest.raises(LimitsError):
        parser._check_limits(CatchesLimits, (Die(6), 1000, 900), ())
    assert parser._dice_pool_counter == 1  # It checked Limits for DicePool and failed


def test_parse_within_limits_unfilled_default_value():
    assert NewParser().parse_die_within_limits("Exploding(Die(5))") == Exploding(Die(5))
    actual = NewParser().parse_die_within_limits("ExplodingOn(Die(10), (1, 2, 3))")
    assert actual == ExplodingOn(Die(10), (1, 2, 3))

    with pytest.raises(LimitsError):
        NewParser().parse_die_within_limits(
            "ExplodingOn(Die(10), (1, 2, 3, 4, 5, 6, 7, 8, 9))"
        )


def test_parse_within_limits_unfilled_default_value_can_pass_limiter_and_fails_elsewhere():
    with pytest.raises(TypeError):
        NewParser().parse_die_within_limits("Die()")
    with pytest.raises(TypeError):
        NewParser().parse_die_within_limits("WeightedDie()")
    with pytest.raises(TypeError):
        NewParser().parse_die_within_limits("ExplodingOn(Die(6))")


def test_parse_within_limits_error_message_nested_calls():
    parser = NewParser(max_nested_dice=1)
    msg = "Max number of nested dice: 1"
    with pytest.raises(LimitsError, match=msg):
        parser.parse_die_within_limits("StrongDie(StrongDie(Die(6), 2), 2)")


def test_parse_within_limits_error_message_max_size():
    parser = NewParser(max_size=10)
    msg = "Max die_size: 10"
    with pytest.raises(LimitsError, match=msg):
        parser.parse_die_within_limits("Die(11)")


def test_parse_within_limits_error_message_max_explosions():
    parser = NewParser(max_explosions=2)
    msg = re.escape("Max number of explosions + len(explodes_on): 2")
    with pytest.raises(LimitsError, match=msg):
        parser.parse_die_within_limits("Exploding(Die(5), 3)")


def test_parse_within_limits_error_message_dice_pool():
    msg = re.escape(
        "Die(6) has a get_dict() of size: 6\nFor this die, the largest permitted pool_size is 21"
    )
    with pytest.raises(LimitsError, match=msg):
        NewParser().parse_die_within_limits("BestOfDicePool(Die(6), 100, 1)")


def test_parse_within_limits_error_message_dice_pool_calls():
    three_calls = BestOfDicePool(
        BestOfDicePool(WorstOfDicePool(Die(2), 3, 2), 3, 2), 3, 2
    )
    msg = "Max number of DicePool objects: 2"
    with pytest.raises(LimitsError, match=msg):
        NewParser().parse_die_within_limits(repr(three_calls))


def test_die():
    assert NewParser().parse_die("Die(6)") == Die(6)


def test_mod_die():
    assert NewParser().parse_die("ModDie(6, 2)") == ModDie(6, 2)
    assert NewParser().parse_die("ModDie(6, -2)") == ModDie(6, -2)
    assert NewParser().parse_die("ModDie(6, 0)") == ModDie(6, 0)


def test_weighted_die():
    assert NewParser().parse_die("WeightedDie({1: 2, 3: 4})") == WeightedDie({1: 2, 3: 4})


def test_mod_weighted_die():
    assert NewParser().parse_die("ModWeightedDie({1: 2, 3: 4}, 3)") == ModWeightedDie(
        {1: 2, 3: 4}, 3
    )
    assert NewParser().parse_die("ModWeightedDie({1: 2, 3: 4}, -3)") == ModWeightedDie(
        {1: 2, 3: 4}, -3
    )
    assert NewParser().parse_die("ModWeightedDie({1: 2, 3: 4}, 0)") == ModWeightedDie(
        {1: 2, 3: 4}, 0
    )


def test_strong_die():
    assert NewParser().parse_die("StrongDie(Die(6), 2)") == StrongDie(Die(6), 2)
    assert NewParser().parse_die("StrongDie(Die(6), -2)") == StrongDie(Die(6), -2)
    assert NewParser().parse_die("StrongDie(Die(6), 0)") == StrongDie(Die(6), 0)


def test_modifier():
    assert NewParser().parse_die("Modifier(6)") == Modifier(6)
    assert NewParser().parse_die("Modifier(-6)") == Modifier(-6)
    assert NewParser().parse_die("Modifier(0)") == Modifier(0)


def test_exploding():
    assert NewParser().parse_die("Exploding(Die(6), 3)") == Exploding(Die(6), 3)
    assert NewParser().parse_die("Exploding(Die(6), 0)") == Exploding(Die(6), 0)
    assert NewParser().parse_die("Exploding(Die(6))") == Exploding(Die(6))


def test_exploding_on():
    assert NewParser().parse_die("ExplodingOn(Die(6), (2, 6), 3)") == ExplodingOn(
        Die(6), (2, 6), 3
    )
    assert NewParser().parse_die("ExplodingOn(Die(6), (2, 6), 0)") == ExplodingOn(
        Die(6), (2, 6), 0
    )
    assert NewParser().parse_die("ExplodingOn(Die(6), (2,))") == ExplodingOn(Die(6), (2,))
    assert NewParser().parse_die("ExplodingOn(Die(6), ())") == ExplodingOn(Die(6), ())


def test_best_of_dice_pool():
    assert NewParser().parse_die("BestOfDicePool(Die(2), 5, 2)") == BestOfDicePool(
        Die(2), 5, 2
    )
    assert NewParser().parse_die("BestOfDicePool(Die(2), 5, 5)") == BestOfDicePool(
        Die(2), 5, 5
    )
    assert NewParser().parse_die("BestOfDicePool(Die(2), 5, 0)") == BestOfDicePool(
        Die(2), 5, 0
    )


def test_worst_of_dice_pool():
    assert NewParser().parse_die("WorstOfDicePool(Die(2), 5, 2)") == WorstOfDicePool(
        Die(2), 5, 2
    )


def test_upper_mid_of_dice_pool():
    assert NewParser().parse_die("UpperMidOfDicePool(Die(2), 5, 2)") == UpperMidOfDicePool(
        Die(2), 5, 2
    )


def test_lower_mid_of_dice_pool():
    assert NewParser().parse_die("LowerMidOfDicePool(Die(2), 5, 2)") == LowerMidOfDicePool(
        Die(2), 5, 2
    )


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
    assert NewParser().parse_die("Exploding(input_die=Die(6), explosions=0)") == Exploding(
        Die(6), 0
    )
    assert NewParser().parse_die("Exploding(input_die=Die(6))") == Exploding(Die(6))


def test_exploding_on_with_kwargs():
    actual = NewParser().parse_die(
        "ExplodingOn(input_die=Die(6), explodes_on=(2, 6), explosions=0)"
    )
    assert actual == ExplodingOn(Die(6), (2, 6), 0)
    assert NewParser().parse_die("ExplodingOn(Die(6), explodes_on=(2,))") == ExplodingOn(
        Die(6), (2,)
    )


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
    actual = NewParser().parse_die("Exploding(StrongDie(WeightedDie({1: 2, 3: 4}), 3), 4)")
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
    actual = parser.parse_die('Thing(num=3)')
    other_actual = parser.parse_die('Thing(3)')
    expected = Thing(3)
    assert actual == expected
    assert other_actual == expected


def test_add_class_auto_detect_raises_error_if_no_init_code():
    class Thing(object):
        pass

    msg = "could not find the code for __init__ function at class_.__init__.__code__"
    with pytest.raises(AttributeError, match=msg):
        NewParser().add_class(Thing)


def test_add_class_raises_error_if_no_type_hinting():
    class Thing(object):
        def __init__(self, num):
            self.num = num

    with pytest.raises(AttributeError):
        NewParser().add_class(Thing)


# def test_add_param_type():
#     def a_func(x):
#         return x
#
#     parser = NewParser()
#     parser.add_param_type(, a_func)
#
#     answer = {
#         "int": make_int,
#         "int_dict": make_int_dict,
#         "make_funkiness": a_func,
#         "die": parser.make_die,
#         "int_tuple": make_int_tuple,
#     }
#     assert answer == parser.param_types
#
#
# def test_add_class_override_key():
#     new_parser = NewParser()
#     new_parser.add_class(Die, ("nonsense",))
#
#     assert new_parser.classes[Die] == ("nonsense",)
#
#
# def test_add_param_type_override_key():
#     new_parser = NewParser()
#     new_parser.add_param_type("int", int)
#
#     assert new_parser.param_types["int"] == int
#
#
# def test_add_limits_kwarg_no_default_value():
#     defaults = {
#         "size": [("die_size", None), ("dictionary_input", None)],
#         "explosions": [("explosions", 2)],
#         "explodes_on": [("explodes_on", None)],
#         "input_die": [("input_die", None)],
#         "pool_size": [("pool_size", None)],
#     }
#     parser = NewParser()
#     assert parser.limits_kwargs == defaults
#
#     parser.add_limits_kwarg("size", "new_size_kwarg")
#     answer = {
#         "size": [
#             ("die_size", None),
#             ("dictionary_input", None),
#             ("new_size_kwarg", None),
#         ],
#         "explosions": [("explosions", 2)],
#         "explodes_on": [("explodes_on", None)],
#         "input_die": [("input_die", None)],
#         "pool_size": [("pool_size", None)],
#     }
#     assert parser.limits_kwargs == answer
#
#     parser.add_limits_kwarg("pool_size", "new_pool")
#     answer["pool_size"].append(("new_pool", None))
#     assert parser.limits_kwargs == answer
#
#
# def test_add_limits_kwarg_with_default_value():
#     parser = NewParser()
#     parser.add_limits_kwarg("size", "new_size_kwarg", 11)
#     answer = {
#         "size": [
#             ("die_size", None),
#             ("dictionary_input", None),
#             ("new_size_kwarg", 11),
#         ],
#         "explosions": [("explosions", 2)],
#         "explodes_on": [("explodes_on", None)],
#         "input_die": [("input_die", None)],
#         "pool_size": [("pool_size", None)],
#     }
#     assert parser.limits_kwargs == answer
#
#
# def test_add_limits_kwarg_all_keys():
#     parser = NewParser()
#     answer = parser.limits_kwargs.copy()
#     for key in answer.keys():
#         new_kwarg = "new_{}".format(key)
#         default = 1
#         parser.add_limits_kwarg(key, new_kwarg, default)
#         answer[key].append((new_kwarg, default))
#     assert parser.limits_kwargs == answer
#
#
# def test_add_limits_kwarg_key_not_present():
#     parser = NewParser()
#     expected = parser.limits_kwargs.copy()
#     msg = 'key: "oops" not in self.limits_kwargs. Use add_limits_key.'
#     with pytest.raises(KeyError, match=msg):
#         parser.add_limits_kwarg("oops", "sie", "daisy")
#     assert parser.limits_kwargs == expected
#
#
# def test_add_limits_key():
#     parser = NewParser()
#     expected = parser.limits_kwargs.copy()
#     parser.add_limits_key("so_new")
#     expected["so_new"] = []
#     assert expected == parser.limits_kwargs
#
#     parser.add_limits_kwarg("so_new", "new!")
#
#     expected["so_new"] = [("new!", None)]
#     assert expected == parser.limits_kwargs
#
#
# def test_add_limits_key_error():
#     existing_key = "size"
#     msg = "Tried to add existing key to self.limits_kwargs."
#     with pytest.raises(ValueError, match=msg):
#         NewParser().add_limits_key(existing_key)
#
#
# def test_an_instance_of_parser_with_a_new_die():
#     class StupidDie(Die):
#         def __init__(self, name, size):
#             self.name = name
#             super(StupidDie, self).__init__(size)
#
#         def __eq__(self, other):
#             return super(StupidDie, self).__eq__(other) and self.name == other.name
#
#     new_parser = NewParser()
#     new_parser.add_param_type("string", lambda str_node: str_node.s)
#     new_parser.add_class(StupidDie, ("string", "int"))
#
#     assert new_parser.parse_die('StupidDie("hello", 3)') == StupidDie("hello", 3)
#     assert new_parser.parse_die("Die(3)") == Die(3)
#
#
# def test_new_parser_class_with_new_die():
#     class StupidDie(Die):
#         def __init__(self, name, size):
#             self.name = name
#             super(StupidDie, self).__init__(size)
#
#         def __eq__(self, other):
#             return super(StupidDie, self).__eq__(other) and self.name == other.name
#
#     def make_string(str_node):
#         return str_node.s
#
#     class NewNewParser(Parser):
#         def __init__(self, ignore_case=False, disable_kwargs=False):
#             super(NewNewParser, self).__init__(
#                 ignore_case=ignore_case, disable_kwargs=disable_kwargs
#             )
#             self.add_class(StupidDie, ("string", "int"))
#             self.add_param_type("string", make_string)
#
#     assert NewNewParser().parse_die('StupidDie("hello", 3)') == StupidDie("hello", 3)
#     assert NewNewParser().parse_die("Die(3)") == Die(3)
#
#
# def test_new_parser_class_with_new_die_and_kwargs():
#     class StupidDie(Die):
#         def __init__(self, name, size):
#             self.name = name
#             super(StupidDie, self).__init__(size)
#
#         def __eq__(self, other):
#             return super(StupidDie, self).__eq__(other) and self.name == other.name
#
#     def make_string(str_node):
#         return str_node.s
#
#     class NewNewParser(Parser):
#         def __init__(self, ignore_case=False, disable_kwargs=False):
#             super(NewNewParser, self).__init__(
#                 ignore_case=ignore_case, disable_kwargs=disable_kwargs
#             )
#             self.add_class(StupidDie, ("string", "int"), kwargs=("name", "size"))
#             self.add_param_type("string", make_string)
#
#     assert NewNewParser().parse_die('StupidDie(name="hello", size=3)') == StupidDie(
#         "hello", 3
#     )
#     assert NewNewParser().parse_die("Die(3)") == Die(3)
#
#
# def test_new_parser_class_with_new_die_that_calls_die():
#     class DoubleDie(Die):
#         def __init__(self, die, size):
#             self.die = die
#             super(DoubleDie, self).__init__(size)
#
#         def __eq__(self, other):
#             return super(DoubleDie, self).__eq__(other) and self.die == other.die
#
#     class NewNewParser(Parser):
#         def __init__(self, ignore_case=False, disable_kwargs=False):
#             super(NewNewParser, self).__init__(
#                 ignore_case=ignore_case, disable_kwargs=disable_kwargs
#             )
#             self.add_class(DoubleDie, ("die", "int"))
#
#     assert NewNewParser().parse_die("DoubleDie(DoubleDie(Die(2), 4), 3)") == DoubleDie(
#         DoubleDie(Die(2), 4), 3
#     )
#     assert NewNewParser().parse_die("Die(3)") == Die(3)
#
#
# # parse_within_limits_new_die
# def test_parse_within_limits_new_die_preserves_original_kwargs():
#     class NewDie(Die):
#         def __init__(self, name, die_size):
#             self.name = name
#             super(NewDie, self).__init__(die_size=die_size)
#
#     def make_string(str_node):
#         return str_node.s
#
#     parser = NewParser()
#     parser.add_param_type("string", make_string)
#     parser.add_class(NewDie, ("string", "int"))
#     with pytest.raises(LimitsError):
#         parser.parse_die_within_limits('NewDie("bob", 501)')
#
#
# def test_parse_within_limits_new_die_size_kwarg_int():
#     class NewDie(Die):
#         def __init__(self, funky_new_die_size):
#             super(NewDie, self).__init__(funky_new_die_size)
#
#     parser = NewParser()
#     parser.add_class(NewDie, ("int",))
#     parser.add_limits_kwarg("size", "funky_new_die_size")
#     with pytest.raises(LimitsError):
#         parser.parse_die_within_limits("NewDie(5000)")
#     with pytest.raises(LimitsError):
#         parser.parse_die_within_limits("Die(5000)")
#
#
# def test_parse_within_limits_new_die_size_kwarg_dict():
#     class NewDie(WeightedDie):
#         def __init__(self, funky_new_die_dict):
#             super(NewDie, self).__init__(funky_new_die_dict)
#
#     parser = NewParser()
#     parser.add_class(NewDie, ("int_dict",))
#     parser.add_limits_kwarg("size", "funky_new_die_dict")
#     with pytest.raises(LimitsError):
#         parser.parse_die_within_limits("NewDie({5000: 1})")
#     with pytest.raises(LimitsError):
#         parser.parse_die_within_limits("WeightedDie({5000: 1})")
#
#
# def test_parse_within_limits_new_die_size_kwarg_error():
#     class NewDie(Die):
#         def __init__(self, size_int_as_str):
#             super(NewDie, self).__init__(int(size_int_as_str))
#
#     def make_string(str_node):
#         return str_node.s
#
#     parser = NewParser()
#     parser.add_param_type("string", make_string)
#     parser.add_class(NewDie, ("string",))
#     parser.add_limits_kwarg("size", "size_int_as_str")
#
#     assert parser.parse_die('NewDie("5")') == NewDie("5")
#
#     msg = 'A kwarg declared as a "die size limit" is neither an int nor a dict of ints.'
#     with pytest.raises(ValueError, match=msg):
#         parser.parse_die_within_limits('NewDie("5")')
#
#     with pytest.raises(LimitsError):
#         parser.parse_die_within_limits("WeightedDie({5000: 1})")
#
#
# def test_parse_within_limits_new_explosions_kwarg_int():
#     class NewDie(ExplodingOn):
#         def __init__(self, input_die, explodes_on, biiiiig_booooooms=2):
#             super(NewDie, self).__init__(input_die, explodes_on, biiiiig_booooooms)
#
#     parser = NewParser()
#     parser.add_class(NewDie, ("die", "int_tuple", "int"))
#     parser.add_limits_kwarg("explosions", "biiiiig_booooooms")
#     with pytest.raises(LimitsError):
#         parser.parse_die_within_limits("NewDie(Die(5), (1, 2), 9)")
#     with pytest.raises(LimitsError):
#         parser.parse_die_within_limits("ExplodingOn(Die(5), (1, 2), 9)")
#
#
# def test_parse_within_limits_new_explosions_kwarg_int_tuple():
#     class NewDie(ExplodingOn):
#         def __init__(self, input_die, boom_points, explosions=2):
#             super(NewDie, self).__init__(input_die, boom_points, explosions)
#
#     parser = NewParser()
#     parser.add_class(NewDie, ("die", "int_tuple", "int"))
#     parser.add_limits_kwarg("explodes_on", "boom_points")
#     with pytest.raises(LimitsError):
#         parser.parse_die_within_limits("NewDie(Die(5), (1, 2), 9)")
#     with pytest.raises(LimitsError):
#         parser.parse_die_within_limits("ExplodingOn(Die(5), (1, 2), 9)")
#
#
# def test_parse_within_limits_new_explosions_kwarg_error():
#     class NewDie(ExplodingOn):
#         def __init__(self, input_die, explodes_on, str_splosions="2"):
#             super(NewDie, self).__init__(input_die, explodes_on, int(str_splosions))
#
#     def make_string(str_node):
#         return str_node.s
#
#     parser = NewParser()
#     parser.add_param_type("string", make_string)
#     parser.add_class(NewDie, ("die", "int_tuple", "string"))
#     parser.add_limits_kwarg("explosions", "str_splosions")
#
#     assert parser.parse_die('NewDie(Die(5), (1, 2), "5")') == NewDie(
#         Die(5), (1, 2), "5"
#     )
#
#     msg = 'A kwarg declared as an "explosions" is not an int.'
#     with pytest.raises(ValueError, match=msg):
#         parser.parse_die_within_limits('NewDie(Die(5), (1, 2), "9")')
#
#     with pytest.raises(LimitsError):
#         parser.parse_die_within_limits("ExplodingOn(Die(5), (1, 2), 9)")
#
#
# def test_parse_within_limits_new_explodes_on_kwarg_error():
#     class NewDie(ExplodingOn):
#         def __init__(self, input_die, on_range, explosions=2):
#             super(NewDie, self).__init__(
#                 input_die, tuple(range(1, on_range)), explosions
#             )
#
#     parser = NewParser()
#     parser.add_class(NewDie, ("die", "int", "int"))
#     parser.add_limits_kwarg("explodes_on", "on_range")
#
#     assert parser.parse_die("NewDie(Die(5), 2)") == NewDie(Die(5), 2)
#
#     msg = 'A kwarg declared as an "explodes_on" is not a tuple.'
#     with pytest.raises(ValueError, match=msg):
#         parser.parse_die_within_limits("NewDie(Die(5), 2)")
#
#     with pytest.raises(LimitsError):
#         parser.parse_die_within_limits("ExplodingOn(Die(5), (1, 2), 9)")
#
#
# def test_parse_within_limits_new_input_die_kwarg():
#     class NewDie(BestOfDicePool):
#         def __init__(self, funky_new_die, pool_size, select):
#             super(NewDie, self).__init__(funky_new_die, pool_size, select)
#
#     parser = NewParser()
#     parser.add_class(NewDie, ("die", "int", "int"))
#     parser.add_limits_kwarg("input_die", "funky_new_die")
#     with pytest.raises(LimitsError):
#         parser.parse_die_within_limits("NewDie(Die(100), 5, 4)")
#     with pytest.raises(LimitsError):
#         parser.parse_die_within_limits("BestOfDicePool(Die(100), 5, 4)")
#
#
# def test_parse_within_limits_new_input_kwarg_error():
#     class NewDie(BestOfDicePool):
#         def __init__(self, a_die_size, pool_size, select):
#             die = Die(a_die_size)
#             super(NewDie, self).__init__(die, pool_size, select)
#
#     parser = NewParser()
#     parser.add_class(NewDie, ("int", "int", "int"))
#     parser.add_limits_kwarg("input_die", "a_die_size")
#
#     assert parser.parse_die("NewDie(5, 2, 1)") == NewDie(5, 2, 1)
#
#     msg = 'A kwarg declared as an "input_die" does not inherit from ProtoDie.'
#     with pytest.raises(ValueError, match=msg):
#         parser.parse_die_within_limits("NewDie(5, 4, 1)")
#
#     with pytest.raises(LimitsError):
#         parser.parse_die_within_limits("WeightedDie({5000: 1})")
#
#
# def test_parse_within_limits_new_pool_size_kwarg():
#     class NewDie(BestOfDicePool):
#         def __init__(self, input_die, funky_new_pool, select):
#             super(NewDie, self).__init__(input_die, funky_new_pool, select)
#
#     parser = NewParser()
#     parser.add_class(NewDie, ("die", "int", "int"))
#     parser.add_limits_kwarg("pool_size", "funky_new_pool")
#     with pytest.raises(LimitsError):
#         parser.parse_die_within_limits("NewDie(Die(100), 5, 4)")
#     with pytest.raises(LimitsError):
#         parser.parse_die_within_limits("BestOfDicePool(Die(100), 5, 4)")
#
#
# def test_parse_within_limits_new_pool_size_kwarg_error():
#     class NewDie(BestOfDicePool):
#         def __init__(self, input_die, pool_str, select):
#             super(NewDie, self).__init__(input_die, int(pool_str), select)
#
#     def make_string(str_node):
#         return str_node.s
#
#     parser = NewParser()
#     parser.add_param_type("string", make_string)
#     parser.add_class(NewDie, ("die", "string", "int"))
#     parser.add_limits_kwarg("pool_size", "pool_str")
#
#     assert parser.parse_die('NewDie(Die(5), "2", 1)') == NewDie(Die(5), "2", 1)
#
#     msg = 'A kwarg declared as a "pool_size" is not an int.'
#     with pytest.raises(ValueError, match=msg):
#         parser.parse_die_within_limits('NewDie(Die(5), "4", 1)')
#
#     with pytest.raises(LimitsError):
#         parser.parse_die_within_limits("WeightedDie({5000: 1})")
#
#
# def test_parse_within_limits_new_size_kwarg_with_defaults():
#     class NewDie(Die):
#         def __init__(self, funky_new_die_size=5000):
#             super(NewDie, self).__init__(funky_new_die_size)
#
#     parser = NewParser()
#     parser.add_class(NewDie, ("int",))
#     parser.add_limits_kwarg("size", "funky_new_die_size", 5000)
#     assert parser.parse_die("NewDie()") == NewDie()
#     with pytest.raises(LimitsError):
#         parser.parse_die_within_limits("NewDie()")
#
#
# def test_parse_within_limits_new_explosions_kwarg_with_defaults():
#     class NewDie(ExplodingOn):
#         def __init__(self, input_die, explodes_on, biiiiig_booooooms=11):
#             super(NewDie, self).__init__(input_die, explodes_on, biiiiig_booooooms)
#
#     parser = NewParser()
#     parser.add_class(NewDie, ("die", "int_tuple", "int"))
#     parser.add_limits_kwarg("explosions", "biiiiig_booooooms", 11)
#     assert parser.parse_die("NewDie(Die(5), (1, 2))") == NewDie(Die(5), (1, 2))
#     with pytest.raises(LimitsError):
#         parser.parse_die_within_limits("NewDie(Die(5), (1, 2))")
#
#
# def test_parse_within_limits_new_dice_pool_limit_kwargs_with_defaults():
#     class NewDie(BestOfDicePool):
#         def __init__(self, funky_new_die=Die(6), funky_new_pool_size=4):
#             select = funky_new_pool_size - 1
#             super(NewDie, self).__init__(funky_new_die, funky_new_pool_size, select)
#
#     parser = NewParser()
#     parser.add_class(NewDie, ("die", "int"))
#     parser.add_limits_kwarg("pool_size", "funky_new_pool_size", 4)
#     parser.add_limits_kwarg("input_die", "funky_new_die", Die(6))
#     assert parser.parse_die("NewDie()") == NewDie(Die(6), 4)
#     with pytest.raises(LimitsError):
#         parser.parse_die_within_limits("NewDie(Die(600))")
#     with pytest.raises(LimitsError):
#         parser.parse_die_within_limits("NewDie(funky_new_pool_size=5000)")
#
#
# def test_parse_within_limits_kwarg_with_defaults_beyond_scope_ignoring_limits():
#     class NewDie(Die):
#         def __init__(self, funky_new_die_size=5000):
#             super(NewDie, self).__init__(funky_new_die_size)
#
#     parser = NewParser()
#     parser.add_class(NewDie, ("int",))
#     parser.add_limits_kwarg("size", "funky_new_die_size", 5)
#     assert parser.parse_die("NewDie()") == NewDie(5000)
#     assert parser.parse_die_within_limits("NewDie()") == NewDie(5000)
#
#
# def test_parse_within_limits_kwarg_with_defaults_beyond_scope_catching_false_limits():
#     class NewDie(Die):
#         def __init__(self, funky_new_die_size=5):
#             super(NewDie, self).__init__(funky_new_die_size)
#
#     parser = NewParser()
#     parser.add_class(NewDie, ("int",))
#     parser.add_limits_kwarg("size", "funky_new_die_size", 5000)
#     assert parser.parse_die("NewDie()") == NewDie(5)
#     with pytest.raises(LimitsError):
#         parser.parse_die_within_limits("NewDie()")
#
#
# def test_parse_die_within_limits_failure_to_register_default_beyond_scope():
#     class NewDie(Die):
#         def __init__(self, funky_new_die_size=5000):
#             super(NewDie, self).__init__(funky_new_die_size)
#
#     parser = NewParser()
#     parser.add_class(NewDie, ("int",))
#     parser.add_limits_kwarg("size", "funky_new_die_size")
#     assert parser.parse_die("NewDie()") == NewDie(5000)
#     assert parser.parse_die_within_limits("NewDie()") == NewDie(5000)
