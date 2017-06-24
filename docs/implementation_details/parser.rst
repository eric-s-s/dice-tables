Parser
======

.. module:: dicetables.parser

.. autoclass:: Parser
    :members:
    :undoc-members:


    The Parser object converts strings into dice objects.

    >>> import dicetables as dt
    >>> new_die = dt.Parser().parse_die('Die(6)')
    >>> new_die == dt.Die(6)
    True
    >>> other_die = dt.Parser().parse_die('ModDie(6, modifier=1)')
    >>> other_die == dt.ModDie(6, 1)
    True

    It can ignore case or not.  This applies to dice names and kwarg names. It defaults to ignore_case=False.
    You can also disable allowing kwargs. It defaults to disable_kwargs=False.

    >>> dt.Parser().parse_die('die(6)')
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    ParseError: Die class: <die> not recognized by parser.

    >>> dt.Parser(ignore_case=True).parse_die('stronGdie(dIE(6), MULTIPLIER=4)') == dt.StrongDie(dt.Die(6), 4)
    True

    >>> parser = dt.Parser(disable_kwargs=True)
    >>> parser.parse_die('Die(6)') == dt.Die(6)
    True
    >>> parser.parse_die('Die(die_size=6)')
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    ParseError: Tried to use kwargs on a Parser with disable_kwargs=True

    The Parser can parse all dice in the library: Die, ModDie, WeightedDie, ModWeightedDie, Modifier, StrongDie,
    Exploding and ExplodingOn. It is possible to add other dice to an instance of Parser or make a new class that
    can parse other dice.

**HOW TO CUSTOMIZE PARSER**

Parser can only parse very specific types of parameters.

>>> from dicetables.parser import make_int, make_int_dict, make_int_tuple
>>> parser = dt.Parser()
>>> parser.get_param_types() == {'int': make_int, 'int_dict': make_int_dict,
...                              'die': parser.make_die, 'int_tuple': make_int_tuple}
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
>>> parser.parse_die(die_str) == NamedDie('Tom', ['Dick', 'Harry'], {'friends': 2, 'coolness_factor': 10}, 4)
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
>>> MyParser().parse_die(die_str) == NamedDie('Tom', ['Dick', 'Harry'], {'friends': 2, 'coolness_factor': 10}, 4)
True
>>> upper_lower_who_cares = 'nAmeDdIE("Tom", ["Dick", "Harry"], {"friends": 2, "coolness_factor": 10}, 4)'
>>> t_d_and_h_4_eva = MyParser(ignore_case=True).parse_die(upper_lower_who_cares)
>>> t_d_and_h_4_eva == NamedDie('Tom', ['Dick', 'Harry'], {'friends': 2, 'coolness_factor': 10}, 4)
True
>>> with_kwargs = 'NamedDie("Tom", ["D", "H"], stats={}, size=4)'
>>> MyParser().parse_die(with_kwargs)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ParseError: One or more kwargs not in kwarg_list: ('oops', 'wrong', 'not_enough') for die: <NamedDie>