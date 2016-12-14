###############
dicetables v2.0
###############
=====================================================
a module for statistics of die rolls and other events
=====================================================
CHANGED IN THIS VERSION: all children of AdditiveEvents are now immutable. See "CHANGES" for details

This module uses DiceTable and AdditiveEvents to combine
dice and other events that can be added together. It is used to
figure out the probability of events occurring.  For instance, if you
roll 100 six-sided dice, the chance of rolling any number between 100
and 300 is 0.15 percent.

contents:

- `THE BASICS`_
- `Die Classes`_
- `AdditiveEvents And IntegerEvents`_
- `DiceTable And RichDiceTable`_
- `EventsInformation And EventsCalculations`_
- `Inheritance`_
- `HOW TO GET ERRORS AND BUGS`_
- `CHANGES`_

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

::

    In [1]: import dicetables as dt

    In [2]: new = dt.DiceTable.new()

    In [3]: one_two_sided = new.add_die(1, dt.Die(2))

    In [4]: one_two_sided_one_three_sided = one_two_sided.add_die(1, dt.Die(3))

    In [5]: one_two_sided_one_three_sided.get_dict()
    Out[5]: {2: 1, 3: 2, 4: 2, 5: 1}

    In [6]: one_two_sided.get_dict()
    out[6]: {1: 1, 2: 1}

    In [7]: new.get_dict()
    out[7]: {0: 1}

Here are basic table functions::

    In [4]: table = dt.DiceTable.new().add_die(1, dt.Die(2)).add_die(1, dt.Die(3))

    In [5]: str(table)
    Out[5]: '1D2\n1D3'

    In [6]: table = table.add_die(100, dt.Die(2))

    In [7]: table = table.remove_die(99, dt.Die(2))

    In [17]: print(table)
    2D2
    1D3

    In [20]: table.get_list()
    Out[20]: [(Die(2), 2), (Die(3), 1)]  <-- sorted according to die

    In [22]: table.number_of_dice(dt.Die(10))
    Out[22]: 0

    In [22]: table.number_of_dice(dt.Die(2))
    Out[22]: 2

    In [21]: print(table.weights_info())
    2D2
        No weights

    1D3
        No weights

To get useful information, use EventsInformation object and EventsCalculations object::

    In [1]: table = dt.DiceTable.new()
    In [2]: table = table.add_die(2, dt.StrongDie(dt.Die(2), 3))

    In [3]: table.get_dict()
    Out[3]: {6: 1, 9: 2, 12: 1}

    In [4]: info = dt.EventsInformation(table)

    In [5]: info.all_events()
    Out[5]: [(6, 1), (9, 2), (12, 1)]


    In [6]: info.all_events_include_zeroes()
    Out[6]: [(6, 1), (7, 0), (8, 0), (9, 2), (10, 0), (11, 0), (12, 1)]

    In [7]: info.events_keys()
    Out[7]: [6, 9, 12]

    In [8]: info.events_range()
    Out[8]: (6, 12)

    In [9]: info.get_event(4)
    Out[9]: (4, 0)

    In [11]: info.get_range_of_events(7, 13)
    Out[11]: [(7, 0), (8, 0), (9, 2), (10, 0), (11, 0), (12, 1)]

    In [12]: info.biggest_event()
    Out[12]: (9, 2)

    In [13]: info.total_occurrences()
    Out[13]: 4

    In [14]: calc = dt.EventsCalculations(table)

    In [15]: calc.mean()
    Out[15]: 9.0

    In [16]: calc.stddev()
    Out[16]: 2.1213

    In [17]: calc.percentage_points()
    Out[17]: [(6, 25.0), (7, 0.0), (8, 0.0), (9, 50.0), (10, 0.0), (11, 0.0), (12, 25.0)]

    In [18]: print(calc.full_table_string())
     6: 1
     7: 0
     8: 0
     9: 2
    10: 0
    11: 0
    12: 1

    In [19]: without_zeroes = EventsCalculations(table, include_zeroes=False)

    In [20]: print(without_zeroes.full_table_string())
     6: 1
     9: 2
    12: 1

    In [21]: stats_str = "{} occurred {} times out of {} combinations.\nThat's a one in {} chance or {}%"

    In [22]: print(stats_str.format(*without_zeroes.stats_strings([1, 2, 5, 8, 9, 10])))
    1-2, 5, 8-10 occurred 2 times out of 4 combinations.
    That's a one in 2.000 chance or 50.00%

    In [23]: without_zeroes.percentage_axes()
    Out[23]: [(6, 9, 12), (25.0, 50.0, 25.0)]

Please note that these objects do not follow changes to the DiceTable. You can use
RichDiceTable which keeps a copy of these objects at .info and .calc::

    In [3]: table = dt.DiceTable.new()

    In [5]: info = dt.EventsInformation(table)

    In [6]: calc = dt.EventsCalculations(table)

    In [7]: info.events_range()
    Out[7]: (0, 0)

    In [8]: calc.mean()
    Out[8]: 0.0

    In [9]: table = table.add_die(100, dt.Die(6))

    In [10]: info.events_range()
    Out[10]: (0, 0)

    In [11]: calc.mean()
    Out[11]: 0.0

    In [20]: dt.EventsInformation(table).events_range()
    Out[20]: (100, 600)

    In [12]: r_table = dt.RichDiceTable.new()

    In [13]: r_table.info.events_range()
    Out[13]: (0, 0)

    In [14]: r_table.calc.mean()
    Out[14]: 0.0

    In [15]: r_table = r_table.add_die(100, dt.Die(6))

    In [16]: r_table.info.events_range()
    Out[16]: (100, 600)

    In [17]: r_table.calc.mean()
    Out[17]: 350.0



You may also access this functionality with wrapper functions:

- events_range
- mean
- stddev
- stats
- full_table_string
- percentage_points
- percentage_axe

::

    In [43]: silly_table = dt.AdditiveEvents({1: 123456, 100: 12345*10**1000})

    In [47]: print(dt.full_table_string(silly_table, include_zeroes=False))
      1: 123,456
    100: 1.234e+1004

    In [49]: stats_info = dt.stats(silly_table, list(range(-5000, 5)))

    In [51]: print(stats_str.format(*stats_info))
    (-5,000)-4 occurred 123,456 times out of 1.234e+1004 combinations.
    That's a one in 1.000e+999 chance or 1.000e-997%

Finally, here are all the kinds of dice you can add

- dt.Die(6)
- dt.ModDie(6, -2)
- dt.WeightedDie({1:1, 2:5, 3:2})
- dt.ModWeightedDie({1:1, 2:5, 3:2}, 5)
- dt.StrongDie(dt.Die(6), 5)

That's all of the basic implementation. The rest of this is details about base classes, details of the
die classes, details of dicetable classes, what causes errors and the changes from the previous version.

Top_

-----------
Die Classes
-----------
All dice are subclasses of ProtoDie, which is a subclass of IntegerEvents.
They all require implementations of get_size(), get_weight(), weight_info(),
multiply_str(number), __str__(), __repr__() and get_dict() <-required for any IntegerEvents.

They are all immutable , hashable and rich-comparable. Multiple names can safely point
to the same instance of a Die, they can be used in sets and dictionary keys and they can be
sorted with any other kind of die. Comparisons are done by (size, weight, get_dict, __repr__(as a last resort)).
So::

    In [54]: dice_list
    Out[54]:
    [ModDie(2, 0),
     WeightedDie({1: 1, 2: 1}),
     Die(2),
     ModWeightedDie({1: 1, 2: 1}, 0),
     StrongDie(Die(2), 1),
     StrongDie(WeightedDie({1: 1, 2: 1}), 1)]

    In [58]: [die.get_dict() == {1: 1, 2: 1} for die in dice_list]
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
    dt.ModWeightedDie({1:1, 3:3, 4:6}, 3) is a 4-sided die. 3 is added to all
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

Top_

--------------------------------
AdditiveEvents And IntegerEvents
--------------------------------
All tables and dice inherit from IntegerEvents.  All subclasses of IntegerEvents need the method
get_dict() which returns {event: occurrences, ...} for each NON-ZERO occurrence.  When you instantiate
any subclass, it checks to make sure you're get_dict() is legal.

AdditiveEvents is the parent of DiceTable.  You can add and remove events using the ".combine" method which tries
to pick the fastest combining algorithm. You can pick it yourself by calling ".combine_by_<algorithm>". You can
combine and remove DiceTable, AdditiveEvents, Die or any other IntegerEvents with the "combine" and "remove" methods,
but there's no record of it::

    In [31]: first = dt.DiceTable.new()

    In [32]: first = first.add_die(20, dt.Die(6))

    In [33]: first = first.add_die(7, dt.Die(9))

    In [34]: second = dt.DiceTable.new()

    In [35]: second = second.combine(1, first)

    In [36]: second.get_dict() == first.get_dict()
    Out[36]: True

    In [37]: second.get_list()
    Out[37]: []

    In [41]: print(first)
    20D6
    7D9
    10D10

    In [42]: first = first.combine_by_dictionary(2, dt.Die(1234))

    In [43]: first = first.combine_by_indexed_values(2, dt.AdditiveEvents({1: 2, 3: 4})

    In [44]: print(first)
    20D6
    7D9
    10D10

    In [45]: second.get_dict() == first.get_dict()
    Out[45]: False

Top_

---------------------------
DiceTable And RichDiceTable
---------------------------
You can instantiate any DiceTable or RichDiceTable with any data you like.
This allows you to create a DiceTable from stored information or to copy.
Please note that the "dice_data" method is ambiguously named on purpose. It's
function is to get correct input to instantiate a new DiceTable, whatever that
happens to be. To get consistent output, use "get_list".
::

    In [14]: old = dt.DiceTable.new()

    In [16]: old = old.add_die(100, dt.Die(6))

    In [17]: events_record = old.get_dict()

    In [18]: dice_record = old.dice_data()

    In [19]: new = dt.DiceTable(events_record, dice_record)

    In [20]: print(new)
    100D6

    In [21]: also_new = dt.RichDiceTable(new.get_list(), {dt.Die(6): 100}, calc_includes_zeroes=False)

    In [46]: old.get_dict() == new.get_dict() == also_new.get_dict()
    Out[46]: True

    In [47]: old.get_list() == new.get_list() == also_new.get_list()
    Out[47]: True


To get an identity table,
use the class method AdditiveEvents.new(), DiceTable.new() or RichDiceTable.new().
This creates a table with an empty dice record and the events
identity {0: 1}.

RichDiceTable.calc_includes_zeroes is as follows.
::

    In [85]: r_table = dt.RichDiceTable.new()

    In [91]: r_table.calc_includes_zeroes = True

    In [88]: r_table = r_table.add_die(1, dt.StrongDie(dt.Die(2), 2))

    In [89]: print(r_table.calc.full_table_string())
    2: 1
    3: 0
    4: 1

    In [91]: r_table = r_table.switch_boolean()

    In [92]: print(r_table.calc.full_table_string())
    2: 1
    4: 1

    In [93]: r_table = r_table.add_die(1, dt.StrongDie(dt.Die(2), 2))

    In [94]: print(r_table.calc.full_table_string())
    4: 1
    6: 2
    8: 1

    In [95]: r_table = r_table.switch_boolean()

    In [96]: print(r_table.calc.full_table_string())
    4: 1
    5: 0
    6: 2
    7: 0
    8: 1

Top_

----------------------------------------
EventsInformation And EventsCalculations
----------------------------------------

The methods are

EventsInformation:
- all_events
- all_events_include_zeroes
- biggest_event
- biggest_events_all <- returns the list of all events that have biggest occurrence
- events_keys
- events_range
- get_event
- get_items <- returns dict.items(): a list in py2 and an iterator in py3.
- get_range_of_events
- total_occurrences

EventsCalculations:
- full_table_string
- info
- mean
- percentage_axes  <- very fast but only good to 10 decimal places
- percentage_axes_exact
- percentage_points
- percentage_points_exact
- stats_strings
- stddev

EventsCalculations.include_zeroes is only settable at instantiation. It does
exactly what it says. EventCalculations owns an EventsInformation. So
instantiating EventsCalculations gets you
two for the price of one. It's accessed with the property
EventsCalculations.info .
::

    In[4]: table.add_die(1, dt.StrongDie(dt.Die(3), 2))

    In[5]: calc = dt.EventsCalculations(table, True)

    In[6]: print(calc.full_table_string())
    2: 1
    3: 0
    4: 1
    5: 0
    6: 1

    In[7]: calc = dt.EventsCalculations(table, False)

    In[8]: print(calc.full_table_string())
    2: 1
    4: 1
    6: 1

    In [10]: calc.info.events_range()
    Out[10]: (2, 6)

Top_

-----------
Inheritance
-----------
If you inherit from any child of AdditiveEvents and you do not load the new information
into EventsFactory, it will complain and give you instructions. The EventsFactory will try to create
your new class and if it fails, will return the closest related type::

    In[9]: class A(dt.DiceTable):
      ...:     pass
      ...:
    In[10]: A.new()
    E:\work\dice_tables\dicetables\baseevents.py:74: EventsFactoryWarning:
    factory: <class 'dicetables.factory.eventsfactory.EventsFactory'>
    Warning code: CONSTRUCT
    Failed to find/add the following class to the EventsFactory -
    class: <class '__main__.A'>
    ..... blah blah blah.....

    Out[10]: <__main__.A at 0x4c25400>  <-- you got lucky. it's your class

    In[11]: class B(dt.DiceTable):
      ...:     def __init__(self, name, number, events_dict, dice_data):
      ...:         self.name = name
      ...:         self.num = number
      ...:
    In[12]: B.new()
    E:\work\dice_tables\dicetables\baseevents.py:74: EventsFactoryWarning:
    factory: <class 'dicetables.factory.eventsfactory.EventsFactory'>
    Warning code: CONSTRUCT
    Failed to find/add the following class to the EventsFactory -
    class: <class '__main__.B'>
    ..... blah blah blah.....
    Out[12]: <dicetables.dicetable.DiceTable at 0x4c23f28>  <-- Oops. EventsFactory can't figure out how to make one.

| Now I will try again, but I will give the factory the info it needs.
| The factory knows how to get 'dictionary', 'dice'
| and 'calc_bool'. If you need it to get anything else, you need tuples of
| (<key name>, <getter name>, <default value>, 'property' or 'method')

::

    In[6]: class B(dt.DiceTable):
      ...:     factory_keys = ('name', 'number', 'dictionary', 'dice')
      ...:     new_keys = (('name', 'name', '', 'property'), ('number', 'get_num', 0, 'method'))
      ...:     def __init__(self, name, number, events_dict, dice_data):
      ...:         self.name = name
      ...:         self._num = number
      ...:     def get_num(self):
      ...:         return self._num
      ...:
    In[7]: B.new()
    Out[7]: <__main__.B at 0x4ca94a8>

    In[8]: class C(dt.DiceTable):
      ...:     factory_keys = ('dictionary', 'dice')
      ...:     def fancy_add_die(self, times, die):
      ...:         new = self.add_die(times, die)
      ...:         return 'so fancy', new
      ...:
    In[9]: x = C.new().fancy_add_die(2, dt.Die(3))
    In[10]: x[1].get_dict()
    Out[10]: {2: 1, 3: 2, 4: 3, 5: 2, 6: 1}
    In[11]: x
    Out[11]: ('so fancy', <__main__.C at 0x5eb4d68>)  <-- notice it returned C and not DiceTable

Top_

--------------------------
HOW TO GET ERRORS AND BUGS
--------------------------
Every time you instantiate any IntegerEvents, it is checked.  The get_dict() method returns a dict, and every value
in get_dict().values() must be >=1. get_dict() may not be empty.
since dt.Die(-2).get_dict() returns {}::

    In [3]: dt.Die(-2)
    dicetables.tools.eventerrors.InvalidEventsError: events may not be empty. a good alternative is the identity - {0: 1}.

    In [5]: dt.AdditiveEvents({1.0: 2})
    dicetables.tools.eventerrors.InvalidEventsError: all values must be ints

    In [6]: dt.WeightedDie({1: 1, 2: -5})
    dicetables.tools.eventerrors.InvalidEventsError: no negative or zero occurrences in Events.get_dict()

Because AdditiveEvents and WeightedDie specifically
scrub the zeroes from their get_dict() methods, these will not throw errors.
::

    In [9]: dt.AdditiveEvents({1: 1, 2: 0}).get_dict()
    Out[9]: {1: 1}

    In [11]: weird = dt.WeightedDie({1: 1, 2: 0})

    In [12]: weird.get_dict()
    Out[12]: {1: 1}

    In [13]: weird.get_size()
    Out[13]: 2

    In [14]: weird.get_raw_dict()
    Out[14]: {1: 1, 2: 0}

Special rule for WeightedDie and ModWeightedDie::

    In [15]: dt.WeightedDie({0: 1})
    ValueError: rolls may not be less than 1. use ModWeightedDie

    In [16]: dt.ModWeightedDie({0: 1}, 1)
    ValueError: rolls may not be less than 1. use ModWeightedDie

Here's how to add 0 one time (which does nothing, btw)::

    In [18]: dt.ModWeightedDie({1: 1}, -1).get_dict()
    Out[18]: {0: 1}

StrongDie also has a weird case that can be unpredictable.  Basically, don't multiply by zero::

    In [43]: table = dt.DiceTable.new()

    In [44]: table = table.add_die(1, dt.Die(6))

    In [45]: table = table.add_die(100, dt.StrongDie(dt.Die(100), 0))

    In [46]: table.get_dict()

    Out[46]: {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1}

    In [47]: print(table)
    1D6
    (100D100)X(0)

    In [48]: table = table.add_die(2, dt.StrongDie(dt.ModWeightedDie({1: 2, 3: 4}, -1), 0)) <- this rolls zero with weight 4

    In [49]: print(table)
    (2D3-2  W:6)X(0)
    1D6
    (100D100)X(0)

    In [50]: table.get_dict()
    Out[50]: {1: 16, 2: 16, 3: 16, 4: 16, 5: 16, 6: 16} <- this is correct, it's just stupid.


"remove_die" and "add_die" are safe. They raise an error if you
remove too many dice or add or remove a negative number.
If you remove or combine with a negative number, nothing should happen.
If you use "remove" to remove what you haven't added,
it may or may not raise an error, but it's guaranteed buggy::

    In [19]: table = dt.DiceTable.new().add_die(1, dt.Die(6))

    In [21]: table = table.remove_die(4, dt.Die(6))
    dicetables.tools.eventerrors.DiceRecordError: Tried to create a DiceRecord with a negative value at Die(6): -3

    In [22]: table = table.remove_die(1, dt.Die(10))
    dicetables.tools.eventerrors.DiceRecordError: Tried to create a DiceRecord with a negative value at Die(10): -1

    In [26]: table = table.add_die(-3, dt.Die(6))
    dicetables.tools.eventerrors.DiceRecordError: Tried to add_die or remove_die with a negative number.

    In [27]: table = table.remove_die(-3, dt.Die(6))
    dicetables.tools.eventerrors.DiceRecordError: Tried to add_die or remove_die with a negative number.

    In [30]: table.get_dict()
    Out[30]: {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1}

    In [31]: table = table.remove(10, dt.Die(2))
    ValueError: min() arg is an empty sequence <-didn't know this would happen, but at least failed loudly

    In [32]: table = table.remove(2, dt.Die(2))

    In [33]: table.get_dict()
    Out[33]: {-1: 1, 1: 1} <-bad. this is a random answer

    In [34]: table = table.remove(1, dt.AdditiveEvents({-5: 100}))

    In [35]: table.get_dict()
    Out[35]: {} <-very bad. this is an illegal answer.

Since you can instantiate a DiceTable with any legal input,
you can make a table with utter nonsense. It will work horribly.
for instance, the dictionary for 2D6 is

{2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6, 8: 5, 9: 4, 10: 3, 11: 2, 12: 1}
::

    In[22]: nonsense = dt.DiceTable({1: 1}, {dt.Die(6): 2}) <- BAD DATA!!!!

    In[23]: print(nonsense)  <- the dice record says it has 2D6, but the events dictionary is WRONG
    2D6

    In[24]: nonsense = nonsense.remove_die(2, dt.Die(6))  <- so here's your error. I hope you're happy.
    ValueError: min() arg is an empty sequence

But, you cannot instantiate a DiceTable with negative values for dice.
And you cannot instantiate a DiceTable with non-sense values for dice.
::

    In[11]: dt.DiceTable({1: 1}, {dt.Die(3): 3, dt.Die(5): -1})
    dicetables.tools.eventerrors.DiceRecordError: Tried to create a DiceRecord with a negative value at Die(5): -1

    In[12]: dt.DiceTable({1: 1}, {'a': 2.0})
    dicetables.tools.eventerrors.DiceRecordError: input must be {ProtoDie: int, ...}

Calling combine_by_flattened_list can be risky::

    In [36]: x = dt.AdditiveEvents({1:1, 2: 5})

    In [37]: x = x.combine_by_flattened_list(5, dt.AdditiveEvents({1: 2, 3: 4}))

    In [39]: x = x.combine_by_flattened_list(5, dt.AdditiveEvents({1: 2, 3: 4*10**10}))
    MemoryError

    In [42]: x = x.combine_by_flattened_list(1, dt.AdditiveEvents({1: 2, 3: 4*10**700}))
    OverflowError: cannot fit 'int' into an index-sized integer

Combining events with themselves is safe::

    In [51]: x = dt.AdditiveEvents({1: 1, 2: 1})

    In [52]: x = x.combine(1, x)

    In [53]: x.get_dict()
    Out[53]: {2: 1, 3: 2, 4: 1}

    In [54]: x = x.combine(1, x)

    In [55]: x.get_dict()
    Out[55]: {4: 1, 5: 4, 6: 6, 7: 4, 8: 1}

Top_

=======
CHANGES
=======
---------------------------------
from version 0.4.6 to version 1.0
---------------------------------
There are several major changes:

- Modules and classes  and methods got renamed. see the dictionary at the bottom. There are new classes
- DiceTable.__init__() now takes arguments. The class method DiceTable.new() creates an empty table.
- DiceTable and its parent AdditiveEvents are no longer responsible for obtaining any but the most basic information.
- All the calculations and information are now done by EventsInformation and EventsCalculations
- Aside from the above two classes, every other object is now a child of IntegerEvents.
- Dice classes no longer have "tuple_list()" method. They use the same "get_dict()" method that all IntegerEvents use

The following modules and classes have been renamed.

- longintmath.py: baseevents.py
- dicestats.py: dieevents.py, dicetable.py
- tableinfo.py: eventsinfo.py
- LongIntTable: AdditiveEvents

The following classes have been added:

- baseevents.InvalidEventsError
- dicetable.DiceRecordError
- baseevents.IntegerEvents
- dicetable.RichDiceTable
- eventsinfo.EventsInformation
- eventsinfo.EventsCalculations


DiceTable.__init__() now takes two arguments - a dictionary of {event: occurrences}
and a list of [(die, number), ]. to create a new table, call the class method DiceTable.new(). This change allows
easy creation of a new dice table from data. new_table = DiceTable(old_table.get_dict(), old_table.get_list()) or
new_table = DiceTable(stored_dict, stored_dice_list). To create a DiceTable with no dice, use DiceTable.new().

The base class of DiceTable is now called AdditiveEvents and not LongIntTable. If any IntegerEvents events is
instantiated in a way that would cause bugs, it raises an error; the same is true for any dice.

AdditiveEvents.combine/remove take any IntegerEvents as an argument whereas LongIntTable.add/remove took a list of
tuples as an argument. the methods for getting basic information from LongIntTable are now in EventsInformation.  mean()
and stddev() are part of EventsCalculations object. These objects work on ANY kind of IntegerEvents, not just DiceTable.

all of tableinfo was rewritten as objects. although they are deprecated, the following still exist as wrapper
functions for those objects:

- events_range
- format_number
- full_table_string
- graph_pts
- graph_pts_overflow
- mean
- percentage_axes
- percentage_points
- safe_true_div
- stats
- stddev

the new objects are:

- NumberFormatter
- EventsInformation
- EventsCalculations

for details, see their headings in the README.

For output:
stats() now shows tiny percentages, and if infinite, shows 'Infinity'.
Any exponent between 10 and -10 has that extraneous zero removed: '1.2e+05' is now '1.2e+5'.

Any subclass of ProtoDie no longer has the .tuple_list() method.  It has been replaced by the .get_dict() method
which returns a dictionary and not a list of tuples. The string for StrongDie now puts parentheses around the multiplier.
::

    CONVERSIONS = {
        'DiceTable()': 'DiceTable.new()',
        'LongIntTable.add': 'AdditiveEvents.combine',
        'LongIntTable.frequency': 'EventsInformation(event).get_event',
        'LongIntTable.frequency_all': 'EventsInformation(event).all_events',
        'LongIntTable.frequency_highest': 'EventsInformation(event).biggest_event',
        'LongIntTable.frequency_range': 'EventsInformation(event).get_range_of_events',
        'LongIntTable.mean': 'EventsCalculations(event).mean',
        'LongIntTable.merge': 'GONE',
        'LongIntTable.remove': 'AdditiveEvents.remove',
        'LongIntTable.stddev': 'EventsCalculations(event).stddev',
        'LongIntTable.total_frequency': 'EventsInformation(event).total_occurrences',
        'LongIntTable.update_frequency': 'GONE',
        'LongIntTable.update_value_add': 'GONE',
        'LongIntTable.update_value_ow': 'GONE',
        'LongIntTable.values': 'EventsInformation(event).event_keys',
        'LongIntTable.values_max': 'EventsInformation(event).event_range[0]',
        'LongIntTable.values_min': 'EventsInformation(event).event_range[1]',
        'LongIntTable.values_range': 'EventsInformation(event).event_range',
        'DiceTable.update_list': 'GONE (DiceTable owns a DiceRecord object that handles this)',
        'ProtoDie.tuple_list': ('sorted(ProtoDie.get_dict().items)', 'EventsInformation(ProtoDie).all_events'),
        'scinote': ('format_number', 'NumberFormatter.format'),
        'full_table_string', 'EventsCalculations(event).full_table_string',
        'stats', 'EventsCalculations(event).stats_strings',
        'long_int_div': 'safe_true_div',
        'graph_pts': ('graph_pts',
                      'EventsCalculations(event).percentage_points',
                      'EventsCalculations(event).percentage_points_exact',
                      'EventsCalculations(event).percentage_axes',
                      'EventsCalculations(event).percentage_axes_exact',
                      'EventsInformation(events).all_events',
                      'EventsInformation(events).all_events_include_zeroes')
        }


Top_

-------------------------------
from version 1.0 to version 2.0
-------------------------------
::

    in [12]: new = dt.AdditiveEvents.new()

    in [12]: new.combine(2, dt.AdditiveEvents({1: 1, 2: 5}))
    Out[13]: <dicetables.baseevents.AdditiveEvents at 0x5e73828>

