from dicetables.tools.orderedcombinations import ordered_combinations_of_events

from dicetables.dieevents import ProtoDie


class SomethingOf(ProtoDie):
    def __init__(self, input_die, pool, select):
        self._input_die = input_die
        self._pool = pool
        self._select = select
        self._dict = self._generate_dict()
        super(SomethingOf, self).__init__()

    def _generate_dict(self):
        raise NotImplementedError

    def get_input_die(self):
        return self._input_die

    def get_pool_size(self):
        return self._pool

    def get_select_size(self):
        return self._select

    def get_dict(self):
        return self._dict.copy()

    def get_size(self):
        return self._input_die.get_size() * self._pool

    def get_weight(self):
        return self._input_die.get_weight() * self._pool

    def weight_info(self):
        original_weight_info = self._input_die.weight_info().replace(str(self._input_die), 'input die info:')
        return '{}\n{}'.format(self, original_weight_info)

    def multiply_str(self, number):
        return '{}({})'.format(number, self)

    def __str__(self):
        descriptor = self.__class__.__name__.replace('Of', '')
        return '{} {} of {}'.format(descriptor, self._select, self._input_die.multiply_str(self._pool))

    def __repr__(self):
        return '{}({!r}, {}, {})'.format(self.__class__.__name__, self._input_die, self._pool, self._select)


class BestOf(SomethingOf):
    def __init__(self, input_die, pool, select):
        super(BestOf, self).__init__(input_die, pool, select)

    def _generate_dict(self):
        ordered_combinations = ordered_combinations_of_events(self._input_die, self._pool)
        slice_at = self._pool - self._select
        master_dict = {}
        for key, val in ordered_combinations.items():
            master_key = sum(key[slice_at:])
            master_dict[master_key] = master_dict.get(master_key, 0) + val
        return master_dict


