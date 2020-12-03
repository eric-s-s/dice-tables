from inspect import signature
from typing import List, Type, Union

import pytest

from dicetables import (
    Die,
    BestOfDicePool,
    ModDie,
    ModWeightedDie,
    Exploding,
    ExplodingOn,
)
from dicetables.dicepool import DicePool
from dicetables.eventsbases.protodie import ProtoDie
from dicetables.tools.limit_checker import NoOpLimitChecker, LimitChecker, LimitsError
from dicetables.tools.orderedcombinations import count_unique_combination_keys


class TestNoOpLimitChecker(object):
    @pytest.fixture(params=[signature(open).bind("x"), signature(divmod).bind(1, 2)])
    def bound_args(self, request):
        yield request.param

    @pytest.fixture(params=[[], [Die], [BestOfDicePool], [Die, BestOfDicePool] * 100])
    def dice(self, request):
        yield request.param

    def test_assert_dice_pool_within_limits(self, bound_args):
        NoOpLimitChecker().assert_dice_pool_within_limits(bound_args)

    def test_assert_die_size_within_limits(self, bound_args):
        NoOpLimitChecker().assert_die_size_within_limits(bound_args)

    def test_assert_numbers_of_calls_within_limits(self, dice):
        NoOpLimitChecker().assert_numbers_of_calls_within_limits(dice)

    def test_assert_explosions_within_limits(self, dice):
        NoOpLimitChecker().assert_explosions_within_limits(dice)


class TestLimitChecker(object):
    def test_limit_checker_defaults(self):
        checker = LimitChecker()
        assert checker.max_dice_calls == 5
        assert checker.max_dice_pool_calls == 2
        assert checker.max_size == 500
        assert checker.max_explosions == 10
        assert checker.max_dice_pool_combinations_per_dict_size == {
            2: 600,
            3: 8700,
            4: 30000,
            5: 55000,
            6: 70000,
            7: 100000,
            12: 200000,
            30: 250000,
        }

    @pytest.mark.parametrize("dice, raises_error", [(2, False), (3, False), (4, True)])
    def test_assert_number_of_calls_within_limits_dice_limit_three(
            self, dice, raises_error
    ):
        checker = LimitChecker(max_dice=3, max_dice_pools=4)
        if raises_error:
            with pytest.raises(LimitsError):
                checker.assert_numbers_of_calls_within_limits([Die] * dice)
        else:
            checker.assert_numbers_of_calls_within_limits([Die] * dice)

    @pytest.mark.parametrize("dice, raises_error", [(2, False), (3, False), (4, True)])
    def test_assert_number_of_calls_within_limits_max_dice_ignores_dice_pools(
        self, dice, raises_error
    ):
        checker = LimitChecker(max_dice=3, max_dice_pools=4)
        if raises_error:
            with pytest.raises(LimitsError):
                checker.assert_numbers_of_calls_within_limits([Die, DicePool] * dice)
        else:
            checker.assert_numbers_of_calls_within_limits([Die, DicePool] * dice)

    @pytest.mark.parametrize(
        "dice_pools, raises_error", [(2, False), (3, False), (4, True)]
    )
    def test_assert_number_of_calls_within_limits_dice_pool_limit_three(
        self, dice_pools, raises_error
    ):
        checker = LimitChecker(max_dice=5, max_dice_pools=3)
        to_check = []  # type: List[Union[Type[ProtoDie], Type[DicePool]]]
        to_check += [BestOfDicePool] * 5
        to_check += [DicePool] * dice_pools
        if raises_error:
            with pytest.raises(LimitsError):
                checker.assert_numbers_of_calls_within_limits(to_check)
        else:
            checker.assert_numbers_of_calls_within_limits(to_check)

    @pytest.mark.parametrize(
        "die_size, raises_error", [(9, False), (10, False), (11, True)]
    )
    def test_assert_die_size_die_with_size_argument(self, die_size, raises_error):
        checker = LimitChecker(max_size=10)
        bound_args = signature(ModDie).bind(die_size, 1000)
        if raises_error:
            with pytest.raises(LimitsError):
                checker.assert_die_size_within_limits(bound_args)
        else:
            checker.assert_die_size_within_limits(bound_args)

    @pytest.mark.parametrize(
        "die_size, raises_error", [(9, False), (10, False), (11, True)]
    )
    def test_assert_die_size_die_with_dictionary_argument(self, die_size, raises_error):
        checker = LimitChecker(max_size=10)
        bound_args = signature(ModWeightedDie).bind({die_size: 1}, 1000)
        if raises_error:
            with pytest.raises(LimitsError):
                checker.assert_die_size_within_limits(bound_args)
        else:
            checker.assert_die_size_within_limits(bound_args)

    def test_assert_die_size_ignores_input_dice(self):
        input_die = ModDie(1000, 1000)
        bound_args = signature(Exploding).bind(input_die)
        checker = LimitChecker(max_size=5)
        checker.assert_die_size_within_limits(bound_args)

    def test_assert_explosions_no_explosions(self):
        checker = LimitChecker()
        bound_args = signature(Die).bind(1000)
        checker.assert_explosions_within_limits(bound_args)

    @pytest.mark.parametrize(
        "explosions, raises_error", [(4, False), (5, False), (6, True)]
    )
    def test_assert_explosions_no_explodes_on(self, explosions, raises_error):
        input_die = ModDie(100, 100)
        bound_args = signature(Exploding).bind(input_die, explosions)
        checker = LimitChecker(max_explosions=5)
        if raises_error:
            with pytest.raises(LimitsError):
                checker.assert_explosions_within_limits(bound_args)
        else:
            checker.assert_explosions_within_limits(bound_args)

    @pytest.mark.parametrize(
        "explodes_on_len, raises_error", [(4, False), (5, False), (6, True)]
    )
    def test_assert_explosions_explosions_plus_len_explodes_on(
        self, explodes_on_len, raises_error
    ):
        input_die = ModDie(100, 100)
        explosions = 10
        explodes_on = tuple(range(explodes_on_len))
        bound_args = signature(ExplodingOn).bind(
            input_die, explodes_on, explosions=explosions
        )
        checker = LimitChecker(max_explosions=5 + explosions)
        if raises_error:
            with pytest.raises(LimitsError):
                checker.assert_explosions_within_limits(bound_args)
        else:
            checker.assert_explosions_within_limits(bound_args)

    def test_assert_dice_pool_limits_no_dice_pool(self):
        checker = LimitChecker()
        bound_args = signature(Die).bind(1000)
        checker.assert_dice_pool_within_limits(bound_args)

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
    def test_assert_dice_pool_within_limits_on_dice_pool(
        self, die_size, die_pool, max_combinations
    ):
        """
        self.max_dice_pool_combinations_per_dict_size = {
            2: 600, 3: 8700, 4: 30000, 5: 55000, 6: 70000,
            7: 100000, 12: 200000, 30: 250000
        }
        """
        checker = LimitChecker()
        bound_args_passing = signature(DicePool).bind(Die(die_size), die_pool)
        bound_args_failing = signature(DicePool).bind(
            Die(die_size), die_pool + 1
        )
        assert (
            count_unique_combination_keys(Die(die_size), die_pool) <= max_combinations
        )
        checker.assert_dice_pool_within_limits(bound_args_passing)

        assert (
            count_unique_combination_keys(Die(die_size), die_pool + 1)
            > max_combinations
        )
        with pytest.raises(LimitsError):
            checker.assert_dice_pool_within_limits(bound_args_failing)

    def test_assert_dice_pool_within_limits_pool_of_one_fails(self):
        checker = LimitChecker()
        bound_args = signature(DicePool).bind(Die(1), 1)
        with pytest.raises(LimitsError):
            checker.assert_dice_pool_within_limits(bound_args)
