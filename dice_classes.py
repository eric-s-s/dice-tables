from longinttable import LongIntTable



class BasicDiceTable(object):
    '''docstring'''
    
    
    def __init__(self, dsize):
        self._dsize = dsize
        self._table = LongIntTable({0:1})
    def __getattr__(self, attr):
        attr = attr.replace('rolls', 'values')
        if attr in LongIntTable_imports:
            return getattr(self._table, attr)
    def __str__(self):
        return str(self.rolls_min())+'D'+str(self._dsize)
    def add_a_die(self):
        self._table.add_a_die(range(1,self._dsize+1))
    def add_dice(self, num_dice):
        for _ in range(num_dice):
            self.add_a_die()
    '''def min_roll(self):
        return self.values_min()
    def max_roll(self):
        return self.values_max()
    '''


class MultipleDiceTable(object):
    '''docstring'''
    
    
    def __init__(self):
        self._dsize_table = {}
        self._table = LongIntTable({0:1})
    def __getattr__(self, attr):
        attr = attr.replace('rolls', 'values')
        if attr in LongIntTable_imports:
            return getattr(self._table, attr)
    def __str__(self):
        answer = ''
        for dsize, number in self._dsize_table.items():
            answer = answer + str(number) + 'D' + str(dsize) + '\n'
        return answer.rstrip('\n')

    def add_a_die(self, dsize):
        self._dsize_table[dsize] = self._dsize_table.get(dsize, 0) + 1
        self._table.add_a_die(range(1,dsize+1))
    def add_dice(self, num_dice, dsize):
        for _ in range(num_dice):
            self.add_a_die(dsize)
    
class WeightedDiceTable(object):
    '''docstring'''
    
    
    def __init__(self, dsize):
        self._dsize = dsize
        self._table = LongIntTable({0:1})
    def __getattr__(self, attr):
        attr = attr.replace('rolls', 'values')
        if attr in LongIntTable_imports:
            return getattr(self._table, attr)
    def __str__(self):
        return str(self.rolls_min())+'D'+str(self._dsize)
    def add_a_die(self):
        self._table.add_a_die(range(1,self._dsize+1))
    def add_dice(self, num_dice):
        for _ in range(num_dice):
            self.add_a_die()