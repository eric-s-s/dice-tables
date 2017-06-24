How to Get Errors and Bugs
==========================

.. _Top:

- `get_dict errors`_
- `errors for dice`_
- `add_die and remove_die are relatively safe`_
- `combine and remove are not`_
- `making a DiceTable with nonsense`_


get_dict errors
---------------

Every time you instantiate any IntegerEvents, it is checked.  The get_dict() method returns a dict, and every value
in get_dict().values() must be >=1. get_dict() may not be empty.
since dt.Die(-2).get_dict() returns {}

>>> import dicetables as dt
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

errors for :doc:`dice <../the_dice>`
------------------------------------

`Top`_

.. _errors for dice:

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

add_die and remove_die are relatively safe
------------------------------------------

`Top`_


:py:meth:`dicetables.dicetable.DiceTable.add_die`
and :py:meth:`dicetables.dicetable.DiceTable.add_die`
are safe. They raise an error if you
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

combine and remove are not
--------------------------

`Top`_

And now, this is the trouble you can get into with
:py:meth:`dicetables.additiveevents.AdditiveEvents.combine` and
:py:meth:`dicetables.additiveevents.AdditiveEvents.remove`

>>> table = dt.DiceTable.new().add_die(dt.Die(6))
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

making a DiceTable with nonsense
--------------------------------

`Top`_


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
