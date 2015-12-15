import longintmath as lim
import dicestats as ds
import graphing_and_printing as gap
import time
import decimal as dec
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
    a = lim.LongIntTable({0:1})
    add_dices(a, num_adds, lst)
    print 'basic\n', time.clock()-start_a
    print a.mean(), a.stddev(), '\n'

    start_b = time.clock()
    b = lim.LongIntTable({0:1})
    add_weighted_dice(b, num_adds, t_list)
    print 'tuple list\n', time.clock()-start_b
    print b.mean(), b.stddev(), '\n'

    start_c = time.clock()
    c = lim.LongIntTable({0:1})
    c.add(num_adds, lst)
    print 'add funct list\n', time.clock()-start_c
    print c.mean(), c.stddev(), '\n'

    start_d = time.clock()
    d = lim.LongIntTable({0:1})
    d.add(num_adds, dic)
    print 'add funct dictionary\n', time.clock()-start_d
    print d.mean(), d.stddev(), '\n'

    start_e = time.clock()
    e = lim.LongIntTable({0:1})
    e.add(num_adds, t_list)
    print 'add funct tuple list\n', time.clock()-start_e
    print e.mean(), e.stddev(), '\n'

    start_f = time.clock()
    f = lim.LongIntTable({0:1})
    f.add(num_adds, lim.LongIntTable(dic))
    print 'add funct LIT\n', time.clock()-start_f
    print f.mean(), f.stddev(), '\n'
    return a, b, c, d, e, f




def tst_pow(num, exp_top,exp_bottom):
    start1 = time.clock()
    print 'LI %s' % (lim.long_int_pow(num, exp_top, exp_bottom))
    print time.clock() - start1
    start2 = time.clock()
    print 'reg %s' % (num**(float(exp_top)/exp_bottom))
    print time.clock() - start2
    
def tst_div(num, denom):
    tst = lim.LongIntTable({1: 10**1000})
    start1 = time.clock()
    lit = tst.divide(num, denom)
    time1 = time.clock() - start1
    start2 = time.clock()
    lid = lim.long_int_div(num, denom)
    time2 = time.clock() - start2
    pct = 100*(lid-lit)/lid
    if isinstance(lid, float):
        print lid
    print 'err %s\ntable  time %s\nl.i.d. time %s' % (pct, time1, time2)
    
def stddev_time(table):
    s = time.clock()
    ans = stddev_div(table) 
    print 'dec    ', ans, 'time' , time.clock()-s
    s = time.clock()
    ans = stddev_floor(table)
    print 'floor  ', ans, 'time' , time.clock()-s
    s = time.clock()
    ans = stddev_lid(table)
    print 'lid    ', ans, 'time' , time.clock()-s

def stddev_div(table):
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
        sqs += (lim.long_int_div(frequency, factor, (sig_figs + extra_digits))
                * (avg - value)**2)
        count += frequency
    new_count = lim.long_int_div(count, factor, (sig_figs + extra_digits))
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

def showit2(table, function):
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