from dice_class import DiceTable
           
            

class WeightedDiceTable(DiceTable):
    def __init__(self, lst):
        DiceTable.__init__(self, len(lst))
        
        def _int_the_weights(in_lst):
            '''takes list of weights and makes them ints.
            outputs tuples of weight and die value.'''
            factor = 1
            out_lst = []
            for value in in_lst:
                if not isinstance(value, int):
                    found_one = False
                    for guess in range(factor,1000, factor):
                        if value*guess == int(value*guess):
                            factor = guess
                            found_one = True
                            break
                    if found_one == False:
                        factor = 1000
                        break
            for index in range(len(in_lst)):
                out_lst.append((index+1, int(factor*in_lst[index])))
            return out_lst
        self._weights = _int_the_weights(lst)
        self._total_weight = sum([pair[1] for pair in self._weights])
        
    def weight_info(self):
        print self
        for die_val, weight in self._weights:
            print 'a roll of '+str(die_val)+' has a weight '+str(weight)
        print 'the total weight is '+str(self._total_weight)
        
    def add_a_die(self):
        '''Takes your dicetable object, and calculates all the new combinations
        if you add a new die of the dsize of the object.'''
        #so for d3, this would take {0:1,1:2} and
        #update to {1:1,2:1,3:1}+{2:2,3:2,4:2}
        if (not self._int_so_no_overflow and
                self.total_combinations() > self.OVERFLOW_CUTOFF):
            self._int_so_no_overflow = True
        self._totaldice += 1
        newdic = {}
        #for roll in self._table:
        #    currentval = self._table[roll]
        for roll, current_frequency in self._table.items():
            for die_value, weight in self._weights:

                newdic[roll+die_value] = \
                (newdic.get(roll+die_value, 0)+weight*current_frequency)
        self._table = newdic
    
    def total_combinations(self):
        '''Returns the total possible number of combinations from a dice table.'''
        return self._total_weight**self._totaldice
    def mean(self):
        numerator = 0
        denominator = self.total_combinations()
        for roll, frequency in self._table.items():
            numerator += roll*frequency
        return self.divide(numerator, denominator, 10)  
    def roll_frequency_highest(self):
        '''Returns a tuple of (one of) the roll with the highest frequency,
        and it's frequency'''
        highest = (0,0)
        for roll, frequency in self._table.items():
            if frequency > highest[1]:
                highest = (roll, frequency)
        return highest 
                                            
    def __str__(self):
        return str(self._totaldice)+'D'+str(self._dsize)+' weighted' 



class MultipleDiceTable(DiceTable):
    
    def __init__(self):
        DiceTable.__init__(self, {})
         
    def total_combinations(self):
        '''Returns the total possible number of combinations from a dice table.'''
        answer = 1
        for dsize, number_of_dice in self._dsize.items():
            if dsize*number_of_dice != 0:
                answer *= dsize**number_of_dice
        return answer    
    
    def roll_range_top(self):
        '''Returns the highest die roll in table.'''
        answer = 0
        for dsize, number_of_dice in self._dsize.items():
            answer += dsize*number_of_dice
        return answer
    
    def roll_range(self):
        '''Returns a tuple of the range_bottom and range_top.'''
        return (self.roll_range_bottom(), self.roll_range_top())
    
    def mean(self):
        answer = 0
        for dsize, number_of_dice in self._dsize.items():
            answer += (dsize + 1)*number_of_dice/2.0
        return answer
          
    def roll_frequency_highest(self):
        '''Returns a tuple of (one of) the roll with the highest frequency,
        and it's frequency'''
        highest = (0,0)
        for roll, frequency in self._table.items():
            if frequency > highest[1]:
                highest = (roll, frequency)
        return highest 
    
    def add_a_die(self, dsize):
        '''dsize is the kind of die you want to add.
        Takes your dicetable object, and calculates all the new combinations
        if you add a new die of the dsize of the object.'''
        #so for d3, this would take {0:1,1:2} and
        #update to {1:1,2:1,3:1}+{2:2,3:2,4:2}
        if (not self._int_so_no_overflow and
                self.total_combinations() > self.OVERFLOW_CUTOFF):
            self._int_so_no_overflow = True
        self._totaldice += 1
        self._dsize[dsize] = self._dsize.get(dsize, 0)+1
        newdic = {}
        for roll, current_frequency in self._table.items():
            for die_value in range(1, dsize+1):
                newdic[roll+die_value] = \
                (newdic.get(roll+die_value, 0)+current_frequency)
        self._table = newdic
    def add_many_dice(self, dsize, num_dice):
        '''dsize and num_dice are ints.  
        Add that num_dice dice of kind dsize.'''
        for x in range(num_dice):
            self.add_a_die(dsize)


    def __str__(self):
        answer = ''
        for dsize, number in self._dsize.items():
            answer = answer + str(number) + 'D' + str(dsize) + '\n'
        return answer.rstrip()

