

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
            avg = (self.totaldice*(1+self.dsize)/2.0)
            sqs = 0
            count = 0
            for x in self.table.keys():
                sqs += self.table[x]*((avg - x)**2)
                count += self.table[x]
            return round((sqs/count)**0.5,4)
        except OverflowError:
            print 'this standard deviation is a gross approximation '+\
            'as i had to int() all the sqrt, because the numbers are just too big'
            avg = (self.totaldice*(1+self.dsize)/2.0)
            sqs = 0
            count = 0
            for x in self.table.keys():
                sqs += self.table[x]*int((avg - x)**2)
                count += self.table[x]
            return round((sqs/count)**0.5,4)
        
    def grapher(self):
        '''returns a graph of self'''
        maxx = self.table[int(self.mean())]           
        divisor = 1
        divstring = '1'
        #this sets the divisor so that max height of graph is 80 x's
        if maxx > 80 and maxx<=80000000:
            divisor = maxx/80.0
            divstring = str(divisor)
        if maxx > 80000000:
            #this code just outputs as a string with sci notation assuming no decimals
            divisor = maxx/80
            divstring = str(divisor)
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
        maxx = self.table[int(self.mean())]           
        divisor = 1
        divstring = '1'
        
        if maxx > 80 and maxx<=80000000:
            divisor = maxx/80.0
            divstring = str(divisor)
        if maxx > 80000000:
            #this code just outputs as a string with sci notation assuming no decimals
            divisor = maxx/80
            divstring = str(divisor)
            power = len(divstring)-1
            digits = divstring[0]+'.'+divstring[1:4]
            divstring =digits+'e+'+str(power)
        
        count = 0        
        for x in range (self.min() , self.max()+1):
            val = self.table.get(x,0)
            
            multiplier = int(round(val/divisor))
            if multiplier == 0:
                count+=1
            else:
                if x<10:
                    print ' '+str(x)+': '+multiplier*'x'
                else:
                    print str(x)+': '+multiplier*'x'
        if count !=0:
            outrange = count/2-1
            start = self.totaldice
            finish = self.totaldice*self.dsize
            outbottom = str(start)+' - '+str(start+outrange)
            outtop = str(finish-outrange)+' - '+str(finish)
        print 'each x represents '+(divstring)+' occurences' 
        if count != 0:
            print 'not included: '+outbottom+' and '+outtop
        print self
    
    
            
            
def scinote(num):
    '''returns str of a rounded INT in sci notation. 
    if you int(the string) it's legal input for python'''
    string = str(num)
    power = str(len(string)-1)
    digits = string[0]+'.'+string[1:4]
    return digits+'e+'+power


def makealist():
    '''take user input of a range of numbers
    and outputs (list of numbers,input string)
    a helper function for getstat'''
    x = raw_input('enter number(s) you want stats of separated by commas or you can use a dash \nfor a range of numbers: ')
    if x == 'q' or x == '':
        return None,None
    out = []
    try:
        for el in x.split(','):
            if '-' in el:
                start = int(el.split('-')[0])
                end = int(el.split('-')[1])
                if start <= end:
                    for num in range(start,end+1):
                        out.append(num)
                else:
                    for num in range(end,start+1):
                        out.append(num)   
            else:
                out.append(int(el))
        
    except ValueError:
        print
        print 'ooops.  looks like someone can\'t follow directions.'
        print 'your prize is a list that includes 0 and some of your elements.'
        print 'here ya go.'
        print
        out.append(0)
    return out,x


#i need to modify the overflowerror, maybe use a function like scinote. 
#right now, since overflowerror just uses int the chance will say 1 in 2 when pct is 34-50
def getstat(dtable):
        '''returns the stats on lst of elements in self'''
        totalval = 0
        tabletotal = dtable.dsize**dtable.totaldice
        #below takes the values from makealist to get lst for function and 
        # str to print the range of values
        lst,lststring = makealist()
        if lst == None:
            return None
        
        for el in lst:
            totalval += dtable.table.get(el,0)
        if totalval == 0:
            print 'you get nothing!  good day, sir!'
            return 0
        
        
        else:
            
            try:
                chance = round(float(tabletotal)/totalval,3)
            except OverflowError:
                #!!personal reminder!!
                #this needs revision.  33-50pct are all 1 in 2 chance for very large numbers
                #all because of this line of code perhaps use funtion like scinote
                #pass a short float and power of ten.  can use in next line for better pct, too
                #end !!personal reminder!!
                chance = (tabletotal)/totalval
            
            try:
                pct = round(float(totalval)*100/tabletotal,3)
            except OverflowError:
                pct = (totalval)*100/tabletotal
            
            #the if elses establish output str based on size of numbers
            #either just display the num, or display it in scientific notation if too big
            if totalval>1000000:
                totalvalstring =scinote(totalval)
            else:
                totalvalstring = str(totalval)
            
            if tabletotal>1000000:
                tabletotalstring =scinote(tabletotal)
            else:
                tabletotalstring =str(tabletotal)
            
            if chance > 1000000:
                chancestring =scinote(int(chance))
            else:
                chancestring = str(chance)
            
            print
            print lststring+' occurred '+totalvalstring+\
            ' times out of a total of '+tabletotalstring+' possible combinations'
            print 'if you roll '+str(dtable)+','
            print 'the chance of '+lststring+' is 1 in '+chancestring+' or '\
            +str(pct)+' percent'
            print
            return 0

#two functions for generating a dicetable of specific size
def mycombos(dval,dice):
    '''generates a dice table of specs, die size, dval(int) and #of dice(int)'''
    x = dicetable(dval)
    for a in range(dice):
        x.addADie()
    return x                    
                                                            
def mycombosDisplay(dval,dice):
    '''generates a dice table of specs, die size, dval(int) and #of dice(int)
    also prints info on table'''
    x = dicetable(dval)
    for a in range(dice):
        x.addADie()
    x.truncategrapher()
    print 'the mean is '+str(x.mean())
    print 'the standard deviation is '+str(x.stddev())
    return x
    
     
#here's a generator and UI that uses it is below -  diceTableYielder()
def genTableStep(dval):
    '''user input adds dice to a generator like mycombos  
    dval is the kind of dice  
    the yield none is used by the parent function(diceTableYielder) to quit'''
    x = dicetable(dval)
    
    while True:
        print 'you currently have ' +str(x)
	step = raw_input('how many dice would you like to add? (\'q\' to quit) ')
	if step == 'q':
	    yield None
	else:
	    try:
	        for count in range(int(step)):
	           x.addADie()
                yield x
            except ValueError:
                print 'incorrect input'
                continue
        

def diceTableYielder():    
    
    x = int(raw_input('what kind of dice? '))
    
        
    for el in genTableStep(x):
        if el == None:
            break
        choice = raw_input('type "t" for a table, "g" for a graph or the anykey to skip ')
        if choice == 't':
            el.printTable()
        if choice == 'g':
            el.truncategrapher()
        
        while True:
            
            
            statyn = raw_input\
            ('would you like stats on your table? \'y\' or \'n\' ')
            if statyn == 'y':
                print
                print el
                print 'the mean is '+str(el.mean())
                print 'the standard deviation is '+str(el.stddev())
                print 'the range is '+str(el.min())+'-'+str(el.max())
                print
                x = getstat(el)
                if x == None:
                    break
            if statyn == 'n':
                break
            else:
                continue



diceTableYielder()