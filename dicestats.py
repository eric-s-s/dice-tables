'''for all things dicey.  this contains DiceInfo and DiceTable and add_dice.'''
from longintmath import LongIntTable

class ProtoDie(object):
    '''a blanket object for any kind of die so that different types of Die can
    be compared.  all Die objects need these five methods.'''
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

    def __lt__(self, other):
        '''Dice are compared by size, then weight, then tuple_list'''
        return ((self.get_size(), self.get_weight(), self.tuple_list()) <
                (other.get_size(), other.get_weight(), other.tuple_list()))
    def __eq__(self, other):
        return ((self.tuple_list(), self.get_size(), self.get_weight()) ==
                (other.tuple_list(), other.get_size(), other.get_weight()))
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
        return '%s%s' % (number, self)
    def __str__(self):
        return 'D%s' % (self._die_size)

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
        return '%s%s%s' % (number, str(self)[:-1], number * abs(self._mod))
    def __str__(self):
        return 'D{0}{1:+}'.format(self._die_size, self._mod)


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
            out = (out +'    a roll of %s has a weight of %s\n' %
                   (roll, self._dic.get(roll, 0)))
        return out.rstrip('\n')
    def multiply_str(self, number):
        '''return the str of die times a number. 5, D6+3 --> 5D6+15'''
        return '%s%s' % (number, self)
    def __str__(self):
        return 'D%s  W:%s' % (self._die_size, self._weight)

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

class DiceTable(LongIntTable):
    '''this is a LongIntTable with a list that holds information about the dice
    added to it and removed from it.'''
    def __init__(self):
        LongIntTable.__init__(self, {0:1})
        self._dice_list = []

    def update_list(self, add_number, new_die):
        '''adds die and number of dice to the list. if die is already in list,
        adds old and new number together.'''
        new_list = []
        in_list = False
        for old_die, number in self._dice_list:
            if new_die == old_die:
                if number + add_number != 0:
                    new_list.append((new_die, number + add_number))
                in_list = True
            else:
                new_list.append((old_die, number))
        if not in_list and add_number != 0:
            new_list.append((new_die, add_number))
        new_list.sort()
        self._dice_list = new_list

    def get_list(self):
        '''return copy of dice list. a list of tuples, (die, number of dice)'''
        return self._dice_list[:]
    def number_of_dice(self, query_die):
        '''returns the number of that die in the dice list, or zero if not in
        the list'''
        answer = 0
        for die, number in self._dice_list:
            if die == query_die:
                answer = number
                break
        return answer

    def weights_info(self):
        '''return detailed info of dice in the list'''
        out_str = ''
        for die, number in self._dice_list:
            out_str = (out_str +
                       die.weight_info().replace(str(die), die.multiply_str(number))
                       + '\n\n')
        return out_str.rstrip('\n')

    def __str__(self):
        out_str = ''
        for die, number in self._dice_list:
            out_str = out_str + '%s\n' % (die.multiply_str(number))
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



#some wrapper functions for ease of use
def make_die(die_input, mod):
    '''takes legal input for Die or WeightedDie and returns object. input can
    be int for Die, or list, tuple_list, dict for WeightedDie. mod is an int
    [1,1,1,2,3], {1:3, 2:1, 3:1}, [(1,3), (2,1), (3,1)] all make a weighted die
    of size 3 and where one gets rolled 3 times as often as 2 or 3'''
    if isinstance(die_input, int):
        if mod == 0:
            return Die(die_input)
        else:
            return ModDie(die_input, mod)
    else:
        if mod == 0:
            return WeightedDie(dictionary_maker(die_input))
        else:
            return ModWeightedDie(dictionary_maker(die_input), mod)

#helper to make_die
def dictionary_maker(mystery_input):
    '''mystery input can be a list, a list of tuples or a dictionary. returns the
    dictionary of the input. all are shallow copies!! if elements are mutable,
    new element points to original element.'''
    if isinstance(mystery_input, list):
        if isinstance(mystery_input[0], tuple):
            return dict(pair for pair in mystery_input)
        else:
            out = {}
            for value in mystery_input:
                out[value] = out.get(value, 0) + 1
            return out
    else:
        return mystery_input.copy()

def add_dice(table, num, die_input, mod=0):
    '''a wrapper function to make table.add_dice quicker and easier. takes legal
    input for Die or WeightedDie and returns object. input can be int for Die,
    or list, tuple_list, dict for WeightedDie. mod is an int[1,1,1,2,3],
    {1:3, 2:1, 3:1} [(1,3), (2,1), (3,1)] all make a weighted die of size 3 and
    where one gets rolled 3 times as often as 2 or 3'''
    table.add_die(num, make_die(die_input, mod))

def remove_dice(table, num, die_input, mod=0):
    '''a wrapper function to make table.remove_dice quicker and easier. takes
    legal input for Die or WeightedDie and returns object. input can be int for
    Die, or list, tuple_list, dict for WeightedDie. mod is an int[1,1,1,2,3],
    {1:3, 2:1, 3:1} [(1,3), (2,1), (3,1)] all make a weighted die of size 3 and
    where one gets rolled 3 times as often as 2 or 3'''
    table.remove_die(num, make_die(die_input, mod))

