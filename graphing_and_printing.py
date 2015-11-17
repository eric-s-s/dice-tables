from dice_class import *
import pylab           

#helper function. used everywhere to make numbers look purty.           
def scinote(num):
    '''checks a positive int or float.  outputs a string of the number.
    float(string) will give you the number.
    if number lower than scinonote_cutoff, no change.
    if number already in scientific notation, just prints first 4 digits
    else prints first four digits in scientific notation.'''
    scinote_cutoff = 10**6
    if num < scinote_cutoff:
        return str(num)
    elif 'e' in str(num):
        left,right = str(num).split('e')
        return left[0:5]+'e'+right
    else:
        string = str(int(num))
        power = str(len(string)-1)
        digits = string[0]+'.'+string[1:4]
        return digits+'e+'+power

#helper function for truncate_grapher() and stats()
def list_to_string(lst):
    '''outputs a list of intergers as a nice string.
    [1,2,3,7,9,10] becomes "1-3, 7, 9-10"
    [1,1,2,2,3] becomes "1-3"'''
    lst.sort()
    start_index = 0
    tuple_list = []
    for index in range(len(lst)-1):
        if lst[index+1]-lst[index] > 1:
            tuple_list.append((lst[start_index], lst[index]))
            start_index = index+1
    tuple_list.append((lst[start_index], lst[-1]))
    out_list = []
    for pair in tuple_list:
        if pair[0] == pair[1]:
            out_list.append(str(pair[0]))
        else:
            out_list.append(str(pair[0])+'-'+str(pair[1]))
    return ', '.join(out_list)     

#helper function. currently used in print_table(), grapher() 
#and truncate_grapher()       
def justify_right(roll, max_roll):
    '''takes a roll, and the largest roll from a DiceTable.
    outputs a string of the roll with enough added spaces so that
    "roll:" and "max_roll:" will be the same number of characters.'''
    max_len = len(str(max_roll))
    out_roll = str(roll)
    spaces = (max_len - len(out_roll))*' '
    return spaces + out_roll

#helper function.  currently only used in stats()    
def more_sig_figs(numerator, denominator):
    MAX_POWER = 6
    '''two ints.  returns a float of numerator/denominator. it's a way to 
    divide two really big ints and get a useful float. '''
    if numerator*10**MAX_POWER < denominator:
        return 0.0
    if numerator/denominator > 10**MAX_POWER:
        return numerator/denominator
    else:
        power = len(str(numerator)) - MAX_POWER - 1
        factor = 10**power
        new_numerator = float(numerator/factor)
        new_denominator = float(denominator/factor)
        return round(new_numerator/new_denominator, MAX_POWER-1)    

#helper function that's really only useful for grapher and truncate_grapher                        
def graph_list(table):
    '''makes a list of tuples.  (roll-int, grapher output for roll-str).
    it's a helper function for grapher and truncate_grapher'''
    graph_list = []
    
    max_frequency = table.roll_frequency_highest()[1]
    max_roll = table.roll_range_top()
    MAX_GRAPH_HEIGHT = 80.0
                  
    divisor = 1
    divstring = '1'
    #this sets the divisor so that max height of graph is MAX_GRAPH_HEIGHT x's
    if max_frequency > MAX_GRAPH_HEIGHT:
        divisor = max_frequency/table.int_or_float(MAX_GRAPH_HEIGHT)
        divstring = scinote(divisor)    
        
    for roll, frequency in table.roll_frequency_all():
        num_of_xs = int(round(frequency/divisor))
        graph_list.append((roll, 
                         justify_right(roll, max_roll) +':'+num_of_xs*'x'))
        
    graph_list.append((None, 'each x represents '+divstring+' occurences'))      
    return graph_list

def print_table(table):
    '''input - DiceTable.  Prints all the rolls and their frequencies.'''
    max_roll = table.roll_range_top()
    for roll, frequency in table.roll_frequency_all():
        print justify_right(roll, max_roll) +':'+scinote(frequency)
    
def grapher(table):
    '''input = DiceTable. output = a graph of x's'''
    for output in graph_list(table):
        print output[1]
    print table
    
def truncate_grapher(table):
    '''input = DiceTable. output = a graph of x's 
    but doesn't print zero-x rolls'''
    excluded = []
    for output in graph_list(table):
        if 'x' in output[1]:
            print output[1]
        else:
            excluded.append(output[0])
    if excluded !=[]:
        print 'not included: '+list_to_string(excluded).replace(',',' and')
    print table
        
def fancy_grapher(table,figure = 1,style = 'bo'):
    '''makes a pylab plot of a DiceTable. 
    You can set other figures and styles'''
    x_axis = []
    y_axis =[]
    factor = 1
    
    pylab.figure(figure)
    pylab.ylabel('number of combinations')
    #A work-around for the limitations of pylab.
    #It can't handle really fucking big ints and can't use my workarounds
    if type(table.int_or_float(1.)) is int:
        power = len(str(table.roll_frequency_highest()[1])) - 5
        factor = 10**power
        pylab.ylabel('number of combinations times 10^'+str(power)) 
    
    for roll, frequency in table.roll_frequency_all():
        x_axis.append(roll)
        y_axis.append(frequency/factor)
    
    pylab.xlabel('roll value')
    pylab.title('all the combinations for '+str(table))
    pylab.plot(x_axis,y_axis,style)
    pylab.draw()                

#TODO: delete
#for eval purposes
def highest(table):
    return scinote(table.roll_frequency_highest()[1])
       

         
def stats(table, rolls):
        '''returns the stats from a DiceTable for the rolls(a list)'''
        ints_only = False
        if type(table.int_or_float(1.)) is int:
            ints_only = True
        
        all_combos = table.total_combinations()
        total_frequency = 0
        for roll in rolls:
            total_frequency += table.roll_frequency(roll)[1]
        if total_frequency == 0:
            print 'no results'
            return None
        if ints_only:
            chance = more_sig_figs(all_combos,total_frequency)
            pct = 100*more_sig_figs(total_frequency,all_combos)
        else:
            chance = round(float(all_combos)/total_frequency, 5)
            pct =  round(float(total_frequency*100)/all_combos, 3)
        
        total_frequency_str = scinote(total_frequency)
        chance_str = scinote(chance)
        all_combos_str = scinote(all_combos)
        rolls_str = list_to_string(rolls)
        print
        print (rolls_str+' occurred '+total_frequency_str+
                ' times out of a total of '+all_combos_str+
                ' possible combinations')
        print 'if you roll '+str(table)+','
        print ('the chance of '+rolls_str+' is 1 in '+
                chance_str+' or '+str(pct)+' percent')
        print    





