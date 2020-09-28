from abc import ABC, abstractmethod
from inspect import BoundArguments

from dicetables.eventsbases.protodie import ProtoDie


class AbstractLimitChecker(ABC):
    @property
    @abstractmethod
    def dice_creation_calls(self) -> int:
        pass

    @property
    @abstractmethod
    def dicepool_creation_calls(self) -> int:
        pass

    @abstractmethod
    def reset_call_counters(self) -> None:
        pass

    @abstractmethod
    def check_limits(self, die_class: ProtoDie, bound_args: BoundArguments) -> 'AbstractLimitChecker':
        pass

