'''this module will run a dice program.  to start,  type main_menu().  the two
global variables are global_save_list and global_count.  the first is where
the saved tables are kept. to reset it, reload the module.  otherwise, you
will have the same list of saves every time you run main menu. the second is
for pylab figures.'''
import dicestats as ds
import graphing_and_printing as gap
import pylab
import random
from copy import deepcopy
#TODO add and remove changed.  also, str methods for dice table.  change it all
class SaveList(object):
    '''this class save copies of objects and returns them. uses copy.deepcopy().
    this SHOULD keep any mutability problems from happening.'''
    def __init__(self):
        self._save_list = []
        self._last_index = None
    def save_overwrite(self, thing):
        '''if there's a last_index - made when retrieving or saving - overwrites
        to that index.  else,save_new'''
        if self._last_index == None:
            self.save_new(thing)
        else:
            ow_save = deepcopy(thing)
            self._save_list[self._last_index] = ow_save
    def save_new(self, thing):
        '''saves a new object at new index'''
        new_save = deepcopy(thing)
        self._last_index = len(self._save_list)
        self._save_list.append(new_save)
    def retrieve(self, index):
        '''returns a copy.deepcopy() of the object.'''
        out = deepcopy(self._save_list[index])
        self._last_index = index
        return out
    def delete(self, index):
        '''you'll never guess'''
        if self._last_index == index or self._last_index == None:
            self._last_index = None
        if self._last_index > index:
            self._last_index -= 1
        del self._save_list[index]
    def forget_last(self):
        '''tells the list to forget the last thing opened or saved so it won't
        get overwritten.'''
        self._last_index = None
    def __str__(self):
        out = ''
        width = len(str(len(self._save_list)-1))
        fix_return = '\n'+(width + 2)*' '
        for index in range(len(self._save_list)):
            out = (out + '%s: %s\n' %
                   (str(index).rjust(width),
                    str(self._save_list[index]).replace('\n', fix_return)))
        return out

class Choices(object):
    '''a convenient way to make menu choices.  the first element in a choice list
    is the string to add to each element string. each element in a choice list is
    a tuple.  it contains
    (function name, (args for function), 'what to display', ('cmnd1', 'cmd2'...))
    '''
    def __init__(self, filler, choice_list=None):
        '''nose_choice = Choices(['to', (pick_nose, (nose, finger),
                                         'pick yr nose',('p', 'pick')),
                                        ( (choice2) )]'''
        if choice_list == None:
            self._choices = []
        else:
            self._choices = choice_list
        self._filler = filler
    def add_choice(self, function, args, string, *shortcuts):
        '''input - (pick_nose2, (nose, finger), 'pick it!', 'p2', 'pick2')'''
        self._choices.append((function, args, string, shortcuts))
    def _max_str(self):
        '''get len of longest str for printing purposes'''
        max_len = 0
        for choice in self._choices:
            if len(choice[2]) > max_len:
                max_len = len(choice[2])
        return max_len
    def do_choice(self, action):
        '''nose_choice.do_choice('p') returns pick_nose(nose, finger)'''
        found_it = False
        for choice in self._choices:
            if action in choice[3]:
                found_it = True
                if not isinstance(choice[1], tuple):
                    return choice[0](choice[1])
                else:
                    return choice[0](*choice[1])
        if not found_it:
            raise IndexError
    def do_user_choice(self):
        '''as do_choice, but get's user input to choose'''
        while True:
            print '\n\n%s' % (self)
            out = raw_input('Please choose an action.\n>>> ')
            try:
                self.do_choice(out)
                break
            except IndexError:
                print 'learn how to pick choices, MF'
                continue

    def __str__(self):
        width = self._max_str() + 2
        out = ''
        for choice in self._choices:
            out = (out + self._filler + ' ' + choice[2].ljust(width) +
                   ' please type: ' + ', '.join(choice[3]) + '\n')
        out = out.rstrip('\n')
        return out


GLOBAL_SAVE_LIST = SaveList()
GLOBAL_COUNT = 0
def main_menu():
    '''the start of a chain of menus'''
    m_choices = Choices('To',
                        [(new_table, (), 'make a NEW table', ('new', 'n')),
                         (open_table, (), 'OPEN a table', ('open', 'o')),
                         (delete_table, (), 'DELETE a table', ('del', 'd')),
                         (quit_program, (), 'QUIT', ('quit', 'q'))])
    GLOBAL_SAVE_LIST.forget_last()
    m_choices.do_user_choice()

def open_table():
    '''opens a table from the global_save_list'''
    if str(GLOBAL_SAVE_LIST) == '':
        print 'nothing to open.  back to main'
        main_menu()
    while True:
        print GLOBAL_SAVE_LIST
        to_get = raw_input('pick an index number\n>>> ')
        check_quit(to_get)
        try:
            table = GLOBAL_SAVE_LIST.retrieve(int(to_get))
            break
        except IndexError:
            print 'i said pick a one of the index numbers'
            continue
        except ValueError:
            print 'ok. i\'ll speak slowly. p i c k   a   n u m b e r'
            continue
    print 'opening %s' % (table)
    table_actions(table)

def delete_table():
    '''deletes a table from the global_save_list'''
    if str(GLOBAL_SAVE_LIST) == '':
        print 'nothing to delete.  back to main'
        main_menu()
    while True:
        print GLOBAL_SAVE_LIST
        to_get = raw_input('pick an index number\n>>> ')
        check_quit(to_get)
        try:
            GLOBAL_SAVE_LIST.delete(int(to_get))
            break
        except IndexError:
            print 'i said pick a one of the index numbers'
            continue
        except ValueError:
            print 'ok. i\'ll speak slowly. p i c k   a   n u m b e r'
            continue
    main_menu()

def check_quit(usr_input, table=None):
    '''checks user input to see if quit was enetered'''
    if usr_input in ('quit', 'q'):
        if table == None:
            quit_program()
        else:
            save(table, 'quit')
def quit_program():
    '''quits and manages global variables on the way out'''
    GLOBAL_SAVE_LIST.forget_last()
    global GLOBAL_COUNT
    GLOBAL_COUNT = 0
    raise SystemExit('exiting program')

def new_table():
    '''make a new table'''
    new_table_obj = ds.DiceTable()
    print 'Making a new table.'
    table_actions(new_table_obj)

def table_actions(table):
    '''all the actions you ever wanted to do on a dice table'''
    t_choices = Choices('to',
                        [(adder, (table), 'ADD dice', ('add', 'a')),
                         (get_stats, (table), 'GET stats', ('get', 'g')),
                         (graphing, (table), 'MAKE graphs', ('make', 'm')),
                         (save, (table, 'action'), 'SAVE the table',
                          ('save', 's')),
                         (save_new, (table), 'save the table as NEW',
                          ('new', 'n')),
                         (save, (table, 'main menu'), 'BACK to main menu',
                          ('back', 'b')),
                         (save, (table, 'quit'), 'QUIT', ('quit', 'q'))])
    print '\n\nyou current dice are:'
    print table
    print 'the last die added was:'
    table.last_die_info()
    t_choices.do_user_choice()

def save_new(table):
    '''save the table as a new entry in global_save_list'''
    GLOBAL_SAVE_LIST.save_new(table)
    table_actions(table)
def save(table, menu_choice):
    '''if you got here by quitting or back to main, checks to see if you
    want to save, then continues to your action'''
    s_actions = Choices('', [(quit_program, (), 'q', ('quit')),
                             (main_menu, (), 'm', ('main menu')),
                             (table_actions, (table), 'a', ('action'))])
    yes = True
    if menu_choice != 'action':
        yes = save_it(menu_choice)
    if yes:
        GLOBAL_SAVE_LIST.save_overwrite(table)
    s_actions.do_choice(menu_choice)
def save_it(menu_choice):
    '''helper function to see if you want to save'''
    print 'save before %s? (y/n)' % (menu_choice)
    answer = raw_input('>>> ')
    if answer.lower() == 'y':
        return True
    elif answer.lower() == 'n':
        return False
    else:
        print 'huh?'
        save_it(menu_choice)

def get_stats(table):
    '''gets stats for your table'''
    print '\n\nhere is your table info\n'
    table.weights_info()
    print table
    print ('the range of numbers is %s-%s\nthe mean is %s\nthe stddev is %s'
           % (table.values_min(), table.values_max(),
              table.mean(), table.stddev()))
    usr_input = make_a_list(table)
    gap.stats(table, usr_input)
    raw_input('when you are done, (gently) hit ENTER ')
    table_actions(table)

def graphing(table):
    '''all the graphing choices'''
    g_choices = Choices('To show a',
                        [(gap.print_table, (table), 'PRINTOUT of the table',
                          ('print', 'p')),
                         (gap.grapher, (table), 'REGULAR graph of X\'s',
                          ('reg', 'r')),
                         (gap.truncate_grapher, (table),
                          'TRUNCATED graph with all boring bits removed',
                          ('trunc', 't')),
                         (fancy, (table), 'a fancy but buggy pylab GRAPH',
                          ('graph', 'g'))])
    g_choices.do_user_choice()
    table_actions(table)

def fancy(table):
    '''print a pylab graph'''
    points = ('o', '<', '>', 'v', 's', 'p', '*', 'h', 'H', '+', 'x', 'D', 'd')
    colors = ('b', 'g', 'y', 'r', 'c', 'm', 'y', 'k', 'w')
    style = random.choice(points) + '-' + random.choice(colors)
    overlay = raw_input('overlay on old grap(y/n)?\n>>> ')
    global GLOBAL_COUNT
    if overlay != 'y':
        GLOBAL_COUNT += 1
    figure = GLOBAL_COUNT
    pylab.ion()
    if overlay == 'y':
        gap.fancy_grapher_pct(table, figure, style, True)
    else:
        gap.fancy_grapher_pct(table, figure, style)
    pylab.pause(0.1)

def adder(table):
    '''the first function for the add dice process'''
    same_dice = Choices('To', [(add_same, (table), 'add the SAME die', ('s')),
                               (add_new, (table), 'add a NEW die', ('n')),
                               (save, (table, 'quit'), 'QUIT', ('quit', 'q'))])
    same_dice.do_user_choice()
def add_same(table):
    '''process for adding the same kind of dice'''
    if table.last_info() == 'None':
        print 'Never added a die'
        add_new(table)
    num_dice = get_num('How many dice would you like to add?', table)
    print 'please wait. adding dice. this may take time.\n...'
    ds.add_dice(table, num_dice)
    print 'all done.  there! that wasn\'t so bad. back to action menu'
    table_actions(table)
def add_new(table):
    '''process for adding new dice'''
    if str(table) == '':
        print '\n\nyou current table is empty'
    else:
        print '\n\nhere is your table info'
        print table
    num_dice = get_num('How many dice would you like to add?', table)
    size = get_num('what size for your dice?', table)
    print '\n\nenter "y" for regular dice or anykey for weighted dice'
    no_weight = raw_input('>>> ')
    if no_weight == 'y':
        print 'please wait. adding dice. this may take time.\n...'
        print ''
        ds.add_dice(table, num_dice, ds.Die(size))
    else:
        out_dic = {}
        print 'time to make weights for a D%s' % (size)
        for d_val in range(1, size+1):
            question = 'enter an int value for the weight of roll: %s' % (d_val)
            weight = get_num(question, table, True)
            out_dic[d_val] = weight
        print 'please wait. adding dice. this may take time.\n...'
        ds.add_dice(table, num_dice, ds.WeightedDie(out_dic))
    print 'all done.  there! that wasn\'t so bad. back to action menu'
    table_actions(table)


def get_num(question, table, zero_ok=False):
    '''used by several functions to make sure user input is either a whole or
    counting number.  prompts with question(a string) and returns when the user
    finally gets their act together'''
    while True:
        print '\n\n' + question
        ans = raw_input('>>> ')
        check_quit(ans, table)
        try:
            int(ans)
        except ValueError:
            print 'really? enter a number too tough for you?\n'
            continue
        if int(ans) > 0:
            return int(ans)
        elif int(ans) == 0 and zero_ok:
            return 0
        else:
            print 'try something greater than 0. that would totally work!'
            if zero_ok:
                print ('well, ok. you can try 0 if you like. but that\'s as low'
                       + ' as i go!')
            print

def make_a_list(table):
    '''take user input of a range of numbers
    and outputs a list of all those numbers'''
    while True:
        print '\nplease input the numbers you would like stats about'
        print 'enter number(s) separated by commas'
        print 'or you can use a dash for a range of numbers: '
        user_input = raw_input('>>> ')
        check_quit(user_input, table)
        out = []
        try:
            for value in user_input.split(','):
                if '-' in value:
                    start, end = value.split('-')
                    start = int(start)
                    end = int(end)
                    if start <= end:
                        for num in range(start, end+1):
                            out.append(num)
                    else:
                        for num in range(end, start+1):
                            out.append(num)
                else:
                    out.append(int(value))
            break
        except ValueError:
            print 'ooops.  looks like someone can\'t follow directions.'
            continue
    return out

if __name__ == '__main__':
    print 'welcome to the dice stats generator.  follow the directions.'
    print 'if you quit, you can get back in by typing main_menu().'
    print 'if you want to erase your save data, reload the module.'
    main_menu()