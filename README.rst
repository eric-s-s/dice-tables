##########
dicetables
##########
=====================================================
a module for statistics of die rolls and other events
=====================================================
this module uses DiceTable and LongIntTable to do actions on a  
table of (event represented by an int, frequency that event occurs)  
since dice combinations quickly balloon, it's been designed to do float  
math with ints over 10^309.::

    In [1]: import dicetables as dt
	
    In [2]: table = dt.DiceTable()
	
    In [3]: table.add_die(3, dt.Die(2))
	
have now created a table contains all the rolls and their combinations  
for three two-sided dice.  useful for quick demo.::

    In [4]: table.values()
    Out[4]: [3, 4, 5, 6]
	
    In [5]: table.values_range()
    Out[5]: (3, 6)

values functions tell the range of rolls or other non-zero events stored in the table.::  

    In [7]: table.frequency_all()
    Out[7]: [(3, 1), (4, 3), (5, 3), (6, 1)]

here are all the possible rolls and the frequencies with which they occur.  
3 has one possible combination (1,1,1) and 4 has 3 [(1,1,2), (1,2,1), (2,1,1)]::

    In [8]: table.frequency(5)
    Out[8]: (5, 3)

    In [10]: table.frequency_range(1, 5)
    Out[10]: [(1, 0), (2, 0), (3, 1), (4, 3)]

the range function follows range's (start, stop_before) and list zero for any roll that won't happen::

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
