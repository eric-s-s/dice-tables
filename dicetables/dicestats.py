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

    def get_dict(self):
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
                                                      self.get_dict()))

    def __lt__(self, other):
        return (
            (self.get_size(), self.get_weight(), sorted(self.get_dict().items()), repr(self)) <
            (other.get_size(), other.get_weight(), sorted(other.get_dict().items()), repr(other))
        )

    def __eq__(self, other):
        return (
            (self.get_size(), self.get_weight(), sorted(self.get_dict().items()), repr(self)) ==
            (other.get_size(), other.get_weight(), sorted(other.get_dict().items()), repr(other))
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

    def get_dict(self):
        return dict.fromkeys(range(1, self._die_size + 1), 1)

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

    def get_dict(self):
        return dict.fromkeys(range(1 + self._mod, self.get_size() + 1 + self._mod), 1)

    def multiply_str(self, number):
        return '{}D{}{:+}'.format(number, self.get_size(), number * self._mod)

    def __str__(self):
        return 'D{}{:+}'.format(self.get_size(), self._mod)

    def __repr__(self):
        return 'ModDie({}, {})'.format(self.get_size(), self._mod)


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

        self._raw_dic = dictionary_input.copy()
        self._raise_value_error_for_rolls_less_than_one()
        super(WeightedDie, self).__init__()

    def _raise_value_error_for_rolls_less_than_one(self):
        if any(roll < 1 for roll in self._raw_dic.keys()):
            raise ValueError('rolls may not be less than 1. use ModWeightedDie')

    def get_raw_dict(self):
        return self._raw_dic.copy()

    def get_size(self):
        return max(self._raw_dic.keys())

    def get_weight(self):
        return sum(self._raw_dic.values())

    def get_dict(self):
        return dict([item for item in self._raw_dic.items() if item[1]])

    def weight_info(self):
        max_roll_str_len = len(str(self.get_size()))
        out = str(self) + '\n'
        for roll in range(1, self.get_size() + 1):
            out += ('    a roll of {:>{}} has a weight of {}\n'
                    .format(roll, max_roll_str_len, self._raw_dic.get(roll, 0)))
        return out.rstrip('\n')

    def multiply_str(self, number):
        return '{}{}'.format(number, self)

    def __str__(self):
        return 'D{}  W:{}'.format(self.get_size(), self.get_weight())

    def __repr__(self):
        new_dic = {}
        for roll in range(1, self.get_size() + 1):
            new_dic[roll] = self._raw_dic.get(roll, 0)
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

    def get_dict(self):
        new = {}
        for roll, weight in self.get_raw_dict().items():
            if weight:
                new[roll + self._mod] = weight
        return new

    def multiply_str(self, number):
        return '{}D{}{:+}  W:{}'.format(number, self.get_size(),
                                        number * self._mod, self.get_weight())

    def __str__(self):
        return 'D{}{:+}  W:{}'.format(self.get_size(), self._mod, self.get_weight())

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
        :param multiplier: int
        """
        self._multiplier = multiplier
        self._original = input_die
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

    def get_dict(self):
        new = {}
        old = self._original.get_dict()
        for roll, weight in old.items():
            new[roll * self._multiplier] = weight
        return new

    def weight_info(self):
        return self._original.weight_info().replace(str(self._original), str(self))

    def multiply_str(self, number):
        return '({})X({})'.format(self._original.multiply_str(number), self._multiplier)

    def __str__(self):
        return '({})X({})'.format(self._original, self._multiplier)

    def __repr__(self):
        return 'StrongDie({!r}, {})'.format(self._original, self._multiplier)


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
        raise_error_for_negative_number(number)
        self.combine(number, die)
        self.update_list(number, die)

    def remove_die(self, number, die):
        """

        :param number: int>=number of "die" in table
        :param die: Die, ModDie, WeightedDie, ModWeightedDie, StrongDie or new ProtoDie subclass
        """
        raise_error_for_negative_number(number)
        self._raise_error_for_too_many_removes(number, die)
        self.remove(number, die)
        self.update_list(-1 * number, die)

    def _raise_error_for_too_many_removes(self, num, die):
        if self.number_of_dice(die) < num:
            raise ValueError('dice not in table, or removed too many dice')


def raise_error_for_negative_number(number):
    if number < 0:
        raise ValueError('number must be int >= 0')