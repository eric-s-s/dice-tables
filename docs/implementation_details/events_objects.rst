Events Objects
==============

.. module:: dicetables
    :noindex:


.. autoclass:: dicetables.eventsbases.integerevents.IntegerEvents

    All tables and dice inherit from dicetables.eventsbases.IntegerEvents. IntegerEvents is a collection
    of {event: number of times it occurs} where events are.... integers! and number of occurrences is int >=0.
    Any Events is assumed to contain all zero-occurrences events.

    All subclasses of IntegerEvents need the method
    get_dict() which returns {event: occurrences, ...} for each NON-ZERO occurrence.  When you instantiate
    any subclass, it checks to make sure you're get_dict() is legal.

    Any of the classes that take a dictionary of events as input scrub the zero
    occurrences out of the dictionary for you.

    >>> import dicetables as dt
    >>> dt.DiceTable({1: 1, 2: 0}, dt.DiceRecord.new()).get_dict()
    {1: 1}
    >>> dt.AdditiveEvents({1: 2, 3: 0, 4: 1}).get_dict()
    {1: 2, 4: 1}
    >>> dt.ModWeightedDie({1: 2, 3: 0, 4: 1}, -5).get_dict()
    {-4: 2, -1: 1}

    Any child of IntegerEvents has access to :code:`__eq__` and :code:`__ne__` evaluated by type and then get_dict().
    It can be compared to any object and two events that are not the exact same class will be !=.

.. autoclass:: dicetables.eventsbases.protodie.ProtoDie


.. autoclass:: dicetables.additiveevents.AdditiveEvents
    :members:
    :undoc-members:

    This is the basis for the :py:class:`dicetables.dicetable.DiceTable` class. It is an Events that can
    combine with other Events. It is immutable. When it combines with other Events, the result is a new
    object.


    It has the class method :code:`new()` which returns the identity. This method is
    inherited by its children. You can add and remove events using the :code:`.combine` method which tries
    to pick the fastest combining algorithm. You can pick it yourself by calling :code:`.combine_by_<algorithm>`.
    You can combine and remove DiceTable, AdditiveEvents, Die or any other IntegerEvents,
    but there's no record of it.

    >>> three_D2 = dt.AdditiveEvents.new().combine_by_dictionary(dt.Die(2), 3)
    >>> also_three_D2 = dt.AdditiveEvents({3: 1, 4: 3, 5: 3, 6: 1})
    >>> still_three_D2 = dt.AdditiveEvents.new().combine(dt.AdditiveEvents({1: 1, 2: 1}), 3)
    >>> three_D2.get_dict() == also_three_D2.get_dict() == still_three_D2.get_dict()
    True
    >>> identity = three_D2.remove(dt.Die(2), 3)
    >>> three_D2 == also_three_D2 == still_three_D2
    True
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

    Since :py:class:`dicetables.dicetable.DiceTable` is the child of AdditiveEvents, it can do all this combining and
    removing, but it won't be recorded in the dice record.
