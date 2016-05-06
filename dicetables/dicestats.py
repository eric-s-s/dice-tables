'''for all things dicey.  this contains DiceInfo and DiceTable and add_dice.'''
from __future__ import absolute_import


from dicetables.longintmath import LongIntTable

class ProtoDie(object):
    '''a blanket object for any kind of die so that different types of Die can
    be compared.  all Die objects need these five methods. str and repr'''
    def get_size(self):
        '''return the size of the die'''
        raise NotImplementedError
    def get_weight(self):
        '''return the total weight of the die, if weighted'''
        raise NotImplementedError
    def tuple_list(self):
        '''return an ordered tuple list of [(die, weight) ... ] with zero weights
        removed'''
        raise NotImplementedError
    def weight_info(self):
        '''return detailed info of how the die is weighted'''
        raise NotImplementedError
    def multiply_str(self, number):
        '''return a string that is the die string multiplied by a number. i.e.,
        D6+1 times 3 is 3D6+3'''
        raise NotImplementedError
    def __str__(self):
        raise NotImplementedError
    def __repr__(self):
        raise NotImplementedError
    def __hash__(self):
        return hash('hash of {!r}, {}, {}, {}'.format(self, self.get_size(),
                                                      self.get_weight(),
                                                      self.tuple_list()))

    def __lt__(self, other):
        '''Dice are compared by size, then weight, then tuple_list, and finally
        repr'''
        return (
            (self.get_size(), self.get_weight(), self.tuple_list(), repr(self)) <
            (other.get_size(), other.get_weight(), other.tuple_list(), repr(other))
            )
    def __eq__(self, other):
        return (
            (self.get_size(), self.get_weight(), self.tuple_list(), repr(self)) ==
            (other.get_size(), other.get_weight(), other.tuple_list(), repr(other))
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
    '''makes instance of a die.  it has a size and a weight of 0 (for comparing
    with weighted dice which have non-zero weight)'''
    def __init__(self, die_size):
        '''die size is a positive int. creates a die containing 1 to die_size
        values'''
        self._die_size = die_size
        self._weight = 0
    def get_size(self):
        '''returns the size of the die'''
        return self._die_size
    def get_weight(self):
        '''returns the weight of the die'''
        return self._weight
    def tuple_list(self):
        '''returns the tuple list that is the dice values'''
        return [(value, 1) for value in range(1, self._die_size + 1)]

    def weight_info(self):
        '''returns detailed weight info, indented'''
        return str(self) + '\n    No weights'
    def multiply_str(self, number):
        '''return the str of die times a number. 5, D6+3 --> 5D6+15'''
        return '{}{}'.format(number, self)
    def __str__(self):
        return 'D{}'.format(self._die_size)
    def __repr__(self):
        return 'Die({})'.format(self.get_size())

class ModDie(Die):
    '''a Die with a modifier.  i.e. D6-3.'''
    def __init__(self, die_size, modifier):
        '''as Die init, die_size is a positive int.  modifier is an int'''
        Die.__init__(self, die_size)
        self._mod = modifier

    def get_modifier(self):
        '''returns the modifier of a modded die'''
        return self._mod
    def tuple_list(self):
        '''returns the tuple list with the values adjusted by the modifier'''
        return [(value + self._mod, 1)
                for value in range(1, self._die_size + 1)]

    def multiply_str(self, number):
        '''return the str of die times a number. 5, D6+3 --> 5D6+15'''
        return '{}D{}{:+}'.format(number, self._die_size, number * self._mod)
    def __str__(self):
        return 'D{0}{1:+}'.format(self._die_size, self._mod)
    def __repr__(self):
        return 'ModDie({}, {})'.format(self.get_size(), self.get_modifier())

class WeightedDie(ProtoDie):
    '''stores and returns info for a weighted die.'''
    def __init__(self, dictionary_input):
        '''dictionary input is a dictionary of value:weight. values are positive
        int and weights are zero or positive ints.
        {1:3, 2:0, 3:1} creates a D3 that rolls a one 3 times more than a three
        and never rolls a two.'''
        self._dic = dictionary_input.copy()
        self._die_size = max(self._dic.keys())
        self._weight = sum(self._dic.values())

    def get_size(self):
        '''returns the size of the die'''
        return self._die_size
    def get_weight(self):
        '''returns the weight of the die'''
        return self._weight

    def tuple_list(self):
        '''returns the tuple list that is the dice values'''
        out = []
        for value, weight in self._dic.items():
            if weight != 0:
                out.append((value, weight))
        out.sort()
        return out

    def weight_info(self):
        '''returns detailed weight info, indented'''
        out = str(self) + '\n'
        for roll in range(1, self._die_size + 1):
            out += ('    a roll of {} has a weight of {}\n'
                    .format(roll, self._dic.get(roll, 0)))
        return out.rstrip('\n')
    def multiply_str(self, number):
        '''return the str of die times a number. 5, D6+3 --> 5D6+15'''
        return '{}{}'.format(number, self)
    def __str__(self):
        return 'D{}  W:{}'.format(self._die_size, self._weight)
    def __repr__(self):
        new_dic = {}
        for roll in range(1, self.get_size() + 1):
            new_dic[roll] = self._dic.get(roll, 0)
        return 'WeightedDie({})'.format(new_dic)


class ModWeightedDie(WeightedDie):
    '''stores and returns info for a weighted die. and a modifier modifies the
    values'''
    def __init__(self, dictionary_input, modifier):
        '''dictionary input is a dictionary of positive ints, value:weight.
        modifier is an int that modifies values. {1:3, 2:1, 3:1}, -3 creates a
        D3 that rolls a one(-3) 3 times more than a two(-3) or a three(-3).'''
        WeightedDie.__init__(self, dictionary_input)
        self._mod = modifier
    def get_modifier(self):
        '''returns the modifier on the die'''
        return self._mod
    def tuple_list(self):
        '''returns the tuple list that is the dice values adjust by the mod'''
        out = []
        for value, weight in self._dic.items():
            if weight != 0:
                out.append((value + self._mod, weight))
        out.sort()
        return out

    def multiply_str(self, number):
        '''return the str of die times a number. 5, D6+3 --> 5D6+15'''
        return '{0}D{1}{2:+}  W:{3}'.format(number, self._die_size,
                                            number * self._mod, self._weight)
    def __str__(self):
        return 'D{0}{1:+}  W:{2}'.format(self._die_size, self._mod, self._weight)
    def __repr__(self):
        to_fix = super(ModWeightedDie, self).__repr__()[:-1]
        return 'Mod' + to_fix + ', {})'.format(self.get_modifier())

class DiceTable(LongIntTable):
    '''this is a LongIntTable with a list that holds information about the dice
    added to it and removed from it.'''
    def __init__(self):
        LongIntTable.__init__(self, {0:1})
        self._dice_list = {}

    def update_list(self, add_number, new_die):
        '''adds die and number of dice to the list. if die is already in list,
        adds old and new number together.'''
        self._dice_list[new_die] = self._dice_list.get(new_die, 0) + add_number
        if self._dice_list[new_die] == 0:
            del self._dice_list[new_die]

    def get_list(self):
        '''return copy of dice list. a list of tuples, (die, number of dice)'''
        return sorted(self._dice_list.items())
    def number_of_dice(self, query_die):
        '''returns the number of that die in the dice list, or zero if not in
        the list'''
        return self._dice_list.get(query_die, 0)

    def weights_info(self):
        '''return detailed info of dice in the list'''
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

    def add_die(self, num, die):
        '''adds the die to the table num times and updates the table, list.  die
        is a  Die or WeightedDie and num is a positive int or 0.'''
        self.add(num, die.tuple_list())
        self.update_list(num, die)

    def remove_die(self, num, die):
        '''die is a  Die or WeightedDie and num is a positive int or 0.first
        makes sure the dice to be removed are in the list. then removes those
        dice from the list and the table.'''
        if self.number_of_dice(die) - num < 0:
            raise ValueError('dice not in table, or removed too many dice')
        else:
            self.remove(num, die.tuple_list())
            self.update_list(-num, die)





