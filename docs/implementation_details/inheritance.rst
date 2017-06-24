Inheritance
===========

If you inherit from any child of AdditiveEvents and you do not load the new information
into EventsFactory, it will complain and give you instructions. The EventsFactory will try to create
your new class and if it fails, will return the closest related type

>>> import  dicetables as dt
>>> class A(dt.DiceTable):
...     pass
...
>>> A.new()  # EventsFactory takes a stab at it, and guesses right. It returns the new class
<...A...>

But it also issues a warning::

    E:\work\dice_tables\dicetables\baseevents.py:74: EventsFactoryWarning:
    factory: <class 'dicetables.factory.eventsfactory.EventsFactory'>
    Warning code: CONSTRUCT
    Failed to find/add the following class to the EventsFactory -
    class: <class '__main__.A'>
    ..... blah blah blah.....

Here, it will fail create "B" class, and return its parent.

>>> class B(dt.DiceTable):
...     def __init__(self, name, number, events_dict, dice_data):
...         self.name = name
...         self.num = number
...         super(B, self).__init__(events_dict, dice_data)
...

>>> B.new()
<...DiceTable...>

and give you the following warning::

    E:\work\dice_tables\dicetables\baseevents.py:74: EventsFactoryWarning:
    factory: <class 'dicetables.factory.eventsfactory.EventsFactory'>
    Warning code: CONSTRUCT
    Failed to find/add the following class to the EventsFactory -
    class: <class '__main__.B'>
    ..... blah blah blah.....

Now I will try again, but I will give the factory the info it needs.
The factory knows how to get 'get_dict', 'dice_data'
and 'calc_includes_zeroes'. If you need it to get anything else, you need tuples of
(<getter name>, <default value>, 'property' or 'method')

>>> class B(dt.DiceTable):
...     factory_keys = ('name', 'get_num', 'get_dict', 'dice_data')
...     new_keys = (('name', '', 'property'), ('get_num', 0, 'method'))
...     def __init__(self, name, number, events_dict, dice_data):
...         self.name = name
...         self._num = number
...         super(B, self).__init__(events_dict, dice_data)
...     def get_num(self):
...         return self._num
...
>>> B.new()
<...B...>

>>> class C(dt.DiceTable):
...     factory_keys = ('get_dict', 'dice_data')
...     def fancy_add_die(self, die, times):
...         new = self.add_die(die, times)
...         return 'so fancy', new
...
>>> x = C.new().fancy_add_die(dt.Die(3), 2)
>>> x[1].get_dict()
{2: 1, 3: 2, 4: 3, 5: 2, 6: 1}
>>> x
('so fancy', <C...>)

Notice that C is returned and not DiceTable

The other way to do this is to directly add the class to the EventsFactory

>>> factory = dt.factory.eventsfactory.EventsFactory
>>> factory.add_getter('get_num', 0, 'method')
>>> class A(dt.DiceTable):
...     def __init__(self, number, events_dict, dice):
...         self._num = number
...         super(A, self).__init__(events_dict, dice)
...     def get_num(self):
...         return self._num
...
>>> factory.add_class(A, ('get_num', 'get_dict', 'dice_data'))
>>> A.new()
<A ...>

>>> factory.reset()
>>> factory.has_class(A)
False

When creating new methods, you can generate new events dictionaries by using
dicetables.additiveevents.EventsDictCreator.  the factory can create new instances with
EventsFactory.from_params.  For an example see
`tests.factory.test_eventsfactory 1 <https://github.com/eric-s-s/dice-tables/blob/master/tests/factory/test_eventsfactory.py#L691>`_
. other examples of inheritance with DiceTable can be found just above that at:
`tests.factory.test_eventsfactory 2 <https://github.com/eric-s-s/dice-tables/blob/master/tests/factory/test_eventsfactory.py#L618>`_
