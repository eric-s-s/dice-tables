from dicetables.tools.orderedcombinations import ordered_combinations_of_events

from dicetables.dieevents import ProtoDie

# TODO DOCUMENTATION  don't forget to include in docs and doctest
class DicePool(ProtoDie):
    def __init__(self, input_die, pool_size, select):
        if select > pool_size:
            raise ValueError('you cannot select more dice than the pool_size.')
        self._input_die = input_die
        self._pool = pool_size
        self._select = select
        self._dict = self._generate_dict()
        super(DicePool, self).__init__()

    def _generate_dict(self):
        raise NotImplementedError

    def get_input_die(self):
        return self._input_die

    def get_pool_size(self):
        return self._pool

    def get_select(self):
        return self._select

    def get_dict(self):
        return self._dict.copy()

    def get_size(self):
        return self._input_die.get_size() * self._select

    def get_weight(self):
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
    def __init__(self, input_die, pool_size, select):
        super(BestOfDicePool, self).__init__(input_die, pool_size, select)

    def _generate_dict(self):
        ordered_combinations = ordered_combinations_of_events(self._input_die, self._pool)
        start_at = self._pool - self._select
        stop_before = self._pool
        return generate_events_dict(ordered_combinations, start_at, stop_before)


class WorstOfDicePool(DicePool):
    def __init__(self, input_die, pool_size, select):
        super(WorstOfDicePool, self).__init__(input_die, pool_size, select)

    def _generate_dict(self):
        ordered_combinations = ordered_combinations_of_events(self._input_die, self._pool)
        start_at = 0
        stop_before = self._select
        return generate_events_dict(ordered_combinations, start_at, stop_before)


class UpperMidOfDicePool(DicePool):
    def __init__(self, input_die, pool_size, select):
        super(UpperMidOfDicePool, self).__init__(input_die, pool_size, select)

    def _generate_dict(self):
        ordered_combinations = ordered_combinations_of_events(self._input_die, self._pool)
        end_slice, extra = divmod(self._pool - self._select, 2)
        start_at = end_slice + extra
        stop_before = self._pool - end_slice
        return generate_events_dict(ordered_combinations, start_at, stop_before)


class LowerMidOfDicePool(DicePool):
    def __init__(self, input_die, pool_size, select):
        super(LowerMidOfDicePool, self).__init__(input_die, pool_size, select)

    def _generate_dict(self):
        ordered_combinations = ordered_combinations_of_events(self._input_die, self._pool)
        end_slice, extra = divmod(self._pool - self._select, 2)
        start_at = end_slice
        stop_before = self._pool - (end_slice + extra)
        return generate_events_dict(ordered_combinations, start_at, stop_before)


def generate_events_dict(ordered_combinations, start_at, stop_before):
    master_dict = {}
    for key, val in ordered_combinations.items():
        master_key = sum(key[start_at:stop_before])
        master_dict[master_key] = master_dict.get(master_key, 0) + val
    return master_dict
