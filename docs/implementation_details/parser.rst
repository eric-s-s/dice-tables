Parser
======
- `Customizing Parser`_
- `Limiting Max Values`_
- `Limits and DicePool Objects`_


.. module:: dicetables.parser

.. autoclass:: Parser
    :members:
    :undoc-members:

    .. automethod:: __init__


    The Parser object converts strings into dice objects.

    >>> import dicetables as dt
    >>> new_die = dt.Parser().parse_die('Die(6)')
    >>> new_die == dt.Die(6)
    True
    >>> dt.Parser().parse_die('ModDie(6, modifier=1)')
    ModDie(6, 1)

    It can ignore case or not.  This applies to dice names and kwarg names. It defaults to ignore_case=False.
    You can also disable allowing kwargs. It defaults to disable_kwargs=False.

    >>> dt.Parser().parse_die('die(6)')
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    ParseError: Die class: <die> not recognized by parser.

    >>> dt.Parser(ignore_case=True).parse_die('stronGdie(dIE(6), MULTIPLIER=4)')
    StrongDie(Die(6), 4)

    >>> parser = dt.Parser(disable_kwargs=True)
    >>> parser.parse_die('Die(6)')
    Die(6)
    >>> parser.parse_die('Die(die_size=6)')
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    ParseError: Tried to use kwargs on a Parser with disable_kwargs=True

    The Parser can parse all dice in the library: Die, ModDie, WeightedDie, ModWeightedDie, Modifier, StrongDie,
    Exploding and ExplodingOn. It is possible to add other dice to an instance of Parser or make a new class that
    can parse other dice.

Customizing Parser
------------------

Parser can only parse very specific types of parameters.

>>> from dicetables.parser import make_int, make_int_dict, make_int_tuple
>>> parser = dt.Parser()
>>> parser.param_types == {'int': make_int, 'int_dict': make_int_dict,
...                        'die': parser.make_die, 'int_tuple': make_int_tuple}
True

If, for example, you need Parser to know how to parse a string, a list of strings and
dictionary of keys=str: values=int, you first need to create functions that can parse
the appropriate Nodes. Then you assign the functions to the parser.

    First, a very very quick introduction to the Abstract Syntax Tree:

    The nodes are derived using the `ast <https://docs.python.org/3/library/ast.html>`_
    module. ast, very briefly, takes a string and parses it into nodes. To see what
    it does, use :code:`ast.dump(ast.parse(<your_string>))`.  Create and test nodes by using
    :code:`my_node = ast.parse(<your_string>).body[0].value`

    >>> import ast
    >>> ast.dump(ast.parse('{1: "a", 2: "b"}'))
    "Module(body=[Expr(value=Dict(keys=[Num(n=1), Num(n=2)], values=[Str(s='a'), Str(s='b')]))])"
    >>> my_list_node = ast.parse('[1, "A"]').body[0].value
    >>> ast.dump(my_list_node)
    "List(elts=[Num(n=1), Str(s='A')], ctx=Load())"

    This says that the List node points to its elts:

    - a Num node: value=1
    - a Str node: value='A'

Now, to my example.

>>> str_value =  ast.Str(s="abd")
>>> str_value.s
'abd'
>>> str_list = ast.List(elts=[ast.Str(s='a'), ast.Str(s='b'), ast.Str(s='c')])
>>> str_int_dict = ast.parse("{'a': 2, 'b': 10}").body[0].value

and here are conversion methods.

>>> from dicetables.parser import make_int
>>> def make_str(str_node):
...     return str_node.s
>>> make_str(str_value)
'abd'

>>> def make_str_list(lst_node):
...     return [make_str(node) for node in lst_node.elts]
>>> make_str_list(str_list)
['a', 'b', 'c']

>>> def make_str_int_dict(dict_node):
...     keys = [make_str(node) for node in dict_node.keys]
...     values = [make_int(node) for node in dict_node.values]
...     return dict(zip(keys, values))
>>> make_str_int_dict(str_int_dict) == {'a': 2, 'b': 10}
True

Now you tell the parser that a key of your choice corresponds to the method.

>>> parser = dt.Parser()
>>> parser.add_param_type('str', make_str)
>>> parser.add_param_type('str_list', make_str_list)
>>> parser.add_param_type('str_int_dict', make_str_int_dict)

To add a new dice class to the parser, give the parser the class and a tuple of the param_types keys for each parameter.
The parser will assume you're adding a class with an __init__ function and will try to auto_detect kwargs. You can
disable this and add your own kwargs (or not).

>>> class NamedDie(dt.Die):
...     def __init__(self, name, buddys_names, stats, size):
...         self.name = name
...         self.best_buds = buddys_names[:]
...         self.stats = stats.copy()
...         super(NamedDie, self).__init__(size)
...
...     def __eq__(self, other):
...         return (super(NamedDie, self).__eq__(other) and
...                 self.name == other.name and
...                 self.best_buds == other.best_buds and
...                 self.stats == other.stats)

>>> parser.add_class(NamedDie, ('str', 'str_list', 'str_int_dict', 'int'))
>>> die_str = 'NamedDie("Tom", ["Dick", "Harry"], stats={"friends": 2, "coolness_factor": 10}, size=4)'
>>> die = NamedDie('Tom', ['Dick', 'Harry'], {'friends': 2, 'coolness_factor': 10}, 4)
>>> parser.parse_die(die_str) == die
True

You can make a new parser class instead of a specific instance of Parser. Notice that I turned off the auto_detect and
told it some bad kwarg names.

>>> class MyParser(dt.Parser):
...     def __init__(self, ignore_case=False):
...         super(MyParser, self).__init__(ignore_case)
...         self.add_param_type('str', make_str)
...         self.add_param_type('str_list', make_str_list)
...         self.add_param_type('str_int_dict', make_str_int_dict)
...         self.add_class(NamedDie, ('str', 'str_list', 'str_int_dict', 'int'),
...                        auto_detect_kwargs=False, kwargs=('oops', 'wrong', 'not_enough'))

>>> die_str = 'NamedDie("Tom", ["Dick", "Harry"], {"friends": 2, "coolness_factor": 10}, 4)'
>>> t_d_and_h_4_eva = NamedDie('Tom', ['Dick', 'Harry'], {'friends': 2, 'coolness_factor': 10}, 4)
>>> MyParser().parse_die(die_str) == t_d_and_h_4_eva
True
>>> upper_lower_who_cares = 'nAmeDdIE("Tom", ["Dick", "Harry"], {"friends": 2, "coolness_factor": 10}, 4)'
>>> MyParser(ignore_case=True).parse_die(upper_lower_who_cares) == t_d_and_h_4_eva
True
>>> with_kwargs = 'NamedDie("Tom", ["D", "H"], stats={}, size=4)'
>>> MyParser().parse_die(with_kwargs)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ParseError: One or more kwargs not in kwarg_list: ('oops', 'wrong', 'not_enough') for die: <NamedDie>

Limiting Max Values
-------------------

You can make the parser enforce limits with :meth:`Parser.parse_die_within_limits`. This uses the limits
declared in :meth:`Parser.__init__` (and two for DicePool not in the `init`. see: `Limits and DicePool objects`_).
It limits the size, explosions and number of nested dice in a die.

The size is limited according to the `die_size` parameter or the max value of the `dictionary_input` parameter.
The explosions is limited according to `explosions` parameter and the `len` of the `explodes_on` parameter. The number
of nested dice is limited according to how many times the parser has to make a die while creating the die.
:code:`StrongDie(Exploding(Die(4)), 3)` is a `StrongDie` containing two nested dice.

.. _`kwargs issue`:

The number of nested dice is calculated according to how many times :meth:`Parser.make_die` is called.
In order to check the size and explosions, the parser must know what parameter name is assigned to values that
control size and explosions. It recognizes the following kwarg names:

- 'die_size'
- 'dictionary_input'
- 'explosions'
- 'explodes_on'
- 'input_die'
- 'pool_size'

If you make a die that doesn't use these key-word arguments, the parser will have no way to check limits for you and
will simply parse the die string.

ex:

>>> dt.Parser().parse_die_within_limits('Die(500)')
Die(500)
>>> dt.Parser().parse_die_within_limits('Die(501)')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
LimitsError: Max die_size: 500
>>> stupid = 'StrongDie(' * 20 + 'Die(5)' + ', 2)' * 20
>>> dt.Parser().parse_die_within_limits(stupid)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
LimitsError: Max number of nested dice: 5

>>> class NewDie(dt.Die):
...    def __init__(self, funky_new_die_size=6):
...        super(NewDie, self).__init__(funky_new_die_size)
...
...    def __repr__(self):
...        return 'NewDie({})'.format(self.get_size())

>>> parser = dt.Parser()
>>> parser.add_class(NewDie, ('int',))

>>> parser.parse_die_within_limits('NewDie(5000)')
NewDie(5000)
>>> parser.parse_die_within_limits('Die(5000)')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
LimitsError: Max die_size: 500

You can add your new and exciting key-words to the parser with :meth:`Parser.add_limits_kwarg`.
If this has a default value, you can add that too.

>>> new_parser = dt.Parser()
>>> new_parser.add_class(NewDie, ('int',))
>>> new_parser.add_limits_kwarg('size', 'funky_new_die_size', default=6)

>>> new_parser.parse_die_within_limits('NewDie(5000)')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
LimitsError: Max die_size: 500
>>> new_parser.parse_die_within_limits('Die(5000)')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
LimitsError: Max die_size: 500

>>> new_parser.parse_die_within_limits('NewDie()')
NewDie(6)
>>> new_parser.max_size = 5
>>> new_parser.parse_die_within_limits('NewDie()')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
LimitsError: Max die_size: 5

The parser only knows how to evaluate size based on a parameter that represents size as an `int` or dictionary of
`{int: int}` where the size is the highest key value. Similarly, the parser assumes that it can count the explosions
by evaluating an `int` or the length of a `list` or `tuple`. If these are not the case, you will need to delve into the
code and over-ride :meth:`Parser._check_die_size`, :meth:`Parser._check_explosions` or :meth:`Parser._check_limits`

>>> class NewDie(dt.Die):
...    def __init__(self, size_int_as_str):
...        super(NewDie, self).__init__(int(size_int_as_str))

>>> def make_string(str_node):
...     return str_node.s

>>> parser = dt.Parser()
>>> parser.add_param_type('string', make_string)
>>> parser.add_class(NewDie, ('string',))
>>> parser.add_limits_kwarg('size', 'size_int_as_str')

>>> parser.parse_die('NewDie("5")') == NewDie("5")
True
>>> parser.parse_die_within_limits('NewDie("5")')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ValueError: A kwarg declared as a "die size limit" is neither an int nor a dict of ints.

and **a** solution

>>> class NewParser(dt.Parser):
...     def _check_die_size(self, die_size_param):
...         if isinstance(die_size_param, str):
...             die_size_param = int(die_size_param)
...         super(NewParser, self)._check_die_size(die_size_param)
...
>>> parser = NewParser()
>>> parser.add_param_type('string', make_string)
>>> parser.add_class(NewDie, ('string',))
>>> parser.add_limits_kwarg('size', 'size_int_as_str')

>>> parser.parse_die_within_limits('NewDie("5000")')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
LimitsError: Max die_size: 500
>>> parser.parse_die_within_limits('Die(5000)')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
LimitsError: Max die_size: 500

Limits and DicePool Objects
---------------------------

DicePool can take a surprisingly long time to calculate. See the :ref:`Dice-Pools-Section` for a proper explanation.
Suffice it to say that the limits on any DicePool can be determined by :code:`len(input_die.get_dict())` and
:code:`pool_size`. The parser uses a dictionary of {max_dict_len: max_unique_combination_keys} at
:code:`Parser().max_dice_pool_combinations_per_dict_size`. This is determined from the input_die using,
:func:`dicetables.tools.orderedcombinations.count_unique_combination_keys(events, pool_size)`. The current dictionary
was determined using the extremely scientific approach of "trying different things and seeing how long they took". This
is likely going to be different with whatever computer you will be using. That's why this a public variable.

The other variable is :code:`Parser().max_dice_pool_calls`, currently set to "2". This is separate from
`max_nested_dice`. A dice pool call is still counted against nested dice.

>>> parser = dt.Parser(max_nested_dice=3)
>>> two_pools_three_nested_dice = 'BestOfDicePool(StrongDie(WorstOfDicePool(Die(2), 3, 2), 2), 3, 2)'
>>> parser.parse_die_within_limits(two_pools_three_nested_dice)
BestOfDicePool(StrongDie(WorstOfDicePool(Die(2), 3, 2), 2), 3, 2)
>>> three_pools = 'three_calls = BestOfDicePool(BestOfDicePool(WorstOfDicePool(Die(2), 3, 2), 3, 2), 3, 2)'
>>> parser.parse_die_within_limits(three_pools)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
LimitsError: Max number of DicePool objects: 2
>>> four_nested_dice = 'BestOfDicePool(StrongDie(StrongDie(StrongDie(Die(2), 2), 2), 2), 2, 2)'
>>> parser.parse_die_within_limits(four_nested_dice)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
LimitsError: Max number of nested dice: 3

With the current limits in place,
an implementation of a dice pool could take up to 0.5s. If five calls were allowed, that would be 2.5s to parse a
single die. It is hard to imagine any practical reason to use more than one pool.
:code:`BestOfDicePool(WorstOfDicePool(Die(6), 4, 3), 2, 1)` would mean: "Roll 4D6 and take the worst three. Do that
twice and take the best one". If the current limit of two feels too limiting, change it.

Just as in `kwargs issue`_, the parser looks for the key-word arguments: "input_die" and "pool_size"
to figure things out. If you make a new DicePool that doesn't use these variable names, you'll need to tell the
parser.  use the methods: :meth:`Parser.add_limits_kwarg` with the appropriate `existing_key`.
