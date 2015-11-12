from multiple_dice_class import *
import pylab

    
            
            
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


#TODO i need to modify the overflowerror, maybe use a function like scinote. 
#right now, since overflowerror just uses int the chance will say 1 in 2 when pct is 34-50
def getstat(dtable):
        '''returns the stats on lst of elements in self'''
        totalval = 0
        tabletotal = dtable.totalcombos()
        #below takes the values from makealist to get lst for function and 
        # str to print the range of values
        lst,lststring = makealist()
        if lst == None:
            return None
        
        for el in lst:
            totalval += dtable.getTableVal(el)
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
                
                chance = (tabletotal)/totalval
            
            try:
                pct = round(float(totalval)*100/tabletotal,3)
            except OverflowError:
                pct = (totalval)*100/tabletotal
            
            #the if elses establish output str based on size of numbers
            #either just display the num, or display it in scientific notation if too big
            scinoteCutoff = 1000000
            
            if totalval>scinoteCutoff:
                totalvalstring =scinote(totalval)
            else:
                totalvalstring = str(totalval)
            
            if tabletotal>scinoteCutoff:
                tabletotalstring =scinote(tabletotal)
            else:
                tabletotalstring =str(tabletotal)
            
            if chance > scinoteCutoff:
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

#start the UI
def table_setup():
    '''set up a table.  output init-ed table or "q"'''
    while True:
        print "what kind of dicetable would you like to work with?"
        usr_input = raw_input("'q' quits\ntype 'r' for a regular table, 'm' for multi-value table, 'w' for weighted table: ")
        if usr_input == 'r':
            out = _table_setup_R()
            if out == 'b':
                print '\n            up one menu'
                continue
            else:
                return out
           
        if usr_input == 'm':
            out = _table_setup_M()
            if out == 'b':
                print '\n            up one menu'
                continue
            else:
                return out
        
        if usr_input == 'w':
            out = _table_setup_W()
            if out == 'b':
                print '\n            up one menu'
                continue
            else:
                return out
                
        if usr_input == 'q':
            return 'q'
        else:
            print
            print
            print 'nice try dickhead'
            print                

def _table_setup_R():
    '''regular table'''
    while True:
        set_up_val = raw_input('    regular dicetable. \n    \'b\' for back or input a positive int >1 for dice value: ')
        if set_up_val == 'b':
            return 'b'
        try:
            x =int(set_up_val)
            if x<2:
                raise ValueError
            print '        creating table'
            return dicetable(x)
        except ValueError:
            print '\n        asshole'
            continue
        #end REGULAR table


def _table_setup_M():
    '''multiple table'''
    print 'creating empty dicetable'
    return MultipleDiceTable()
    #end MULTIPLE table

def _table_setup_W():
    '''weighted table'''
    raise NotImplementedError
    #end WEIGHTED table



def add_what(table):
    '''input how much to add to your table or "q" or "b"'''
    def _add_what_dt(table):
        x = raw_input('            time to add dice\n'\
        +'            "b" for "back", "q" for "quit" of pos interger/0 for how many dice to add ')
        if x == 'b':
            print 'chose b'
            return 'b'
            
        if x == 'q':
            print 'chose q'
            return 'q'
            
        else:
            try:
                table.generator(int(x))
            except ValueError:
                print 'oh come on.  you\'re not even trying. adding 0 dice'
                table.generator(0)

    
    def _add_what_MDT(table):
        x = raw_input('            time to add dice\n'\
        +'            "b" for "back", "q" for "quit" of pos interger/0 for how many dice to add ')
        
        if x == 'b':
            print 'chose b'
            return 'b'
            
        if x == 'q':
            print 'chose q'
            return 'q'
        dsize = raw_input('          now what kind of dice are we adding, hmmm?')    
        
        try:
            table.generator(int(x),int(dsize))
        except ValueError:
            print 'oh come on.  you\'re not even trying. adding 0 dice'
            table.generator(0,0)            
    
    if type(table) == dicetable:
        return _add_what_dt(table)
   
    if type(table) == MultipleDiceTable:
        return _add_what_MDT(table)

        
                                                                                                
def another_UI():
    x = 'go on'
    while x != 'q':
        x = table_setup()
        if x == 'q':
            break
        
        while True:
            ans = add_what(x)
            
            if ans=='q':
                x = 'q'
                break
            if ans =='b':
                
                break
            
            choice = raw_input('type "t" for a table, "g" for a graph or the anykey to skip ')
            if choice == 't':
                x.printTable()
            if choice == 'g':
                x.truncategrapher()
            if choice == 'f':
                fancy_grapher(x,1)
            
            while True: 
                #TODO a hot mess rewrite getstat
                #then again, the whole thing feels like a hot mess   
                stat_choice = raw_input('stats? y/n  or q')
                if stat_choice == 'y':
                    print
                    print x
                    print 'the mean is '+str(x.mean())
                    print 'the standard deviation is '+str(x.stddev())
                    print 'the range is '+str(x.min())+'-'+str(x.max())
                    print
                    argh = getstat(x)
                    if argh == None:
                        break
                if stat_choice == 'n':
                    break
                if stat_choice == 'q':
                   
                    
                    break        
        
        #TODO the cache when get here, put value in cache.  cache holds ten tables
        #how the fuc to access?
             
def input_weights(dsize):
    outlst = []
    for x in range(dsize):
        usr_says = ''
        while type(usr_says) == str:
            usr_says = raw_input('put in your weight for a roll of '+str(x+1)+': ')
            try:
                usr_says = float(usr_says)
                if usr_says <0:
                    print '\nno such thing as a negative weight'
                    usr_says = str(usr_says)
                    raise ValueError
            except ValueError:
                print '\nincorrect input'
        outlst.append(usr_says)
    return outlst
#if __name__ == '__main__':
#    diceTableYielder()