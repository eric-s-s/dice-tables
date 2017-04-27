"""
All the descendants of ProtoDie.  These are IntegerEvents that represent different types of dice.
"""

from dicetables.eventsbases.protodie import ProtoDie


class Modifier(ProtoDie):
    """
    stores and returns info for a modifier to add to the final die roll.
    Modifier(-3) rolls -3 and only -3
    """
    def __init__(self, modifier):
        self._mod = modifier
        super(Modifier, self).__init__()

    def get_modifier(self):
        return self._mod

    def get_size(self):
        return 0

    def get_weight(self):
        return 0

    def get_dict(self):
        return {self._mod: 1}

    def weight_info(self):
        return str(self)

    def multiply_str(self, number):
        return '\n'.join([str(self)] * number)

    def __str__(self):
        return '{:+}'.format(self._mod)

    def __repr__(self):
        return 'Modifier({})'.format(self._mod)


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
        return '{}\n    No weights'.format(self)

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

        self._raw_dic = self._create_raw_dict(dictionary_input)
        super(WeightedDie, self).__init__()

    def _create_raw_dict(self, dictionary):
        self._raise_value_error_for_rolls_less_than_one(dictionary)
        output = {}
        for key in range(1, max(dictionary.keys()) + 1):
            output[key] = dictionary.get(key, 0)
        return output

    @staticmethod
    def _raise_value_error_for_rolls_less_than_one(dictionary):
        if any(roll < 1 for roll in dictionary):
            raise ValueError('rolls may not be less than 1. use ModWeightedDie')

    def get_raw_dict(self):
        return self._raw_dic.copy()

    def get_size(self):
        return max(self._raw_dic.keys())

    def get_weight(self):
        return sum(self._raw_dic.values())

    def get_dict(self):
        return {key: value for key, value in self._raw_dic.items() if value}

    def weight_info(self):
        max_roll_str_len = len(str(self.get_size()))
        out = str(self) + '\n'
        for roll, weight in sorted(self.get_raw_dict().items()):
            out += '    a roll of {:>{}} has a weight of {}\n'.format(roll, max_roll_str_len, weight)
        return out.rstrip('\n')

    def multiply_str(self, number):
        return '{}{}'.format(number, self)

    def __str__(self):
        return 'D{}  W:{}'.format(self.get_size(), self.get_weight())

    def __repr__(self):
        return 'WeightedDie({})'.format(self._raw_dic)


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
        return {roll + self._mod: weight for roll, weight in self.get_raw_dict().items() if weight}

    def multiply_str(self, number):
        return '{}D{}{:+}  W:{}'.format(number, self.get_size(),
                                        number * self._mod, self.get_weight())

    def __str__(self):
        return 'D{}{:+}  W:{}'.format(self.get_size(), self._mod, self.get_weight())

    def __repr__(self):
        return 'ModWeightedDie({}, {})'.format(self.get_raw_dict(), self._mod)


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
        return {roll * self._multiplier: weight for roll, weight in self._original.get_dict().items()}

    def weight_info(self):
        return self._original.weight_info().replace(str(self._original), str(self))

    def multiply_str(self, number):
        return '({})X({})'.format(self._original.multiply_str(number), self._multiplier)

    def __str__(self):
        return '({})X({})'.format(self._original, self._multiplier)

    def __repr__(self):
        return 'StrongDie({!r}, {})'.format(self._original, self._multiplier)
