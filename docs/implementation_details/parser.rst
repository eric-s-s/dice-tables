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

    >>> dt.Parser().parse_die('die(6)')
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    ParseError: Die class: <die> not recognized by parser.

    >>> dt.Parser(ignore_case=True).parse_die('stronGdie(dIE(6), MULTIPLIER=4)')
    StrongDie(Die(6), 4)

    The Parser can parse all dice in the library: Die, ModDie, WeightedDie, ModWeightedDie, Modifier, StrongDie,
    Exploding, ExplodingOn and all of the DicePools. It is possible to add other dice to an instance of
    Parser or make a new class that can parse other dice.

Customizing Parser
------------------

Parser can only parse very specific types of parameters.

>>> from dicetables.parser import make_int, make_int_dict, make_int_tuple
>>> from typing import Dict, Iterable
>>> from dicetables.eventsbases.protodie import ProtoDie
>>> parser = dt.Parser()
>>> parser.param_types == {int: make_int, Dict[int, int]: make_int_dict, dt.DicePool: parser.make_pool,
...                        ProtoDie: parser.make_die, Iterable[int]: make_int_tuple}
True

If, for example, you need Parser to know how to parse a string, a list of strings and
dictionary of keys=str: values=int, you first need to create functions that can parse
the appropriate Nodes. Then you assign the functions to the parser.

    First, a very very quick introduction to the Abstract Syntax Tree:

    The nodes are derived using the `ast <https://docs.python.org/3/library/ast.html>`_
    module. ast, very briefly, takes a string and parses it into nodes. To see what
    it does, use :code:`ast.dump(ast.parse(<your_string>))`.  Create and test nodes by using
    :code:`my_node = ast.parse(<your_string>).body[0].value`

    Note that before py3.8 the elipsis below will be classes "Num" and "Str".
    After 3.8 they are "Constant".

    >>> import ast
    >>> ast.dump(ast.parse('{1: "a", 2: "b"}'))
    "Module(body=[Expr(value=Dict(keys=[...], values=[...]))]...)"
    >>> my_list_node = ast.parse('[1, "A"]').body[0].value
    >>> ast.dump(my_list_node)
    "List(elts=[...], ctx=Load())"

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
Notice that we are specifically setting the typing to List and not Iterable.  If we also
want to be able to handle `Iterable[str]`, we will need to explicitly add that. Our use-case takes a list
and copies it.  That requires a `List`. But the case where we just need an iterable would be different.

>>> from typing import List
>>> parser = dt.Parser()
>>> parser.add_param_type(str, make_str)
>>> parser.add_param_type(List[str], make_str_list)
>>> parser.add_param_type(Dict[str, int], make_str_int_dict)

To add a new dice class to the parser, give the parser the class and a tuple of the param_types keys for each parameter.
The parser will assume you're adding a class with an __init__ function and will try to auto_detect kwargs. You can
disable this and add your own kwargs (or not).

To add a new dice class to the parser, **you must use type hints**. The parser uses the annotations in the `__init__`
to parse a die

>>> class NamedDie(dt.Die):
...     def __init__(self, name: str, buddys_names: List[str], stats: Dict[str, int], size: int):
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

>>> parser.add_class(NamedDie)
>>> die_str = 'NamedDie("Tom", ["Dick", "Harry"], stats={"friends": 2, "coolness_factor": 10}, size=4)'
>>> die = NamedDie('Tom', ['Dick', 'Harry'], {'friends': 2, 'coolness_factor': 10}, 4)
>>> parser.parse_die(die_str) == die
True

You can make a new parser class instead of a specific instance of Parser.

>>> class MyParser(dt.Parser):
...     def __init__(self, ignore_case=False):
...         super(MyParser, self).__init__(ignore_case)
...         self.add_param_type(str, make_str)
...         self.add_param_type(List[str], make_str_list)
...         self.add_param_type(Dict[str, int], make_str_int_dict)
...         self.add_class(NamedDie)

>>> die_str = 'NamedDie("Tom", ["Dick", "Harry"], {"friends": 2, "coolness_factor": 10}, 4)'
>>> t_d_and_h_4_eva = NamedDie('Tom', ['Dick', 'Harry'], {'friends': 2, 'coolness_factor': 10}, 4)
>>> MyParser().parse_die(die_str) == t_d_and_h_4_eva
True
>>> upper_lower_who_cares = 'nAmeDdIE("Tom", ["Dick", "Harry"], stats={"friends": 2, "coolness_factor": 10}, size=4)'
>>> MyParser(ignore_case=True).parse_die(upper_lower_who_cares) == t_d_and_h_4_eva
True

Limiting Max Values
-------------------

A parser is instantiated with a :class:`dicetables.tools.limit_checker.AbstractLimitChecker`.

.. autoclass:: dicetables.tools.limit_checker.AbstractLimitChecker
    :members:
    :undoc-members:

The default limit checker is a `NoOpLimitChecker` which does not check limits. If you use the
factory function, :meth:`Parser.with_limits`, you will create a parser that uses a
:class:`dicetables.tools.limit_checker.LimitChecker`.

The size is limited according to the `die_size` parameter or the max value of the `dictionary_input` parameter.
The explosions is limited according to `explosions` parameter and the `len` of the `explodes_on` parameter. The number
of nested dice is limited according to how many times the parser has to make a die while creating the die.
:code:`StrongDie(Exploding(Die(4)), 3)` has three calls.

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

>>> parser = dt.Parser.with_limits()
>>> parser.parse_die('Die(500)')
Die(500)
>>> parser.parse_die('Die(501)')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
LimitsError: Max die_size: 500
>>> stupid = 'StrongDie(' * 20 + 'Die(5)' + ', 2)' * 20
>>> parser.parse_die(stupid)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
LimitsError: Limits exceeded. Max dice calls: 6.

>>> class NewDie(dt.Die):
...    def __init__(self, funky_new_die_size: int = 6):
...        super(NewDie, self).__init__(funky_new_die_size)
...
...    def __repr__(self):
...        return 'NewDie({})'.format(self.get_size())

>>> parser = dt.Parser.with_limits()
>>> parser.add_class(NewDie)

>>> parser.parse_die('NewDie(5000)')
NewDie(5000)
>>> parser.parse_die('Die(5000)')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
LimitsError: Limits exceeded. Max dice calls: 6.

In order to make sure your new and exciting key-word gets checked, you'll need to subclass the Limit Checker

>>> from dicetables.tools.limit_checker import LimitChecker, LimitsError
>>> from inspect import BoundArguments
>>> def get_new_size_args(bound_args):
...     return bound_args.arguments.get("funky_new_die_size")

>>> class MyChecker(LimitChecker):
...     def assert_die_size_within_limits(self, bound_args: BoundArguments) -> None:
...         super(MyChecker, self).assert_die_size_within_limits(bound_args)
...         new_size_arg = get_new_size_args(bound_args)
...         if new_size_arg and new_size_arg > self.max_size:
...             raise LimitsError("your funky new die size is too funky fresh for this parser")

>>> new_parser = dt.Parser(checker=MyChecker())
>>> new_parser.add_class(NewDie)

>>> new_parser.parse_die('NewDie(5000)')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
LimitsError: your funky new die size ...
>>> new_parser.parse_die('Die(5000)')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
LimitsError: Limits exceeded. Max dice calls: 6.

Limits and DicePool Objects
---------------------------

DicePool can take a surprisingly long time to calculate. See the :ref:`Dice-Pools-Section` for a proper explanation.
Suffice it to say that the limits on any DicePool can be determined by :code:`len(input_die.get_dict())` and
:code:`pool_size`. The parser uses a dictionary of {max_dict_len: max_unique_combination_keys} at
:code:`Parser().max_dice_pool_combinations_per_dict_size`. This is determined from the input_die using,
:func:`dicetables.tools.orderedcombinations.count_unique_combination_keys(events, pool_size)`. The current dictionary
was determined using the extremely scientific approach of "trying different things and seeing how long they took". This
is likely going to be different with whatever computer you will be using. That's why this a public variable.

The other variable is :code:`Parser.with_limits().checker.max_dice_pools`, currently set to "2".
This is separate from `max_nested_dice`. This checks the number of calls to construct a :code:`Dicepool`
The sheer unreadability of nested dice pools does beg the question of why you would ever want to do this.

>>> parser = dt.Parser.with_limits(max_dice=4)
>>> two_pools_three_dice = 'BestOfDicePool(DicePool(StrongDie(WorstOfDicePool(DicePool(Die(2), 3), 2), 2), 3), 2)'
>>> parser.parse_die(two_pools_three_dice)
BestOfDicePool(DicePool(StrongDie(WorstOfDicePool(DicePool(Die(2), 3), 2), 2), 3), 2)
>>> three_pools = 'BestOfDicePool(DicePool(BestOfDicePool(DicePool(WorstOfDicePool(DicePool(Die(2), 3), 2), 3), 2), 4), 3)'
>>> parser.parse_die(three_pools)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
LimitsError: "Limits exceeded. Max dice calls: 4. Max dice pool calls: 2 ...
>>> five_dice = 'BestOfDicePool(DicePool(StrongDie(StrongDie(StrongDie(Die(2), 2), 2), 2), 2), 2)'
>>> parser.parse_die(five_dice)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
LimitsError: "Limits exceeded. Max dice calls: 4. Max dice pool calls: 2 ...

With the current limits in place,
an implementation of a dice pool could take up to 0.5s. If five calls were allowed, that would be 2.5s to parse a
single die. It is hard to imagine any practical reason to use more than one pool.
:code:`BestOfDicePool(DicePool(WorstOfDicePool(DicePool(Die(6), 4), 3), 2), 1)` would mean:
"Roll 4D6 and take the worst three. Do that
twice and take the best one". If the current limit of two feels too limiting, change it.
