''' this module contains the class LongIntTable and longint math that the table
needs to deal with it's BFN'''
#these three functions are concerned with float-math for long ints.
def long_int_div(numerator, denominator, sig_figs=8):
    '''does float division for any number, including long ints
    returns floats where possible, otherwise long ints.'''
    man_figs = sig_figs+2
    exp_ans = exp(numerator) - exp(denominator)
    man_ans = mantissa(numerator, man_figs)/mantissa(denominator, man_figs)
    return make_answer(man_ans, exp_ans, sig_figs)
        
    
    
def long_int_times(factor_1, factor_2, sig_figs=8):
    '''does float multiplication for any number, including long ints
    returns floats where possible, otherwise long ints.'''
    man_figs = sig_figs+2
    exp_ans = exp(factor_1) + exp(factor_2)
    man_ans = mantissa(factor_1, man_figs) * mantissa(factor_2, man_figs)
    return make_answer(man_ans, exp_ans, sig_figs)
    
def long_int_pow(number, numerator, denominator, sig_figs=8):
    '''does anything to any exp.  inputs can be ints or floats.
    returns floats where possible, otherwise long ints.'''
    man_figs = sig_figs+2
    exp_num = exp(number)
    exp_remainder = exp_num % denominator
    exp_ans = (exp_num//denominator)*numerator
    man_ans = mantissa(number, man_figs)*10**exp_remainder
    man_ans = man_ans**(numerator/float(denominator))
    total_exp = exp(man_ans)+exp_ans
    total_man = mantissa(man_ans, man_figs)
    return make_answer(total_man, total_exp, sig_figs)
    

#the helper functions for the float-math functions
def exp(num):
    '''return the exp of a number'''
    if num == 0:
        return 'zero'
    if 'e' in str(num):
        return int(str(num).split('e')[1])
    elif abs(num) >= 1:
        return len(str(abs(int(num))))-1
    else:
        after_decimal = str(num).split('.')[1]
        count = -1
        for el in after_decimal:
            if el == '0':
                count -=1
            else:
                return count
def mantissa(num, sig_figs=10):
    '''mantissa(1.23455e+245) returns 1.23455 up to sig_fig digits.'''
    if num == 0:
        return 0
    elif 'e' in str(num):
        mantissa = float(str(num).split('e')[0])
        #return round(mantissa, sig_figs)
        return mantissa
    elif abs(num) >= 1:
        factor = 10**(exp(num) - sig_figs - 1)
        reduced = num//factor
        reduced = float(reduced)
        #return round(reduced/(10**(sig_figs+1)), sig_figs)
        return reduced/10**(sig_figs+1)
    else:
        factor = 10**(-exp(num))
        #return round(num*factor, sig_figs)
        return num*factor
    
def make_answer(mantissa, exp, sig_figs):
    '''takes raw answer and outputs appropriate answer'''
    max_float_exp = 300
    if exp < -max_float_exp:
        return 0.0
    #print 'exp = %s\nmantissa = %s' % (exp, mantissa)
    if exp <= max_float_exp:
        return round(mantissa*10**exp, sig_figs-exp)
    if exp > max_float_exp:
        new_mantissa = int(round(mantissa, sig_figs)*10**(sig_figs))
        new_pow = exp - sig_figs
        return new_mantissa*10**new_pow
def tst_pm(num):
    try:
        out =  mantissa(num)*10**exp(num)
    except OverflowError:
        temp = int(mantissa(num)*10**12)
        out = temp*10**(exp(num)-12)
    print out
    print num - out
    
        
class LongIntTable(object):
    '''a table of big fucking numbers and some math function for them.
    The table implicitly contains 0 occurences of all unassigned intergers.'''

    OVERFLOW_CUTOFF = 10**100
    def __init__(self, seed_dictionary):
        '''seed_dictionary is a dictionary of ints
        {value1: frequency of value1, value2: frequency of value 2, ...}'''
        self._table = seed_dictionary.copy()
        #for value, frequency in seed_dictionary.items():
        #   self._table[value] = frequency
        self._overflow_control = False

    def values(self):
        '''return the all the values, in order, that have non-zero frequency'''
        the_values = []
        for value, freq in self._table.items():
            if freq != 0:
                the_values.append(value)
        the_values.sort()
        return the_values
    def values_min(self):
        '''returns the min value'''
        if self.values() == []:
            return None
        else:
            return self.values()[0]
    def values_max(self):
        '''returns the max value'''
        if self.values() == []:
            return None
        else:
            return self.values()[-1]
    def values_range(self):
        '''returns a tuple of min and max values'''
        return self.values_min(), self.values_max()

    def frequency(self, value):
        '''Returns a tuple of the value and it's frequency.'''
        return value, self._table.get(value, 0)
    def frequency_range(self, start, stopbefore):
        '''Returns a list of tuples (value,frequency).
        Like regular range function, it stops before endvalue.'''
        tuple_list = []
        for value in range(start, stopbefore):
            tuple_list.append(self.frequency(value))
        return tuple_list
    def frequency_all(self):
        '''Returns a list of tuples IN ORDER for all non-zero-frequency
        values in table.'''
        value_list = self.values()
        tuple_list = []
        for value in value_list:
            tuple_list.append(self.frequency(value))
        return tuple_list
    def frequency_highest(self):
        '''Returns a tuple of (one of) the value(s) with the highest frequency,
        and it's frequency'''
        hf_val, hf_freq = None, 0
        for value, frequency in self._table.items():
            if frequency > hf_freq:
                hf_val, hf_freq = value, frequency
        return hf_val, hf_freq

    def total_frequency(self):
        '''returns the sum all the freuencies in a table'''
        all_freq = self._table.values()
        return sum(all_freq)

    def __str__(self):
        return ('table from %s to %s' %
                (self.values_min(), self.values_max()))

    #the next three functions deal with overflow
    def check_overflow(self):
        '''if table is too big, and overflow control is false, set to true'''
        if (not self._overflow_control and
                self.total_frequency() > self.OVERFLOW_CUTOFF):
            self._overflow_control = True
        return self._overflow_control

    def copy(self):
        '''returns a copy of a LIT'''
        new_dic = dict((val, freq) for val, freq in self.frequency_all())
        return LongIntTable(new_dic)

    def divide(self, numerator, denominator, sig_figs=5):
        '''numerator and denominator >=1 or <= -1.
        a special divide function for the large numbers in these tables.
        if overflow control is tripped, does the division accurately and
        returns either a large int, a float with the right number of sig figs,
        or 0.0 if answer would be less than 10**(-sig_figs)'''
        power_n = len(str(abs(int(numerator))))-1
        power_d = len(str(abs(int(denominator))))-1
        power_diff = power_n - power_d
        if not self.check_overflow():
            return round(float(numerator)/denominator, sig_figs - power_diff)
        else:
            if power_diff > sig_figs:
                return int(numerator)//int(denominator)
            elif -1*power_diff > sig_figs:
                return 0.0
            else:
                if power_diff >= 0:
                    factor = 10**(power_d - sig_figs)
                else:
                    factor = 10**(power_n - sig_figs)
                new_numerator = int(numerator)/factor
                new_denominator = int(denominator)/factor
                return round(float(new_numerator)/new_denominator,
                             sig_figs - power_diff)
    def mean(self):
        '''i mean, don't you just sometimes look at a table of values
        and wonder what the mean is?'''
        numerator = sum([value*freq for value, freq in self._table.items()])
        denominator = self.total_frequency()
        #return self.divide(numerator, denominator)
        return long_int_div(numerator, denominator, 5)#, self.divide(numerator, denominator)
    def stddev(self):
        '''returns the standdard deviation of the table, with special measures
        to deal with long ints.'''
        omfg_thisll_take_all_day = 10**750
        avg = self.mean()
        sig_figs = 4
        extra_digits = 5
        power = len(str(self.frequency_highest()[1])) - 1
        factor = 10**(power - (sig_figs + extra_digits))
        sqs = 0
        count = 0
        if self.total_frequency() > omfg_thisll_take_all_day:
            for value, frequency in self._table.items():
                sqs += (frequency//factor) * (avg - value)**2
                count += frequency
            new_count = count//factor
        else:
            for value, frequency in self._table.items():
                sqs += (self.divide(frequency, factor, (sig_figs + extra_digits))
                        * (avg - value)**2)
                #sqs += (long_int_div(frequency, factor, (sig_figs + extra_digits))
                #        * (avg - value)**2)
                count += frequency
            new_count = self.divide(count, factor, (sig_figs + extra_digits))
            #new_count = long_int_div(count, factor, (sig_figs + extra_digits))
        return round((sqs/new_count)**0.5, sig_figs)

    def add(self, times, values):
        '''this updates your table to be the frequency of it's orignal values
        plus the new list of values and frequencies
        times is (pos int) how many times to add the values to the table.
        values contains only ints.  it can be
        1 - lst of ints, 2 - list of tuples of [(val, freq), ...]
        3 - dict{val:freq, ...}, 4 - LongIntTable
        here's how it works - original list event A is 3 out of 5.
        event B is 2 out of 5 or {A:3, B:5}. add {A:2, B:1} ( [A,A,B] ) this way.
        A+A = 3*2, A+B = (3*1+5*2) B+B = 5*1.  new dict = {AA:6, AB:8, BB:5}'''
        #first convert any input to the same kind
        if isinstance(values, LongIntTable):
            to_add = values.frequency_all()
        elif isinstance(values, list) and isinstance(values[0], int):
            make_dic = {}
            for number in values:
                make_dic[number] = make_dic.get(number, 0)+1
            to_add = [(val, freq) for val, freq in make_dic.items()]
        elif isinstance(values, dict):
            to_add = [(val, freq) for val, freq in values.items()]
        else:
            to_add = values[:]
        to_add.sort()
        def _fastest(tuple_list):
            '''returns fastest method'''
            difference = 0
            cut_off = 3
            for pair in tuple_list:
                frequency = pair[1]
                if frequency != 0:
                    difference += abs(frequency) - 1
            if difference > cut_off:
                return tuple_list
            else:
                new_list = []
                for val, freq in tuple_list:
                    for _ in range(freq):
                        new_list.append(val)
                return new_list

        the_list = _fastest(to_add)
        #print the_list
        #if a list of ints is faster, will do that
        if isinstance(the_list[0], int):
            for _ in range(times):
                self._add_a_list(the_list)
        #otherwise adds by tuple
        else:
            for _ in range(times):
                self._add_tuple_list(the_list)

    def _add_a_list(self, lst):
        '''lst is ints. takes the table.  for each int in the list, makes new
        tables with each value changed to value+int. merges those new tables
        and updates the existing table to become the merge.'''
        #so for [1,2,3], this would take {0:1,1:2} and
        #update to {1:1, 2:2} + {2:1, 3:2} + {3:1, 4:2}
        newdic = {}
        for value, current_frequency in self._table.items():
            for val in lst:
                newdic[value+val] = (newdic.get(value+val, 0)+current_frequency)
        self._table = newdic

    def _add_tuple_list(self, lst):
        '''as add_list_to_values, but now pass a list of tuples of ints.
        [(2,3), (5,7)] means add 2 three times and add 5 seven times. much more
        efficient if numbers repeat a lot in your list.'''
        newdic = {}
        for value, current_frequency in self._table.items():
            for val, freq in lst:
                if freq != 0:
                    newdic[value+val] = (newdic.get(value+val, 0)+
                                         freq*current_frequency)
        self._table = newdic

    def merge(self, other):
        '''other can be LongIntTable, dictionary of ints {value:freq} or list
        of int tuples [(value, freq)].  adds all those value, freq to self'''
        if isinstance(other, LongIntTable):
            for val, freq in other.frequency_all():
                self._table[val] = self._table.get(val, 0) + freq
        elif isinstance(other, dict):
            for val, freq in other.items():
                self._table[val] = self._table.get(val, 0) + freq
        else:
            for val, freq in other:
                self._table[val] = self._table.get(val, 0) + freq

    def update_frequency(self, value, new_freq):
        '''looks up a value, and changes its frequency to the new one'''
        self._table[value] = new_freq

    def update_value_ow(self, old_val, new_val):
        '''takes the frequency at old_val and moves it to new_val'''
        freq = self._table[old_val]
        self._table[old_val] = 0
        self._table[new_val] = freq

    def update_value_add(self, old_val, new_val):
        '''takes the frequency at old_vall and moves it to new_val where it adds
        to the frequency already at new_val'''
        freq = self._table[old_val]
        self._table[old_val] = 0
        self._table[new_val] = self._table.get(new_val, 0)+freq


#testing
import time
def add_dices(table, num_times, lst):
    '''repeat the add_ function num_times times.'''
    for _ in range(num_times):
        table._add_a_list(lst)

def add_weighted_dice(table, num_times, lst):
    '''num_times is an int.  repeat add_tuple_list that many times.'''
    for _ in range(num_times):
        table._add_tuple_list(lst)

def stddevtst(table, mean):
    '''regular verstion of stddev for testing'''
    sqs = 0
    total_freq = 0
    for val, freq in table.items():
        sqs += (mean - val)**2*freq
        total_freq += freq
    return (sqs/total_freq)**0.5

def timetrial(lst, num_adds):
    '''a very lazily written timetrial for add_dice'''
    lst.sort()
    dic = {10:0, 11:0, 12:0}
    for el in lst:
        dic[el] = 1+dic.get(el, 0)
    t_list = []
    for die, weight in dic.items():
        t_list.append((die, weight))
    t_list.sort()
    print 'list', lst, '\ndictionary', dic, '\ntuples', t_list

    start_a = time.clock()
    a = LongIntTable({0:1})
    add_dices(a, num_adds, lst)
    print 'basic\n', time.clock()-start_a
    print a.mean(), a.stddev(), '\n'

    start_b = time.clock()
    b = LongIntTable({0:1})
    add_weighted_dice(b, num_adds, t_list)
    print 'tuple list\n', time.clock()-start_b
    print b.mean(), b.stddev(), '\n'

    start_c = time.clock()
    c = LongIntTable({0:1})
    c.add(num_adds, lst)
    print 'add funct list\n', time.clock()-start_c
    print c.mean(), c.stddev(), '\n'

    start_d = time.clock()
    d = LongIntTable({0:1})
    d.add(num_adds, dic)
    print 'add funct dictionary\n', time.clock()-start_d
    print d.mean(), d.stddev(), '\n'

    start_e = time.clock()
    e = LongIntTable({0:1})
    e.add(num_adds, t_list)
    print 'add funct tuple list\n', time.clock()-start_e
    print e.mean(), e.stddev(), '\n'

    start_f = time.clock()
    f = LongIntTable({0:1})
    f.add(num_adds, LongIntTable(dic))
    print 'add funct LIT\n', time.clock()-start_f
    print f.mean(), f.stddev(), '\n'
    return a, b, c, d, e, f

def tst_pow(num, exp_top,exp_bottom):
    start1 = time.clock()
    print 'LI %s' % (long_int_pow(num, exp_top, exp_bottom))
    print time.clock() - start1
    start2 = time.clock()
    print 'reg %s' % (num**(float(exp_top)/exp_bottom))
    print time.clock() - start2
    
def tst_div(num, denom):
    tst = LongIntTable({1: 10**1000})
    start1 = time.clock()
    lit = tst.divide(num, denom)
    time1 = time.clock() - start1
    start2 = time.clock()
    lid = long_int_div(num, denom)
    time2 = time.clock() - start2
    pct = 100*(lid-lit)/lid
    if isinstance(lid, float):
        print lid
    print 'err %s\ntable  time %s\nl.i.d. time %s' % (pct, time1, time2)
    
def stddev_time(table):
    s = time.clock()
    ans = table.stddev()
     
    print '.divide', ans, 'time' , time.clock()-s
    s = time.clock()
    ans = stddev_floor(table)
    print 'floor  ', ans, 'time' , time.clock()-s
    s = time.clock()
    ans = stddev_lid(table)
    print 'lid    ', ans, 'time' , time.clock()-s
    
def stddev_floor(table):
    avg = table.mean()
    sig_figs = 4
    extra_digits = 5
    power = len(str(table.frequency_highest()[1])) - 1
    factor = 10**(power - (sig_figs + extra_digits))
    sqs = 0
    count = 0
    for value, frequency in table._table.items():
        sqs += (frequency//factor) * (avg - value)**2
        count += frequency
    new_count = count//factor
    return round((sqs/new_count)**0.5, sig_figs)
def stddev_lid(table):
    avg = table.mean()
    sig_figs = 4
    extra_digits = 5
    power = len(str(table.frequency_highest()[1])) - 1
    factor = 10**(power - (sig_figs + extra_digits))
    sqs = 0
    count = 0
    for value, frequency in table._table.items():
                
        sqs += (long_int_div(frequency, factor, (sig_figs + extra_digits))
                * (avg - value)**2)
        count += frequency
    new_count = long_int_div(count, factor, (sig_figs + extra_digits))
    return round((sqs/new_count)**0.5, sig_figs)
 