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