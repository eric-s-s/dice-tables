.. image:: https://travis-ci.org/eric-s-s/dice-tables.svg?branch=master
    :target: https://travis-ci.org/eric-s-s/dice-tables

.. image:: https://coveralls.io/repos/github/eric-s-s/dice-tables/badge.svg?branch=master
    :target: https://coveralls.io/github/eric-s-s/dice-tables?branch=master



#################
dicetables v4.0.1
#################

Calculate the Combinations For Any Set of Dice
==============================================

Have you ever wondered what the chances were for killing that 25 hp creature
with your lvl-5 fireball? Of course you have(it's 3.24%. Good luck with that).
What about if you could use your loaded dice that roll 6 twice as often.
We've got you covered (still only a 10% chance). Want to make sure
you'll win a bet on a number spread for DND dice randomly grabbed from a bag?
No problem("i'll bet you can't roll 150-200 on 7D4, 4D8, 5D12 and 4D20" ...
because it's a 0.3% chance). Ever wondered what would happen if you flipped a
coin a thousand times? (Your chance of flipping heads more than 600 times
is 0.000000009%.)

Impress your friends. Wow the gender of your choice -
with .... DICETABLES!!!

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

for details about the dice, see `The Dice`_.
for details about the dice-tables see
`DiceTable and DetailedDiceTable <http://dice-tables.readthedocs.io/en/latest/the_dicetable.html>`_

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
 55: 3072,
 56: 1608,
 57: 768,
 58: 327,
 59: 120,
 60: 36,
 61: 8,
 62: 1}

To get more detailed information, use
`EventsCalculations <http://dice-tables.readthedocs.io/en/latest/events_info.html>`_.
It can get the mean, stddev, a nice string of the
combinations, points and axes for graphing, and stats for any set of rolls.

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

You can now roll events with a `Roller`

>>> events = dt.DiceTable.new().add_die(dt.Die(6))
>>> roller = dt.Roller(events)
>>> roller.roll() in [1, 2, 3, 4, 5, 6]
True

That should get you started. For details see
`<http://dice-tables.readthedocs.io/en/latest/>`_

and the github repository at `<https://github.com/eric-s-s/dice-tables>`_

---------
ChangeLog
---------

v4.0.2
------

fixed bug in Parser.  Before `Parser().parse_die("Die(1, 2, 3)")` returned `Die(1)`.  Now, it raises a ParserError.
`Parser().parse_die("ModDie(1, 2, modifier=3")` also raises `ParserError` as does not enough arguments.

v4.0.0
------

**Breaking change again!**

Revamped DicePools and the Parser.

Dice Pools
^^^^^^^^^^

BestOfDicePool, WorstOfDicePool, UpperMidOfDicePool and LowerMidOfDicePool are now ProtoDie
wrappers around a DicePool object.  :code:`DicePool(Die(6), 4)` is now a non-IntegerEvents
object. It is immutable and can get passed around to various DicePoolCollection objects which
are ProtoDie.  So now it is:

>>> import dicetables as dt
>>> pool = dt.DicePool(dt.Die(6), 4)
>>> best_of = dt.BestOfDicePool(pool=pool, select=3)
>>> worst_of = dt.BestOfDicePool(pool=pool, select=3)
>>> super_best_of = dt.BestOfDicePool(pool=pool, select=1)

Parser
^^^^^^

The parser now takes a LimitChecker object.  This defaults to a NoOpLimitChecker
which doesn't check limits and there's a class method to make a parser with a useful
limit checker that is the same as the old behavior.  You can pass in your own limit
checker provided that it inherits from
:code:`dicetables.tools.limit_checker.AbstractLimitChecker`.

>>> from dicetables import Parser, Die, LimitsError
>>> no_limit = Parser()
>>> Die(1000) == no_limit.parse_die("Die(1000)")
True
>>> limited = Parser.with_limits()
>>> limited.parse_die("Die(1000)")
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
LimitsError: Max die_size: 500

v3.0.0
------

Breaking change!  Python 2 is no longer supported

Type hints have been added!

v2.6.0
------

- added `Roller`

.. _`The Dice` : http://dice-tables.readthedocs.io/en/latest/the_dice.html

.. _`DicePool` : http://dice-tables.readthedocs.io/en/latest/the_dice.html#dice-pools


v2.5.0
------

- added `DicePool`_ die objects:
    - `BestOfDicePool`
    - `WorstOfDicePool`
    - `UpperMidOfDicePool`
    - `LowerMidOfDicePool`

- `Parser().add_die_size_limit_kwarg` and `Parser().add_explosions_limit_kwarg` are removed. Use
  `Parser().add_limits_kwarg`

from v2.4.0 to v2.4.4
---------------------

- fixed error where `parse_die_within_limits` failed when using default values for dice.
- `Parser` can parse strings with leading and trailing whitespaces.
- `parse_die_within_limits` now raises `LimitsError`
- added `max_power_for_commaed` option to `EventsCalculations.full_table_string`.
- added `max_power_for_commaed` and `min_power_for_fixed_pt` to `EventsCalculations.stats_strings`.

since v2.2.0
------------

- Improved ExplodingOn speed.
- Added `parse_die_within_limits` function to parser. Also added limit values. Changed getters to properties.

since v2.1.0
------------

- EventsCalculations added functions log10_points and log10_axes
- New dice: Exploding(other_die, explosions=2), ExplodingOn(other_die, explodes_on, explosions=2)
- see `The Dice`_. and
  `Events info <http://dice-tables.readthedocs.io/en/latest/events_info.html>`_ for details
- New object: `Parser <http://dice-tables.readthedocs.io/en/latest/implementation_details/parser.html>`_ -
  It converts strings to dice objects.
