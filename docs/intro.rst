Basic Math for Dice and Events
==============================

Think of a six-sided die as a list of events. Each roll has an equal chance of occurring and could
be represented by the dictionary {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1}.
If you want to combine this with another six-sided die, when the new die rolls a one, you add that to each
of the original rolls (1-6 + 1) and the same for when the new die adds a two (1-6 + 2), etc...
This gives you::

    {2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1}
          {3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1}
                {4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1}
                      {5: 1, 6: 1, 7: 1, 8: 1, 9: 1, 10: 1}
                            {6: 1, 7: 1, 8: 1, 9: 1, 10: 1, 11: 1}
    +                             {7: 1, 8: 1, 9: 1, 10: 1, 11: 1, 12: 1}
    ---------------------------------------------------------------------
    {2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6, 8: 5, 9: 4, 10: 3, 11: 2, 12: 1}

In this set of events, "7" happens six times as often as one and there are a total of 36 occurrences.
Your chance of rolling a 7 on 2D6 is 6 in 36 and your chance or rolling a 1 is 1 in 36.

Then add a weighted 2-sided die (a die that only rolls 1 or 2) that rolls 2 twice as often as 1.
This means adding {1: 1, 2: 2} to the current set of events. You take the new set of events and add
one to each roll for the 1: 1.  Then you add 2 to each roll twice for 2: 2, giving you::


    {3: 1, 4: 2, 5: 3, 6: 4,  7: 5,  8: 6,  9: 5,  10: 4,  11: 3,  12: 2, 13: 1}
          {4: 1, 5: 2, 6: 3,  7: 4,  8: 5,  9: 6,  10: 5,  11: 4,  12: 3, 13: 2, 14: 1}
    +     {4: 1, 5: 2, 6: 3,  7: 4,  8: 5,  9: 6,  10: 5,  11: 4,  12: 3, 13: 2, 14: 1}
    -----------------------------------------------------------------------------------------
    {3: 1, 4: 4, 5: 7, 6: 10, 7: 13, 8: 16, 9: 17, 10: 14, 11: 11, 12: 8, 13: 5, 14: 2}

So if you rolled 2D6 and 1WeightedDie({1: 1, 2: 2}). You'd get the following distribution.
There are 108 total occurrences. 3 happens once, giving it a 0.93% chance, and 9 happens
17 times, giving you a 15.7% chance of rolling a 9.

.. image:: /_static/figure_1.png