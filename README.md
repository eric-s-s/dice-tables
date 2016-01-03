#contains two modules


##dice_class.py
###contains dice table class and its functions

the class object

makes a table of all possible outcomes for a a certain number of dice.
for instance 2d6 has 36 possibilities, with 6 combinations for "7" so rolling a 7 is 1 in 6
this class creates a table of all the dice rolls you can get with a set of dice and how many combinations for each roll.
it also records how many dice and what kind
to deal with overflow problems, it also records if floats are allowed.  when the numbers are too big, floats throw an error.


###class functions and init
x = DiceTable(dsize)

class init creates 0d(dsize) table, a dicesize and total dice of 0

x.add_a_die() = adds a die of dsize.     
x.add_many_dice(number) = adds number of dice.

x.stddev()    
x.mean()    
just what you think

x.int_or_float(num) outputs number as float (even if originally int) if allowed. -- for overflow control

x.roll_range()  (also roll_range_top and roll_range_bottom) gives range of rolls

x.roll_frequency(roll)  (also roll_frequency_range/all/highest) returns tuple or list of tuples of roll,frequency

x.dice_size() x.number_of_dice()  x.total_combinations()  all tell what and how many dice or dval^num_dice 

#graphing_and_printing.py
##5 main functions

grapher(x), turncate_grapher(x), fancy_grapher(x) all print a graph.

**note**
fancy_grapher needs to import pylab - you should have it with any python

print_table(x) prints out the table

stats(x, list_of_rolls) gives you the stats on a list of rolls



