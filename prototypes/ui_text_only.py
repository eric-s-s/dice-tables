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
        '''nose_choice = Choices('to', [(pick_nose, (nose, finger),
                                         'pick yr nose',('p', 'pick')),
                                        ( (choice2) )])'''
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
                return self.do_choice(out)
                #break
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
                         (remover, (table), 'REMOVE dice', ('rm', 'r')),
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
    t_choices.do_user_choice()

def save_new(table):
    '''save the table as a new entry in global_save_list'''
    GLOBAL_SAVE_LIST.save_new(table)
    table_actions(table)
def save(table, menu_choice):
    '''if you got here by quitting or back to main, checks to see if you
    want to save, then continues to your action'''
    s_actions = Choices('', [(quit_program, (), 'q', ('quit',)),
                             (main_menu, (), 'm', ('main menu',)),
                             (table_actions, (table), 'a', ('action',))])
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
    print table.weights_info()
    print ('\nthe range of numbers is %s-%s\nthe mean is %s\nthe stddev is %s'
           % (table.event_keys_min(), table.event_keys_max(),
              table.mean(), table.stddev()))
    usr_input = make_a_list(table)
    print gap.stats(table, usr_input)
    raw_input('when you are done, hit ENTER ')
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
                         (fancy, (table), 'a fancy pylab GRAPH',
                          ('graph', 'g'))])
    g_choices.do_user_choice()
    table_actions(table)

def fancy(table):
    '''print a pylab graph'''
    points = ('o', '<', '>', 'v', 's', 'p', '*', 'h', 'H', '+', 'x', 'D', 'd')
    colors = ('b', 'g', 'y', 'r', 'c', 'm', 'y', 'k')
    style = random.choice(points) + '-' + random.choice(colors)
    overlay = raw_input('overlay on old graph(y/n)?\n>>> ')
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
    same_dice = Choices('To', [(add_old, (table), 'add a PREVIOUS die', ('p',)),
                               (add_new, (table), 'add a NEW die', ('n',)),
                               (save, (table, 'quit'), 'QUIT', ('quit', 'q'))])
    same_dice.do_user_choice()
def add_old(table):
    '''process for adding the same kind of dice'''
    add_die, empty_check = choose_a_die(table)

    if empty_check == 0:
        print 'Never added a die'
        add_new(table)
    print add_die
    num_dice = get_num('How many dice would you like to add?', table)
    print 'please wait. adding dice. this may take time.\n...'
    table.add_die(num_dice, add_die)
    print 'all done.  there! that wasn\'t so bad. back to action menu'
    table_actions(table)
def add_new(table):
    '''process for adding new dice'''
    if str(table) == '':
        print '\n\nyou current table is empty'
    else:
        print '\n\nhere is your table info'
        print table
    new_die = make_die(table)
    num_dice = get_num('How many dice would you like to add?', table)
    table.add_die(num_dice, new_die)
    print 'all done.  there! that wasn\'t so bad. back to action menu'
    table_actions(table)
def make_die(table):
    '''the top level menu to get user to make a die'''
    dice_type = Choices('To',
                        [(make_basic, (table, False),
                          'make a BASIC die', ('b',)),
                         (make_basic, (table, True),
                          'make a BASIC die with MODIFIER', ('bm',)),
                         (make_weighted, (table, False),
                          'make a WEIGHTED die', ('w',)),
                         (make_weighted, (table, True),
                          'make a WEIGHTED die with MODIFIER', ('wm',)),
                         (save, (table, 'quit'), 'QUIT', ('quit', 'q'))])
    return dice_type.do_user_choice()
def make_basic(table, mod_it):
    '''takes user inpute to create a Die or ModDie'''
    size = get_num('what size for your dice?', table)
    if mod_it:
        mod = get_num('+/- how much?', table, True, True)
        return ds.ModDie(size, mod)
    else:
        return ds.Die(size)
def make_weighted(table, mod_it):
    '''takes user input to create a WeightedDie or ModWeightedDie'''
    size = get_num('what size for your dice?', table)
    out_dic = {}
    print 'time to make weights for a D%s' % (size)
    for d_val in range(size, 0, -1):
        question = 'enter an int value for the weight of roll: %s' % (d_val)
        weight = get_num(question, table, True)
        out_dic[d_val] = weight
    if mod_it:
        mod = get_num('+/- how much?', table, True, True)
        return ds.ModWeightedDie(out_dic, mod)
    else:
        return ds.WeightedDie(out_dic)

def remover(table):
    '''uses user input to remove a dice from the table'''
    rm_die, highest_num = choose_a_die(table)
    if highest_num == 0:
        print 'cannot remove from an empty list'
        table_actions(table)
    print rm_die
    print 'choose how many dice to remove'
    rm_num = get_num_range(table, 0, highest_num)
    table.remove_die(rm_num, rm_die)
    table_actions(table)

def choose_a_die(table):
    '''makes user choose a die from a table's list. or returns dummy die of zero
    counts if list is empty'''
    dice_list = table.get_list()
    if dice_list == []:
        return ds.Die(1), 0
    for index in range(len(dice_list)):
        die, number = dice_list[index]
        print 'index %s -> %s %s' % (index, number, die)
    print 'choose die by index'
    the_index = get_num_range(table, 0, len(dice_list) - 1)
    die, number = dice_list[the_index]
    return die, number
def get_num(question, table, zero_ok=False, neg_ok=False):
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
        elif int(ans) < 0 and neg_ok:
            return int(ans)
        else:
            print 'try something greater than 0. that would totally work!'
            if zero_ok:
                print ('well, ok. you can try 0 if you like. but that\'s as low'
                       + ' as i go!\n')
def get_num_range(table, bottom, top):
    '''prompts the user choose an int in the range, (bottom <= choice <= top)
    keeps prompting user until inputs proper answer or type 'q', 'quit' '''
    question = 'Please input an interger from %s to %s' % (bottom, top)
    while True:
        answer = get_num(question, table, True)
        if bottom <= answer <= top:
            return answer
        else:
            print '\nnaughty naughty out of range'

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
                no_dashes = value.split('-')
                #single pos or neg number
                if (len(no_dashes) == 1 or
                        no_dashes[0] in ('', ' ') and len(no_dashes) == 2):
                    out.append(int(value))
                #pos or neg numbers separated by a '-'
                else:
                    if len(no_dashes) == 2:
                        start, end = no_dashes
                    elif no_dashes[0] in ('', ' '):
                        start = '-' + no_dashes[1]
                        if no_dashes[2] in ('', ' '):
                            end = '-' + no_dashes[3]
                        else:
                            end = no_dashes[2]
                    else:
                        start = no_dashes[0]
                        end = '-' + no_dashes[2]
                    start = int(start)
                    end = int(end)
                    if start < end:
                        out.extend(range(start, end+1))
                    else:
                        out.extend(range(end, start+1))
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
