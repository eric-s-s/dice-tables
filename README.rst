#################
dicetables v2.1.4
#################
=========
CHANGELOG
=========

Added Modifier die class

EventsCalculations.stats_strings now returns a namedtuple StatsStrings
(which behaves like a tuple with added goodies)

=====================================================
a module for statistics of die rolls and other events
=====================================================


This module uses DiceTable and AdditiveEvents to combine
dice and other events that can be added together. It is used to
figure out the probability of events occurring.  For instance, if you
roll 100 six-sided dice, the chance of rolling any number between 100
and 300 is 0.15 percent.

contents:

- `THE BASICS`_
- `Die Classes`_
- `AdditiveEvents And IntegerEvents`_
- `DiceTable And DetailedDiceTable`_
- `EventsInformation And EventsCalculations`_
- `Inheritance`_
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

::

    In [1]: import dicetables as dt

    In [2]: new = dt.DiceTable.new()

    In [3]: one_two_sided = new.add_die(dt.Die(2), times=1)

    In [4]: one_two_sided_one_three_sided = one_two_sided.add_die(dt.Die(3), 1)

    In [5]: one_two_sided_one_three_sided.get_dict()
    Out[5]: {2: 1, 3: 2, 4: 2, 5: 1}

    In [6]: one_two_sided.get_dict()
    out[6]: {1: 1, 2: 1}

    In [7]: new.get_dict()
    out[7]: {0: 1}

Here are basic table functions. note that times added defaults to one.::

    In [4]: table = dt.DiceTable.new().add_die(dt.Die(2)).add_die(dt.Die(3))

    In [5]: str(table)
    Out[5]: '1D2\n1D3'

    In [6]: table = table.add_die(dt.Die(2), 100)

    In [7]: table = table.remove_die(dt.Die(2), 99)

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
    In [2]: table = table.add_die(dt.StrongDie(dt.Die(2), 3), 2)

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

DetailedDiceTable keeps a copy of these objects at .info and .calc calc_includes_zeros defaults to True::

    In [12]: d_table = dt.DetailedDiceTable.new()

    In [13]: d_table.info.events_range()
    Out[13]: (0, 0)

    In [14]: d_table.calc.mean()
    Out[14]: 0.0

    In [15]: d_table = d_table.add_die(dt.Die(6), 100)

    In [16]: d_table.info.events_range()
    Out[16]: (100, 600)

    In [17]: d_table.calc.mean()
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

    In [47]: print(dt.full_table_string(silly_table, include_zeroes=False, shown_digits=6))
      1: 123,456
    100: 1.23450e+1004

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
- dt.Modifier(-6)

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

Modifier
    A simple +/- modifier that adds to the total dice roll.

    Modifier(-3) is a one-sided die that always rolls a -3.  size=0, weight=0.

    so dt.DiceTable.new().add_die(dt.Die(6), 2).add_die(dt.Modifier(-2)) has die rolls in the range
    2 (-2) to 12 (-2) or 0 to 10.

    added methods:

    - .get_modifier()

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
::

    In [19]: dt.DiceTable({1: 1, 2:0}, {}).get_dict()
    Out[19]: {1: 1}

    In [20]: dt.AdditiveEvents({1: 2, 3: 0, 4: 1}).get_dict()
    Out[20]: {1: 2, 4: 1}

    In [21]: dt.ModWeightedDie({1: 2, 3: 0, 4: 1}, -5).get_dict()
    Out[21]: {-4: 2, -1: 1}

AdditiveEvents is the parent of DiceTable. It has the class method new() which returns the identity. This method is
inherited by its children. You can add and remove events using the ".combine" method which tries
to pick the fastest combining algorithm. You can pick it yourself by calling ".combine_by_<algorithm>". You can
combine and remove DiceTable, AdditiveEvents, Die or any other IntegerEvents with the "combine" and "remove" methods,
but there's no record of it.  AdditiveEvents has __eq__ method that tests type and get_dict(). This is inherited
from IntegerEvents.::

    In [32]: three_D2 = dt.AdditiveEvents.new().combine_by_dictionary(dt.Die(2), 3)

    In [33]: also_three_D2 = dt.AdditiveEvents({3: 1, 4: 3, 5: 3, 6: 1})

    In [34]: still_three_D2 = dt.AdditiveEvents.new().combine(dt.AdditiveEvents({1: 1, 2: 1}), 3)

    In [35]: three_D2.get_dict() == also_three_D2.get_dict() == still_three_D2.get_dict()
    Out[35]: True

    In [36]: identity = three_D2.remove(dt.Die(2), 3)

    In [37]: identity.get_dict() == dt.AdditiveEvents.new().get_dict()
    Out[37]: True

    In [38]: identity == dt.AdditiveEvents.new()
    Out[38]: True

    In [41]: print(three_D2)
    table from 3 to 6

    In [42]: twenty_one_D2 = three_D2.combine_by_indexed_values(three_D2, 6)

    In [43]: twenty_one_D2_five_D4 = twenty_one_D2.combine_by_flattened_list(dt.Die(4), 5)

    In [44]: five_D4 = twenty_one_D2_five_D4.remove(dt.Die(2), 21)

    In [45]: dt.DiceTable.new().add_die(dt.Die(4), 5).get_dict() == five_D4.get_dict()
    Out[45]: True

    In [45]: dt.DiceTable.new().add_die(dt.Die(4), 5) == five_D4
    Out[45]: False  <-- DiceTable is not AdditiveEvents

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
::

    In [14]: old = dt.DiceTable.new()

    In [16]: old = old.add_die(dt.Die(6), 100)

    In [17]: events_record = old.get_dict()

    In [18]: dice_record = old.dice_data()

    In [19]: new = dt.DiceTable(events_record, dice_record)

    In [20]: print(new)
    100D6

    In [21]: record = dt.DiceRecord({dt.Die(6): 100})

    In [22]: also_new = dt.DetailedDiceTable(new.get_dict(), record, calc_includes_zeroes=False)

    In [46]: old.get_dict() == new.get_dict() == also_new.get_dict()
    Out[46]: True

    In [47]: old.get_list() == new.get_list() == also_new.get_list()
    Out[47]: True

    In [47]: old == new
    Out[47]: True

    In [47]: old == also_new
    Out[47]: False  <- by type

    In [47]: isinstance(also_new, DiceTable)
    Out[47]: True

    In [47]: type(also_new) is DiceTable
    Out[47]: False

DetailedDiceTable.calc_includes_zeroes defaults to True. It is as follows.
::

    In [85]: d_table = dt.DetailedDiceTable.new()

    In [86]: d_table.calc_includes_zeroes
    out[86]: True

    In [87]: d_table = d_table.add_die(dt.StrongDie(dt.Die(2), 2))

    In [88]: print(d_table.calc.full_table_string())

    2: 1
    3: 0
    4: 1

    In [89]: d_table = d_table.switch_boolean()

    In [90]: the_same = dt.DetailedDiceTable({2: 1, 4: 1}, d_table.dice_data(), False)

    In [91]: print(d_table.calc.full_table_string())
    2: 1
    4: 1

    In [92]: print(the_same.calc.full_table_string())
    2: 1
    4: 1

    In [93]: d_table = d_table.add_die(1, dt.StrongDie(dt.Die(2), 2))


    In [94]: print(d_table.calc.full_table_string())
    4: 1
    6: 2
    8: 1

    In [95]: d_table = d_table.switch_boolean()

    In [96]: print(d_table.calc.full_table_string())
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

::

    In[34]: table = dt.DiceTable.new().add_die(dt.Die(6), 1000)

    In[35]: calc = dt.EventsCalculations(table)

    In[36]: calc.stddev(7)
    Out[36]: 54.0061725

    In[37]: calc.mean()
    Out[37]: 3500.0

    In[38]: the_stats = calc.stats_strings([3500], shown_digits=6)

    In[39]: the_stats
    Out[39]: StatsStrings(query_values='3,500',
                          query_occurrences='1.04628e+776',
                          total_occurrences='1.41661e+778',
                          one_in_chance='135.395',
                          pct_chance='0.738580')
    (yes, that is correct. out of 5000 possible rolls, 3500 has a 0.7% chance of occurring)

    In[40]: the_stats.one_in_chance
    out[40]: '135.395'

    In[41]: calc.stats_strings(list(range(1000, 3001)) + list(range(4000, 10000)))

    Out[41]:
    StatsStrings(query_values='1,000-3,000, 4,000-9,999',
                 query_occurrences='2.183e+758',
                 total_occurrences='1.417e+778',
                 one_in_chance='6.490e+19',
                 pct_chance='1.541e-18')

    (this is also correct; rolls not in the middle 1000 collectively have a much smaller chance than the mean.)

    In[42]: silly_table = dt.AdditiveEvents({1: 123456, 100: 12345*10**1000})

    In[43]: silly_calc = dt.EventsCalculations(silly_table, include_zeroes=False)

    In[44]:  print(silly_calc.full_table_string(shown_digits=6))
      1: 123,456
    100: 1.23457e+1006


EventsCalculations.include_zeroes is only settable at instantiation. It does
exactly what it says. EventCalculations owns an EventsInformation. So
instantiating EventsCalculations gets you
two for the price of one. It's accessed with the property
EventsCalculations.info .
::

    In[4]: table.add_die(dt.StrongDie(dt.Die(3), 2))

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
| The factory knows how to get 'get_dict', 'dice_data'
| and 'calc_includes_zeroes'. If you need it to get anything else, you need tuples of
| (<getter name>, <default value>, 'property' or 'method')

::

    In[6]: class B(dt.DiceTable):
      ...:     factory_keys = ('name', 'get_num', 'get_dict', 'dice_data')
      ...:     new_keys = (('name', '', 'property'), ('get_num', 0, 'method'))
      ...:     def __init__(self, name, number, events_dict, dice_data):
      ...:         self.name = name
      ...:         self._num = number
      ...:         super(B, self).__init__(events_dict, dice_data)
      ...:     def get_num(self):
      ...:         return self._num
      ...:
    In[7]: B.new()
    Out[7]: <__main__.B at 0x4ca94a8>

    In[8]: class C(dt.DiceTable):
      ...:     factory_keys = ('get_dict', 'dice_data')
      ...:     def fancy_add_die(self, die, times):
      ...:         new = self.add_die(die, times)
      ...:         return 'so fancy', new
      ...:
    In[9]: x = C.new().fancy_add_die(dt.Die(3), 2)
    In[10]: x[1].get_dict()
    Out[10]: {2: 1, 3: 2, 4: 3, 5: 2, 6: 1}
    In[11]: x
    Out[11]: ('so fancy', <__main__.C at 0x5eb4d68>)  <-- notice it returned C and not DiceTable

The other way to do this is to directly add the class to the EventsFactory::

    In[49]: factory = dt.factory.eventsfactory.EventsFactory

    In[50]: factory.add_getter('get_num', 0, 'method')

    In[51]: class A(dt.DiceTable):
       ...:     def __init__(self, number, events_dict, dice):
       ...:         self._num = number
       ...:         super(A, self).__init__(events_dict, dice)
       ...:     def get_num(self):
       ...:         return self._num
       ...:

    In[53]: factory.add_class(A, ('get_num', 'get_dict', 'dice_data'))

    In[55]: A.new()
    Out[55]: <__main__.A at 0x5f951d0>

    In[63]: factory.reset()

    In[64]: factory.has_class(A)
    Out[64]: False

When creating new methods, you can generate new events dictionaries by using
dicetables.additiveevents.EventsDictCreator.  the factory can create new instances with
EventsFactory.from_params.  For examples see the last few test in tests.factory.test_eventsfactory
Top_

--------------------------
HOW TO GET ERRORS AND BUGS
--------------------------
Every time you instantiate any IntegerEvents, it is checked.  The get_dict() method returns a dict, and every value
in get_dict().values() must be >=1. get_dict() may not be empty.
since dt.Die(-2).get_dict() returns {}::

    In [3]: dt.Die(-2)
    dicetables.eventsbases.eventerrors.InvalidEventsError: events may not be empty. a good alternative is the identity - {0: 1}.

    In [5]: dt.AdditiveEvents({1.0: 2})
    dicetables.eventsbases.eventerrors.InvalidEventsError: all values must be ints

    In [6]: dt.WeightedDie({1: 1, 2: -5})
    dicetables.eventsbases.eventerrors.InvalidEventsError: no negative or zero occurrences in Events.get_dict()

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

    In [44]: table = dt.DiceTable.new().add_die(dt.Die(6))

    In [45]: table = table.add_die(dt.StrongDie(dt.Die(100), 0), 100)

    In [46]: table.get_dict()

    Out[46]: {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1}

    In [47]: print(table)
    1D6
    (100D100)X(0)

    In [48]: stupid_die = dt.StrongDie(dt.ModWeightedDie({1: 2, 3: 4}, -1), 0)

    In [49]: table = table.add_die(stupid_die, 2) <- this rolls zero with weight 4

    In [50]: print(table)
    (2D3-2  W:6)X(0)
    1D6
    (100D100)X(0)

    In [51]: table.get_dict()
    Out[51]: {1: 16, 2: 16, 3: 16, 4: 16, 5: 16, 6: 16} <- this is correct, it's just stupid.


"remove_die" and "add_die" are safe. They raise an error if you
remove too many dice or add or remove a negative number.

If you "remove" or "combine" with a negative number, nothing should happen,
but i make no guarantees.

If you use "remove" to remove what you haven't added,
it may or may not raise an error, but it's guaranteed buggy::

    In [19]: table = dt.DiceTable.new().add_die(dt.Die(6))

    In [21]: table = table.remove_die(dt.Die(6), 4)
    dicetables.eventsbases.eventerrors.DiceRecordError: Tried to create a DiceRecord with a negative value at Die(6): -3

    In [22]: table = table.remove_die(dt.Die(10))
    dicetables.eventsbases.eventerrors.DiceRecordError: Tried to create a DiceRecord with a negative value at Die(10): -1

    In [26]: table = table.add_die(dt.Die(6), -3)
    dicetables.eventsbases.eventerrors.DiceRecordError: Tried to add_die or remove_die with a negative number.

    In [27]: table = table.remove_die(dt.Die(6), -3)
    dicetables.eventsbases.eventerrors.DiceRecordError: Tried to add_die or remove_die with a negative number.

    In [28]: table.get_dict()
    Out[28]: {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1}

    In [29]: table = table.combine(dt.Die(10000), -100)

    In [30]: table.get_dict()
    Out[30]: {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1}

    In [31]: table = table.remove(dt.Die(2), 10)
    ValueError: min() arg is an empty sequence <-didn't know this would happen, but at least failed loudly

    In [32]: table = table.remove(dt.Die(2), 2)

    In [33]: table.get_dict()
    Out[33]: {-1: 1, 1: 1} <-bad. this is a random answer

    (I know why you're about to get wacky and inaccurate errors, and I could fix the bug, except ...
     YOU SHOULD NEVER EVER DO THIS!!!!)
    In [34]: table = table.remove(dt.AdditiveEvents({-5: 100}))
    dicetables.eventsbases.eventerrors.InvalidEventsError: events may not be empty. a good alternative is the identity - {0: 1}.

    During handling of the above exception, another exception occurred:

    dicetables.factory.errorhandler.EventsFactoryError: Error Code: SIGNATURES DIFFERENT
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
::

    In[22]: nonsense = dt.DiceTable({1: 1}, dt.DiceRecord({dt.Die(6): 2})) <- BAD DATA!!!!

    In[23]: print(nonsense)  <- the dice record says it has 2D6, but the events dictionary is WRONG
    2D6

    In[24]: nonsense = nonsense.remove_die(dt.Die(6), 2)  <- so here's your error. I hope you're happy.
    ValueError: min() arg is an empty sequence

But, you cannot instantiate a DiceTable with negative values for dice.
And you cannot instantiate a DiceTable with non-sense values for dice.
::

    In[11]: dt.DiceTable({1: 1}, dt.DiceRecord({dt.Die(3): 3, dt.Die(5): -1}))
    dicetables.eventsbases.eventerrors.DiceRecordError: Tried to create a DiceRecord with a negative value at Die(5): -1

    In[12]: dt.DiceTable({1: 1}, dt.DiceRecord({'a': 2.0}))
    dicetables.eventsbases.eventerrors.DiceRecordError: input must be {ProtoDie: int, ...}

Calling combine_by_flattened_list can be risky::

    In [36]: x = dt.AdditiveEvents({1:1, 2: 5})

    In [37]: x = x.combine_by_flattened_list(dt.AdditiveEvents({1: 2, 3: 4}), 5)

    In [39]: x = x.combine_by_flattened_list(dt.AdditiveEvents({1: 2, 3: 4*10**10}), 5)
    MemoryError

    In [42]: x = x.combine_by_flattened_list(dt.AdditiveEvents({1: 2, 3: 4*10**700}))
    OverflowError: cannot fit 'int' into an index-sized integer

Top_
