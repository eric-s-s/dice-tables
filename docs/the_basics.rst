Getting Started
===============

This module has no dependencies and no requirements. So to get started, simply:

.. code-block:: bash

    $ pip install dicetables

or:

.. code-block:: bash

    $ git clone https://github.com/eric-s-s/dice-tables.git
    $ cd dice-tables
    $ python setup.py install

The basic objects to use are DiceTable or DetailedDiceTable, and any of the dice classes.  They are:

- Die
- ModDie
- WeightedDie
- ModWeightedDie
- Modifier
- StrongDie
- Exploding
- ExplodingOn
- BestOfDicePool
- WorstOfDicePool
- UpperMidOfDicePool
- LowerMidOfDicePool

for details about the dice, see :doc:`the_dice`.
for details about the dice-tables see :doc:`the_dicetable`.

These are all immutable objects. When you add dice to a DiceTable, it returns a new object and
doesn't alter the original. Use the :code:`DiceTable.new()` class method to create an empty DiceTable.

>>> import dicetables as dt
>>> empty = dt.DiceTable.new()
>>> empty
<DiceTable containing []>
>>> empty.add_die(dt.Die(6), times=10)
<DiceTable containing [10D6]>
>>> empty
<DiceTable containing []>
>>> table = empty.add_die(dt.Die(4), times=3)
>>> table = table.add_die(dt.Die(10), times=5)
>>> table.get_list()
[(Die(4), 3), (Die(10), 5)]
>>> print(table.get_dict())  # This is each roll and how many times it occurs.
{8: 1,
 9: 8,
 10: 36,
 11: 120,
 12: 327,
 ...
 ...
 58: 327,
 59: 120,
 60: 36,
 61: 8,
 62: 1}

To get more detailed information, use :doc:`EventsCalculations <events_info>`.
It can get the mean, stddev, a nice string of the
combinations, points and axes for graphing, and stats for any set of rolls. (and a few others)

>>> calculator = dt.EventsCalculations(table)
>>> calculator.mean()
35.0
>>> calculator.stddev(decimal_place=8)
6.70820393
>>> calculator.stats_strings(list(range(8, 20)) + [35] + list(range(50, 63)))
StatsStrings(query_values='8-19, 35, 50-62',
             query_occurrences='515,778',
             total_occurrences='6,400,000',
             one_in_chance='12.41',
             pct_chance='8.059')
>>> calculator.percentage_points()
[(8, 1.5624999999999997e-05),
 (9, 0.00012499999999999998),
 (10, 0.0005625),
 ...
 (59, 0.001875),
 (60, 0.0005625),
 (61, 0.00012499999999999998),
 (62, 1.5624999999999997e-05)]
>>> big_table = dt.DetailedDiceTable.new().add_die(dt.Die(6), 1000)
>>> print(big_table.calc.full_table_string())  # DetailedDiceTable owns an EventsCalculations
1000: 1
1001: 1,000
1002: 500,500
1003: 1.672e+8
1004: 4.192e+10
1005: 8.417e+12
...
3513: 1.016e+776
3514: 1.012e+776
3515: 1.007e+776
3516: 1.001e+776
3517: 9.957e+775
3518: 9.898e+775
...
5998: 500,500
5999: 1,000
6000: 1
>>> big_table.calc.stats_strings(list(range(1000, 1501)))
StatsStrings(query_values='1,000-1,500',
             query_occurrences='2.439e+412',
             total_occurrences='1.417e+778',
             one_in_chance='5.809e+365',
             pct_chance='1.722e-364')

You can roll events with a :doc:`roller`

>>> events = dt.DiceTable.new().add_die(dt.Die(6))
>>> roller = dt.Roller(events)
>>> roller.roll() in [1, 2, 3, 4, 5, 6]
True
