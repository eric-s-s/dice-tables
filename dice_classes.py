from longinttable import LongIntTable
class BasicDiceTable(object):
    '''docstring'''
    LongIntTable_imports = ['values', 'values_min', 'values_max', 'values_range',
                            'frequency', 'frequency_range', 'frequency_all',
                            'frequency_highest', 'total_frequency', 
                            'divide', 'mean', 'stddev', 'check_overflow']
    
    def __init__(self, dsize):
        self._dsize = dsize
        self._table = LongIntTable({0:1})
    def __getattr__(self, attr):
        if attr in self.LongIntTable_imports:
            return getattr(self._table, attr)
    def __str__(self):
        return str(self.min_roll())+'D'+str(self._dsize)
    def add_a_die(self):
        self._table.add_a_die(range(1,self._dsize+1))
    def add_dice(self, num_dice):
        for _ in range(num_dice):
            self.add_a_die()
    def min_roll(self):
        return self.values_min()
    def max_roll(self):
        return self.values_max()
    


#class MultipleDiceTable(object):
    
#class WeightedDiceTable(object):