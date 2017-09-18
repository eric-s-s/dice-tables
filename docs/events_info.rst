EventsInformation And EventsCalculations
========================================

These two objects can get information from any
Events class. Below the class docs are some code examples.

.. module:: dicetables.eventsinfo

.. autoclass:: EventsInformation
    :members:
    :undoc-members:

.. autoclass:: EventsCalculations
    :members:
    :undoc-members:

>>> import dicetables as dt
>>> table = dt.DiceTable.new().add_die(dt.Die(6), 1000)
>>> calc = dt.EventsCalculations(table)
>>> calc.stddev(7)
54.0061725
>>> calc.mean()
3500.0
>>> the_stats = calc.stats_strings([3500], shown_digits=6) # Shown_digits defaults to 4.
>>> the_stats
StatsStrings(query_values='3,500',
             query_occurrences='1.04628e+776',
             total_occurrences='1.41661e+778',
             one_in_chance='135.395',
             pct_chance='0.738580')

This is correct. Out of 5000 possible rolls, 3500 has a 0.7% chance of occurring.

>>> the_stats.one_in_chance
'135.395'
>>> calc.stats_strings(list(range(1000, 3001)) + list(range(4000, 10000)))
StatsStrings(query_values='1,000-3,000, 4,000-9,999',
             query_occurrences='2.183e+758',
             total_occurrences='1.417e+778',
             one_in_chance='6.490e+19',
             pct_chance='1.541e-18')

This is also correct. Rolls not in the middle 1000 collectively have a much smaller chance than the mean.

>>> silly_table = dt.AdditiveEvents({1: 123456, 100: 1234567*10**1000})
>>> silly_calc = dt.EventsCalculations(silly_table, include_zeroes=False)
>>> print(silly_calc.full_table_string(shown_digits=6))
  1: 123,456
100: 1.23457e+1006
<BLANKLINE>

`EventsCalculations.include_zeroes` is only settable at instantiation. It does
exactly what it says. EventCalculations owns an EventsInformation. So
instantiating EventsCalculations gets you
two for the price of one. It's accessed with the property
EventsCalculations.info .

>>> table = dt.DiceTable.new().add_die(dt.StrongDie(dt.Die(3), 2))
>>> calc = dt.EventsCalculations(table, True)
>>> print(calc.full_table_string())
2: 1
3: 0
4: 1
5: 0
6: 1
<BLANKLINE>
>>> calc = dt.EventsCalculations(table, False)
>>> print(calc.full_table_string())
2: 1
4: 1
6: 1
<BLANKLINE>
>>> calc.info.events_range()
(2, 6)


You can also access some functionality as wrapper functions.

.. py:function:: events_range(events)

.. py:function:: mean(events)

.. py:function:: stddev(events, decimal_place=4)

.. py:function:: percentage_points(events, include_zeroes=True)

.. py:function:: percentage_axes(events, include_zeroes=True)

.. py:function:: stats(events, query_values, shown_digits=4)

.. py:function:: full_table_string(events, include_zeroes=True, shown_digits=4)
