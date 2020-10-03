from abc import ABC, abstractmethod
from inspect import BoundArguments
from typing import Iterable

from dicetables.eventsbases.protodie import ProtoDie


class AbstractLimitChecker(ABC):
    @abstractmethod
    def is_numbers_of_calls_within_limits(self, die_classes: Iterable[ProtoDie]) -> bool:
        pass

    @abstractmethod
    def check_limits(self, die_class: ProtoDie, bound_args: BoundArguments) -> None:
        pass

    @abstractmethod
    def is_dice_pool_within_limits(self, bound_args: BoundArguments) -> bool:
        pass

    @abstractmethod
    def is_die_size_within_limits(self, bound_args: BoundArguments) -> bool:
        pass

    @abstractmethod
    def are_explosions_within_limits(self, bound_args: BoundArguments) -> bool:
        pass


class NoOpLimitChecker(AbstractLimitChecker):
    def __init__(self):
        pass