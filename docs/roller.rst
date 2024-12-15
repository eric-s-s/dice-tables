Roller
======

A Roller performs random rolls on any `IntegerEvents`, including dice and DiceTables.
You can pass it your own random generator or let it use the python default random generator.
Python has specs on how to subclass `random.Random` `here
<https://docs.python.org/3/library/random.html>`_.

    Class Random can also be subclassed if you want to use a different basic generator of your own devising:
    in that case, override the random(), seed(), getstate(), and setstate() methods.
    Optionally, a new generator can supply a getrandbits() method — this allows randrange()
    to produce selections over an arbitrarily large range.

This roller relies on `random.randrange` and alias tables.  Since it relies on random integer generation
and not a random float, it is accurate for any IntegerEvents.  So, for instance, on 1000D6, a roll of "1000"
has a 1 in 6**1000 chance of occurring (a 7.059e-777% chance).  The roller can accurately model that, so that::

    table = dt.DiceTable.new().add_die(dt.Die(6), 1000)
    roller = Roller(table)
    my_roll = roller.roll()

`my_roll` actually has a chance of being `1000`, although if that actually happened ...  er ...
um ... hmmm ... get your computer checked. Seriously! You probably have a higher chance of winning the lottery while
getting eaten by a shark as you're struck by lightning.

.. module:: dicetables.roller


.. autoclass:: Roller
    :members:
    :undoc-members:

Here's an example with a custom "random" generator

>>> import random
>>> import dicetables as dt
>>> class ZeroForever(random.Random):
...     def __init__(self, *args, **kwargs):
...         self.even_odd_counter = 0
...         super(ZeroForever, self).__init__(*args, **kwargs)
...
...     def randrange(self, start, stop=None, step=1, _int=int):
...         return 0
...
>>> my_die = dt.WeightedDie({1: 1, 2: 10**1000})
>>> roller = dt.Roller(my_die, random_generator=ZeroForever())
>>> roller.roll_many(10)
[1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
