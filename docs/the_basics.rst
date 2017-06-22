The Basics
==========

| Here's a quick bit of math.  if you combine a 2-sided die and a 3-sided die,
| you get the following combinations.
| (1,1) / (1, 2) (2, 1) / (2, 2), (1, 3) / (2, 3):

- roll - 2: 1 occurrence  (1 in 6 chance)
- roll - 3: 2 occurrences  (2 in 6 chance)
- roll - 4: 2 occurrences  (2 in 6 chance)
- roll - 5: 1 occurrence  (1 in 6 chance)

>>> import dicetables as dt
>>> new = dt.DiceTable.new()
>>> one_two_sided = new.add_die(dt.Die(2), times=1)
>>> one_two_sided_one_three_sided = one_two_sided.add_die(dt.Die(3), 1)
>>> one_two_sided_one_three_sided.get_dict()
{2: 1, 3: 2, 4: 2, 5: 1}
>>> one_two_sided.get_dict()
{1: 1, 2: 1}
>>> new.get_dict()
{0: 1}

Here are basic table functions. note that times added defaults to one.
Also note that DiceTable is immutable. adding and removing dice creates a new table. The original table is intact.


>>> table = dt.DiceTable.new().add_die(dt.Die(2)).add_die(dt.Die(3))
>>> str(table)
'1D2\n1D3'
>>> table = table.add_die(dt.Die(2), 100)
>>> table = table.remove_die(dt.Die(2), 99)
>>> print(table)
2D2
1D3
>>> print(table.add_die(dt.Modifier(5), 2))
+5
+5
2D2
1D3
>>> table.get_list()  # list is sorted according to die
[(Die(2), 2), (Die(3), 1)]
>>> table.number_of_dice(dt.Die(10))
0
>>> table.number_of_dice(dt.Die(2))
2
>>> print(table.weights_info())
2D2
    No weights
<BLANKLINE>
1D3
    No weights

To get useful information, use EventsInformation object and EventsCalculations object

>>> table = dt.DiceTable.new()
>>> table = table.add_die(dt.StrongDie(dt.Die(2), 3), 2)
>>> table.get_dict() == {6: 1, 9: 2, 12: 1}
True
>>> info = dt.EventsInformation(table)
>>> info.all_events()
[(6, 1), (9, 2), (12, 1)]
>>> info.all_events_include_zeroes()
[(6, 1), (7, 0), (8, 0), (9, 2), (10, 0), (11, 0), (12, 1)]
>>> info.events_keys()
[6, 9, 12]
>>> info.events_range()
(6, 12)
>>> info.get_event(4)
(4, 0)
>>> info.get_range_of_events(7, 13)
[(7, 0), (8, 0), (9, 2), (10, 0), (11, 0), (12, 1)]
>>> info.biggest_event()
(9, 2)
>>> info.total_occurrences()
4
>>> calc = dt.EventsCalculations(table)
>>> calc.mean()
9.0
>>> calc.stddev()
2.1213
>>> calc.percentage_points()
[(6, 25.0), (7, 0.0), (8, 0.0), (9, 50.0), (10, 0.0), (11, 0.0), (12, 25.0)]
>>> print(calc.full_table_string())
 6: 1
 7: 0
 8: 0
 9: 2
10: 0
11: 0
12: 1
>>> without_zeroes = dt.EventsCalculations(table, include_zeroes=False)
>>> print(without_zeroes.full_table_string())
 6: 1
 9: 2
12: 1
<BLANKLINE>
>>> stats_str = "{} occurred {} times out of {} combinations.\nThat's a one in {} chance or {}%"
>>> print(stats_str.format(*without_zeroes.stats_strings([1, 2, 5, 8, 9, 10])))
1-2, 5, 8-10 occurred 2 times out of 4 combinations.
That's a one in 2.000 chance or 50.00%
>>> without_zeroes.percentage_axes()
[(6, 9, 12), (25.0, 50.0, 25.0)]

DetailedDiceTable keeps a copy of these objects at .info and .calc calc_includes_zeros defaults to True

>>> d_table = dt.DetailedDiceTable.new()
>>> d_table.info.events_range()
(0, 0)
>>> d_table.calc.mean()
0.0
>>> d_table = d_table.add_die(dt.Die(6), 100)
>>> d_table.info.events_range()
(100, 600)
>>> d_table.calc.mean()
350.0

You may also access this functionality with wrapper functions:

- events_range
- mean
- stddev
- stats
- full_table_string
- percentage_points
- percentage_axes

>>> silly_table = dt.AdditiveEvents({1: 123456, 100: 12345*10**1000})
>>> print(dt.full_table_string(silly_table, include_zeroes=False, shown_digits=6))
  1: 123,456
100: 1.23450e+1004
<BLANKLINE>
>>> stats_info = dt.stats(silly_table, list(range(-5000, 5)))
>>> print(stats_str.format(*stats_info))
(-5,000)-4 occurred 123,456 times out of 1.234e+1004 combinations.
That's a one in 1.000e+999 chance or 1.000e-997%

Finally, here are all the kinds of dice you can add

- dt.Die(6)
- dt.ModDie(6, -2)
- dt.WeightedDie({1:1, 2:5, 3:2})
- dt.ModWeightedDie({1:1, 2:5, 3:2}, 5)
- dt.StrongDie(dt.Die(6), 5)
- dt.Modifier(-6)
- dt.Exploding(dt.Die(6), explosions=4)
- dt.ExplodingOn(dt.Die(6), (1, 3, 6), explosions=2)

That's all of the basic implementation. The rest of this is details about base classes, details of the
die classes, details of dicetable classes, what causes errors and the changes from the previous version.