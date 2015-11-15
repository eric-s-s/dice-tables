#TODO
#10**30 should be very safe overflow cutoff
#getvalue changes to getting a tuple,a list of tuples in a range, or all the tuples

class DiceTable(object):
    '''This is a class for finding how many comdinations for any die roll using
    (number of dice)D(die size).  So it could tell you that on 3D6, you have
    25 different combinations that get you a "9" out of a total of 216 
    combinations - an 11.6 percent chance. Or it could tell you that you have
    a 2.3 percent chance of rolling a 350 on 100D6.'''
    
    OVERFLOW_CUTOFF = 10**100
    def __init__(self, dsize):
        self._totaldice = 0
        self._table = {0:1}
        self._dsize = dsize
        self._int_so_no_overflow = False
        
    
    
    def int_or_float(self, variable):
        '''OverflowError control.  These tables deal with VERY large numbers.
        Floats over 10**300 or so, become "inf". If you explicitly convert 
        certain numbers to intergers, Python can handle the huge-number math.
        Otherwise, you swim in OverflowErrors'''
        if self._int_so_no_overflow:
            return int(variable)
        else:
            return variable    
        

    def dice_size(self):
        return self._dsize
    def number_of_dice(self):
        '''Returns how many dice were used to generate the values in your table.'''
        return self._totaldice
    def total_combinations(self):
        '''Returns the total possible number of combinations from a dice table.'''
        return self._dsize**self._totaldice

    def roll_range_top(self):
        '''Returns the highest die roll in table.'''
        return self._dsize*self._totaldice
    def roll_range_bottom(self):
        '''Returns the lowest die roll in table.'''
        return self._totaldice
    def roll_range(self):
        '''Returns a tuple of the range_bottom and range_top.'''
        return (self.roll_range_bottom(), self.roll_range_top())

    def roll_frequency(self, roll):
        '''Returns tuple of the roll and it's frequency.'''
        return (roll, self._table.get(roll))
    def roll_frequency_range(self, start, stopbefore):
        '''Returns a list of tuples (roll,frequency).
        Like regular range function, it stops before endvalue.'''
        tuple_list = []
        for roll in range(start, stopbefore):
            tuple_list.append((roll, self._table.get(roll)))
        return tuple_list
    def roll_frequency_all(self):
        '''Returns a list of tuples IN ORDER for all rolls in table.'''
        start = self.roll_range_bottom()
        stop = self.roll_range_top()+1
        return self.roll_frequency_range(start, stop)
    def highest_frequency_roll(self):
        '''Returns a tuple of (one of) the roll with the highest frequency,
        and it's frequency'''
        roll = int(self.mean())
        return (roll, self._table[roll])


    def add_a_die(self):
        '''Takes your dicetable object, and calculates all the new combinations
        if you add a new die of the dsize of the object.'''
        #so for d3, this would take {0:1,1:2} and
        #update to {1:1,2:1,3:1}+{2:2,3:2,4:2}
        self._totaldice += 1
        newdic = {}
        for roll in self._table:
            currentval = self._table[roll]
            for die_value in range(1, self._dsize+1):

                newdic[roll+die_value] = \
                (newdic.get(roll+die_value, 0)+currentval)
        self._table = newdic
    def add_many_dice(self, num_dice):
        for x in range(num_dice):
            self.add_a_die()


    def __str__(self):
        return str(self._totaldice)+'D'+str(self._dsize)


    def mean(self):
        '''i mean, don't you just sometimes look at a table of values
        and wonder what the mean is?'''
        return self._totaldice*(1+self._dsize)/2.0 
    def stddev(self):
        '''wassamatter you! you don't know what standard deviation is?'''
        
        #Checks to see if _int_so_no_overflow has tripped.
        #If it hasn't, checks to see if it should trip.
        if (not self._int_so_no_overflow and
                self.total_combinations() > self.OVERFLOW_CUTOFF):
            self._int_so_no_overflow = True
        
        #TODO: remove 2 lines of testing code.  still useful.    
        if self._int_so_no_overflow:
            print 'trip'    
        #TODO ends.
            
        avg = self.mean()
        sqs = 0
        count = 0
        for roll in self._table.keys():
            sqs += self._table[roll]*self.int_or_float(((avg - roll)**2))
            count += self._table[roll]
        return round((sqs/count)**0.5, 4)     
        
    #TODO: remove the next two functions.  they are for testing                
    def stddevtst(self):
        avg = self.mean()
        sqs = 0
        count = 0
        for roll in self._table.keys():
            sqs += self._table[roll]*(((avg - roll)**2))
            count += self._table[roll]
        return round((sqs/count)**0.5, 4)
    def stddeverr(self):
        accurate = self.stddevtst()
        approx = self.stddev()
        return 100*(accurate - approx)/accurate        
    #TODO ends.
     
    
    
class WeightedDiceTable(DiceTable):
    def __init__(self,lst):
        DiceTable.__init__(self,len(lst))
       
        
        #TODO: take these two functions, and make one function that makes a 
        #list of tuples that are floats.  the inter will int them later.
        def _transform_weights(lst):
            #transforms user's lst to a uniform weight table
            total = len(lst)
            lst_total = sum(lst)
            factor = float(total)/lst_total
            newlst = []
            print factor
            for el in lst:
                newlst.append(factor*el)
            return newlst    
        def _overflow_weights(weights):
            #converts transform to to tuples representing
            #one int over another int for overflow problems
            def _fractioner(x):
                for divisor in range(1,1001):
                    if x*divisor == int(x*divisor):
                        return int(x*divisor),divisor
                return int(round(1000*x)),1000 
            tuple_lst = []
            for el in weights:
                tuple_lst.append(_fractioner(el))
            return tuple_lst
        self.weights = _transform_weights(lst) 
        self.overflow_weights = _overflow_weights(self.weights)
        
        
    def addADie(self):
        '''takes your dicetable object, and calculates all the new combinations
        if you add a new die of the dsize of the object and applies weight table'''
        #so for d3, this would take {0:1,1:2} and 
        #update to {1:1,2:1,3:1}+{2:2,3:2,4:2}
        self.totaldice+=1
        newdic = {}
        for el in self.table:
            currentval = self.table[el]
            overflow_cutoff = 1000000000000000000
            for x in range(self.dsize):
                weight_factor = self.weights[x]
                if newdic.get(el+x+1,0)> overflow_cutoff or currentval>overflow_cutoff :
                    
                    weight_top = self.overflow_weights[x][0]
                    weight_bottom = self.overflow_weights[x][1]
                    newdic[el+x+1] = (int(newdic.get(el+x+1,0))+weight_top*int(currentval)/weight_bottom)
                else:
                    newdic[el+x+1] = (newdic.get(el+x+1,0)+weight_factor*currentval)
                    
        self.table= newdic
    def mean(self):
        
        try:
            mean = 0
            for el in self.table.keys():
                mean += el*self.table[el]
        
            mean = mean/self.totalcombos()
        except OverflowError:
            mean = 0
            for el in self.table.keys():
                mean += el*int(self.table[el])
            top = mean
            bottom = self.totalcombos()
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
        

    


            
