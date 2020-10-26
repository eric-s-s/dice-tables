from abc import ABC, abstractmethod
from enum import Enum, auto
from inspect import BoundArguments
from typing import Iterable, Type, Optional, Any

from dicetables.bestworstmid import DicePool
from dicetables.eventsbases.protodie import ProtoDie
from dicetables.tools.orderedcombinations import (
    count_unique_combination_keys,
    largest_permitted_pool_size,
)


class LimitsError(ValueError):
    def __init__(self, *args):
        super(LimitsError, self).__init__(*args)


class ArgumentType(Enum):
    SIZE = auto()
    EXPLOSIONS = auto()
    EXPLODES_ON = auto()
    INPUT_DIE = auto()
    POOL_SIZE = auto()


def get_bound_args(arg_type: ArgumentType, bound_args: BoundArguments) -> Optional[Any]:
    arg_names = {
        ArgumentType.SIZE: ("die_size", "dictionary_input"),
        ArgumentType.EXPLOSIONS: ("explosions",),
        ArgumentType.EXPLODES_ON: ("explodes_on",),
        ArgumentType.INPUT_DIE: ("input_die",),
        ArgumentType.POOL_SIZE: ("pool_size",),
    }
    possible_args = arg_names[arg_type]
    for arg_name, arg_value in bound_args.arguments.items():
        if arg_name in possible_args:
            return arg_value
    return None


class AbstractLimitChecker(ABC):
    @abstractmethod
    def assert_numbers_of_calls_within_limits(
        self, die_classes: Iterable[Type[ProtoDie]]
    ) -> None:
        """
        asserts that the number of `dicetables.ProtoDie` calls and the number of
        `dicetables.bestworstmid.DicePool` calls are within limits.

        :raises LimitsError:
        """
        raise NotImplementedError

    @abstractmethod
    def assert_die_size_within_limits(self, bound_args: BoundArguments) -> None:
        """
        Checks the bound arguments for the size of the die and asserts they are
        within limits.

        This typically uses `dicetables.tools.limit_checker.get_bound_args` to determine what
        is a `dicetables.tools.limit_checker.ArgumentType.SIZE` argument.

        :raises LimitsError:
        """
        raise NotImplementedError

    @abstractmethod
    def assert_explosions_within_limits(self, bound_args: BoundArguments) -> None:
        """
        Asserts that the number of explosions on an `dicetables.Exploding` or an `dicetables.ExplodingOn`
        has a number of explosions withing limits.

        This typically uses `dicetables.tools.limit_checker.get_bound_args` to determine what
        is a `dicetables.tools.limit_checker.ArgumentType.EXPLOSIONS` and
        a `dicetables.tools.limit_checker.ArgumentType.EXPLODES_ON` argument.

        :raises LimitsError:
        """
        raise NotImplementedError

    @abstractmethod
    def assert_dice_pool_within_limits(self, bound_args: BoundArguments) -> None:
        """
        asserts that the size of a dice pool is within limits.  Dice pools can be very expensive
        to calculate. see:

        `DicePools <http://dice-tables.readthedocs.io/en/latest/the_dice.html#dice-pools>`_

        This typically uses `dicetables.tools.limit_checker.get_bound_args` to determine what
        is a `dicetables.tools.limit_checker.ArgumentType.POOL_SIZE` argument.

        :raises LimitsError:
        """
        raise NotImplementedError


class NoOpLimitChecker(AbstractLimitChecker):
    def assert_numbers_of_calls_within_limits(
        self, die_classes: Iterable[Type[ProtoDie]]
    ) -> None:
        pass

    def assert_die_size_within_limits(self, bound_args: BoundArguments) -> None:
        pass

    def assert_explosions_within_limits(self, bound_args: BoundArguments) -> None:
        pass

    def assert_dice_pool_within_limits(self, bound_args: BoundArguments) -> None:
        pass


class LimitChecker(AbstractLimitChecker):
    def __init__(
        self,
        max_size: int = 500,
        max_explosions: int = 10,
        max_dice: int = 5,
        max_dice_pools: int = 2,
    ):
        self.max_size = max_size
        self.max_explosions = max_explosions
        self.max_dice_calls = max_dice
        self.max_dice_pool_calls = max_dice_pools
        self.max_dice_pool_combinations_per_dict_size = {
            2: 600,
            3: 8700,
            4: 30000,
            5: 55000,
            6: 70000,
            7: 100000,
            12: 200000,
            30: 250000,
        }

    def assert_numbers_of_calls_within_limits(
        self, die_classes: Iterable[Type[ProtoDie]]
    ) -> None:
        class_list = list(die_classes)
        dice_pool_list = [el for el in class_list if issubclass(el, DicePool)]
        if (
            len(class_list) > self.max_dice_calls
            or len(dice_pool_list) > self.max_dice_pool_calls
        ):
            msg = (
                f"Limits exceeded. Max dice calls: {self.max_dice_calls}. "
                f"Max dice pool calls: {self.max_dice_pool_calls}. "
                f"Calls requested: {class_list}"
            )
            raise LimitsError(msg)

    def assert_die_size_within_limits(self, bound_args: BoundArguments) -> None:
        sized_value = get_bound_args(ArgumentType.SIZE, bound_args)
        if isinstance(sized_value, dict):
            size = max(sized_value.keys())
        else:
            size = sized_value

        if size and size > self.max_size:
            raise LimitsError(
                f"A die of size: {size} is greater than the allowed max: {self.max_size}"
            )

    def assert_explosions_within_limits(self, bound_args: BoundArguments) -> None:
        explosions = get_bound_args(ArgumentType.EXPLOSIONS, bound_args)
        explodes_on = get_bound_args(ArgumentType.EXPLODES_ON, bound_args)
        if explodes_on:
            explosions += len(explodes_on)

        if explosions and explosions > self.max_explosions:
            raise LimitsError(
                f"Explosions: {explosions} + len({explodes_on}) is greater than allowed max: {self.max_explosions}"
            )

    def assert_dice_pool_within_limits(self, bound_args: BoundArguments) -> None:
        input_die = get_bound_args(ArgumentType.INPUT_DIE, bound_args)
        pool_size = get_bound_args(ArgumentType.POOL_SIZE, bound_args)
        if input_die is None or pool_size is None:
            return

        dict_size = len(input_die.get_dict())
        pool_limit = 0
        for key, limit in sorted(self.max_dice_pool_combinations_per_dict_size.items()):
            if key > dict_size:
                break
            pool_limit = limit

        score = count_unique_combination_keys(input_die, pool_size)
        if score > pool_limit:
            max_pool_size = largest_permitted_pool_size(input_die, pool_limit)
            msg = "{!r} has a get_dict() of size: {}\n".format(input_die, dict_size)
            explanation = "For this die, the largest permitted pool_size is {}".format(
                max_pool_size
            )
            raise LimitsError(msg + explanation)
