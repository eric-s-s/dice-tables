#main module to run things is UI2.py

##UI2.py requirements
python 2.something. probably 2.7

libraries - pylab, decimal.  pylab should be set to an interactive backend

###how to use UI2.py
if started as main, runs main_menu().  or in an interperter, type main_menu()

##details of base modules and classes.

###longintmath.py 
3 wrapper functions for performing float math on large numbers and the LongIntTable class.
####LongIntTable class - a table for keeping track of large numbers of values and their frequencies.
a table for statistical events that can be expressed as intergers and added to each other.
for instance - {0:1, 1:1} representing 1 head and 1 tail.  adding a flip [(0, 1), (1, 1)] 
makes {0:1, 1:2, 2:1} TT = 1/4, HT = 2/4, HH = 1/4.
main methods are add, remove, mean, stddev and information retrieval functions

###dicestats.py
####Die classes - Die, ModDie(Die), WeightedDie, ModWeightedDie(WeightedDie)
two classes for making diffrenent kinds of dice representations.  these are classes for providing
string methods and tuple lists of each die.  a mod die is the base class with a +/- mod.

####DiceTable class.
a LongIntTable that has a list of dice to keep track of dice added and removed from the table.

###graphing_and_printing.py
####functions for displaying info of DiceTable and LongIntTable class	

grapher(x), truncate_grapher(x), fancy_grapher(x), fancy_grapher_pct(x) all print a graph.

**note**
fancy_graphers need to import pylab 

print_table(x) prints out the table

stats(x, list_of_rolls) gives you the stats on a list of rolls



