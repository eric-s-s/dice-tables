DiceTable and DetailedDiceTable
===============================

You can instantiate any DiceTable or DetailedDiceTable with any data you like.
This allows you to create a DiceTable from stored information or to copy.
Please note that the "dice_data" method is ambiguously named on purpose. It's
function is to get correct input to instantiate a new DiceTable, whatever that
happens to be. To get consistent output, use "get_list".  Equality testing is by type, get_dict(), dice_data()
(and calc_includes_zeroes for DetailedDiceTable).

>>> import dicetables as dt
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