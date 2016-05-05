############
dicetablesv2
############
=====================================================
a module for statistics of die rolls and other events
=====================================================
this module uses DiceTable and LongIntTable to do actions on a  
table of (event represented by an int, frequency that event occurs)  
since dice combinations quickly balloon, it's been designed to do float  
math with ints over 10^309.

DiceTable is a LongIntTable that keeps a list of all the Die objects
that have been added and removed using the add_die and remove_die methods.

::

    In [1]: import dicetables as dt

    In [2]: table = dt.DiceTable()

    In [3]: table.add_die(3, dt.Die(2))


I have now created a table contains all the rolls and their combinations  
for three two-sided dice.  useful for quick demo.

values functions tell the range of rolls or other non-zero events stored in the table.::  

    In [4]: table.values()
    Out[4]: [3, 4, 5, 6]

    In [5]: table.values_range()
    Out[5]: (3, 6)

here are all the possible rolls and the frequencies with which they occur.  
3 has one possible combination (1,1,1) and 4 has 3 [(1,1,2), (1,2,1), (2,1,1)]::

    In [7]: table.frequency_all()
    Out[7]: [(3, 1), (4, 3), (5, 3), (6, 1)]

the frequency_range function follows range's (start, stop_before) and list zero
for any roll that won't happen. ::

    In [8]: table.frequency(5)
    Out[8]: (5, 3)

    In [10]: table.frequency_range(1, 5)
    Out[10]: [(1, 0), (2, 0), (3, 1), (4, 3)]

other usefull methods. frequency_highest picks one of the values with highest
frequency and returns the tuple of (value, frequency). ::

    In [11]: table.frequency_highest()
    Out[11]: (4, 3)

    In [12]: table.total_frequency()
    Out[12]: 8

    In [13]: table.mean()
    Out[13]: 4.5

    In [14]: table.stddev()
    Out[14]: 0.866

the above methods are all from base class LongIntTable. The following are specific methods to 
DiceTable. 
The add_die and remove_die method use Die objects. the other 3 kinds of Die are shown here.::

    In [27]: table.add_die(5, dt.ModDie(6, 3))

    In [28]: table.add_die(3, dt.WeightedDie({1:1, 2:2}))

    In [29]: table.add_die(2, dt.ModWeightedDie({1:1, 2:3}, -5))

    In [30]: print(table)
    3D2
    3D2  W:3
    2D2-10  W:4
    5D6+15

    In [31]: table.remove_die(3, dt.Die(2))

    In [32]: table.add_die(1000, dt.Die(4))

    In [34]: table.get_list()
    Out[34]: 
    [(WeightedDie({1: 1, 2: 2}), 3),
     (ModWeightedDie({1: 1, 2: 3}, -5), 2),
     (Die(4), 1000),
     (ModDie(6, 3), 5)]

    In [36]: print(table.weights_info())
    3D2  W:3
        a roll of 1 has a weight of 1
        a roll of 2 has a weight of 2

    2D2-10  W:4
        a roll of 1 has a weight of 1
        a roll of 2 has a weight of 3

    1000D4
        No weights

    5D6+15
        No weights

-------------------------------------------------------------------
non-method functions for graphing, printing and general readability
-------------------------------------------------------------------
::

    In [15]: big_table = dt.LongIntTable({1:10 ** 1000, 3: 4 * 10**1000})

    In [18]: table.get_list()
    Out[18]: [(Die(2), 3)]

    In [19]: dt.graph_pts(table)
    Out[19]: ([3, 4, 5, 6], [12.5, 37.5, 37.5, 12.5])

    In [20]: dt.graph_pts(big_table, axes=False)
    Out[20]: [(1, 20.0), (2, 0.0), (3, 80.0)]

graph pts returns roll\\percent chance for graphing functions. it defaults to returning percent but you can return the actual combinations::

    In [21]: dt.graph_pts(big_table, percent=False)
    Out[21]: 
    ([1, 2, 3],
     [10000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000L,
      0,
      40000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000L])

this is often too large for graphing functions which rely on float math, so graph_pts_overflow
divides everything by a factor and returns a string of that factor::

    In [22]: dt.graph_pts_overflow(big_table)
    Out[22]: (([1, 2, 3], [10000L, 0L, 40000L]), '1.0e+996')

full_table_string uses dt.scinote() to make a readable output of the table::

    In [23]: print(dt.full_table_string(big_table))
    1: 1.000e+1000
    2: 0.0
    3: 4.000e+1000

stats returns the odds of a list occuring in the table::

    In [24]: dt.stats(table, [2,3,4])
    Out[24]: ('2-4', '4', '8', '2.0', '50.0')

on the table of 3 2-sided dice, 2-4 occured 4 times out of 8 total combinations.  
that's a one in 2.0 chance or 50.0 percent

also of note is dt.scinote().  this functions takes any number and returns a
nice string for humans.::

    In [22]: dt.scinote(123**1234, dig_len=10)
    Out[22]: '8.768140821e+2578'

--------------------------
non-method math functions.
--------------------------

long_int_div, long_int_times, long_int_pow are wrapper functions for Decimal class.
they take floats or ints as arguments and return floats if possible, else ints.
they are for dealing with float math on the very large ints these tables generate.::

    In [25]: dt.long_int_div(10**1000, 57*10**1005)
    Out[25]: 1.7543859649122808e-07


==============
niggly details
==============
------------
dice classes
------------
all dice classes are children of ProtoDie.  they all require the same methods
as ProtoDie and use them for hash and comparison.  There are no setter methods
for dice.  they should be treated as immutable values.  if two dice are ==, 
their hash value will be ==.  so::

    In [2]: x = dt.Die(6)

    In [3]: y = dt.Die(6)

    In [4]: z = dt.ModDie(6, -1)

    In [5]: zz = dt.ModDie(6, 0)

    In [6]: x == y
    Out[6]: True

    In [7]: x == z
    Out[7]: False

    In [8]: x == zz
    Out[8]: False

    In [9]: x > z
    Out[9]: True

    In [10]: x > zz
    Out[10]: False

    In [11]: dic = {}

    In [12]: dic[x] = 1

    In [13]: dic[y] = 'abc'

    In [14]: dic[z] = 3

    In [15]: dic[zz] = 4

    In [16]: dic
    Out[16]: {ModDie(6, -1): 3, Die(6): 'abc', ModDie(6, 0): 4}

------------
LongIntTable
------------
LongIntTables are instantiated with a dictionary of {value: frequency it occurs}.
DiceTable instantiates as the identity table, {0:1}

LongIntTable has methods add() and remove() that take an argument of a tuple list.
so you could recreate a DiceTable if you had stored it's tuple list and dice like so.::

    In [40]: table = dt.DiceTable()

    In [41]: table.add_die(1000, dt.Die(4))

    In [42]: tuple_list = table.frequency_all()

    In [43]: new_table = dt.DiceTable()

    In [44]: new_table.add(1, tuple_list)

    In [45]: new_table.get_list()
    Out[45]: []

    In [46]: new_table.update_list(1200, dt.Die(4))

ooopsy! oh no! what to do??::

    In [47]: new_table.update_list(-200, dt.Die(4))

    In [48]: new_table.get_list()
    Out[48]: [(Die(4), 1000)]

    In [49]: new_table.get_list() == table.get_list()
    Out[49]: True

    In [50]: new_table.frequency_all() == table.frequency_all()
    Out[50]: True

 
    



