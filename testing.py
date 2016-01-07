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

def time_it(tuple_list):
    list_too_long = 1000
    diff_too_high = 100
    use_tuple = True
    num_vals = len(tuple_list)
    #if num_vals > list_too_long:
    #    return tuple_list, use_tuple
    #freq_tot = sum([pair[1] for pair in tuple_list])
    #if freq_tot - num_vals > diff_too_high:
    #    return tuple_list, use_tuple
    
    int_list = []
    for val, freq in tuple_list:
        int_list = int_list + [val] * freq
    #test_a = lim.LongIntTable(dict((val, val*2) for val in range(50)))
    #test_b = lim.LongIntTable(dict((val, val*2) for val in range(50)))
    #test_times = 100
    time_limit = 0.1
    test_a = lim.LongIntTable(dict(tuple_list))
    elapsed_time_t = 0
    tuple_count = 0
    tuple_time = time.clock()
    
    while elapsed_time_t < time_limit:
        test_a._add_tuple_list(tuple_list)
        tuple_count +=1
        elapsed_time_t = time.clock() - tuple_time
    
    test_b = lim.LongIntTable(dict(tuple_list))
    elapsed_time_i = 0
    int_count = 0
    int_time = time.clock()
    while elapsed_time_i < time_limit:
        test_b._add_a_list(int_list)
        int_count +=1
        elapsed_time_i = time.clock() - int_time
    
    print 'tuple', tuple_count, elapsed_time_t
    print 'ints ', int_count, elapsed_time_i
    if tuple_count == int_count:
        if elapsed_time_t < elapsed_time_i:
            return use_tuple
        else:
            return not use_tuple
    elif tuple_count > int_count:
        #return tuple_list, use_tuple
        return use_tuple
    else:
        #return int_list, not use_tuple
        return not use_tuple
        
    
def gen_spread(val_range):
    mod = val_range + 1
    while mod > 0:
        lst = []
        for val in range(1, val_range+1):
            lst.append((val, int(val % mod == 0) + 1))
        mod -= 1
        yield lst    

def gen_one_point(val_range, loc='mid'):
    '''a generator for a list of tuples, 1 - val_range. add one to loc = "start",
    "mid" or "end"'''
    lst = [(val, 1) for val in range(1, val_range + 1)]
    if loc == 'start':
        index = 0
    elif loc == 'end':
        index = len(lst) - 1
    else:
        index = val_range // 2
    index_val = lst[index][0]
    while True:
        yield lst
        current_freq = lst[index][1]
        lst[index] = (index_val, current_freq + 1)
        
def gen_n_points(val_range, num_points):
    lst = [(val, 1) for val in range(1, val_range + 1)]
    factor = val_range / float(num_points + 1)
    indexes = [int(factor * multiplier) for multiplier in range(1, num_points + 1)]
    print indexes
    while True:
        yield lst
        #for index in range(step-1, val_range, step)[:num_points]:
        for index in indexes:
            val, freq = lst[index]
            lst[index] = (val, freq + 1)
            
        

def timetrial(t_list, num_adds):
    '''a very lazily written timetrial for add_dice'''
    t_list.sort()
    lst = []
    for val, freq in t_list:
        lst = lst + [val] * freq
    print 'list', lst, '\ntuples', t_list, '\n'
    number_of_vals = len(t_list)
    number_of_freq = len(lst)
    print 'freqs to vals is %s' % (number_of_freq/float(number_of_vals))
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
        
def int_time():
    x = 123456789*10**400
    y = 123456*10**3
    start = time.clock()
    for _ in range(999):
        x *= y
    #print x
    print time.clock() - start
    
def dec_time():
    x = dec.Decimal(123456789*10**400)
    y = dec.Decimal(123456*10**3)
    start = time.clock()
    for _ in range(999):
        x *=y
    #print x
    print time.clock() - start