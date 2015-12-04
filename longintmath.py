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
        return 1
    if 'e' in str(num):
        return int(str(num).split('e')[1])
    elif abs(num) >= 1:
        return len(str(abs(int(num))))-1
    else:
        after_decimal = str(num).split('.')[1]
        count = -1
        for digit in after_decimal:
            if digit == '0':
                count -= 1
            else:
                return count
def mantissa(num, sig_figs=10):
    '''mantissa(1.23455e+245) returns 1.23455 up to sig_fig digits.'''
    if num == 0:
        return 0
    elif 'e' in str(num):
        the_mantissa = float(str(num).split('e')[0])
        #return round(mantissa, sig_figs)
        return the_mantissa
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

def make_answer(a_mantissa, exponent, sig_figs):
    '''takes raw answer and outputs appropriate answer'''
    sig_figs -= 1
    if a_mantissa < 1:
        a_mantissa *= 10
        exponent -= 1
    max_float_exp = 300
    if exponent < -max_float_exp:
        return 0.0
    #print 'exp = %s\nmantissa = %s' % (exp, mantissa)
    if exponent <= max_float_exp:
        return round(a_mantissa*10**exponent, sig_figs - exponent)
    if exponent > max_float_exp:
        new_mantissa = int(round(a_mantissa, sig_figs)*10**(sig_figs))
        new_pow = exponent - sig_figs
        return new_mantissa*10**new_pow


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

    def mean(self):
        '''i mean, don't you just sometimes look at a table of values
        and wonder what the mean is?'''
        sig_figs = 8
        numerator = sum([value*freq for value, freq in self._table.items()])
        denominator = self.total_frequency()
        return long_int_div(numerator, denominator, sig_figs)
    def stddev(self):
        '''returns the standdard deviation of the table, with special measures
        to deal with long ints.'''
        avg = self.mean()
        sig_figs = 4
        extra_digits = 5
        power = len(str(self.frequency_highest()[1])) - 1
        factor = 10**(power - (sig_figs + extra_digits))
        sqs = 0
        count = 0
        for value, frequency in self._table.items():
            sqs += (frequency//factor) * (avg - value)**2
            count += frequency
        new_count = count//factor
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



 