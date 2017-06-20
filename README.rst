#################
dicetables v2.3.0
#################
---------
CHANGELOG
---------
since v2.1.0

- EventsCalculations added functions log10_points and log10_axes
- New dice: Exploding(other_die, explosions=2), ExplodingOn(other_die, explodes_on, explosions=2)
- see `Die Classes`_ and `EventsInformation And EventsCalculations`_ for details
- New object: `Parser`_ - It converts strings to Die objects.

=====================================================
a module for statistics of die rolls and other events
=====================================================


This module uses DiceTable and AdditiveEvents to combine
dice and other events that can be added together. It is used to
figure out the probability of events occurring.  For instance, if you
roll 100 six-sided dice, the chance of rolling any number between 100
and 300 is 0.15 percent while the chance of rolling only 350 is 2.3 percent.

contents:

- `THE BASICS`_
- `Die Classes`_
- `AdditiveEvents And IntegerEvents`_
- `DiceTable And DetailedDiceTable`_
- `EventsInformation And EventsCalculations`_
- `Inheritance`_
- `Parser`_
- `HOW TO GET ERRORS AND BUGS`_

.. _Top:

----------
THE BASICS
----------
| Here's a quick bit of math.  if you combine a 2-sided die and a 3-sided die,
| you get the following combinations.
| (1,1) / (1, 2) (2, 1) / (2, 2), (1, 3) / (2, 3):

- roll - 2: 1 occurrence  (1 in 6 chance)
- roll - 3: 2 occurrences  (2 in 6 chance)
- roll - 4: 2 occurrences  (2 in 6 chance)
- roll - 5: 1 occurrence  (1 in 6 chance)

>>> import dicetables as dt
>>> new = dt.DiceTable.new()
>>> one_two_sided = new.add_die(dt.Die(2), times=1)
>>> one_two_sided_one_three_sided = one_two_sided.add_die(dt.Die(3), 1)
>>> one_two_sided_one_three_sided.get_dict()
{2: 1, 3: 2, 4: 2, 5: 1}
>>> one_two_sided.get_dict()
{1: 1, 2: 1}
>>> new.get_dict()
{0: 1}

Here are basic table functions. note that times added defaults to one.
Also note that DiceTable is immutable. adding and removing dice creates a new table. The original table is intact.


>>> table = dt.DiceTable.new().add_die(dt.Die(2)).add_die(dt.Die(3))
>>> str(table)
'1D2\n1D3'
>>> table = table.add_die(dt.Die(2), 100)
>>> table = table.remove_die(dt.Die(2), 99)
>>> print(table)
2D2
1D3
>>> print(table.add_die(dt.Modifier(5), 2))
+5
+5
2D2
1D3
>>> table.get_list()  # list is sorted according to die
[(Die(2), 2), (Die(3), 1)]
>>> table.number_of_dice(dt.Die(10))
0
>>> table.number_of_dice(dt.Die(2))
2
>>> print(table.weights_info())
2D2
    No weights
<BLANKLINE>
1D3
    No weights

To get useful information, use EventsInformation object and EventsCalculations object

>>> table = dt.DiceTable.new()
>>> table = table.add_die(dt.StrongDie(dt.Die(2), 3), 2)
>>> table.get_dict() == {6: 1, 9: 2, 12: 1}
True
>>> info = dt.EventsInformation(table)
>>> info.all_events()
[(6, 1), (9, 2), (12, 1)]
>>> info.all_events_include_zeroes()
[(6, 1), (7, 0), (8, 0), (9, 2), (10, 0), (11, 0), (12, 1)]
>>> info.events_keys()
[6, 9, 12]
>>> info.events_range()
(6, 12)
>>> info.get_event(4)
(4, 0)
>>> info.get_range_of_events(7, 13)
[(7, 0), (8, 0), (9, 2), (10, 0), (11, 0), (12, 1)]
>>> info.biggest_event()
(9, 2)
>>> info.total_occurrences()
4
>>> calc = dt.EventsCalculations(table)
>>> calc.mean()
9.0
>>> calc.stddev()
2.1213
>>> calc.percentage_points()
[(6, 25.0), (7, 0.0), (8, 0.0), (9, 50.0), (10, 0.0), (11, 0.0), (12, 25.0)]
>>> print(calc.full_table_string())
 6: 1
 7: 0
 8: 0
 9: 2
10: 0
11: 0
12: 1
>>> without_zeroes = dt.EventsCalculations(table, include_zeroes=False)
>>> print(without_zeroes.full_table_string())
 6: 1
 9: 2
12: 1
<BLANKLINE>
>>> stats_str = "{} occurred {} times out of {} combinations.\nThat's a one in {} chance or {}%"
>>> print(stats_str.format(*without_zeroes.stats_strings([1, 2, 5, 8, 9, 10])))
1-2, 5, 8-10 occurred 2 times out of 4 combinations.
That's a one in 2.000 chance or 50.00%
>>> without_zeroes.percentage_axes()
[(6, 9, 12), (25.0, 50.0, 25.0)]

DetailedDiceTable keeps a copy of these objects at .info and .calc calc_includes_zeros defaults to True

>>> d_table = dt.DetailedDiceTable.new()
>>> d_table.info.events_range()
(0, 0)
>>> d_table.calc.mean()
0.0
>>> d_table = d_table.add_die(dt.Die(6), 100)
>>> d_table.info.events_range()
(100, 600)
>>> d_table.calc.mean()
350.0

You may also access this functionality with wrapper functions:

- events_range
- mean
- stddev
- stats
- full_table_string
- percentage_points
- percentage_axes

>>> silly_table = dt.AdditiveEvents({1: 123456, 100: 12345*10**1000})
>>> print(dt.full_table_string(silly_table, include_zeroes=False, shown_digits=6))
  1: 123,456
100: 1.23450e+1004
<BLANKLINE>
>>> stats_info = dt.stats(silly_table, list(range(-5000, 5)))
>>> print(stats_str.format(*stats_info))
(-5,000)-4 occurred 123,456 times out of 1.234e+1004 combinations.
That's a one in 1.000e+999 chance or 1.000e-997%

Finally, here are all the kinds of dice you can add

- dt.Die(6)
- dt.ModDie(6, -2)
- dt.WeightedDie({1:1, 2:5, 3:2})
- dt.ModWeightedDie({1:1, 2:5, 3:2}, 5)
- dt.StrongDie(dt.Die(6), 5)
- dt.Modifier(-6)
- dt.Exploding(dt.Die(6), explosions=4)
- dt.ExplodingOn(dt.Die(6), (1, 3, 6), explosions=2)

That's all of the basic implementation. The rest of this is details about base classes, details of the
die classes, details of dicetable classes, what causes errors and the changes from the previous version.

Top_

-----------
Die Classes
-----------
All dice are subclasses of dicetables.eventsbases.protodie.ProtoDie, which is a subclass of
dicetables.eventsbases.integerevents.IntegerEvents. They all require implementations of
get_size(), get_weight(), weight_info(), multiply_str(number), __str__(), __repr__() and
get_dict() (the final one is a requirement of all IntegerEvents).

They are all immutable , hashable and rich-comparable. Multiple names can safely point
to the same instance of a Die, they can be used in sets and dictionary keys and they can be
sorted with any other kind of die. Comparisons are done by (size, weight, get_dict, __repr__(as a last resort)).
So:

>>> dice_list = [
... dt.ModDie(2, 0),
... dt.WeightedDie({1: 1, 2: 1}),
... dt.Die(2),
... dt.ModWeightedDie({1: 1, 2: 1}, 0),
... dt.StrongDie(dt.Die(2), 1),
... dt.StrongDie(dt.WeightedDie({1: 1, 2: 1}), 1)
... ]
>>> [die.get_dict() == {1: 1, 2: 1} for die in dice_list]
[True, True, True, True, True, True]
>>> sorted(dice_list)
[Die(2),
 ModDie(2, 0),
 StrongDie(Die(2), 1),
 ModWeightedDie({1: 1, 2: 1}, 0),
 StrongDie(WeightedDie({1: 1, 2: 1}), 1),
 WeightedDie({1: 1, 2: 1})]
>>> [die == dt.Die(2) for die in sorted(dice_list)]
[True, False, False, False, False, False]
>>> my_set = {dt.Die(6)}
>>> my_set.add(dt.Die(6))
>>> my_set == {dt.Die(6)}
True
>>> my_set.add(dt.ModDie(6, 0))
>>> my_set == {dt.Die(6), dt.ModDie(6, 0)}
True

The dice:

Die
    A basic die.  dt.Die(4) rolls 1, 2, 3, 4 with equal weight

    No added methods


ModDie
    A die with a modifier.  The modifier is added to each die roll.
    dt.ModDie(4, -2) rolls -1, 0, 1, 2 with equal weight. It is 4-sided die
    with -2 added to each roll (D4-2)

    added methods:

    - .get_modifier(): returns the modifier applied to each roll

WeightedDie
    A die that rolls different rolls with different frequencies.
    dt.WeightedDie({1:1, 3:3, 4:6}) is a 4-sided die.  It rolls 4
    six times as often as 1, rolls 3 three times as often as 1
    and never rolls 2

    added methods:

    - .get_raw_dict(): returns all values in die.get_size() even if they are zero.
      in the above example, it will return {1: 1, 2: 0, 3: 3, 4: 4}

ModWeightedDie
    A die with a modifier that rolls different rolls with different frequencies.
    dt.ModWeightedDie({1:1, 3:3, 4:6}, 3) is a 4-sided die. 3 is added to all
    die rolls.  The same as WeightedDie.

    added methods:

    - .get_raw_dict()
    - .get_modifier()

StrongDie
    A die that is a strong version of any other die (including another StrongDie
    if you're feeling especially silly). So a StrongDie with a multiplier of 2
    would add 2 for each 1 that was rolled. StrongDie(Die(4), 2) rolls 2, 4, 6, and 8

    >>> die = dt.Die(4)
    >>> die.get_dict() == {1: 1, 2: 1, 3: 1, 4: 1}
    True
    >>> dt.StrongDie(die, 5).get_dict() == {5: 1, 10: 1, 15: 1, 20: 1}
    True
    >>> example = dt.StrongDie(die, -2)
    >>> example.get_dict() == {-2: 1, -4: 1, -6: 1, -8: 1}
    True
    >>> example.get_input_die() == die
    True
    >>> example.get_multiplier()
    -2

    added methods:

    - .get_multiplier()
    - .get_input_die()

Modifier
    A simple +/- modifier that adds to the total dice roll.

    Modifier(-3) is a one-sided die that always rolls a -3.  size=0, weight=0.

    >>> table = dt.DiceTable.new().add_die(dt.Die(4))
    >>> table.get_dict() == {1: 1, 2: 1, 3: 1, 4: 1}
    True
    >>> table = table.add_die(dt.Modifier(3))
    >>> print(table)
    +3
    1D4
    >>> table.get_dict() == {4: 1, 5: 1, 6: 1, 7: 1}
    True

    added methods:

    - .get_modifier(): returns the modifier value

Exploding
    An exploding die is a die that has a chance to roll again. Each time the highest number is rolled, you
    add that to the total and keep rolling. An exploding D6 rolls 1-5 as usual. When it rolls a 6, it re-rolls
    and adds that 6. If it rolls a 6 again, this continues, adding 12 to the result. Since this is an infinite
    but increasingly unlikely process, the "explosions" parameter sets the number of re-rolls allowed.

    The number of explosions defaults to 2. **WARNING:** setting the number of explosions too high can make
    instantiation VERY slow.

    Here are the rolls for an exploding D4 that can explode up to 3 times. It rolls 1-3 sixty-four
    times more often than 13-16.

    >>> roll_values = dt.Exploding(dt.Die(4), explosions=3).get_dict()
    >>> sorted(roll_values.items())
     [(1, 64), (2, 64), (3, 64),
      (5, 16), (6, 16), (7, 16),
      (9, 4), (10, 4), (11, 4),
      (13, 1), (14, 1), (15, 1), (16, 1)]

    Any modifiers and multipliers are applied to each re-roll. Exploding D6+1 explodes on a 7.
    On a "7" it rolls 7 + (D6 + 1). On a "14", it rolls 14 + (D6 + 1).

    Here are the rolls for an exploding D6+1 that can explode the default times.

    >>> roll_values = dt.Exploding(dt.ModDie(6, 1)).get_dict()
    >>> sorted(roll_values.items())
    [(2, 36), (3, 36), (4, 36), (5, 36), (6, 36),
     (9, 6), (10, 6), (11, 6), (12, 6), (13, 6),
     (16, 1), (17, 1), (18, 1), (19, 1), (20, 1), (21, 1)]


    added methods:

    - .get_input_die()
    - .get_explosions(): returns the number of re-rolls allowed

ExplodingOn
    This is the same as Exploding, except you also use a tuple of ints to state what values the die continues rolling on.
    dt.ExplodingOn(dt.Die(6), (1, 6), explosions=2) continues rolling and adding the die value when either 1 or 6
    is rolled.

    The number of explosions defaults to 2. **WARNING:** setting the number of explosions too high can make
    instantiation VERY slow.

    Here are the rolls for an exploding D6 that can explode the default times and explodes on 5 and 6.

    >>> roll_values = dt.ExplodingOn(dt.Die(6), (5, 6)).get_dict()
    >>> sorted(roll_values.items())
    [(1, 36), (2, 36), (3, 36), (4, 36),
     (6, 6), (7, 12), (8, 12), (9, 12), (10, 6),
     (11, 1), (12, 3), (13, 4), (14, 4), (15, 4), (16, 4), (17, 3), (18, 1)]

    added methods:

    - .get_input_die()
    - .get_explosions()
    - .get_explodes_on(): returns the tuple of roll values that the die can explode on

Top_

--------------------------------
AdditiveEvents And IntegerEvents
--------------------------------
All tables and dice inherit from dicetables.eventsbases.IntegerEvents.  All subclasses of IntegerEvents need the method
get_dict() which returns {event: occurrences, ...} for each NON-ZERO occurrence.  When you instantiate
any subclass, it checks to make sure you're get_dict() is legal.

Any child of IntegerEvents has access to __eq__ and __ne__ evaluated by type and then get_dict(). It can be compared
to any object and two events that are not the exact same class will be !=.

Any of the classes that take a dictionary of events as input scrub the zero
occurrences out of the dictionary for you.

>>> dt.DiceTable({1: 1, 2:0}, {}).get_dict()
{1: 1}
>>> dt.AdditiveEvents({1: 2, 3: 0, 4: 1}).get_dict()
{1: 2, 4: 1}
>>> dt.ModWeightedDie({1: 2, 3: 0, 4: 1}, -5).get_dict()
{-4: 2, -1: 1}

AdditiveEvents is the parent of DiceTable. It has the class method new() which returns the identity. This method is
inherited by its children. You can add and remove events using the ".combine" method which tries
to pick the fastest combining algorithm. You can pick it yourself by calling ".combine_by_<algorithm>". You can
combine and remove DiceTable, AdditiveEvents, Die or any other IntegerEvents with the "combine" and "remove" methods,
but there's no record of it.  AdditiveEvents has __eq__ method that tests type and get_dict(). This is inherited
from IntegerEvents.

>>> three_D2 = dt.AdditiveEvents.new().combine_by_dictionary(dt.Die(2), 3)
>>> also_three_D2 = dt.AdditiveEvents({3: 1, 4: 3, 5: 3, 6: 1})
>>> still_three_D2 = dt.AdditiveEvents.new().combine(dt.AdditiveEvents({1: 1, 2: 1}), 3)
>>> three_D2.get_dict() == also_three_D2.get_dict() == still_three_D2.get_dict()
True
>>> identity = three_D2.remove(dt.Die(2), 3)
>>> identity.get_dict() == dt.AdditiveEvents.new().get_dict() == {0: 1}
True
>>> identity == dt.AdditiveEvents.new()
True
>>> print(three_D2)
table from 3 to 6
>>> twenty_one_D2 = three_D2.combine_by_indexed_values(three_D2, 6)
>>> twenty_one_D2_five_D4 = twenty_one_D2.combine_by_flattened_list(dt.Die(4), 5)
>>> five_D4 = twenty_one_D2_five_D4.remove(dt.Die(2), 21)
>>> dt.DiceTable.new().add_die(dt.Die(4), 5).get_dict() == five_D4.get_dict()
True
>>> dt.DiceTable.new().add_die(dt.Die(4), 5) == five_D4  # will be False since DiceTable is not AdditiveEvents
False

Since DiceTable is the child of AdditiveEvents, it can do all this combining and removing, but it won't be recorded
in the dice record.

Top_

-------------------------------
DiceTable And DetailedDiceTable
-------------------------------
You can instantiate any DiceTable or DetailedDiceTable with any data you like.
This allows you to create a DiceTable from stored information or to copy.
Please note that the "dice_data" method is ambiguously named on purpose. It's
function is to get correct input to instantiate a new DiceTable, whatever that
happens to be. To get consistent output, use "get_list".  Equality testing is by type, get_dict(), dice_data()
(and calc_includes_zeroes for DetailedDiceTable).

>>> old = dt.DiceTable.new()
>>> old = old.add_die(dt.Die(6), 100)
>>> events_record = old.get_dict()
>>> dice_record = old.dice_data()
>>> new = dt.DiceTable(events_record, dice_record)
>>> print(new)
100D6
>>> record = dt.DiceRecord({dt.Die(6): 100})
>>> also_new = dt.DetailedDiceTable(new.get_dict(), record, calc_includes_zeroes=False)
>>> old.get_dict() == new.get_dict() == also_new.get_dict()
True
>>> old.get_list() == new.get_list() == also_new.get_list()
True
>>> old == new
True
>>> old == also_new  # False by type
False
>>> isinstance(also_new, dt.DiceTable)
True
>>> type(also_new) is dt.DiceTable
False

DetailedDiceTable.calc_includes_zeroes defaults to True. It is as follows.

>>> d_table = dt.DetailedDiceTable.new()
>>> d_table.calc_includes_zeroes
True
>>> d_table = d_table.add_die(dt.StrongDie(dt.Die(2), 2))
>>> print(d_table.calc.full_table_string())
2: 1
3: 0
4: 1
<BLANKLINE>

>>> d_table = d_table.switch_boolean()
>>> the_same = dt.DetailedDiceTable({2: 1, 4: 1}, d_table.dice_data(), False)
>>> d_table == the_same
True
>>> print(d_table.calc.full_table_string())
2: 1
4: 1
<BLANKLINE>
>>> d_table = d_table.add_die(dt.StrongDie(dt.Die(2), 2))
>>> print(d_table.calc.full_table_string())
4: 1
6: 2
8: 1
<BLANKLINE>

>>> d_table = d_table.switch_boolean()
>>> d_table == the_same
False
>>> print(d_table.calc.full_table_string())
4: 1
5: 0
6: 2
7: 0
8: 1
<BLANKLINE>

Top_

----------------------------------------
EventsInformation And EventsCalculations
----------------------------------------

The methods are

EventsInformation:

* all_events
* all_events_include_zeroes
* biggest_event
* biggest_events_all <- returns the list of all events that have biggest occurrence
* events_keys
* events_range
* get_event
* get_items <- returns dict.items(): a list in py2 and an iterator in py3.
* get_range_of_events
* total_occurrences

EventsCalculations:

* full_table_string
    * can set the number of shown_digits

* info
* mean
* percentage_axes
    * very fast but only good to 10 decimal places

* percentage_axes_exact
* percentage_points
    * very fast but only good to 10 decimal places

* log10_axes and log10_points
    * log10 of the combinations.
    * any occurrence of zero is default set to -100.0 but can be assigned any number.

* percentage_points_exact
* stats_strings
    * takes a list of events values you want information for
    * optional parameter is shown_digits
    * returns a namedtuple
        * string of those events
        * number of times those events occurred in the table
        * total number of occurrences of all events in the table
        * the inverse chance of those events occurring: a 1 in (number) chance
        * the percent chance of those events occurring: (number)% chance
* stddev
    * defaults to 4 decimal places, but can be increased or decreased

>>> table = dt.DiceTable.new().add_die(dt.Die(6), 1000)
>>> calc = dt.EventsCalculations(table)
>>> calc.stddev(7)
54.0061725
>>> calc.mean()
3500.0
>>> the_stats = calc.stats_strings([3500], shown_digits=6)
>>> the_stats
StatsStrings(query_values='3,500',
             query_occurrences='1.04628e+776',
             total_occurrences='1.41661e+778',
             one_in_chance='135.395',
             pct_chance='0.738580')

This is correct. Out of 5000 possible rolls, 3500 has a 0.7% chance of occurring.

>>> the_stats.one_in_chance
'135.395'
>>> calc.stats_strings(list(range(1000, 3001)) + list(range(4000, 10000)))
StatsStrings(query_values='1,000-3,000, 4,000-9,999',
             query_occurrences='2.183e+758',
             total_occurrences='1.417e+778',
             one_in_chance='6.490e+19',
             pct_chance='1.541e-18')

This is also correct. Rolls not in the middle 1000 collectively have a much smaller chance than the mean.

>>> silly_table = dt.AdditiveEvents({1: 123456, 100: 1234567*10**1000})
>>> silly_calc = dt.EventsCalculations(silly_table, include_zeroes=False)
>>> print(silly_calc.full_table_string(shown_digits=6))
  1: 123,456
100: 1.23457e+1006
<BLANKLINE>

EventsCalculations.include_zeroes is only settable at instantiation. It does
exactly what it says. EventCalculations owns an EventsInformation. So
instantiating EventsCalculations gets you
two for the price of one. It's accessed with the property
EventsCalculations.info .

>>> table = dt.DiceTable.new().add_die(dt.StrongDie(dt.Die(3), 2))
>>> calc = dt.EventsCalculations(table, True)
>>> print(calc.full_table_string())
2: 1
3: 0
4: 1
5: 0
6: 1
<BLANKLINE>
>>> calc = dt.EventsCalculations(table, False)
>>> print(calc.full_table_string())
2: 1
4: 1
6: 1
<BLANKLINE>
>>> calc.info.events_range()
(2, 6)

Top_

-----------
Inheritance
-----------
If you inherit from any child of AdditiveEvents and you do not load the new information
into EventsFactory, it will complain and give you instructions. The EventsFactory will try to create
your new class and if it fails, will return the closest related type

>>> class A(dt.DiceTable):
...     pass
...
>>> A.new()  # EventsFactory takes a stab at it, and guesses right. It returns the new class
<...A...>

But it also issues a warning::

    E:\work\dice_tables\dicetables\baseevents.py:74: EventsFactoryWarning:
    factory: <class 'dicetables.factory.eventsfactory.EventsFactory'>
    Warning code: CONSTRUCT
    Failed to find/add the following class to the EventsFactory -
    class: <class '__main__.A'>
    ..... blah blah blah.....

Here, it will fail create "B" class, and return its parent.

>>> class B(dt.DiceTable):
...     def __init__(self, name, number, events_dict, dice_data):
...         self.name = name
...         self.num = number
...         super(B, self).__init__(events_dict, dice_data)
...

>>> B.new()
<...DiceTable...>

and give you the following warning::

    E:\work\dice_tables\dicetables\baseevents.py:74: EventsFactoryWarning:
    factory: <class 'dicetables.factory.eventsfactory.EventsFactory'>
    Warning code: CONSTRUCT
    Failed to find/add the following class to the EventsFactory -
    class: <class '__main__.B'>
    ..... blah blah blah.....

| Now I will try again, but I will give the factory the info it needs.
| The factory knows how to get 'get_dict', 'dice_data'
| and 'calc_includes_zeroes'. If you need it to get anything else, you need tuples of
| (<getter name>, <default value>, 'property' or 'method')

>>> class B(dt.DiceTable):
...     factory_keys = ('name', 'get_num', 'get_dict', 'dice_data')
...     new_keys = (('name', '', 'property'), ('get_num', 0, 'method'))
...     def __init__(self, name, number, events_dict, dice_data):
...         self.name = name
...         self._num = number
...         super(B, self).__init__(events_dict, dice_data)
...     def get_num(self):
...         return self._num
...
>>> B.new()
<...B...>

>>> class C(dt.DiceTable):
...     factory_keys = ('get_dict', 'dice_data')
...     def fancy_add_die(self, die, times):
...         new = self.add_die(die, times)
...         return 'so fancy', new
...
>>> x = C.new().fancy_add_die(dt.Die(3), 2)
>>> x[1].get_dict()
{2: 1, 3: 2, 4: 3, 5: 2, 6: 1}
>>> x
('so fancy', <C...>)

Notice that C is returned and not DiceTable

The other way to do this is to directly add the class to the EventsFactory

>>> factory = dt.factory.eventsfactory.EventsFactory
>>> factory.add_getter('get_num', 0, 'method')
>>> class A(dt.DiceTable):
...     def __init__(self, number, events_dict, dice):
...         self._num = number
...         super(A, self).__init__(events_dict, dice)
...     def get_num(self):
...         return self._num
...
>>> factory.add_class(A, ('get_num', 'get_dict', 'dice_data'))
>>> A.new()
<A ...>

>>> factory.reset()
>>> factory.has_class(A)
False

When creating new methods, you can generate new events dictionaries by using
dicetables.additiveevents.EventsDictCreator.  the factory can create new instances with
EventsFactory.from_params.  For examples see the last few test in tests.factory.test_eventsfactory

Top_

------
Parser
------
The Parser object converts strings into dice objects.

>>> new_die = dt.Parser().parse_die('Die(6)')
>>> new_die == dt.Die(6)
True

It can ignore case or not. It defaults to ignore_case=False.

>>> dt.Parser().parse_die('die(6)')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ParseError: Die class: <die> not recognized by parser.

>>> dt.Parser(ignore_case=True).parse_die('stronGdie(dIE(6), 4)') == dt.StrongDie(dt.Die(6), 4)
True

The Parser can parse all dice in the library: Die, ModDie, WeightedDie, ModWeightedDie, Modifier, StrongDie,
Exploding and ExplodingOn. It is possible to add other dice to an instance of Parser or make a new class that
can parse other dice.

**HOW TO CUSTOMIZE PARSER**

Parser can only parse very specific types of parameters.

>>> from dicetables.parser import make_int, make_int_dict, make_int_tuple
>>> parser = dt.Parser()
>>> parser.get_param_types() == {'int': make_int, 'int_dict': make_int_dict,
...                              'die': parser.make_die, 'int_tuple': make_int_tuple}
True

If, for example, you need Parser to know how to parse a string, a list of strings and
dictionary of keys=str: values=int, you first need to create functions that can parse
the appropriate Nodes. Then you assign the functions to the parser.

    First, a very very quick introduction to the Abstract Syntax Tree:

    The nodes are derived using the "ast" module. ast, very briefly, takes a string and parses it into nodes. To see what
    it does, use :code:`ast.dump(ast.parse(<your_string>))`.  Create and test nodes by using
    :code:`my_node = ast.parse(<your_string>).body[0].value`

    >>> import ast
    >>> ast.dump(ast.parse('[1, -1, "A"]'))
    "Module(body=[Expr(value=List(elts=[Num(n=1), UnaryOp(op=USub(), operand=Num(n=1)), Str(s='A')], ctx=Load()))])"
    >>> my_list_node = ast.parse('[1, -1, "A"]').body[0].value
    >>> ast.dump(my_list_node)
    "List(elts=[Num(n=1), UnaryOp(op=USub(), operand=Num(n=1)), Str(s='A')], ctx=Load())"

    This says that the List node points to its elts:

    - a Num node: value=1
    - a unary-operation node that uses unary-subtraction on operand:Num node: value=1
    - a Str node: value='A'

Now, to my example.

>>> str_value =  ast.Str(s="abd")
>>> str_value.s
'abd'
>>> str_list = ast.List(elts=[ast.Str(s='a'), ast.Str(s='b'), ast.Str(s='c')])
>>> str_int_dict = ast.parse("{'a': 2, 'b': 10}").body[0].value

and here are conversion methods.

>>> from dicetables.parser import make_int
>>> def make_str(str_node):
...     return str_node.s
>>> make_str(str_value)
'abd'

>>> def make_str_list(lst_node):
...     return [make_str(node) for node in lst_node.elts]
>>> make_str_list(str_list)
['a', 'b', 'c']

>>> def make_str_int_dict(dict_node):
...     keys = [make_str(node) for node in dict_node.keys]
...     values = [make_int(node) for node in dict_node.values]
...     return dict(zip(keys, values))
>>> make_str_int_dict(str_int_dict) == {'a': 2, 'b': 10}
True

Now you tell the parser that a key of your choice corresponds to the method.

>>> parser = dt.Parser()
>>> parser.add_param_type('str', make_str)
>>> parser.add_param_type('str_list', make_str_list)
>>> parser.add_param_type('str_int_dict', make_str_int_dict)

To add a new dice class to the parser, give the parser the class and a tuple of the param_types keys for each parameter.

>>> class NamedDie(dt.Die):
...     def __init__(self, name, buddys_names, stats, size):
...         self.name = name
...         self.best_buds = buddys_names.copy()
...         self.stats = stats.copy()
...         super(NamedDie, self).__init__(size)
...
...     def __eq__(self, other):
...         return (super(NamedDie, self).__eq__(other) and
...                 self.name == other.name and
...                 self.best_buds == other.best_buds and
...                 self.stats == other.stats)

>>> parser.add_class(NamedDie, ('str', 'str_list', 'str_int_dict', 'int'))
>>> die_str = 'NamedDie("Tom", ["Dick", "Harry"], {"friends": 2, "coolness_factor": 10}, 4)'
>>> parser.parse_die(die_str) == NamedDie('Tom', ['Dick', 'Harry'], {'friends': 2, 'coolness_factor': 10}, 4)
True

You can make a new parser class instead of a specific instance of Parser.

>>> class MyParser(dt.Parser):
...     def __init__(self, ignore_case=False):
...         super(MyParser, self).__init__(ignore_case)
...         self.add_param_type('str', make_str)
...         self.add_param_type('str_list', make_str_list)
...         self.add_param_type('str_int_dict', make_str_int_dict)
...         self.add_class(NamedDie, ('str', 'str_list', 'str_int_dict', 'int'))

>>> die_str = 'NamedDie("Tom", ["Dick", "Harry"], {"friends": 2, "coolness_factor": 10}, 4)'
>>> MyParser().parse_die(die_str) == NamedDie('Tom', ['Dick', 'Harry'], {'friends': 2, 'coolness_factor': 10}, 4)
True
>>> upper_lower_who_cares = 'nAmeDdIE("Tom", ["Dick", "Harry"], {"friends": 2, "coolness_factor": 10}, 4)'
>>> t_d_and_h_4_eva = MyParser(ignore_case=True).parse_die(upper_lower_who_cares)
>>> t_d_and_h_4_eva == NamedDie('Tom', ['Dick', 'Harry'], {'friends': 2, 'coolness_factor': 10}, 4)
True

Top_

--------------------------
HOW TO GET ERRORS AND BUGS
--------------------------
Every time you instantiate any IntegerEvents, it is checked.  The get_dict() method returns a dict, and every value
in get_dict().values() must be >=1. get_dict() may not be empty.
since dt.Die(-2).get_dict() returns {}

>>> dt.Die(-2)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
InvalidEventsError: events may not be empty. a good alternative is the identity - {0: 1}.

>>> dt.AdditiveEvents({1.0: 2})
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
InvalidEventsError: all values must be ints

>>> dt.WeightedDie({1: 1, 2: -5})
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
InvalidEventsError: no negative or zero occurrences in Events.get_dict()

Because AdditiveEvents and WeightedDie specifically
scrub the zeroes from their get_dict() methods, these will not throw errors.

>>> dt.AdditiveEvents({1: 1, 2: 0}).get_dict()
{1: 1}

>>> weird = dt.WeightedDie({1: 1, 2: 0})
>>> weird.get_dict()
{1: 1}
>>> weird.get_size()
2
>>> weird.get_raw_dict() == {1: 1, 2: 0}
True

Special rule for WeightedDie and ModWeightedDie

>>> dt.WeightedDie({0: 1})
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ValueError: rolls may not be less than 1. use ModWeightedDie

>>> dt.ModWeightedDie({0: 1}, 1)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ValueError: rolls may not be less than 1. use ModWeightedDie

Here's how to add 0 one time (which does nothing, btw)

>>> dt.ModWeightedDie({1: 1}, -1).get_dict()
{0: 1}

StrongDie also has a weird case that can be unpredictable.  Basically, don't multiply by zero

>>> table = dt.DiceTable.new().add_die(dt.Die(6))

>>> table = table.add_die(dt.StrongDie(dt.Die(100), 0), 100)

>>> table.get_dict() == {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1}
True

>>> print(table)
1D6
(100D100)X(0)

>>> stupid_die = dt.StrongDie(dt.ModWeightedDie({1: 2, 3: 4}, -1), 0)
>>> table = table.add_die(stupid_die, 2)  # this rolls zero with weight 4
>>> print(table)
(2D3-2  W:6)X(0)
1D6
(100D100)X(0)
>>> table.get_dict() ==  {1: 16, 2: 16, 3: 16, 4: 16, 5: 16, 6: 16}  # this is correct, it's just stupid.
True

ExplodingOn will raise an error if the values in "explodes_on" are not in input_die.get_dict()

>>> input_die = dt.WeightedDie({1: 2, 3: 1, 5: 1, 7: 2})
>>> dt.ExplodingOn(input_die, ()).get_dict() == {1: 72, 3: 36, 5: 36, 7: 72}
True
>>> dt.ExplodingOn(input_die, (2,))
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ValueError: "explodes_on" value not present in input_die.get_dict()

"remove_die" and "add_die" are safe. They raise an error if you
remove too many dice or add or remove a negative number.

If you "remove" or "combine" with a negative number, nothing should happen,
but i make no guarantees.

If you use "remove" to remove what you haven't added,
it may or may not raise an error, but it's guaranteed buggy.

Here are "add_die" and "remove_die" failing fast:

>>> table = dt.DiceTable.new().add_die(dt.Die(6))

>>> table = table.remove_die(dt.Die(6), 4)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
DiceRecordError: Tried to create a DiceRecord with a negative value at Die(6): -3

>>> table = table.remove_die(dt.Die(10))
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
DiceRecordError: Tried to create a DiceRecord with a negative value at Die(10): -1

>>> table = table.add_die(dt.Die(6), -3)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
DiceRecordError: Tried to add_die or remove_die with a negative number.

>>> table = table.remove_die(dt.Die(6), -3)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
DiceRecordError: Tried to add_die or remove_die with a negative number.

And now, this is the trouble you can get into with "combine" and "remove"

>>> table.get_dict() == {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1}
True
>>> table = table.combine(dt.Die(10000), -100)
>>> table.get_dict() == {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1}
True
>>> table = table.remove(dt.Die(2), 10)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ValueError: min() arg is an empty sequence <-didn't know this would happen, but at least failed loudly

>>> table = table.remove(dt.Die(2), 2)

>>> table.get_dict() == {-1: 1, 1: 1}  # bad. this is a random answer
True

(I know why you're about to get wacky and inaccurate errors, and I could fix the bug, except ...
 YOU SHOULD NEVER EVER DO THIS!!!!)

>>> table = table.remove(dt.AdditiveEvents({-5: 100}))
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
EventsFactoryError: Error Code: SIGNATURES DIFFERENT
Factory:    <class 'dicetables.factory.eventsfactory.EventsFactory'>
Error At:   <class 'dicetables.dicetable.DiceTable'>
Attempted to construct a class already present in factory, but with a different signature.
Class: <class 'dicetables.dicetable.DiceTable'>
Signature In Factory: ('get_dict', 'dice_data')
To reset the factory to its base state, use EventsFactory.reset()


Since you can instantiate a DiceTable with any legal input,
you can make a table with utter nonsense. It will work horribly.
for instance, the dictionary for 2D6 is:

{2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6, 8: 5, 9: 4, 10: 3, 11: 2, 12: 1}


>>> nonsense = dt.DiceTable({1: 1}, dt.DiceRecord({dt.Die(6): 2}))  # <- BAD DATA!!!!
>>> print(nonsense)  # <- the dice record says it has 2D6, but the events dictionary is WRONG
2D6
>>> nonsense = nonsense.remove_die(dt.Die(6), 2)  # <- so here's your error. I hope you're happy.
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ValueError: min() arg is an empty sequence

But, you cannot instantiate a DiceTable with negative values for dice.
And you cannot instantiate a DiceTable with non-sense values for dice.


>>> dt.DiceTable({1: 1}, dt.DiceRecord({dt.Die(3): 3, dt.Die(5): -1}))
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
DiceRecordError: Tried to create a DiceRecord with a negative value at Die(5): -1

>>> dt.DiceTable({1: 1}, dt.DiceRecord({'a': 2.0}))
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
DiceRecordError: input must be {ProtoDie: int, ...}

Calling combine_by_flattened_list can be risky

>>> x = dt.AdditiveEvents({1:1, 2: 5})
>>> x = x.combine_by_flattened_list(dt.AdditiveEvents({1: 2, 3: 4}), 5)
>>> x = x.combine_by_flattened_list(dt.AdditiveEvents({1: 2, 3: 4*10**10}), 5)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
MemoryError

>>> x = x.combine_by_flattened_list(dt.AdditiveEvents({1: 2, 3: 4*10**700}))
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
OverflowError: cannot fit 'int' into an index-sized integer

Top_
