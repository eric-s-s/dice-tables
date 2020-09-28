from typing import Dict

from dicetables.dieevents import ProtoDie
from dicetables.tools.orderedcombinations import ordered_combinations_of_events


class DicePool(ProtoDie):
    """
    The abstract class for all DicePool objects. A DicePool is a pool of one kind of die. Select determines how many
    rolls are selected from the pool of total rolls. Different implementations determine which particular rolls
    to select.
    """

    def __init__(self, input_die: ProtoDie, pool_size: int, select: int):
        """

        :param input_die: Any object that inherits from ProtoDie
        :param pool_size: int > 0. How many total dice in the pool.
        :param select: int <= `pool_size`. How many dice to select from the pool.
        """
        if select > pool_size:
            raise ValueError('you cannot select more dice than the pool_size.')
        self._input_die = input_die
        self._pool = pool_size
        self._select = select
        self._dict = self._generate_dict()
        super(DicePool, self).__init__()

    def _generate_dict(self):
        raise NotImplementedError

    def get_input_die(self) -> ProtoDie:
        return self._input_die

    def get_pool_size(self) -> int:
        return self._pool

    def get_select(self) -> int:
        return self._select

    def get_dict(self) -> Dict[int, int]:
        return self._dict.copy()

    def get_size(self) -> int:
        return self._input_die.get_size() * self._select

    def get_weight(self) -> int:
        return self._input_die.get_weight() * self._select

    def weight_info(self):
        original_weight_info = self._input_die.weight_info().replace(str(self._input_die), 'input_die info:')
        return '{}\n{}'.format(self, original_weight_info)

    def multiply_str(self, number):
        return '{}({})'.format(number, self)

    def __str__(self):
        descriptor = self.__class__.__name__.replace('OfDicePool', '')
        return '{} {} of {}'.format(descriptor, self._select, self._input_die.multiply_str(self._pool))

    def __repr__(self):
        return '{}({!r}, {}, {})'.format(self.__class__.__name__, self._input_die, self._pool, self._select)


class BestOfDicePool(DicePool):
    """
    Take the best [select] rolls from a pool of [pool_size] * [input_die].
    BestOfDicePool(Die(6), 4, 3) is the best 3 rolls from four six-sided dice.
    """

    def __init__(self, input_die: ProtoDie, pool_size: int, select: int):
        super(BestOfDicePool, self).__init__(input_die, pool_size, select)

    def _generate_dict(self):
        ordered_combinations = ordered_combinations_of_events(self._input_die, self._pool)
        start_at = self._pool - self._select
        stop_before = self._pool
        return generate_events_dict(ordered_combinations, start_at, stop_before)


class WorstOfDicePool(DicePool):
    """
    Take the worst [select] rolls from a pool of [pool_size] * [input_die].
    WorstOfDicePool(Die(6), 4, 3) is the worst 3 rolls from four six-sided dice.
    """

    def __init__(self, input_die: ProtoDie, pool_size: int, select: int):
        super(WorstOfDicePool, self).__init__(input_die, pool_size, select)

    def _generate_dict(self):
        ordered_combinations = ordered_combinations_of_events(self._input_die, self._pool)
        start_at = 0
        stop_before = self._select
        return generate_events_dict(ordered_combinations, start_at, stop_before)


class UpperMidOfDicePool(DicePool):
    """
    Take the middle [select] rolls from a pool of [pool_size] * [input_die].
    UpperMidOfDicePool(Die(6), 5, 3) is the middle 3 rolls from five six-sided dice.

    If there is no perfect middle, take the higher of two choices. For five dice that roll
    (1, 1, 2, 3, 4), select=3 takes (1, 2, 3) and select=2 takes (2, 3).
    """

    def __init__(self, input_die: ProtoDie, pool_size: int, select: int):
        super(UpperMidOfDicePool, self).__init__(input_die, pool_size, select)

    def _generate_dict(self):
        ordered_combinations = ordered_combinations_of_events(self._input_die, self._pool)
        end_slice, extra = divmod(self._pool - self._select, 2)
        start_at = end_slice + extra
        stop_before = self._pool - end_slice
        return generate_events_dict(ordered_combinations, start_at, stop_before)


class LowerMidOfDicePool(DicePool):
    """
    Take the middle [select] rolls from a pool of [pool_size] * [input_die].
    LowerMidOfDicePool(Die(6), 5, 3) is the middle 3 rolls from five six-sided dice.

    If there is no perfect middle, take the lower of two choices. For five dice that roll
    (1, 1, 2, 3, 4), select=3 takes (1, 2, 3) and select=2 takes (1, 2).
    """

    def __init__(self, input_die: ProtoDie, pool_size: int, select: int):
        super(LowerMidOfDicePool, self).__init__(input_die, pool_size, select)

    def _generate_dict(self):
        ordered_combinations = ordered_combinations_of_events(self._input_die, self._pool)
        end_slice, extra = divmod(self._pool - self._select, 2)
        start_at = end_slice
        stop_before = self._pool - (end_slice + extra)
        return generate_events_dict(ordered_combinations, start_at, stop_before)


def generate_events_dict(ordered_combinations, start_at, stop_before) -> Dict[int, int]:
    master_dict = {}
    for key, val in ordered_combinations.items():
        master_key = sum(key[start_at:stop_before])
        master_dict[master_key] = master_dict.get(master_key, 0) + val
    return master_dict
