DiceTable and DetailedDiceTable
===============================

.. module:: dicetables.dicetable

The two DiceTable classes are below

.. autoclass:: DiceTable
    :members:
    :undoc-members:

    .. automethod:: new

DetailedDiceTable is a dicetable that owns a
:py:class:`dicetables.eventsinfo.EventsCalculations`. This is
accessed from the :code:`.calc` property and you can set whether it
includes zero values with `calc_includes_zeros`. Owning an EventsCalculations
means that it uses more memory.

.. autoclass:: DetailedDiceTable
    :members:
    :undoc-members:


They inherit from :py:class:`dicetables.additiveevents.AdditiveEvents`

You can instantiate any DiceTable or DetailedDiceTable with any data you like.
This allows you to create a DiceTable from stored information or to copy.
:code:`dice_data` returns the correct input to instantiate a new DiceTable, which is
a :py:class:`dicetables.dicerecord.DiceRecord`　(See below for details).
To get consistent and sorted output for dice, use :code:`get_list`.
Equality testing is by:
- type
- get_dict()-
- dice_data()
- (and calc_includes_zeroes for DetailedDiceTable).

>>> import dicetables as dt
>>> ten_d_six = dt.DiceTable.new()
>>> ten_d_six = ten_d_six.add_die(dt.Die(6), 10)
>>> events_record = ten_d_six.get_dict()
>>> dice_record = ten_d_six.dice_data()
>>> new_ten_d_six = dt.DiceTable(events_record, dice_record)
>>> print(new_ten_d_six)
10D6
>>> record = dt.DiceRecord({dt.Die(6): 10})
>>> also_ten_d_six = dt.DetailedDiceTable(new_ten_d_six.get_dict(), record, calc_includes_zeroes=False)
>>> ten_d_six.get_dict() == new_ten_d_six.get_dict() == also_ten_d_six.get_dict()
True
>>> ten_d_six.get_list() == new_ten_d_six.get_list() == also_ten_d_six.get_list()
True
>>> ten_d_six == new_ten_d_six
True
>>> ten_d_six == also_ten_d_six  # False by type
False
>>> isinstance(also_ten_d_six, dt.DiceTable)
True
>>> type(also_ten_d_six) is dt.DiceTable
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

**The DiceRecord**

.. autoclass:: dicetables.dicerecord.DiceRecord
    :members:
    :undoc-members:
    :special-members: __eq__

    This is an immutable record of dice. :code:`add_die`, :code:`remove_die`
    and :code:`new` return new DiceRecord without altering the original.
    You can instantiate one with :code:`{dice_object: number_of_dice}`.
    Trying to create a DiceRecord with a negative number of dice will raise an
    error.