from multiple_dice_class import *
import pylab

    
            
            
def scinote(num):
    '''returns str of a rounded INT in sci notation. 
    if you int(the string) it's legal input for python'''
    string = str(num)
    power = str(len(string)-1)
    digits = string[0]+'.'+string[1:4]
    return digits+'e+'+power
    
def printTable(self):
        '''go on. give it a try.  you'll never guess what this function does.
        it's a surprise'''
        for el in range(self.min(), self.max()+1):
            if el<10:
                print ' '+str(el)+':'+str(self.table[el])
            else:
                print(str(el)+':'+str(self.table[el]))
    
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
            #print 'scinote info . divstring is '+divstring+' max roll size is '+str(max_roll_size)
            power = len(divstring)-1
            digits = divstring[0]+'.'+divstring[1:4]
            divstring =digits+'e+'+str(power)
        
        out_lst = []        
        for x in range (self.min() , self.max()+1):
            val = self.table.get(x,0)
            try:
                multiplier = int(round(val/divisor))
            except OverflowError:
                multiplier =  int(val)/int(divisor)
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
        
def getstat(dtable):
        '''returns the stats on lst of elements in self'''
        
        tabletotal = dtable.totalcombos()
        #below takes the values from makealist to get lst for function and 
        # str to print the range of values
        lst,lststring = makealist()
        if lst == None:
            return None
        try:
            totalval = 0
            for el in lst:
                totalval += dtable.getTableVal(el)
        except OverflowError:
            totalval = 0
            for el in lst:
                totalval += int(dtable.getTableVal(el))
        if totalval == 0:
            print 'you get nothing!  good day, sir!'
            return 0
        
        
        else:
            
            try:
                chance = round(float(tabletotal)/totalval,3)
            except OverflowError:
                #TODO
                #this needs revision.  33-50pct are all 1 in 2 chance for very large numbers
                #all because of this line of code perhaps use funtion like scinote
                #pass a short float and power of ten.  can use in next line for better pct, too
                
                chance = (tabletotal)/int(totalval)
            
            try:
                pct = round(float(totalval)*100/tabletotal,3)
            except OverflowError:
                pct = (totalval)*100/tabletotal
            
            #the if elses establish output str based on size of numbers
            #either just display the num, or display it in scientific notation if too big
            scinoteCutoff = 1000000
            
            if totalval>scinoteCutoff and 'e' not in str(totalval):
                totalvalstring =scinote(totalval)
            else:
                totalvalstring = str(totalval)
            
            if tabletotal>scinoteCutoff and 'e' not in str(tabletotal):
                tabletotalstring =scinote(tabletotal)
            else:
                tabletotalstring =str(tabletotal)
            
            if chance > scinoteCutoff and 'e' not in str(chance):
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



def fancy_grapher(table,figure,style = 'bo'):
    x_axis = []
    y_axis =[]
    the_table = table.getTable()
    for el in the_table.keys():
        x_axis.append(el)
    x_axis.sort()
    for el in x_axis:
        y_axis.append(the_table[el])
    pylab.figure(figure)
    pylab.plot(x_axis,y_axis,style)
    pylab.draw()