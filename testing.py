import longintmath as lim
import dicestats as ds
import graphing_and_printing as gap
import time
import decimal as dec
#testing



def add_dices(table, num_times, lst):
    '''repeat the add_ function num_times times.'''
    for _ in range(num_times):
        table._add_a_list(lst)

def add_weighted_dice(table, num_times, lst):
    '''num_times is an int.  repeat add_tuple_list that many times.'''
    for _ in range(num_times):
        table._add_tuple_list(lst)



def timetrial(lst, num_adds):
    '''a very lazily written timetrial for add_dice'''
    lst.sort()
    dic = {}
    for el in lst:
        dic[el] = 1+dic.get(el, 0)
    t_list = []
    for die, weight in dic.items():
        t_list.append((die, weight))
    t_list.sort()
    print 'list', lst, '\ntuples', t_list, '\n'

    start_a = time.clock()
    a = lim.LongIntTable({0:1})
    add_dices(a, num_adds, lst)
    print 'basic\n', time.clock()-start_a
    print a.mean(), a.stddev(), '\n'

    start_b = time.clock()
    b = lim.LongIntTable({0:1})
    add_weighted_dice(b, num_adds, t_list)
    print 'tuple list\n', time.clock()-start_b
    print b.mean(), b.stddev(), '\n'

    
    return a, b





    
def stddev_time(table):
    s = time.clock()
    ans = stddev_dec(table) 
    print 'dec    ', ans, 'time' , time.clock()-s
    s = time.clock()
    ans = stddev_floor(table)
    print 'floor  ', ans, 'time' , time.clock()-s
    s = time.clock()
    ans = stddev_lid(table)
    print 'lid    ', ans, 'time' , time.clock()-s

def stddev_dec(table):
    avg = table.mean()
    sig_figs = 4
    #extra_digits = 5
    #power = len(str(table.frequency_highest()[1])) - 1
    #factor = 10**(power - (sig_figs + extra_digits))
    sqs = dec.Decimal(0)
    count = 0
    for value, frequency in table._table.items():        
        sqs += dec.Decimal(frequency) * dec.Decimal(((avg - value)**2))
        count += frequency
    new_count = dec.Decimal(count)
    return round(float((sqs/new_count)**dec.Decimal(0.5)), sig_figs)
        
def stddev_floor(table):
    avg = table.mean()
    sig_figs = 4
    extra_digits = 5
    power = len(str(table.frequency_highest()[1])) - 1
    if power < 2*(sig_figs+extra_digits):
        factor = 1
    else:
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
        sqs += (lim.long_int_div(frequency, factor)
                * (avg - value)**2)
        count += frequency
    new_count = lim.long_int_div(count, factor)
    return round((sqs/new_count)**0.5, sig_figs)

def stddev_basic(table):
    '''for evaluating stddev'''
    sig_figs = 4
    avg = table.mean()
    sqs = 0
    count = 0
    for roll, freq in table.frequency_all():
        sqs += freq*(((avg - roll)**2))
        count += freq
    return round((sqs/count)**0.5, sig_figs)

def stddeverr(table, function):
    '''compares stddevtst to the table method and sees pct diff'''
    accurate = stddev_basic(table)
    approx = function(table)
    return 100*(accurate - approx)/accurate

def stddev_tester(table, function):
    '''the final function for stddev checking.  adds a die and prints pctdiff'''
    for _ in range(100):
        ds.add_dice(table)
        print str(stddeverr(table, function))

def highest(table):
    '''quick! gimme the highest val, nicely displayed'''
    return gap.scinote(table.frequency_highest()[1])
#TODO ends

def make_tuple_list(an_input):
    '''get the zero values out to speed up and things and then convert 
    to an ordered tuple list'''
        
    if isinstance(an_input, lim.LongIntTable):
        temp_out = an_input.frequency_all()
    elif isinstance(an_input, list) and isinstance(an_input[0], int):
        make_dic = {}
        for number in an_input:
            make_dic[number] = make_dic.get(number, 0)+1
        temp_out = [(val, freq) for val, freq in make_dic.items()]
    elif isinstance(an_input, dict):
        temp_out = [(val, freq) for val, freq in an_input.items()]
    else:
        temp_out = an_input[:]
    out = []
    for pair in temp_out:
        if pair[1] != 0:
            out.append(pair)
    out.sort()
    return out

def time_scinote(num, dig_len):
     start = time.clock()
     print gap.scinote(num, dig_len)
     print 'time %s' % (time.clock()-start)
def time_fg(table):
     start = time.clock()
     gap.fancy_grapher_pct(table)
     print 'time %s' % (time.clock()-start)  


def tst_scinote(num, dig_len=4):
    exp = get_exp(num)
    mantissa = get_mantissa(num, dig_len+2)
    while mantissa >= 10:
        mantissa = mantissa/10.0
        exp +=1
    while mantissa < 1:
        mantissa = mantissa*10.0
        exp -=1
    mantissa = round(mantissa, dig_len - 1)
    if exp > 6:
        return '%se+%s' % (mantissa, exp)
    elif exp < -4:
        return '%se%s' % (mantissa, exp)
    #elif exp - dig_len >= 0:
    #    return add_commas(str(int(mantissa*10**exp)))
    #else:
    #    return add_commas(str(mantissa*10**exp))    
def get_exp(num):
    '''return the exp of a number'''
    if num == 0:
        return 1
    if 'e' in str(num):
        return int(str(num).split('e')[1])
    elif 'E' in str(num):
        return int(str(num).split('E')[1])
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
def get_mantissa(num, sig_figs=10):
    '''mantissa(1.23455e+245) returns 1.23455 with a min of sig_fig digits.'''
    if num == 0:
        return 0
    elif 'e' in str(num):
        the_mantissa = float(str(num).split('e')[0])
        return the_mantissa
    elif 'E' in str(num):
        the_mantissa = float(str(num).split('E')[0])
        return the_mantissa
    elif abs(num) >= 1:
        factor = 10**(get_exp(num) - sig_figs - 1)
        reduced = num//factor
        reduced = float(reduced)
        return reduced/10**(sig_figs+1)
    else:
        factor = 10**(-get_exp(num))
        return num*factor    