#the program
makes a table of all possible outcomes for a a certain number of dice.
for instance 2d6 has 36 possibilities, with 6 combinations for "7" so rolling a 7 is 1 in 6

if you run the python module you'll get a pretty self explanatory set of menus

at this point, the only thing that should throw an error and terminate program, is if you enter an illegal dsize.  anything else, should bitch at you,repeat itself or just move on.

##useful commands in interpreter
diceTableYielder() will give you menus, it's what runs wehn the module loads

mycombos(dval,num dice) let's you construct a dice table of a specified size

mycombosDisplay(same, same) same as above, and displays graph,mean,stdev etc

getstat(dicetable)  let's you get stats about the chances of certain rolls


##dice table class

the class object

this class creates a dictionary of all the total dice rolls you can get with a set of dice and how many combinations.
it also records how many dice and what kind

ex: on 2d6,

'''
2 - 1 combo (1,1)
3 - 2 combos (1,2  2,1)
4 - 3 combos (1,3 3,1 2,2)

with 6^2 combos that tells your the chance of any die roll represented in a dictionary like so

{2:1, 3:2, 4:3}
''' 
##class functions and init
x = dicetable(dsize)

class init creates 0d(dsize) table, a dicesize and total dice of 0

x.get*Something*()  returns *something* value you wanted

####class functions
stddev()  and mean()   

grapher() and truncategrapher()  make a graph of x's, truncategrapher removes the 0 x's

**_addADie()_**  how the class generates values for tables.  this takes a table of 1d6 and makes it 2d6

x.printTable() - what it says

print(x) - returns (howmany)D(sizeofdice)





###for z to use python interperter IDLE and python commands
[here's a link to how to use IDLE on a mac](http://stackoverflow.com/questions/8792044/how-do-i-launch-idle-the-development-environment-for-python-on-mac-os-10-7)


i wasn't clear how familiar you were with python, (and i have zero idea how it compares to other stuff) so in an interperter, here's the syntax

x = dicetable(dsize)	or	x = mycombos(dsize,total dice)  (x is a dicetabel)

x.classfunction(variables)

nonclassfunction(x)
