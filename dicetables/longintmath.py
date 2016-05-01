''' this module contains the class LongIntTable and longint math that the table
needs to deal with it's BFN'''
#these functions are concerned with float-math for long ints.
from decimal import Decimal as dec
def _convert_back(num):
    '''helper function.  takes a Decimal and returns float if
    possible, else, long_int'''
    if float(num) == float('inf') or float(num) == float('-inf'):
        return int(num)
    else:
        return float(num)

def long_int_div(numerator, denominator):
    '''returns a float division of numbers even if they are over 1e+308'''
    ans = dec(numerator) / dec(denominator)
    return _convert_back(ans)

def long_int_times(number1, number2):
    '''returns a float times of numbers even if they are over 1e+308'''
    ans = dec(number1) * dec(number2)
    return _convert_back(ans)

def long_int_pow(number, exponent):
    '''returns a float exponent of numbers even if they are over 1e+308'''
    ans = dec(number)**dec(exponent)
    return _convert_back(ans)



class LongIntTable(object):
    '''a table of big fucking numbers and some math function for them.
    The table implicitly contains 0 occurences of all unassigned intergers.
    THIS TABLE SHOULD ONLY CONTAIN INT OR LONG.  it will not raise errors if you
    put in other values, but there is not telling what problems will happen.'''

    def __init__(self, seed_dictionary):
        '''seed_dictionary is a dictionary of ints. frequencies MUST BE POSITIVE.
        {value1: (frequency of value1), value2: (frequency of value 2), ...}'''
        self._table = seed_dictionary.copy()

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

    def mean(self):
        '''i mean, don't you just sometimes look at a table of values
        and wonder what the mean is?'''
        numerator = sum([value*freq for value, freq in self._table.items()])
        denominator = self.total_frequency()
        if denominator == 0:
            raise ZeroDivisionError('there are no values in the table')
        return long_int_div(numerator, denominator)
    def stddev(self, decimal_place=4):
        '''returns the standdard deviation of the table, with special measures
        to deal with long ints.'''
        avg = self.mean()
        extra_digits = 5
        power = len(str(self.frequency_highest()[1])) - 1
        if power < 2 * (decimal_place + extra_digits):
            factor = 1
        else:
            factor = 10**(power - (decimal_place + extra_digits))
        sqs = 0
        count = 0
        for value, frequency in self._table.items():
            sqs += (frequency//factor) * (avg - value)**2
            count += frequency
        new_count = count//factor
        return round((sqs/new_count)**0.5, decimal_place)

    def add(self, times, values):
        '''times is positive int or 0. values is a list of tuples(value, frequency)
        value and frequency are ints or longs, NO NEGATIVE FREQUENCIES ALLOWED!
        this function adds your table's values and frequency and the values's.

        here's how it works - original list event A is 3 out of 5.
        event B is 2 out of 5 or {A:3, B:5}. add {A:2, B:1} ( [A,A,B] ) this way.
        A+A = 3*2, A+B = (3*1+5*2) B+B = 5*1.  new dict = {AA:6, AB:8, BB:5}'''
        if times < 0:
            raise ValueError('times must be a positive int')
        to_add = self._check_cull_sort(values)
        def _fastest(tuple_list):
            '''returns fastest method'''
            experimentally_determined_ratio = 1.4
            number_of_values = len(tuple_list)
            total_freq = 0
            use_tuples = True
            for pair in tuple_list:
                total_freq += pair[1]
            list_ratio = long_int_div(total_freq, number_of_values)
            if list_ratio > experimentally_determined_ratio:
                return tuple_list, use_tuples
            else:
                use_tuples = False
                new_list = []
                for val, freq in tuple_list:
                    new_list = new_list + [val] * freq
                return new_list, use_tuples

        the_list, use_tuples = _fastest(to_add)
        #if a list of ints is faster, will do that
        if use_tuples:
            for _ in range(times):
                self._add_tuple_list(the_list)
        #otherwise adds by tuple
        else:
            for _ in range(times):
                self._add_a_list(the_list)
    @staticmethod
    def _check_cull_sort(tuple_list):
        '''prepares a list for add and remove.  removes zero values, raises
        errors where appropriate and returns a sorted list.'''
        new_list = []
        for val, freq in tuple_list:
            if freq < 0:
                raise ValueError('frequencies may not be negative')
            if freq != 0:
                new_list.append((val, freq))
        if new_list == []:
            raise ValueError('cannot add an empty list')
        new_list.sort()
        return new_list

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
        '''as add_a_list, but now pass a list of tuples of ints.
        [(2,3), (5,7)] means add 2 three times and add 5 seven times. much more
        efficient if numbers repeat a lot in your list.'''
        newdic = {}
        for value, current_frequency in self._table.items():
            for val, freq in lst:
                newdic[value+val] = (newdic.get(value+val, 0)+
                                     freq*current_frequency)
        self._table = newdic

    def remove(self, times, to_remove):
        '''times is positive int or 0. values is a list of tuple(value, frequency)
        value and frequency are long or int. NO NEGATIVE FREQUENCIES ALLOWED!
        this function reverses previous adds.  if you remove something you never
        added, or remove it more times than you added it, THERE IS NO RECORD OF
        WHAT YOU ADDED AND NO ERROR WILL BE RAISED. PLEASE BE CAREFUL.'''
        if times < 0:
            raise ValueError('times must be a positive int')
        remove_now = self._check_cull_sort(to_remove)
        for _ in range(times):
            self._remove_tuple_list(remove_now)

    def _remove_tuple_list(self, tuple_list):
        '''tuple_list is a sorted list of tuples (value, frequency) with NO ZERO
        frequencies.  does the opposite of _add_tuple_list'''
        tuples_min = tuple_list[0][0]
        tuples_max = tuple_list[-1][0]

        start = self.values_min()-tuples_min
        stop = self.values_max()- tuples_max
        new_dic = {}
        for value in range(start, stop+1):
            try:
                new_dic_val = self._table[value+tuples_min]
                for tup_val, tup_weight in tuple_list[1:]:
                    the_diff = tup_val - tuples_min
                    new_dic_val = new_dic_val - (new_dic.get(value - the_diff, 0) *
                                                 tup_weight)
                new_dic[value] = new_dic_val // tuple_list[0][1]
            except KeyError:
                continue
        self._table = new_dic

    def merge(self, other):
        '''other is list of int tuples [(value, freq)].  adds all those value,
        freq to self'''
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



 