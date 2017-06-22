#################
dicetables v2.3.0
#################

=====================================================
a module for statistics of die rolls and other events
=====================================================


This module uses DiceTable and AdditiveEvents to combine
dice and other events that can be added together. It is used to
figure out the probability of events occurring.  For instance, if you
roll 100 six-sided dice, the chance of rolling any number between 100
and 300 is 0.15 percent while the chance of rolling only 350 is 2.3 percent.



---------
ChangeLog
---------
since v2.1.0

- EventsCalculations added functions log10_points and log10_axes
- New dice: Exploding(other_die, explosions=2), ExplodingOn(other_die, explodes_on, explosions=2)
- see `Die Classes <http://dice-tables.readthedocs.io/en/latest/the_dice.html>`_. and
  `Events info <http://dice-tables.readthedocs.io/en/latest/events_info.html>`_ for details
- New object: `Parser <http://dice-tables.readthedocs.io/en/latest/nitt_gritty/parser.html>`_ -
  It converts strings to Die objects.


