from dicetables.tools.orderedcombinations import ordered_combinations_of_events
from dicetables.dieevents import ProtoDie


class PoolOfDice(object):
    def __init__(self, input_die, pool_size):
        self._pool_dict = ordered_combinations_of_events(input_die, pool_size)
        self._events = input_die
        self._pool_size = pool_size

    @property
    def input_die(self):
        return self._events

    @property
    def pool_size(self):
        return self._pool_size

    def get_pool(self):
        return self._pool_dict.copy()

    def __eq__(self, other):
        if not isinstance(other, PoolOfDice):
            return False
        return (self.input_die, self.pool_size) == (other.input_die, other.pool_size)

    def __repr__(self):
        return '{}({!r}, {!r})'.format(self.__class__.__name__, self.input_die, self.pool_size)

    def __hash__(self):
        return hash(repr(self))


class AltDicePool(ProtoDie):
    """
    The abstract class for all AltDicePool objects. A AltDicePool is a pool of one kind of die. Select determines how many
    rolls are selected from the pool of total rolls. Different implementations determine which particular rolls
    to select.
    """

    @classmethod
    def from_die_and_pool_size(cls, input_die, pool_size, select):
        pool = PoolOfDice(input_die, pool_size)
        return cls(pool, select)

    def __init__(self, pool: PoolOfDice, select):
        """

        :param pool: a PoolOfDice.
        :param select: int <= `pool_size`. How many dice to select from the pool.
        """
        if select > pool.pool_size:
            raise ValueError('you cannot select more dice than the pool_size.')
        self._pool = pool
        self._select = select
        self._dict = self._generate_dict()
        super(AltDicePool, self).__init__()

    def _generate_dict(self):
        raise NotImplementedError

    def get_pool(self):
        return self._pool

    def get_select(self):
        return self._select

    def get_dict(self):
        return self._dict.copy()

    def get_size(self):
        return self._pool.input_die.get_size() * self._select

    def get_weight(self):
        return self._pool.input_die.get_weight() * self._select

    def weight_info(self):
        original_weight_info = self._pool.input_die.weight_info().replace(str(self._pool.input_die), 'input_die info:')
        return '{}\n{}'.format(self, original_weight_info)

    def multiply_str(self, number):
        return '{}({})'.format(number, self)

    def __str__(self):
        descriptor = self.__class__.__name__.replace('OfAltDicePool', '')
        return '{} {} of {}'.format(descriptor, self._select, self._pool.input_die.multiply_str(self._pool))

    def __repr__(self):
        return '{}({!r}, {}, {})'.format(self.__class__.__name__, self._pool.input_die, self._pool, self._select)


class BestOfAltDicePool(AltDicePool):
    """
    Take the best [select] rolls from a pool of [pool_size] * [input_die].
    BestOfAltDicePool(Die(6), 4, 3) is the best 3 rolls from four six-sided dice.
    """
    def __init__(self, pool, select):
        super(BestOfAltDicePool, self).__init__(pool, select)

    def _generate_dict(self):
        ordered_combinations = self.get_pool().get_pool()
        start_at = self._pool.pool_size - self._select
        stop_before = self._pool.pool_size
        return generate_events_dict(ordered_combinations, start_at, stop_before)


class WorstOfAltDicePool(AltDicePool):
    """
    Take the worst [select] rolls from a pool of [pool_size] * [input_die].
    WorstOfAltDicePool(Die(6), 4, 3) is the worst 3 rolls from four six-sided dice.
    """
    def __init__(self, pool, select):
        super(WorstOfAltDicePool, self).__init__(pool, select)

    def _generate_dict(self):
        ordered_combinations = self.get_pool().get_pool()
        start_at = 0
        stop_before = self._select
        return generate_events_dict(ordered_combinations, start_at, stop_before)


class UpperMidOfAltDicePool(AltDicePool):
    """
    Take the middle [select] rolls from a pool of [pool_size] * [input_die].
    UpperMidOfAltDicePool(Die(6), 5, 3) is the middle 3 rolls from five six-sided dice.

    If there is no perfect middle, take the higher of two choices. For five dice that roll
    (1, 1, 2, 3, 4), select=3 takes (1, 2, 3) and select=2 takes (2, 3).
    """
    def __init__(self, pool, select):
        super(UpperMidOfAltDicePool, self).__init__(pool, select)

    def _generate_dict(self):
        ordered_combinations = self.get_pool().get_pool()
        end_slice, extra = divmod(self._pool.pool_size - self._select, 2)
        start_at = end_slice + extra
        stop_before = self._pool.pool_size - end_slice
        return generate_events_dict(ordered_combinations, start_at, stop_before)


class LowerMidOfAltDicePool(AltDicePool):
    """
    Take the middle [select] rolls from a pool of [pool_size] * [input_die].
    LowerMidOfAltDicePool(Die(6), 5, 3) is the middle 3 rolls from five six-sided dice.

    If there is no perfect middle, take the lower of two choices. For five dice that roll
    (1, 1, 2, 3, 4), select=3 takes (1, 2, 3) and select=2 takes (1, 2).
    """
    def __init__(self, pool, select):
        super(LowerMidOfAltDicePool, self).__init__(pool, select)

    def _generate_dict(self):
        ordered_combinations = self.get_pool().get_pool()
        end_slice, extra = divmod(self._pool.pool_size - self._select, 2)
        start_at = end_slice
        stop_before = self._pool.pool_size - (end_slice + extra)
        return generate_events_dict(ordered_combinations, start_at, stop_before)


def generate_events_dict(ordered_combinations, start_at, stop_before):
    master_dict = {}
    for key, val in ordered_combinations.items():
        master_key = sum(key[start_at:stop_before])
        master_dict[master_key] = master_dict.get(master_key, 0) + val
    return master_dict


