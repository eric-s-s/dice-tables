##########
dicetables
##########
=====================================================
a module for statistics of die rolls and other events
=====================================================
This module uses DiceTable and AdditiveEvents to combine
dice and other events that can be added together.

There are many changes from the previous version, and they will
be listed in "CHANGES" at the bottom of this README.

DiceTable is a list of (event, occurrences) that keeps track of all the
Die objects that have been added and removed using the add_die and remove_die methods.

----------
THE BASICS
----------

| Here's a quick bit of math.  if you combine a 2-sided die and a 3-sided die,
| you get the following combinations.
| (1,1) / (1, 2) (2, 1) / (2, 2), (1, 3) / (2, 3):

- roll - 2: 1 occurrence  (1 in 6 chance)
- roll - 3: 2 occurrences  (2 in 6 chance)
- roll - 4: 2 occurrences  (3 in 6 chance)
- roll - 5: 1 occurrence  (1 in 6 chance)

::

    In [1]: import dicetables as dt

    In [2]: table = dt.DiceTable()

    In [3]: table.add_die(1, dt.Die(2))

    In [4]: table.add_die(1, dt.Die(3))

    In [5]: table.all_events
    Out[5]: [(2, 1), (3, 2), (4, 2), (5, 1)]


Here are basic table functions::

    In [6]: table.add_die(100, dt.Die(2))

    In [7]: table.remove_die(99, dt.Die(2))

    In[17]: print(table)
    2D2
    1D3

    In [11]: table.all_events
    Out[11]: [(3, 1), (4, 3), (5, 4), (6, 3), (7, 1)]

    In [12]: table.event_keys
    Out[12]: [3, 4, 5, 6, 7]

    In [20]: table.total_occurrences
    Out[20]: 12

    In [13]: table.event_range
    Out[13]: (3, 7)

    In [14]: table.biggest_event
    Out[14]: (5, 4)

    In [15]: table.get_event(6)
    Out[15]: (6, 3)

    In [16]: table.get_range_of_events(0, 5)
    Out[16]: [(0, 0), (1, 0), (2, 0), (3, 1), (4, 3)]

    In [18]: table.mean()
    Out[18]: 5.0

    In [19]: table.stddev()
    Out[19]: 1.0801

    In [20]: table.get_list()
    Out[20]: [(Die(2), 2), (Die(3), 1)]

    In [22]: table.number_of_dice(dt.Die(10))
    Out[22]: 0

    In [22]: table.number_of_dice(dt.Die(2))
    Out[22]: 2

    In [21]: print(table.weights_info())
    2D2
        No weights

    1D3
        No weights

Here are the useful non-method functions and objects::

    In [37]: print(dt.full_table_string(table))
    3: 1
    4: 3
    5: 4
    6: 3
    7: 1

    In[39]: stats_str = "{} occurred {} times out of {} combinations.\n \
                  That's a one in {} chance or {}%"

    In[39]: stats_info = dt.stats(table, [1,2,3,4])

    In[40]: print(stat_str.format(*stats_info))
    1-4 occurred 4 times out of 12 combinations.
    That's a one in 3.000 chance or 33.33%

    In [41]: dt.GraphDataGenerator().get_axes(table)
    Out[41]: [(3, 4, 5, 6, 7),
              (8.333333333333334, 25.0, 33.333333333333336, 25.0, 8.333333333333334)]

    In [42]: dt.GraphDataGenerator().get_points(table)
    Out[42]:
    [(3, 8.333333333333334),
     (4, 25.0),
     (5, 33.333333333333336),
     (6, 25.0),
     (7, 8.333333333333334)]

(or you may use the wrapper-function "graph_pts")
::

    In[43]: silly_table = dt.AdditiveEvents({1: 123456, 100: 12345*10**1000})

    In[47]: print(dt.full_table_string(silly_table, include_zeroes=False))
      1: 123,456
    100: 1.234e+1004

(If include_zeroes=True, you'd get also get 2: 0, 3: 0 ... 99: 0)
::

    In[49]: stats_info = dt.stats(silly_table, list(range(-5000, 5)))

    In[51]: print(stats_str.format(*stats_info))
    (-5,000)-4 occurred 123,456 times out of 1.234e+1004 combinations.
    That's a one in 1.000e+999 chance or 1.000e-997%


Finally, here are all the kinds of dice you can add

- dt.Die(6)
- dt.ModDie(6, -2)
- dt.WeightedDie({1:1, 2:5, 3:2})
- dt.ModWeightedDie({1:1, 2:5, 3:2}, 5)
- dt.StrongDie(dt.Die(6), 5)

----------------------
DETAILS OF DIE CLASSES
----------------------
All dice are subclasses of ProtoDie, which is a subclass of IntegerEvents.
They all require implementations of get_size(), get_weight(), weight_info(),
multiply_str(number), __str__(), __repr__() and get_dict() <-required for any IntegerEvents.

They are all immutable , hashable and rich-comparable so that multiple names can safely point
to the same instance of a Die, they can be used in sets and dictionary keys and they can be
sorted with any other kind of die. Comparisons are done by (size, weight, all_events, __repr__(as a last resort)).
So::

    In [54]: dice_list
    Out[54]:
    [ModDie(2, 0),
     WeightedDie({1: 1, 2: 1}),
     Die(2),
     ModWeightedDie({1: 1, 2: 1}, 0),
     StrongDie(Die(2), 1),
     StrongDie(WeightedDie({1: 1, 2: 1}), 1)]

    In [58]: [die.all_events == [(1, 1), (2, 1)] for die in dice_list]
    Out[58]: [True, True, True, True, True, True]

    In [56]: sorted(dice_list)
    Out[56]:
    [Die(2),
     ModDie(2, 0),
     StrongDie(Die(2), 1),
     ModWeightedDie({1: 1, 2: 1}, 0),
     StrongDie(WeightedDie({1: 1, 2: 1}), 1),
     WeightedDie({1: 1, 2: 1})]

    In [67]: [die == dt.Die(2) for die in sorted(dice_list)]
    Out[67]: [True, False, False, False, False, False]

    In [61]: my_set = {dt.Die(6)}

    In [62]: my_set.add(dt.Die(6))

    In [63]: my_set
    Out[63]: {Die(6)}

    In [64]: my_set.add(dt.ModDie(6, 0))

    In [65]: my_set
    Out[65]: {Die(6), ModDie(6, 0)}

The dice:

Die
    A basic die.  dt.Die(4) rolls 1, 2, 3, 4 with equal weight

    No added methods


ModDie
    A die with a modifier.  The modifier is added to each die roll.
    dt.ModDie(4, -2) rolls -1, 0, 1, 2 with equal weight.

    added methods:

    - .get_modifier()

WeightedDie
    A die that rolls different rolls with different frequencies.
    dt.WeightedDie({1:1, 3:3, 4:6}) is a 4-sided die.  It rolls 4
    six times as often as 1, rolls 3 three times as often as 1
    and never rolls 2

    added methods:

    - .get_raw_dict()

ModWeightedDie
    A die with a modifier that rolls different rolls with different frequencies.
    dt.ModWeightedDie({1:1, 3:3, 4:6}, 3) is a 4-sided die. 4 is added to all
    die rolls.  The same as WeightedDie.

    added methods:

    - .get_raw_dict()
    - .get_modifier()

StrongDie
    A die that is a strong version of any other die (including another StrongDie
    if you're feeling especially silly). So a StrongDie with a multiplier of 2
    would add 2 for each 1 that was rolled.

    dt.StrongDie(dt.Die(4), 5) is a 4-sided die that rolls 5, 10, 15, 20 with
    equal weight. dt.StrongDie(dt.Die(4), -1) is a 4 sided die that rolls -1, -2, -3, -4.

    added methods:

    - .get_multiplier()
    - .get_input_die()

-------------------------------------------
DETAILS OF AdditiveEvents AND IntegerEvents
-------------------------------------------
All tables and dice inherit from IntegerEvents.  All subclasses of IntegerEvents need the method
get_dict() which returns {event: occurrences, ...} for each NON-ZERO occurrence.  When you instantiate
any subclass, it checks to make sure you're get_dict() is legal.

AdditiveEvents is the parent of DiceTable.  You can add and remove events using the ".combine" method which tries
to pick the fastest combining algorithm. You can pick it yourself by calling ".combine_by_<algorithm>". You can
combine and remove DiceTable, AdditiveEvents, Die or any other IntegerEvents with the "combine" and "remove" methods,
but there's no record of it.  You can use this to copy a table::

    In [31]: first = dt.DiceTable()

    In [32]: first.add_die(20, dt.Die(6))

    In [33]: first.add_die(7, dt.Die(9))

    In [34]: second = dt.DiceTable()

    In [35]: second.combine(1, first)

    In [36]: second.get_dict() == first.get_dict()
    Out[36]: True

    In [37]: for die, number in first.get_list():
                second.update_list(number, die)

    In [38]: second.get_list() == first.get_list()
    Out[38]: True

--------------------------
HOW TO GET ERRORS AND BUGS
--------------------------
::

    In[3]: dt.Die(0)
    dicetables.baseevents.InvalidEventsError: events may not be empty. a good alternative is the identity - {0: 1}.

    In[5]: dt.AdditiveEvents({1.0: 2})
    dicetables.baseevents.InvalidEventsError: all values must be ints

    In[6]: dt.WeightedDie({1: 1, 2: -5})
    dicetables.baseevents.InvalidEventsError: no negative or zero occurrences in Events.get_dict()

but these are ok, because .get_dict() scrubs the zeroes::

    In [9]: dt.AdditiveEvents({1: 1, 2: 0}).get_dict()
    Out[9]: {1: 1}

    In [11]: weird = dt.WeightedDie({1: 1, 2: 0})

    In [12]: weird.get_dict()
    Out[12]: {1: 1}

    In[13]: weird.get_size()
    Out[13]: 2

    In[14]: weird.__repr__()
    Out[14]: 'WeightedDie({1: 1, 2: 0})'

Special rule for WeightedDie and ModWeightedDie::

    In[15]: dt.WeightedDie({0: 1})
    ValueError: rolls may not be less than 1. use ModWeightedDie

    In[16]: dt.ModWeightedDie({0: 1}, 1)
    ValueError: rolls may not be less than 1. use ModWeightedDie

Here's how to add 0 one time (which does nothing, btw)::

    In[18]: dt.ModWeightedDie({1: 1}, -1).get_dict()
    Out[18]: {0: 1}

StrongDie also has a weird case that can be unpredictable.  Basically, don't multiply by zero::

    In[43]: table = dt.DiceTable()

    In[44]: table.add_die(1, dt.Die(6))

    In[45]: table.add_die(100, dt.StrongDie(dt.Die(100), 0))

    In[46]: table.get_dict()

    Out[46]: {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1}

    In[47]: print(table)
    1D6
    (100D100)X(0)

    In[48]: table.add_die(2, dt.StrongDie(dt.ModWeightedDie({1: 2, 3: 4}, -1), 0)) <- this rolls zero with weight 4

    In[49]: print(table)
    (2D3-2  W:6)X(0)
    1D6
    (100D100)X(0)

    In[50]: table.get_dict()
    Out[50]: {1: 16, 2: 16, 3: 16, 4: 16, 5: 16, 6: 16} <- this is correct, it's just stupid.



"remove_die" and "add_die" are safe. They raise an error if you
remove too many dice or add or remove a negative number.
If you remove or combine with a negative number, nothing should happen.
If you use "remove" to remove what you haven't added,
it may or may not raise an error, but it's guaranteed buggy::

    In [19]: table = dt.DiceTable()

    In [20]: table.add_die(1, dt.Die(6))

    In [21]: table.remove_die(4, dt.Die(6))
    ValueError: dice not in table, or removed too many dice

    In [22]: table.remove_die(1, dt.Die(10))
    ValueError: dice not in table, or removed too many dice

    In [6]: table.add_die(-3, dt.Die(6))
    ValueError: number must be int >= 0

    In [6]: table.remove_die(-3, dt.Die(6))
    ValueError: number must be int >= 0

    In [10]: table.get_dict()
    Out[10]: {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1}

    In[31]: table.remove(10, dt.Die(2))
    ValueError: min() arg is an empty sequence <-not bad

    In[32]: table.remove(2, dt.Die(2))

    In[33]: table.get_dict()
    Out[33]: {-1: 1, 1: 1} <-ok bad.  garbage

    In[34]: table.remove(1, dt.AdditiveEvents({-5: 100}))

    In[35]: table.get_dict()
    Out[35]: {} <- very bad.

Calling combine_by_flattened_list can be risky::

    In[36]: x = dt.AdditiveEvents({1:1, 2: 5})

    In[37]: x.combine_by_flattened_list(5, dt.AdditiveEvents({1: 2, 3: 4}))

    In[39]: x.combine_by_flattened_list(5, dt.AdditiveEvents({1: 2, 3: 4*10**10}))
    MemoryError

    In[42]: x.combine_by_flattened_list(1, dt.AdditiveEvents({1: 2, 3: 4*10**700}))
    OverflowError: cannot fit 'int' into an index-sized integer

Combining events with themselves is safe::

    In[51]: x = dt.AdditiveEvents({1: 1, 2: 1})

    In[52]: x.combine(1, x)

    In[53]: x.get_dict()
    Out[53]: {2: 1, 3: 2, 4: 1}

    In[54]: x.combine(1, x)

    In[55]: x.get_dict()
    Out[55]: {4: 1, 5: 4, 6: 6, 7: 4, 8: 1}

=======
CHANGES
=======
The base class of DiceTable is now called AdditiveEvents and not LongIntTable.  the module longintmath.py
is renamed baseevents.py. If any IntegerEvents events is instantiated in a way that would cause bugs,
it raises an error; the same is true for any dice.

AdditiveEvents.combine take any IntegerEvents as an argument whereas LongIntTable.add took a list of tuples as
an argument.

Any subclass of ProtoDie no longer has the .tuple_list() method.  It has been replaced by the .get_dict() method
which returns a dictionary and not a list of tuples.

scinote and graph_pts were re-written as objects: NumberFormatter and GraphDataGenerator.
Two functions, format_number and graph_pts, are wrapper functions for these objects.

For output: The string for StrongDie now puts parentheses around the multiplier. stats() now shows tiny percentages.
Any exponent between 10 and -10 has that extraneous zero removed: '1.2e+05' is now '1.2e+5'.

Several AdditiveEvents class methods were changed to properties.
Here are all the original methods and their changes. You should be able to copy and paste this.

CONVERSIONS = {

    | 'LongIntTable.add()': 'AdditiveEvents.combine()',
    | 'LongIntTable.frequency()': 'AdditiveEvents.get_event()',
    | 'LongIntTable.frequency_all()': 'AdditiveEvents.all_events',
    | 'LongIntTable.frequency_highest()': 'AdditiveEvents.biggest_event',
    | 'LongIntTable.frequency_range()': 'AdditiveEvents.get_range_of_events()',
    | 'LongIntTable.mean()': 'AdditiveEvents.mean()',
    | 'LongIntTable.merge()': 'GONE',
    | 'LongIntTable.remove()': 'AdditiveEvents.remove()',
    | 'LongIntTable.stddev()': 'AdditiveEvents.stddev()',
    | 'LongIntTable.total_frequency()': 'AdditiveEvents.total_occurrences',
    | 'LongIntTable.update_frequency()': 'GONE',
    | 'LongIntTable.update_value_add()': 'GONE',
    | 'LongIntTable.update_value_ow()': 'GONE',
    | 'LongIntTable.values()': 'AdditiveEvents.event_keys',
    | 'LongIntTable.values_max()': 'AdditiveEvents.event_range[0]',
    | 'LongIntTable.values_min()': 'AdditiveEvents.event_range[1]',
    | 'LongIntTable.values_range()': 'AdditiveEvents.event_range',
    | 'ProtoDie.tuple_list()': 'sorted(ProtoDie.get_dict().items())',
    | 'scinote()': ('format_number()', 'NumberFormatter.format()'),
    | }


