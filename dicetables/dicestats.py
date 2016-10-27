"""for all things dicey."""
from __future__ import absolute_import

from dicetables.baseevents import AdditiveEvents, IntegerEvents


class ProtoDie(IntegerEvents):
    """
    base object for any kind of die.


    :all Die objects need: get_size(), get_weight(), weight_info(), multiply_str(), all_events
    :all_events: must be sorted and have no zero occurrences.

    """
    def __init__(self):
        super(ProtoDie, self).__init__()

    def get_size(self):
        raise NotImplementedError

    def get_weight(self):
        raise NotImplementedError

    @property
    def all_events(self):
        raise NotImplementedError

    def weight_info(self):
        """return detailed info of how the die is weighted"""
        raise NotImplementedError

    def multiply_str(self, number):
        """return a string that is the die string multiplied by a number. i.e.,
        D6+1 times 3 is '3D6+3' """
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError

    def __repr__(self):
        raise NotImplementedError

    def __hash__(self):
        return hash('hash of {!r}, {}, {}, {}'.format(self,
                                                      self.get_size(),
                                                      self.get_weight(),
                                                      self.all_events))

    def __lt__(self, other):
        return (
            (self.get_size(), self.get_weight(), self.all_events, repr(self)) <
            (other.get_size(), other.get_weight(), other.all_events, repr(other))
        )

    def __eq__(self, other):
        return (
            (self.get_size(), self.get_weight(), self.all_events, repr(self)) ==
            (other.get_size(), other.get_weight(), other.all_events, repr(other))
        )

    def __ne__(self, other):
        return not self == other

    def __le__(self, other):
        return self < other or self == other

    def __gt__(self, other):
        return not self <= other

    def __ge__(self, other):
        return self == other or self > other


class Die(ProtoDie):
    """
    stores and returns info for a basic Die.
    Die(4) rolls 1, 2, 3, 4 with equal weight
    """
    def __init__(self, die_size):
        """

        :param die_size: int > 0
        """
        self._die_size = die_size
        super(Die, self).__init__()

    def get_size(self):
        return self._die_size

    def get_weight(self):
        return 0

    @property
    def all_events(self):
        return [(value, 1) for value in range(1, self._die_size + 1)]

    def weight_info(self):
        return str(self) + '\n    No weights'

    def multiply_str(self, number):
        return '{}{}'.format(number, self)

    def __str__(self):
        return 'D{}'.format(self._die_size)

    def __repr__(self):
        return 'Die({})'.format(self._die_size)


class ModDie(Die):
    """
    stores and returns info for a Die with a modifier
    that changes the values of the rolls.
    ModDie(4, -1) rolls 0, 1, 2, 3 with equal weight
    """
    def __init__(self, die_size, modifier):
        """

        :param die_size: int >0
        :param modifier: int
        """
        self._mod = modifier
        super(ModDie, self).__init__(die_size)

    def get_modifier(self):
        return self._mod

    @property
    def all_events(self):
        return [(value + self._mod, 1) for value in range(1, self._die_size + 1)]

    def multiply_str(self, number):
        return '{}D{}{:+}'.format(number, self._die_size, number * self._mod)

    def __str__(self):
        return 'D{0}{1:+}'.format(self._die_size, self._mod)

    def __repr__(self):
        return 'ModDie({}, {})'.format(self._die_size, self._mod)


class WeightedDie(ProtoDie):
    """
    stores and returns info for die with different chances for different rolls.
    WeightedDie({1:1, 2:5}) rolls 1 once for every five times that 2 is rolled.
    """
    def __init__(self, dictionary_input):
        """

        :param dictionary_input: {roll: weight} roll: int>1, weight: int>=0\n
            the sum of all weights >0
        """
        self._dic = dictionary_input.copy()
        self._raise_value_error_for_rolls_less_than_one()
        self._die_size = max(self._dic.keys())
        self._weight = sum(self._dic.values())
        super(WeightedDie, self).__init__()

    def _raise_value_error_for_rolls_less_than_one(self):
        if any(roll < 1 for roll in self._dic.keys()):
            raise ValueError('rolls may not be less than 1. use ModWeightedDie')

    def get_size(self):
        return self._die_size

    def get_weight(self):
        return self._weight

    @property
    def all_events(self):
        return sorted([pair for pair in self._dic.items() if pair[1]])

    def weight_info(self):
        num_len = len(str(self._die_size))
        out = str(self) + '\n'
        for roll in range(1, self._die_size + 1):
            out += ('    a roll of {:>{}} has a weight of {}\n'
                    .format(roll, num_len, self._dic.get(roll, 0)))
        return out.rstrip('\n')

    def multiply_str(self, number):
        return '{}{}'.format(number, self)

    def __str__(self):
        return 'D{}  W:{}'.format(self._die_size, self._weight)

    def __repr__(self):
        new_dic = {}
        for roll in range(1, self.get_size() + 1):
            new_dic[roll] = self._dic.get(roll, 0)
        return 'WeightedDie({})'.format(new_dic)


class ModWeightedDie(WeightedDie):
    """
    stores and returns info for die with different chances for different rolls.
    The modifier changes all die rolls
    WeightedDie({1:1, 2:5}, -1) rolls 0 once for every five times that 1 is rolled.
    """

    def __init__(self, dictionary_input, modifier):
        """

        :param dictionary_input: {roll: weight} roll: int, weight: int>=0\n
            sum of all weights >0
        :param modifier: int
        """
        self._mod = modifier
        super(ModWeightedDie, self).__init__(dictionary_input)

    def get_modifier(self):
        return self._mod

    @property
    def all_events(self):
        return sorted([(roll + self._mod, weight) for roll, weight in self._dic.items() if weight])

    def multiply_str(self, number):
        return '{0}D{1}{2:+}  W:{3}'.format(number, self._die_size,
                                            number * self._mod, self._weight)

    def __str__(self):
        return 'D{0}{1:+}  W:{2}'.format(self._die_size, self._mod, self._weight)

    def __repr__(self):
        to_fix = super(ModWeightedDie, self).__repr__()[:-1]
        return 'Mod' + to_fix + ', {})'.format(self._mod)


class StrongDie(ProtoDie):
    """
    stores and returns info for a stronger version of another die.
    The multiplier multiplies all die rolls of original Die.
    StrongDie(ModDie(3, -1), 2) rolls (1-1)*2, (2-1)*2, (3-1)*2 with equal weight.
    """

    def __init__(self, input_die, multiplier):
        """

        :param input_die: Die, ModDie, WeightedDie, ModWeightedDie, StrongDie or subclass of ProtoDie
        :param multiplier: int >=1
        """
        self._original = input_die
        self._multiplier = multiplier
        super(StrongDie, self).__init__()

    def get_size(self):
        return self._original.get_size()

    def get_weight(self):
        return self._original.get_weight()

    def get_multiplier(self):
        return self._multiplier

    def get_input_die(self):
        """returns an instance of the original die"""
        return self._original

    @property
    def all_events(self):
        old = self._original.all_events
        return [(pair[0] * self._multiplier, pair[1]) for pair in old]

    def weight_info(self):
        return self._original.weight_info().replace(str(self._original), str(self))

    def multiply_str(self, number):
        return '({})X{}'.format(self._original.multiply_str(number),
                                self._multiplier)

    def __str__(self):
        return '({})X{}'.format(self._original, self.get_multiplier())

    def __repr__(self):
        return 'StrongDie({!r}, {})'.format(self._original,
                                            self._multiplier)


class DiceTable(AdditiveEvents):
    """
    DiceTable() creates an empty table that dice can be added to and removed from
    """

    def __init__(self):
        super(DiceTable, self).__init__({0: 1})
        self._dice_list = {}

    def update_list(self, number_added, die):
        """

        :param number_added: int: can be negative but should not reduce "die" count below zero
        :param die: Die, ModDie, WeightedDie, ModWeightedDie, StrongDie or new ProtoDie subclass
        """
        self._dice_list[die] = self._dice_list.get(die, 0) + number_added
        if self._dice_list[die] == 0:
            del self._dice_list[die]

    def get_list(self):
        """

        :return: sorted copy of dice list: [(die, number of dice), ...]
        """
        return sorted(self._dice_list.items())

    def number_of_dice(self, query_die):
        return self._dice_list.get(query_die, 0)

    def weights_info(self):
        """

        :return: str: complete info for all dice
        """
        out_str = ''
        for die, number in self.get_list():
            adjusted = die.weight_info().replace(str(die),
                                                 die.multiply_str(number))
            out_str += adjusted + '\n\n'
        return out_str.rstrip('\n')

    def __str__(self):
        out_str = ''
        for die, number in self.get_list():
            out_str += '{}\n'.format(die.multiply_str(number))
        return out_str.rstrip('\n')

    def add_die(self, number, die):
        """

        :param number: int>= 0
        :param die: Die, ModDie, WeightedDie, ModWeightedDie, StrongDie or new ProtoDie subclass
        """
        self.combine(number, die)
        self.update_list(number, die)

    def raise_error_for_too_many_removes(self, num, die):
        if self.number_of_dice(die) < num:
            raise ValueError('dice not in table, or removed too many dice')

    def remove_die(self, number, die):
        """

        :param number: int>=number of "die" in table
        :param die: Die, ModDie, WeightedDie, ModWeightedDie, StrongDie or new ProtoDie subclass
        """
        self.raise_error_for_too_many_removes(number, die)
        self.remove(number, die)
        self.update_list(-1 * number, die)

