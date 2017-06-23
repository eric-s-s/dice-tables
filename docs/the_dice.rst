The Dice
========

All dice are subclasses of dicetables.eventsbases.protodie.ProtoDie, which is a subclass of
dicetables.eventsbases.integerevents.IntegerEvents. They all require implementations of
get_size(), get_weight(), weight_info(), multiply_str(number), __str__(), __repr__() and
get_dict() (the final one is a requirement of all IntegerEvents).

They are all immutable , hashable and rich-comparable. Multiple names can safely point
to the same instance of a Die, they can be used in sets and dictionary keys and they can be
sorted with any other kind of die. Comparisons are done by (size, weight, get_dict, __repr__(as a last resort)).
So:

>>> import dicetables as dt
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

.. module:: dicetables.dieevents

.. autoclass:: Die
    :members:
    :undoc-members:

    Base methods for all dice:


.. autoclass:: ModDie
    :members: get_modifier
    :undoc-members:

    It is 4-sided die with -1 added to each roll (D4-1)

    added methods:


.. autoclass:: WeightedDie
    :members: get_raw_dict
    :undoc-members:

    dt.WeightedDie({1:1, 3:3, 4:6}) is a 4-sided die.  It rolls 4
    six times as often as 1, rolls 3 three times as often as 1
    and never rolls 2

    added methods:

get_raw_dict(): returns all values in die.get_size() even if they are zero.
dt.WeightedDie({1:1, 3:3, 4:6}).get_raw_dict() returns {1: 1, 2: 0, 3: 3, 4: 4}

.. autoclass:: ModWeightedDie
    :members: get_raw_dict, get_modifier
    :undoc-members:

    added methods:

.. autoclass:: StrongDie
    :members: get_multiplier, get_input_die
    :undoc-members:

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

.. autoclass:: Modifier
    :members: get_modifier
    :undoc-members:

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

.. autoclass:: Exploding
    :members: get_input_die, get_explosions
    :undoc-members:

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

.. autoclass:: ExplodingOn
    :members: get_input_die, get_explosions, get_explodes_on
    :undoc-members:

    Here are the rolls for an exploding D6 that can explode the default times and explodes on 5 and 6.

    >>> roll_values = dt.ExplodingOn(dt.Die(6), (5, 6)).get_dict()
    >>> sorted(roll_values.items())
    [(1, 36), (2, 36), (3, 36), (4, 36),
     (6, 6), (7, 12), (8, 12), (9, 12), (10, 6),
     (11, 1), (12, 3), (13, 4), (14, 4), (15, 4), (16, 4), (17, 3), (18, 1)]

    added methods: