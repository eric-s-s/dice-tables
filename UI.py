from longinttable import *
from dice_classes import *
from graphing_and_printing import *
import pylab

saved_tables = {}

def main_menu():
    choices = ('Make a new table:'.ljust(30)+"enter 'new' or 'n'\n"+
               'Open an existing table:'.ljust(30)+'enter \'open\' or \'o\'\n'+
               'Delete an existing table:'.ljust(30)+'enter \'del\' or \'d\'\n'+
               'Quit'.ljust(30)+'enter \'q\' or \'quit\'\n')
    
    print choices
    ans = raw_input('>>> ').lower()
    if ans in ('new', 'n'): new_table(),
    if ans in ('open', 'o'): open_table(),
    if ans in ('del', 'd', 'delete', 'rm'): delete_table(),
    if ans in ('q', 'quit'): quit()
    else:
        print 'huh?'
        main_menu()
def open_table():
    raise NotImplementedError
    table_actions(table)    
    
def delete_table():
    raise NotImplementedError
    main_menu()
        
def quit():
    raise SystemExit('exiting program')            
def new_table():
    new_table = DiceTable()
    print 'Making a new table.'
    table_actions(new_table)                



def table_actions(table):
    menu_choices = {'add dice': ('add', 'a'),
                    'save this table' : ('save', 's'),
                    'get stats' : ('get', 'g'),
                    'make graphs' : ('make', 'm'),
                    'back to main menu' : ('back', 'b'), 
                    'quit' : ('quit', 'q'),   
                    }
    print table
    for choice, kw in menu_choices.items():
        print 'To %s, type "%s" or "%s"' % (choice, kw[0], kw[1])
    ans = raw_input('>>> ')
    if ans in ('q', 'quit'): check_save('quit', table)
    elif ans in ('back', 'b'): check_save('main', table)
    elif ans in ('g', 'get'): get_stats(table)
    elif ans in ('m', 'make'): graphing(table)
    elif ans in ('add', 'a'): adder(table)
    elif ans in ('save', 's'): save_menu('action', table)
    else: 
        print 'whu?'
        table_actions(table)               
def save_menu(menu_choice, table):
    raise NotImplementedError
def get_stats(table):
    raise NotImplementedError
    table_actions(table)
def graphing(table):
    raise NotImplementedError
    table_actions(table) 
def adder(table):
    raise NotImplementedError
    table_actions(table)
def check_save(string, table):
    if string == 'quit':
        choice = raw_input('save before quitting? (y/n)\n>>> ')
        if choice == 'n':
            quit()
        elif choice == 'y':
            save_menu(string, table)
        else:
            'wuuuut?'
            check_save(string, table) 
    if string == 'main':
        choice = raw_input('save before going to main menu? (y/n)\n>>> ')
        if choice == 'n':
            main_menu()
        elif choice == 'y':
            save_menu(string, table)
        else:
            'wuuuut?'
            check_save(string, table)              
class SomethingError(Exception):
    '''an error'''

def make_a_list():
    '''take user input of a range of numbers
    and outputs a list of all those numbers'''
    user_input = raw_input('enter number(s) separated '+
                           'by commas \nor you can '+
                           'use a dash for a range of numbers: ')
    if user_input == 'q' or user_input == 'quit':
        raise SystemExit
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