from dice_class import *

        
    
class WeightedDiceTable(DiceTable):
    def __init__(self,lst):
        DiceTable.__init__(self,len(lst))
        
        def _tranform_weights(lst):
            converted = []
            conversion_numerator = float(len(lst))
            conversion_denominator = sum(lst)
            for value in lst:
                converted.append(value*conversion_numerator/
                                conversion_denominator)
            def fractioner_maker(weight):
                final_denominator =1000
                for denominator in range(1,final_denominator):
                    numerator = weight*denominator
                    if numerator == int(numerator):
                        return int(numerator),float(denominator)
                final_numerator = int(round(final_denominator*weight))
                return (final_numerator, float(final_denominator))
            weights_out = []
            for value in converted:
                weights_out.append(fractioner_maker(value))
            return weights_out           
        self._weights = _tranform_weights(lst)
        
        
    def add_a_die(self):
        '''takes your dicetable object, and calculates all the new combinations
        if you add a new die of the dsize of the object and applies weight table'''
        #so for d3, this would take {0:1,1:2} and 
        #update to {1:1,2:1,3:1}+{2:2,3:2,4:2}
        self._totaldice+=1
        newdic = {}
        for el in self._table:
            currentval = self._table[el]
            overflow_cutoff = 1000000000000000000
            for x in range(self._dsize):
                weight_factor = self.weights[x]
                if newdic.get(el+x+1,0)> overflow_cutoff or currentval>overflow_cutoff :
                    
                    weight_top = self.overflow_weights[x][0]
                    weight_bottom = self.overflow_weights[x][1]
                    newdic[el+x+1] = (int(newdic.get(el+x+1,0))+weight_top*int(currentval)/weight_bottom)
                else:
                    newdic[el+x+1] = (newdic.get(el+x+1,0)+weight_factor*currentval)
                    
        self._table= newdic
    def mean(self):
        
        try:
            mean = 0
            for el in self._table.keys():
                mean += el*self._table[el]
        
            mean = mean/self.total_combinations()
        except OverflowError:
            mean = 0
            for el in self._table.keys():
                mean += el*int(self._table[el])
            top = mean
            bottom = self.total_combinations()
            remainder = top%bottom
            if remainder*10000<bottom:
                mean = top/bottom
                print 'remainder '+str(remainder)
            else:
                mean = top/bottom
                print 'implement here '+str(remainder)
        return mean




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