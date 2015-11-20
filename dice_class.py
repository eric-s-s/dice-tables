'''module contains DiceTable class only.'''
class DiceTable(object):
    '''This is a class for finding how many comdinations for any die roll using
    (number of dice)D(die size).  So it could tell you that on 3D6, you have
    25 different combinations that get you a "9" out of a total of 216
    combinations - an 11.6 percent chance. Or it could tell you that you have
    a 2.3 percent chance of rolling a 350 on 100D6.'''

    OVERFLOW_CUTOFF = 10**100
    def __init__(self, dsize):
        '''dsize is a positive interger.
        the kind of dice you want.  6-sided dice = 6'''
        self._totaldice = 0
        self._table = {0:1}
        self._dsize = dsize
        self._int_so_no_overflow = False

    def dice_size(self):
        '''Returns what kind of dice the table uses.'''
        return self._dsize
    def number_of_dice(self):
        '''Returns how many dice were used to generate the values in your table.'''
        return self._totaldice
    def total_combinations(self):
        '''Returns the total possible number of combinations from a dice table.'''
        return self._dsize**self._totaldice

    def roll_range_top(self):
        '''Returns the highest die roll in table.'''
        return self._dsize*self._totaldice
    def roll_range_bottom(self):
        '''Returns the lowest die roll in table.'''
        return self._totaldice
    def roll_range(self):
        '''Returns a tuple of the range_bottom and range_top.'''
        return (self.roll_range_bottom(), self.roll_range_top())

    def roll_frequency(self, roll):
        '''Returns tuple of the roll and it's frequency.'''
        return roll, self._table.get(roll, 0)
    def roll_frequency_range(self, start, stopbefore):
        '''Returns a list of tuples (roll,frequency).
        Like regular range function, it stops before endvalue.'''
        tuple_list = []
        for roll in range(start, stopbefore):
            #tuple_list.append((roll, self._table.get(roll)))
            tuple_list.append(self.roll_frequency(roll))
        return tuple_list
    def roll_frequency_all(self):
        '''Returns a list of tuples IN ORDER for all rolls in table.'''
        start = self.roll_range_bottom()
        stop = self.roll_range_top()+1
        return self.roll_frequency_range(start, stop)
    def roll_frequency_highest(self):
        '''Returns a tuple of (one of) the roll with the highest frequency,
        and it's frequency'''
        roll = int(self.mean())
        return (roll, self._table[roll])


    def add_a_die(self):
        '''Takes your dicetable object, and calculates all the new combinations
        if you add a new die of the dsize of the object.'''
        #so for d3, this would take {0:1,1:2} and
        #update to {1:1,2:1,3:1}+{2:2,3:2,4:2}
        if (not self._int_so_no_overflow and
                self.total_combinations() > self.OVERFLOW_CUTOFF):
            self._int_so_no_overflow = True
        self._totaldice += 1
        newdic = {}
        for roll, current_frequency in self._table.items():
            for die_value in range(1, self._dsize+1):
                newdic[roll+die_value] = \
                (newdic.get(roll+die_value, 0)+current_frequency)
        self._table = newdic
    def add_many_dice(self, num_dice):
        '''num_dice is an int.  add that many dice.'''
        for x in range(num_dice):
            self.add_a_die()


    def __str__(self):
        return str(self._totaldice)+'D'+str(self._dsize)


    def mean(self):
        '''i mean, don't you just sometimes look at a table of values
        and wonder what the mean is?'''
        return self._totaldice*(1+self._dsize)/2.0

    def stddev2(self):
        '''Returns the standard deviation of the table.'''
        avg = self.mean()
        sqs = 0
        count = 0
        for roll, frequency in self._table.items():
            sqs += frequency*self.int_or_float((avg - roll)**2)
            count += frequency
        return round((sqs/count)**0.5, 4)

    def stddev(self):
        omfg_thisll_take_all_day = 10**750
        avg = self.mean()
        sig_figs = 4
        extra_digits = 5
        power = len(str(self.roll_frequency_highest()[1])) - 1
        factor = 10**(power - (sig_figs + extra_digits))
        sqs = 0
        count = 0
        if self.total_combinations() > omfg_thisll_take_all_day:
            for roll, frequency in self._table.items():
                sqs += (frequency//factor) * (avg - roll)**2
                count += frequency
            new_count = count//factor
        else:
            for roll, frequency in self._table.items():
                sqs += (self.divide(frequency, factor, (sig_figs + extra_digits))
                        * (avg - roll)**2)
                count += frequency
            new_count = self.divide(count, factor, (sig_figs + extra_digits))    
        return round((sqs/new_count)**0.5,sig_figs)

    def int_or_float(self, variable):
        '''OverflowError control.  These tables deal with VERY large numbers.
        Floats over 10**300 or so, become "inf". If you explicitly convert
        certain numbers to intergers, Python can handle the huge-number math.
        Otherwise, you swim in OverflowErrors'''
        if self._int_so_no_overflow:
            return int(variable)
        else:
            return float(variable)

    def divide(self, numerator, denominator, sig_figs=5):
        '''numerator and denominator >=1.
        a special divide function for the large numbers in these tables.
        if overflow control is tripped, does the division accurately and
        returns either a large int, a float with the right number of sig figs,
        or 0.0 if answer would be less than 10**(-sig_figs)'''
        power_n = len(str(int(numerator)))-1
        power_d = len(str(int(denominator)))-1
        power_diff = power_n - power_d

        if not self._int_so_no_overflow:
            return round(float(numerator)/denominator, sig_figs - power_diff)
        else:
            if power_diff > sig_figs:
                return int(numerator)/int(denominator)
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



        

    #TODO ends.

