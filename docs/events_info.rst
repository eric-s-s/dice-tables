EventsInformation And EventsCalculations
========================================

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

* log10_axes and log10_points
    * log10 of the combinations.
    * any occurrence of zero is default set to -100.0 but can be assigned any number.

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

>>> import dicetables as dt
>>> table = dt.DiceTable.new().add_die(dt.Die(6), 1000)
>>> calc = dt.EventsCalculations(table)
>>> calc.stddev(7)
54.0061725
>>> calc.mean()
3500.0
>>> the_stats = calc.stats_strings([3500], shown_digits=6)
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

EventsCalculations.include_zeroes is only settable at instantiation. It does
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