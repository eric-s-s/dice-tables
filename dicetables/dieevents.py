"""
All the descendants of ProtoDie.  These are IntegerEvents that represent different types of dice.
"""
import itertools
from typing import Dict, Iterable, Tuple

from dicetables.eventsbases.protodie import ProtoDie


class Modifier(ProtoDie):
    """
    stores and returns info for a modifier to add to the final die roll.
    :code:`Modifier(-3)` rolls -3 and only -3. A Modifier's size and weight are
    always 0.
    """

    def __init__(self, modifier: int):
        self._mod = modifier
        super(Modifier, self).__init__()

    def get_modifier(self) -> int:
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
    :code:`Die(4)` rolls 1, 2, 3, 4 with equal weight
    """

    def __init__(self, die_size: int):
        """

        :param die_size: int > 0
        """
        self._die_size = die_size
        super(Die, self).__init__()

    def get_size(self):
        return self._die_size

    def get_weight(self):
        return 0

    def get_dict(self) -> Dict[int, int]:
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
    :code:`ModDie(4, -1)` rolls 0, 1, 2, 3 with equal weight
    """

    def __init__(self, die_size: int, modifier: int):
        """

        :param die_size: int >0
        :param modifier: int
        """
        self._mod = modifier
        super(ModDie, self).__init__(die_size)

    def get_modifier(self) -> int:
        return self._mod

    def get_dict(self) -> Dict[int, int]:
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
    :code:`WeightedDie({1:1, 2:5})` rolls 1 once for every five times that 2 is rolled.
    """

    def __init__(self, dictionary_input: Dict[int, int]):
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

    def get_raw_dict(self) -> Dict[int, int]:
        return self._raw_dic.copy()

    def get_size(self):
        return max(self._raw_dic.keys())

    def get_weight(self):
        return sum(self._raw_dic.values())

    def get_dict(self) -> Dict[int, int]:
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
    The modifier changes all die rolls.
    :code:`ModWeightedDie({1:1, 3:5}, -1)` is a 3-sided die - 1. It
    rolls 0 once for every five times that 2 is rolled.
    """

    def __init__(self, dictionary_input: Dict[int, int], modifier: int):
        """

        :param dictionary_input: {roll: weight} roll: int, weight: int>=0\n
            sum of all weights >0
        :param modifier: int
        """
        self._mod = modifier
        super(ModWeightedDie, self).__init__(dictionary_input)

    def get_modifier(self) -> int:
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
    stores and returns info for a stronger version of another die (including
    StrongDie if you're feeling especially silly).
    The multiplier multiplies all die rolls of original Die.
    :code:`StrongDie(ModDie(3, -1), 2)` rolls (1-1)*2, (2-1)*2, (3-1)*2 with equal weight.
    """

    def __init__(self, input_die: ProtoDie, multiplier: int):
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

    def get_input_die(self) -> ProtoDie:
        """returns an instance of the original die"""
        return self._original

    def get_dict(self) -> Dict[int, int]:
        return {roll * self._multiplier: weight for roll, weight in self._original.get_dict().items()}

    def weight_info(self):
        return self._original.weight_info().replace(str(self._original), str(self))

    def multiply_str(self, number):
        return '({})X({})'.format(self._original.multiply_str(number), self._multiplier)

    def __str__(self):
        return '({})X({})'.format(self._original, self._multiplier)

    def __repr__(self):
        return 'StrongDie({!r}, {})'.format(self._original, self._multiplier)


class Exploding(ProtoDie):
    """
    Stores and returns info for an exploding version of another die.
    Each time the highest number is rolled, you
    add that to the total and keep rolling. An exploding D6 rolls 1-5 as usual.
    When it rolls a 6, it re-rolls and adds that 6. If it rolls a 6 again, this continues,
    adding 12 to the result. Since this is an infinite but increasingly unlikely process,
    the "explosions" parameter sets the number of re-rolls allowed.

    Explosions are applied after modifiers and multipliers.
    :code:`Exploding(ModDie(4, -2))` explodes on a 2 so it rolls:
    [-1, 0, 1, (2 -1), (2 + 0), (2 + 1), (2+2 - 1) ..]

    **WARNING:** setting the number of explosions too high can make
    instantiation VERY slow. The time is proportional to explosions and die_size.
    """

    def __init__(self, input_die: ProtoDie, explosions: int = 2):
        """

        :param input_die: Die, ModDie, WeightedDie, ModWeightedDie, StrongDie or subclass of ProtoDie
        :param explosions: int >=0
        """
        self._original = input_die
        self._explosions = explosions
        self._raise_error_for_negative_explosions()
        self._dict = self._get_exploding_dict()
        super(Exploding, self).__init__()

    def _raise_error_for_negative_explosions(self):
        if self._explosions < 0:
            raise ValueError('"explosions" must be >=0.')

    def _get_exploding_dict(self):
        base_dict = self._original.get_dict()

        new_dict = {}
        for explosion_level in range(self._explosions + 1):
            level_dict = self._get_level_dict(explosion_level, base_dict)
            new_dict = add_dicts(new_dict, level_dict)
        return new_dict

    def _get_level_dict(self, explosion_level, base_dict):
        highest_roll = max(base_dict)

        all_occurrences = sum(base_dict.values())
        level_depth_multiplier = all_occurrences ** (self._explosions - explosion_level)
        highest_roll_multiplier = base_dict[highest_roll] ** explosion_level

        occurrence_mod = level_depth_multiplier * highest_roll_multiplier
        roll_mod = explosion_level * highest_roll

        level_dict = {roll + roll_mod: occurrence * occurrence_mod for roll, occurrence in base_dict.items()}
        if explosion_level == self._explosions:
            return level_dict
        return remove_keys_after_applying_modifier(level_dict, (highest_roll,), roll_mod)

    def get_size(self):
        return self._original.get_size()

    def get_weight(self):
        return self._original.get_weight() + 1

    def get_explosions(self) -> int:
        return self._explosions

    def get_input_die(self) -> ProtoDie:
        """returns an instance of the original die"""
        return self._original

    def get_dict(self) -> Dict[int, int]:
        return self._dict.copy()

    def weight_info(self):
        return '{}\nExploding adds weight: 1'.format(
            self._original.weight_info().replace(str(self._original), str(self)))

    def multiply_str(self, number):
        return '{}({})'.format(number, self)

    def __str__(self):
        return '{}: Explosions={}'.format(self._original, self._explosions)

    def __repr__(self):
        return 'Exploding({!r}, {})'.format(self._original, self._explosions)


class ExplodingOn(ProtoDie):
    """
    Stores and returns info for an exploding version of another die.
    Each time the values in (explodes_on) are rolled, the die continues to roll,
    adding that value to the result. The die only continues rolling an (explosions) number of times.

    :code:`ExplodingOn(Die(6), (1, 6), explosions=2)` rolls:
    [2 to 5], 1+[2 to 5], 6+[2 to 5], 1+1+[1 to 6], 1+6+[1 to 6], 6+1+[1 to 6] and 6+6+[1 to 6].

    Explosions are applied after modifiers and multipliers.
    :code:`ExplodingOn(ModDie(4, -2), (2,))` explodes on a 2 so it rolls:
    [-1, 0, 1, (2 -1), (2 + 0), (2 + 1), (2+2 - 1) ..]

    **WARNING:** setting the number of explosions too high can make
    instantiation VERY slow. Time is proportional to explosion**(len(explodes_on)). It's also linear
    with size which gets overshadowed by the first factor.
    """

    def __init__(self, input_die: ProtoDie, explodes_on: Iterable[int], explosions: int=2):
        """

        :param input_die: Die, ModDie, WeightedDie, ModWeightedDie, StrongDie or subclass of ProtoDie
        :param explodes_on: tuple[int] - rolls that die explodes on. Must be in keys of input_die.get_dict().
        :param explosions: int >=0
        """
        self._explodes_on = remove_duplicates(explodes_on)
        self._explosions = explosions
        self._original = input_die
        self._raise_error_for_bad_explodes_on()
        self._raise_error_for_negative_explosions()
        self._dict = self._get_exploding_dict()
        super(ExplodingOn, self).__init__()

    def _raise_error_for_bad_explodes_on(self):
        base_dict = self._original.get_dict()
        if any(key not in base_dict for key in self._explodes_on):
            raise ValueError('"explodes_on" value not present in input_die.get_dict()')

    def _raise_error_for_negative_explosions(self):
        if self._explosions < 0:
            raise ValueError('"explosions" value must be >= 0.')

    def _get_exploding_dict(self):
        base_dict = self._original.get_dict()
        answer = {}
        for level in range(self._explosions + 1):
            roll_and_weight_modifiers = self._get_roll_and_weight_mods(level, base_dict)
            level_dict = self._get_level_dict(base_dict, level, roll_and_weight_modifiers)
            answer = add_dicts(answer, level_dict)
        return answer

    def _get_roll_and_weight_mods(self, level, base_dict):
        if level == 0:
            return [(0, 1)]
        base_roll_weight_mods = [(roll, base_dict[roll]) for roll in self._explodes_on]
        groups_of_roll_weight_mods = itertools.product(base_roll_weight_mods, repeat=level)
        return [calc_roll_and_weight_mods(group_of_rollweights) for group_of_rollweights in groups_of_roll_weight_mods]

    def _get_level_dict(self, base_dict, level, roll_weights):
        answer = {}
        roll_weight_dict = combine_rollweights_with_same_roll_value(roll_weights)
        for roll_mod, weight_mod in roll_weight_dict.items():
            to_add = self._get_partial_level_dict(base_dict, level, roll_mod, weight_mod)
            answer = add_dicts(answer, to_add)
        return answer

    def _get_partial_level_dict(self, base_dict, level, roll_mod, weight_multiplier):
        base_level_multiplier = sum(base_dict.values())
        level_multiplier = base_level_multiplier ** (self._explosions - level)
        current_level_all_rolls = {roll + roll_mod: occurrence * weight_multiplier * level_multiplier
                                   for roll, occurrence in base_dict.items()}
        if level == self._explosions:
            return current_level_all_rolls

        return remove_keys_after_applying_modifier(current_level_all_rolls, self._explodes_on, roll_mod)

    def get_size(self):
        return self._original.get_size()

    def get_weight(self):
        return self._original.get_weight() + len(self._explodes_on)

    def get_explosions(self):
        return self._explosions

    def get_explodes_on(self) -> Tuple[int, ...]:
        return self._explodes_on

    def get_input_die(self) -> ProtoDie:
        """returns an instance of the original die"""
        return self._original

    def get_dict(self) -> Dict[int, int]:
        return self._dict.copy()

    def weight_info(self):
        base_weight_info = self._original.weight_info().replace(str(self._original), str(self))
        num_of_values = len(self._explodes_on)
        value_str = 'value' if num_of_values == 1 else 'values'
        return '{0}\nExploding on {1} {2} adds weight: {1}'.format(base_weight_info, num_of_values, value_str)

    def multiply_str(self, number):
        return '{}({})'.format(number, self)

    def __str__(self):
        explodes_on = ', '.join([str(val) for val in self._explodes_on])
        return '{}: Explosions={} On: {}'.format(self._original, self._explosions, explodes_on)

    def __repr__(self):
        return 'ExplodingOn({!r}, {}, {})'.format(self._original, self._explodes_on, self._explosions)


def remove_duplicates(input_tuple: Iterable[int]) -> Tuple[int, ...]:
    list_version = []
    for val in input_tuple:
        if val not in list_version:
            list_version.append(val)
    return tuple(list_version)


def add_dicts(dict_1, dict_2):
    out = dict_1.copy()
    for key, val in dict_2.items():
        out[key] = out.get(key, 0) + val
    return out


def calc_roll_and_weight_mods(group_of_rollweights):
    total_roll_mod = 0
    total_weight_mod = 1
    for roll, weight in group_of_rollweights:
        total_roll_mod += roll
        total_weight_mod *= weight
    return total_roll_mod, total_weight_mod


def remove_keys_after_applying_modifier(modified_dict, original_excluded_keys, key_modifier):
    return {key: val for key, val in modified_dict.items() if key - key_modifier not in original_excluded_keys}


def combine_rollweights_with_same_roll_value(rollweight_tuples):
    answer = {}
    for roll, weight in rollweight_tuples:
        answer[roll] = weight + answer.get(roll, 0)
    return answer
