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
        return self.tuple_list() == other.tuple_list()

    def __str__(self):
        return 'D%s' % (self._die_size)


class WeightedDie(object):
    '''stores and returns info for a weighted die.'''
    def __init__(self, die_input):
        '''die_input can be a list of values, or a dictionary or a list
        of tuples.  weights - positive intergers and 0.  die values are
        positive ints. [1,1,1,2,3], {1:3, 2:1, 3:1} and [(1,3), (2,1), (3,1)] all
        create a D3 that rolls a one 3 times more than a two or a three.'''
        #helper for init function
        def _make_dic(an_input):
            '''turns any appropriate die representation into a dictionary'''
            if isinstance(an_input, dict):
                return an_input
            elif isinstance(an_input, list) and isinstance(an_input[0], int):
                dic = {}
                for val in an_input:
                    dic[val] = dic.get(val, 0) + 1
                return dic
            elif isinstance(an_input, list) and isinstance(an_input[0], tuple):
                return dict((pair) for pair in an_input)
        self._dic = _make_dic(die_input)
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
        '''returns detailed weight info'''
        out = str(self)
        for roll in range(1, self._die_size + 1):
            out = (out +'\n    a roll of %s has a weight of %s' %
                   (roll, self._dic.get(roll, 0)))
        return out

    def __lt__(self, other):
        '''dice info's are compared by size of dice, not number of dice'''
        return (self.get_size() < other.get_size() or self.get_size() ==
                other.get_size() and self.get_weight < other.get_weight())

    def __eq__(self, other):
        '''two DiceInfo are equal if their dictionary of values are a match'''
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

    def last_tuple(self):
        '''return tuple list of the last die added'''
        return self._last_die.tuple_list()
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

    def add_dice(self, num=1, die='last'):
        '''adds dice to the table and updates the table, list.  die is a  Die or
        WeightedDie and num is a positive int.'''
        if die == 'last':
            to_add = self._last_die
        else:
            to_add = die
        self.add(num, to_add.tuple_list())
        self.update_list(num, to_add)

    def remove_dice(self, num=1, die='last'):
        '''die is a  Die or WeightedDie and num is a positive int.first makes
        sure the dice to be removed are in the list. then removes those dice
        from the list and the table.'''
        if die == 'last':
            to_rm = self._last_die
        else:
            to_rm = die
        if self.number_of_dice(to_rm) - num < 0:
            raise ValueError('dice not in table, or removed too many dice')
        else:
            self.remove(num, to_rm.tuple_list())
            self.update_list(-num, to_rm)


def make_die(die_input):
    '''takes legal input for Die or WeightedDie and returns object. input can
    be int for Die, or list, tuple_list, dict for WeightedDie. [1,1,1,2,3],
    {1:3, 2:1, 3:1} [(1,3), (2,1), (3,1)] all make a weighted die of size 3 and
    where one gets rolled 3 times as often as 2 or 3'''
    if isinstance(die_input, int):
        return Die(die_input)
    else:
        return WeightedDie(die_input)

def add_wrapper(table, num=1, die_input='last'):
    '''a wrapper function to make table.add_dice quicker and easier. takes legal
    input for Die or WeightedDie and returns object. input can be int for Die,
    or list, tuple_list, dict for WeightedDie. [1,1,1,2,3], {1:3, 2:1, 3:1}
    [(1,3), (2,1), (3,1)] all make a weighted die of size 3 and
    where one gets rolled 3 times as often as 2 or 3'''
    table.add_dice(num, make_die(die_input))

def remove_wrapper(table, num=1, die_input='last'):
    '''a wrapper function to make table.remove_dice quicker and easier. takes
    legal input for Die or WeightedDie and returns object. input can be int for
    Die, or list, tuple_list, dict for WeightedDie. [1,1,1,2,3], {1:3, 2:1, 3:1}
    [(1,3), (2,1), (3,1)] all make a weighted die of size 3 and
    where one gets rolled 3 times as often as 2 or 3'''
    table.remove_dice(num, make_die(die_input))

