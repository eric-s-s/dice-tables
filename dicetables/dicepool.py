from typing import Dict, Tuple

from dicetables.eventsbases.protodie import ProtoDie
from dicetables.tools.orderedcombinations import ordered_combinations_of_events


class DicePool(object):
    def __init__(self, input_die: ProtoDie, pool_size: int):
        if pool_size < 1:
            raise ValueError("Minimum DicePool size is 1")
        self._input_die = input_die
        self._pool_size = pool_size
        self._rolls = ordered_combinations_of_events(input_die, pool_size)

    @property
    def die(self) -> ProtoDie:
        return self._input_die

    @property
    def size(self) -> int:
        return self._pool_size

    @property
    def rolls(self) -> Dict[Tuple[int, ...], int]:
        return self._rolls.copy()

    def __eq__(self, other):
        if not isinstance(other, DicePool):
            return False
        return (self.die, self.size) == (other.die, other.size)

    def __hash__(self):
        return hash((self.die, self.size))

    def __repr__(self):
        return "{}({!r}, {})".format(self.__class__.__name__, self.die, self.size)
