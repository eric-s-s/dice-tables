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
        
        self.table = {0:1}
        self.dsize_table = {} 
        
    
    def getDsize(self):
        return self.dsize_table
    def getTotalDice(self):
        '''returns how many dice were used to generate the values in your table'''
        total_dice = 0
        for dice_num in self.dsize_table.values():
            total_dice += dice_num
        return total_dice
    def max(self):
        '''returns the highest die roll in table'''
        out = 0
        for dsize in self.dsize_table.keys():
            out += dsize*self.dsize_table[dsize]
        return out
    def min(self):
        '''returns the lowest die roll in table'''
        total_dice = 0
        for dice_num in self.dsize_table.values():
            total_dice += dice_num
        return total_dice
    def totalcombos(self):
        '''returns the total possible number of combinations from a dice table'''
        out = 1
        for dsize in self.dsize_table.keys():
            #if dsize !=0 and self.dsize_table[dsize] !=0:
            out *= dsize**self.dsize_table[dsize]
        return out
    def highest_frequency(self):
        '''returns die roll that has the number of rolls (arbitrarily picks one of two equal ones)'''
        hf_index = 0
        hf_value = 0        
        for roll_value in self.table:
            if self.table[roll_value]>hf_value:
                hf_value = self.table[roll_value]
                hf_index = roll_value
        return hf_index
            
    
    def addADie(self,dsize):
        '''takes your dicetable object, and calculates all the new combinations
        if you add a new die of the dsize of the object'''
        #so for d3, this would take {0:1,1:2} and 
        #update to {1:1,2:1,3:1}+{2:2,3:2,4:2}
        self.dsize_table[dsize] = self.dsize_table.get(dsize,0) + 1
        newdic = {}
        for el in self.table:
            currentval = self.table[el]
            for x in range(dsize):
                
                newdic[el+x+1] = (newdic.get(el+x+1,0)+currentval)
        self.table= newdic
     
    def __str__(self):
        out = ''
        for dsize in self.dsize_table:
            out = out+str(self.dsize_table[dsize])+'D'+str(dsize)+'\n'
        return out    
      
    def generator(self,num_dice,dsize):
        for x in range (num_dice):
            self.addADie(dsize)            
    
    def mean(self):
        '''i mean, don't you just sometimes look at a table of values
        and wonder what the mean is?'''
        mean = 0
        for dsize in self.dsize_table:
            mean += self.dsize_table[dsize]*(dsize+1)/2.0 
        return mean