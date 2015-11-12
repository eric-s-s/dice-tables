class dicetable(object):
    def __init__(self,dsize):
        self.totaldice = 0
        self.table = {0:1}
        self.dsize = dsize
        

    def getTableVal(self,value):
        return self.table.get(value,0)
    def getTable(self):
        return self.table
    def getDsize(self):
        return self.dsize
    def getTotalDice(self):
        '''returns how many dice were used to generate the values in your table'''
        return self.totaldice
    def max(self):
        '''returns the highest die roll in table'''
        return self.dsize*self.totaldice
    def min(self):
        '''returns the lowest die roll in table'''
        return self.totaldice
    def totalcombos(self):
        '''returns the total possible number of combinations from a dice table'''
        return self.dsize**self.totaldice
    def highest_frequency(self):
        '''returns die roll that has the number of rolls (arbitrarily picks one of two equal ones)'''
        return int(self.mean())
    
    def addADie(self):
        '''takes your dicetable object, and calculates all the new combinations
        if you add a new die of the dsize of the object'''
        #so for d3, this would take {0:1,1:2} and 
        #update to {1:1,2:1,3:1}+{2:2,3:2,4:2}
        self.totaldice+=1
        newdic = {}
        for el in self.table:
            currentval = self.table[el]
            for x in range(self.dsize):
                
                newdic[el+x+1] = (newdic.get(el+x+1,0)+currentval)
        self.table= newdic
    def generator(self,num_dice):
        for x in range (num_dice):
            self.addADie()
        #return self
        
         
          
            
    def __str__(self):
        return str(self.totaldice)+'D'+str(self.dsize)    
    def printTable(self):
        '''go on. give it a try.  you'll never guess what this function does.
        it's a surprise'''
        for el in range(self.min(), self.max()+1):
            if el<10:
                print ' '+str(el)+':'+str(self.table[el])
            else:
                print(str(el)+':'+str(self.table[el]))  
                
    def mean(self):
        '''i mean, don't you just sometimes look at a table of values
        and wonder what the mean is?'''
        return (self.totaldice*(1+self.dsize)/2.0) 
    def stddev(self):
        '''wassamatter you! you don't know what standard deviation is?'''
        try:
            avg = self.mean()
            sqs = 0
            count = 0
            for x in self.table.keys():
                sqs += self.table[x]*((avg - x)**2)
                count += self.table[x]
            return round((sqs/count)**0.5,4)
        except OverflowError:
            print 'this standard deviation is a gross approximation '+\
            'as i had to int() all the sqrt, because the numbers are just too big'
            avg = self.mean()
            sqs = 0
            count = 0
            for x in self.table.keys():
                sqs += self.table[x]*int((avg - x)**2)
                count += self.table[x]
            return round((sqs/count)**0.5,4)
        
    def grapher(self):
        '''returns a graph of self'''
        max_roll_size = self.getTableVal(self.highest_frequency())
        max_graph_height = 80.0
                  
        divisor = 1
        divstring = '1'
        #this sets the divisor so that max height of graph is 80 x's
        if max_roll_size > max_graph_height:
            try:
                divisor = max_roll_size/max_graph_height
            except OverflowError:
                divisor = max_roll_size/int(max_graph_height)
            divstring = str(divisor)
        
        sci_note_cutoff = 1000000
        if divisor > sci_note_cutoff and 'e' not in divstring:
            #this code just outputs as a string with sci notation assuming no decimals
            power = len(divstring)-1
            digits = divstring[0]+'.'+divstring[1:4]
            divstring =digits+'e+'+str(power)
        
                
        for x in range (self.min() , self.max()+1):
            val = self.table.get(x,0)
            if x<10:
                print ' '+str(x)+': '+(int(round(val/divisor)))*'x'
            else:
                print str(x)+': '+(int(round(val/divisor)))*'x'
        print 'each x represents '+(divstring)+' occurences'      
        print self

    def truncategrapher(self):
        '''prints a graph of self with  the 0-'x' bits removed'''
        max_roll_size = self.getTableVal(self.highest_frequency())
        max_graph_height = 80.0
                  
        divisor = 1
        divstring = '1'
        #this sets the divisor so that max height of graph is 80 x's
        if max_roll_size > max_graph_height:
            try:
                divisor = max_roll_size/max_graph_height
            except OverflowError:
                divisor = max_roll_size/int(max_graph_height)
            divstring = str(divisor)
        
        sci_note_cutoff = 1000000
        if divisor > sci_note_cutoff and 'e' not in divstring:
            #the second arg above is to make sure divstring isn't already sci-note(python implements for floats above 10^16 and doesn't implement for ints. i want to implement for float above 10^6)
            #this code just outputs as a string with sci notation assuming no decimals
            print 'scinote info . divstring is '+divstring+' max roll size is '+str(max_roll_size)
            power = len(divstring)-1
            digits = divstring[0]+'.'+divstring[1:4]
            divstring =digits+'e+'+str(power)
        
        out_lst = []        
        for x in range (self.min() , self.max()+1):
            val = self.table.get(x,0)
            
            multiplier = int(round(val/divisor))
            if multiplier == 0:
                out_lst.append(x)
            else:
                if x<10:
                    print ' '+str(x)+': '+multiplier*'x'
                else:
                    print str(x)+': '+multiplier*'x'
        if out_lst !=[]:
            
            for index in range(len(out_lst)-1):
                if out_lst[index+1]-out_lst[index]>1:
                    bottom_bottom = (out_lst[0])
                    bottom_top =(out_lst[index])
                    top_bottom = (out_lst[index+1])
                    top_top = (out_lst[-1])
                    break

            outbottom = str(bottom_bottom)+' - '+str(bottom_top)
            outtop = str(top_bottom)+' - '+str(top_top)
        print 'each x represents '+(divstring)+' occurences' 
        if out_lst !=[]:
            print 'not included: '+outbottom+' and '+outtop
        print self
    





class MultipleDiceTable(dicetable):
    
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
        

    
class WeightedDiceTable(dicetable):
    def __init__(self,lst):
        dicetable.__init__(self,len(lst))
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
            for x in range(self.dsize):
                weight_factor = self.weights[x]
                
                newdic[el+x+1] = (newdic.get(el+x+1,0)+weight_factor*currentval)
        self.table= newdic
    def mean(self):
        mean = 0
        for el in self.table.keys():
            mean += el*self.table[el]
        mean = mean/self.totalcombos()
        return mean

            
'''rewrite for truncate grapher uses this
for el in range(len(x)-1):
    if x[el+1]-x[el]>1:
        y.append(x[0])
        y.append(x[el])
        z.append(x[el+1])
        z.append(x[-1])
'''            