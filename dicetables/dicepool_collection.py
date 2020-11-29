from typing import Dict

from dicetables.dieevents import ProtoDie
from dicetables.dicepool import DicePool


class DicePoolCollection(ProtoDie):
    """
    The abstract class for all DicePoolCollection objects. A DicePoolCollection creates a new die by selecting from a
    DicePool. Select determines how many rolls are selected from the pool of total rolls.
    Different implementations determine which particular rolls to select.
    """

    def __init__(self, pool: DicePool, select: int):
        """

        :param pool: the dice pool to select from
        :param select: int <= `pool.size`. How many dice to select from the pool.
        """
        self._dice_pool = pool
        if select > self._dice_pool.size:
            raise ValueError('you cannot select more dice than the pool_size.')
        self._select = select
        self._dict = self._generate_dict()
        super(DicePoolCollection, self).__init__()

    def _generate_dict(self):
        raise NotImplementedError

    def get_pool(self) -> DicePool:
        return self._dice_pool

    def get_select(self) -> int:
        return self._select

    def get_dict(self) -> Dict[int, int]:
        return self._dict.copy()

    def get_size(self) -> int:
        return self._dice_pool.die.get_size() * self._select

    def get_weight(self) -> int:
        return self._dice_pool.die.get_weight() * self._select

    def weight_info(self):
        input_die = self._dice_pool.die
        original_weight_info = input_die.weight_info().replace(str(input_die), 'input_die info:')
        return '{}\n{}'.format(self, original_weight_info)

    def multiply_str(self, number):
        return '{}({})'.format(number, self)

    def __str__(self):
        descriptor = self.__class__.__name__.replace('OfDicePool', '')
        return '{} {} of {}'.format(descriptor, self._select, self._dice_pool.die.multiply_str(self._dice_pool.size))

    def __repr__(self):
        return '{}({!r}, {})'.format(
            self.__class__.__name__, self._dice_pool, self._select
        )


class BestOfDicePool(DicePoolCollection):
    """
    Take the best [select] rolls from a DicePool of [pool_size] * [input_die].
    BestOfDicePool(DicePool(Die(6), 4), 3) is the best 3 rolls from four six-sided dice.
    """

    def __init__(self, pool: DicePool, select: int):
        super().__init__(pool, select)

    def _generate_dict(self):
        ordered_combinations = self._dice_pool.rolls
        start_at = self._dice_pool.size - self._select
        stop_before = self._dice_pool.size
        return generate_events_dict(ordered_combinations, start_at, stop_before)


class WorstOfDicePool(DicePoolCollection):
    """
    Take the worst [select] rolls from a DicePool of [pool_size] * [input_die].
    WorstOfDicePool(DicePool(Die(6), 4), 3) is the worst 3 rolls from four six-sided dice.
    """

    def __init__(self, pool: DicePool, select: int):
        super().__init__(pool, select)

    def _generate_dict(self):
        ordered_combinations = self._dice_pool.rolls
        start_at = 0
        stop_before = self._select
        return generate_events_dict(ordered_combinations, start_at, stop_before)


class UpperMidOfDicePool(DicePoolCollection):
    """
    Take the middle [select] rolls from a DicePool of [pool_size] * [input_die].
    UpperMidOfDicePool(DicePool(Die(6), 5), 3) is the middle 3 rolls from five six-sided dice.

    If there is no perfect middle, take the higher of two choices. For five dice that roll
    (1, 1, 2, 3, 4), select=3 takes (1, 2, 3) and select=2 takes (2, 3).
    """

    def __init__(self, pool: DicePool, select: int):
        super().__init__(pool, select)

    def _generate_dict(self):
        ordered_combinations = self._dice_pool.rolls
        end_slice, extra = divmod(self._dice_pool.size - self._select, 2)
        start_at = end_slice + extra
        stop_before = self._dice_pool.size - end_slice
        return generate_events_dict(ordered_combinations, start_at, stop_before)


class LowerMidOfDicePool(DicePoolCollection):
    """
    Take the middle [select] rolls from a DicePool of [pool_size] * [input_die].
    LowerMidOfDicePool(DicePool(Die(6), 5), 3) is the middle 3 rolls from five six-sided dice.

    If there is no perfect middle, take the lower of two choices. For five dice that roll
    (1, 1, 2, 3, 4), select=3 takes (1, 2, 3) and select=2 takes (1, 2).
    """

    def __init__(self, pool: DicePool, select: int):
        super().__init__(pool, select)

    def _generate_dict(self):
        ordered_combinations = self._dice_pool.rolls
        end_slice, extra = divmod(self._dice_pool.size - self._select, 2)
        start_at = end_slice
        stop_before = self._dice_pool.size - (end_slice + extra)
        return generate_events_dict(ordered_combinations, start_at, stop_before)


def generate_events_dict(ordered_combinations, start_at, stop_before) -> Dict[int, int]:
    master_dict = {}
    for key, val in ordered_combinations.items():
        master_key = sum(key[start_at:stop_before])
        master_dict[master_key] = master_dict.get(master_key, 0) + val
    return master_dict
