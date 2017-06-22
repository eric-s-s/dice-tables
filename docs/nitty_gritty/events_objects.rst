Events Objects
==============

All tables and dice inherit from dicetables.eventsbases.IntegerEvents.  All subclasses of IntegerEvents need the method
get_dict() which returns {event: occurrences, ...} for each NON-ZERO occurrence.  When you instantiate
any subclass, it checks to make sure you're get_dict() is legal.

Any child of IntegerEvents has access to __eq__ and __ne__ evaluated by type and then get_dict(). It can be compared
to any object and two events that are not the exact same class will be !=.

Any of the classes that take a dictionary of events as input scrub the zero
occurrences out of the dictionary for you.

>>> import dicetables as dt
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