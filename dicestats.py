'''for all things dicey.  this contains DiceInfo and DiceTable and add_dice.'''
from longintmath import LongIntTable


class Die(object):
    '''makes instance of a die.  it has a size and a weight of 0 (for comparing
    with weighted dice which have non-zero weight'''
    def __init__(self, die_size):
        '''die size is a positive int. creates a die containing 1 - die_size
        values'''
        self._die_size = die_size
        self._weight = 0
    def get_size(self):
        '''returns the size of the die'''
        return self._die_size
    def get_weight(self):
        '''returns the weight of the die'''
        return self._weight
    def get_copy(self):
        '''returns a copy of the die object'''
        return Die(self._die_size)
    def tuple_list(self):
        '''returns the tuple list that is the dice values'''
        return [(value, 1) for value in range(1, self._die_size + 1)]
    def weight_info(self):
        '''returns detailed weight info'''
        return '%s\n    No weights' % (self)
    def __lt__(self, other):
        '''dice are compared by size and then weight.'''
        return (self.get_size() < other.get_size() or
                self.get_size() == other.get_size() and 0 < other.get_weight())

    def __eq__(self, other):
        '''two DiceInfo are equal if their tuple lists match'''
        if not isinstance(other, Die):
            return False
        else:
            return self.get_size() == other.get_size()

    def __str__(self):
        return 'D%s' % (self._die_size)


class WeightedDie(object):
    '''stores and returns info for a weighted die.'''
    def __init__(self, dictionary_input):
        '''dictionary input is a dictionary of int, value:weight {1:3, 2:1, 3:1}
        create a D3 that rolls a one 3 times more than a two or a three.'''
        self._dic = dictionary_input
        self._die_size = max(self._dic.keys())
        self._weight = sum(self._dic.values())

    def get_size(self):
        '''returns the size of the die'''
        return self._die_size
    def get_weight(self):
        '''returns the weight of the die'''
        return self._weight
    def get_copy(self):
        '''returns a copy of the die'''
        new_dic = self._dic.copy()
        return WeightedDie(new_dic)
    def tuple_list(self):
        '''returns the tuple list that is the dice values'''
        out = []
        for value, weight in self._dic.items():
            if weight != 0:
                out.append((value, weight))
        out.sort()
        return out
    def weight_info(self):
        '''returns detailed weight info'''
        out = str(self)
        for roll in range(1, self._die_size + 1):
            out = (out +'\n    a roll of %s has a weight of %s' %
                   (roll, self._dic.get(roll, 0)))
        return out

    def __lt__(self, other):
        '''dice info's are compared by size of dice, and then weight'''
        return (self.get_size() < other.get_size() or self.get_size() ==
                other.get_size() and self.get_weight() < other.get_weight())

    def __eq__(self, other):
        '''two Dice are equal if their dictionary of values are a match'''
        if not isinstance(other, WeightedDie):
            return False
        else:
            return self.tuple_list() == other.tuple_list()
    def __str__(self):
        return 'D%s  W:%s' % (self._die_size, self._weight)


class DiceTable(LongIntTable):
    '''this is a LongIntTable with a list that holds information about the dice
    added to it and removed from it.'''
    def __init__(self):
        LongIntTable.__init__(self, {0:1})
        self._dice_list = []
        self._last_die = None

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
        if not in_list:
            new_list.append((new_die, add_number))
        new_list.sort()
        self._dice_list = new_list
        self._last_die = new_die

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

    def get_last(self):
        '''return tuple list of the last die added'''
        if self._last_die is None:
            return None
        else:
            return self._last_die.get_copy()
    def last_info(self, weight_info=False):
        '''returns str of either last die or it's weight info'''
        if weight_info:
            return self._last_die.weight_info()
        else:
            return str(self._last_die)

    def weights_info(self):
        '''return detailed info of dice in the list'''
        out_str = ''
        for die, number in self._dice_list:
            out_str = out_str + '%s%s\n\n' % (number, die.weight_info())
        return out_str.rstrip('\n')

    def __str__(self):
        out_str = ''
        for die, number in self._dice_list:
            out_str = out_str + '%s%s\n' % (number, die)
        return out_str.rstrip('\n')

    def add_die(self, num, die):
        '''adds the die to the table num times and updates the table, list.  die
        is a  Die or WeightedDie and num is a positive int.'''
        self.add(num, die.tuple_list())
        self.update_list(num, die)

    def remove_die(self, num, die):
        '''die is a  Die or WeightedDie and num is a positive int.first makes
        sure the dice to be removed are in the list. then removes those dice
        from the list and the table.'''
        if self.number_of_dice(die) - num < 0:
            raise ValueError('dice not in table, or removed too many dice')
        else:
            self.remove(num, die.tuple_list())
            self.update_list(-num, die)

#some wrapper functions for ease of use
def make_die(table, die_input):
    '''takes legal input for Die or WeightedDie and returns object. input can
    be int for Die, or list, tuple_list, dict for WeightedDie. [1,1,1,2,3],
    {1:3, 2:1, 3:1} [(1,3), (2,1), (3,1)] all make a weighted die of size 3 and
    where one gets rolled 3 times as often as 2 or 3'''
    if die_input == 'last':
        if table.get_last() == None:
            raise ValueError('no last die')
        return table.get_last()
    elif isinstance(die_input, int):
        return Die(die_input)
    else:
        return WeightedDie(dictionary_maker(die_input))

#helper to make_die
def dictionary_maker(mystery_input):
    '''mystery input can be a list, a list of tuples or a dictionary. returns the
    dictionary of the input'''
    if isinstance(mystery_input, list):
        if isinstance(mystery_input[0], tuple):
            return dict(pair for pair in mystery_input)
        else:
            out = {}
            for value in mystery_input:
                out[value] = out.get(value, 0) + 1
            return out
    else:
        return dict((pair) for pair in mystery_input.items())

def add_dice(table, num=1, die_input='last'):
    '''a wrapper function to make table.add_dice quicker and easier. takes legal
    input for Die or WeightedDie and returns object. input can be int for Die,
    or list, tuple_list, dict for WeightedDie. [1,1,1,2,3], {1:3, 2:1, 3:1}
    [(1,3), (2,1), (3,1)] all make a weighted die of size 3 and
    where one gets rolled 3 times as often as 2 or 3'''
    table.add_die(num, make_die(table, die_input))

def remove_dice(table, num=1, die_input='last'):
    '''a wrapper function to make table.remove_dice quicker and easier. takes
    legal input for Die or WeightedDie and returns object. input can be int for
    Die, or list, tuple_list, dict for WeightedDie. [1,1,1,2,3], {1:3, 2:1, 3:1}
    [(1,3), (2,1), (3,1)] all make a weighted die of size 3 and
    where one gets rolled 3 times as often as 2 or 3'''
    table.remove_die(num, make_die(table, die_input))

