from dice_class import DiceTable
from graphing_and_printing import *
import pylab

def menu_choices(user_input):
    if user_input == 'q':
        raise SystemExit


def make_a_list():
    '''take user input of a range of numbers
    and outputs a list of all those numbers'''
    user_input = raw_input('enter number(s) you want stats of separated '+
                           'by commas \nor you can '+
                           'use a dash for a range of numbers: ')
    if user_input == 'q' or user_input == '':
        return None
    out = []
    try:
        for el in user_input.split(','):
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
    return out




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
            return DiceTable(x)
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
            raise SystemExit()
        
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