import longintmath as lim
import dicestats as ds
import graphing_and_printing as gap

class SaveList(object):
    def __init__(self):
        self._save_list = []
        self._use_index = 0
        self._last_open = None
    def save(self, thing):
        self._save_list.insert(self._use_index, thing)
        self._last_open = None
        self._use_index = len(self._save_list)
    def revert(self, thing):
        if self._last_open != None:
            self._save_list.insert(self._use_index, self._last_open)
        self._last_open = None
        self._use_index = len(self._save_list)
    def retrieve(self, index):
        out = self._save_list.pop(index)
        self._use_index = index
        try:
            self._last_open = out.copy()
        except AttributeError:
            self._last_open = eval(repr(out))
        return out
    def delete(self, index):
        del(self._save_list[index])
        self._use_index = len(self._save_list)
    def have_it(self, thing):
        if thing in self._save_list:
            return True
        else:
            return False
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
    def __init__(self, filler, choice_list=None):
        if choice_list == None:
            self._choices = []
        else:
            self._choices = choice_list
        self._filler = filler
    def add_choice(self, function, args, string, *shortcuts):
        self._choices.append((function, args, string, shortcuts))
    def max_str(self):
        max_len = 0
        for choice in self._choices:
            if len(choice[2]) > max_len:
                max_len = len(choice[2])
        return max_len
    def do_choice(self, action):
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
        width = self.max_str() + 2
        out = ''
        for choice in self._choices:
            out = (out + self._filler + ' ' + choice[2].ljust(width) + 
                  ' please type: ' + ', '.join(choice[3]) + '\n')
        out = out.rstrip('\n')
        return out


gsl = SaveList()
def main_menu():
    m_choices = Choices('To', [
                        (new_table, (), 'make a NEW table', ('new', 'n')),
                        (open_table, (), 'OPEN a table', ('open', 'o')),
                        (delete_table, (), 'DELETE a table', ('del', 'd')),
                        (quit, (), 'QUIT', ('quit', 'q'))])
    m_choices.do_user_choice()
#TODO FIX TRY ERRIR  - hope it's fixed.   
def open_table():
    if str(gsl) == '':
        print 'nothing to open.  back to main'
        main_menu()
    while True:
        print gsl
        to_get = raw_input('pick an index number\n>>> ')
        check_quit(to_get)
        try:
            table = gsl.retrieve(int(to_get))
            break
        except IndexError:
            print 'i said pick a one of the index numbers'
            continue
        except ValueError:
            print 'ok. i\'ll speak slowly. p i c k   a   n u m b e r'
            continue
    print 'opening %s' % (table)
    table_actions(table)    
#TODO FIX TRY ERRIR    
def delete_table():
    if str(gsl) == '':
        print 'nothing to delete.  back to main'
        main_menu()
    while True:
        print gsl
        to_get = raw_input('pick an index number\n>>> ')
        check_quit(to_get)
        try:
            gsl.delete(int(to_get))
            break
        except IndexError:
            print 'i said pick a one of the index numbers'
            continue
        except ValueError:
            print 'ok. i\'ll speak slowly. p i c k   a   n u m b e r'
            continue
    main_menu()

def check_quit(usr_input, table=None):
    if usr_input in ('quit', 'q'):
        if table == None:
            quit()
        else:
            save(table, 'quit')        
def quit():
    raise SystemExit('exiting program')            
def new_table():
    new_table_obj = ds.DiceTable()
    print 'Making a new table.'
    table_actions(new_table_obj)                

def table_actions(table):
    t_choices = Choices('to', 
                      [(adder, (table), 'add dice', ('add', 'a')),
                       (save, (table, 'action'), 'save the table', 
                        ('save', 's')),
                       (get_stats, (table), 'get stats', ('get', 'g')),
                       (graphing, (table), 'make graphs', ('make', 'm')),
                       (save, (table, 'main menu'), 'BACK to main menu', 
                        ('back', 'b')), 
                       (save, (table, 'quit'), 'quit', ('quit', 'q'))])  
    print '\n\nyou current dice are:'
    print table
    print 'the last die added was:'
    table.last_die_info()
    t_choices.do_user_choice()
                        
                  
def save(table, menu_choice):
    s_actions = Choices('',[(quit, (), 'q', ('quit')),
                          (main_menu, (), 'm', ('main menu')),
                          (table_actions, (table), 'a', ('action'))])
    yes = True
    if menu_choice != 'action':
        yes = save_it(menu_choice)
    if gsl.have_it(table):
        print 'already saved'
        yes = False
    if yes:
        gsl.save(table)
    s_actions.do_choice(menu_choice)
def save_it(menu_choice):
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
    raise NotImplementedError
    table_actions(table)
def graphing(table):
    raise NotImplementedError
    table_actions(table) 
def adder(table):
    same_dice = Choices('To', [(add_same, (table), 'add the SAME die', ('s')),
                               (add_new, (table), 'add a NEW die', ('n')),
                               (save, (table, 'quit'), 'QUIT', ('quit', 'q'))])
    same_dice.do_user_choice()
def add_same(table):
    if table.get_last() == None:
        print 'Never added a die'
        add_new(table)
    num_dice = get_num('How many dice would you like to add?', table)
    print 'please wait. adding dice. this may take time.\n...'
    ds.add_dice(table, num_dice)
    print 'all done.  there! that wasn\'t so bad. back to action menu'        
    table_actions(table)
def add_new(table):
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
        ds.add_dice(table, num_dice, size)
    else:
        out_dic = {}
        print 'time to make weights for a D%s' % (size)
        for d_val in range(1, size+1):
            question = 'enter an int value for the weight of roll: %s' % (d_val)
            weight = get_num(question, table, True)
            out_dic[d_val] = weight
        print 'please wait. adding dice. this may take time.\n...'
        ds.add_dice(table, num_dice, out_dic)
    print 'all done.  there! that wasn\'t so bad. back to action menu'        
    table_actions(table)
            
        

def get_num(question, table, zero_ok=False):
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
        print 'enter number(s) separated by commas'
        print'or you can use a dash for a range of numbers: '
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
                        for num in range(start,end+1):
                            out.append(num)
                    else:
                        for num in range(end,start+1):
                            out.append(num)   
                else:
                    out.append(int(value))
            break
        except ValueError:
            print 'ooops.  looks like someone can\'t follow directions.'
            continue    
    return out

#if __name__ == '__main__':
#    diceTableYielder()
