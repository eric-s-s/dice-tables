import ast

from dicetables.eventsbases.protodie import ProtoDie
from dicetables.dieevents import Die, ModDie, Modifier, ModWeightedDie, WeightedDie, StrongDie, Exploding, ExplodingOn
from dicetables.bestworstmid import DicePool, BestOfDicePool, WorstOfDicePool, UpperMidOfDicePool, LowerMidOfDicePool
from dicetables.tools.orderedcombinations import count_unique_combination_keys, largest_permitted_pool_size


class ParseError(ValueError):
    def __init__(self, *args):
        super(ParseError, self).__init__(*args)


class LimitsError(ValueError):
    def __init__(self, *args):
        super(LimitsError, self).__init__(*args)


class Parser(object):
    def __init__(self, ignore_case=False, disable_kwargs=False, max_size=500, max_explosions=10, max_nested_dice=5):
        """

        :param ignore_case: False: Can the parser ignore case on die names and kwargs.
        :param disable_kwargs: False: Is the ability to parse kwargs disabled.
        :param max_size: 500: The maximum allowed die size when :code:`parse_die_within_limits`
        :param max_explosions: 10: The maximum allowed (explosions + len(explodes_on)) when
            :code:`parse_die_within_limits`
        :param max_nested_dice: 5: The maximum number of nested dice beyond first when :code:`parse_die_within_limits`.
            Ex: :code:`StrongDie(Exploding(Die(5), 2), 3)` has 2 nested dice.

        For explanation of how or why to change `max_dice_pool_combinations_per_dict_size`, and
        `max_dice_pool_calls`, see
        `Parser <http://dice-tables.readthedocs.io/en/latest/implementation_details/parser.html#limits-and-dicepool-objects>`_
        """
        self._classes = {Die: ('int',), ModDie: ('int', 'int'), Modifier: ('int',),
                         ModWeightedDie: ('int_dict', 'int'), WeightedDie: ('int_dict',),
                         StrongDie: ('die', 'int'), Exploding: ('die', 'int'),
                         ExplodingOn: ('die', 'int_tuple', 'int'), BestOfDicePool: ('die', 'int', 'int'),
                         WorstOfDicePool: ('die', 'int', 'int'), UpperMidOfDicePool: ('die', 'int', 'int'),
                         LowerMidOfDicePool: ('die', 'int', 'int')}
        self._param_types = {'int': make_int, 'int_dict': make_int_dict,
                             'die': self.make_die, 'int_tuple': make_int_tuple}

        self._kwargs = {Die: ('die_size',), ModDie: ('die_size', 'modifier'), Modifier: ('modifier',),
                        ModWeightedDie: ('dictionary_input', 'modifier'), WeightedDie: ('dictionary_input',),
                        StrongDie: ('input_die', 'multiplier'), Exploding: ('input_die', 'explosions'),
                        ExplodingOn: ('input_die', 'explodes_on', 'explosions'),
                        BestOfDicePool: ('input_die', 'pool_size', 'select'),
                        WorstOfDicePool: ('input_die', 'pool_size', 'select'),
                        UpperMidOfDicePool: ('input_die', 'pool_size', 'select'),
                        LowerMidOfDicePool: ('input_die', 'pool_size', 'select')}

        self._limits_values = {'size': [('die_size', None), ('dictionary_input', None)],
                               'explosions': [('explosions', 2)],
                               'explodes_on': [('explodes_on', None)],
                               'input_die': [('input_die', None)],
                               'pool_size': [('pool_size', None)]}

        self.ignore_case = ignore_case
        self.disable_kwargs = disable_kwargs
        self.max_size = max_size
        self.max_explosions = max_explosions
        self.max_nested_dice = max_nested_dice

        self.max_dice_pool_combinations_per_dict_size = {
            2: 600, 3: 8700, 4: 30000, 5: 55000, 6: 70000,
            7: 100000, 12: 200000, 30: 250000
        }
        self.max_dice_pool_calls = 2

        self._nested_dice_counter = 0
        self._dice_pool_counter = 0
        self._use_limits = False

    @property
    def param_types(self):
        return self._param_types.copy()

    @property
    def classes(self):
        return self._classes.copy()

    @property
    def kwargs(self):
        return self._kwargs.copy()

    @property
    def limits_kwargs(self):
        return self._limits_values.copy()

    def parse_die(self, die_string):
        die_string = die_string.strip()
        ast_call_node = ast.parse(die_string).body[0].value

        self._use_limits = False
        return self.make_die(ast_call_node)

    def parse_die_within_limits(self, die_string):
        """
        Checks to see if limits are exceeded. If not, parses string. This only works with die classes that contain the
        following key-word arguments:

        - die_size
        - dictionary_input
        - explosions
        - explodes_on
        - input_die AND pool_size

        If your die classes use different kwargs to describe any of the above, they will
        be parsed as if there were no limits. You may register those kwargs (and any default value) with
        :code:`add_limits_kwarg`.
        """
        die_string = die_string.strip()
        ast_call_node = ast.parse(die_string).body[0].value

        self._use_limits = True
        self._nested_dice_counter = 0
        self._dice_pool_counter = 0

        die = self.make_die(ast_call_node)

        return die

    def make_die(self, call_node):
        die_class_name = call_node.func.id
        param_nodes = call_node.args
        kwarg_nodes = call_node.keywords
        die_class = self._get_die_class(die_class_name)
        die_params = self._get_params(param_nodes, die_class)
        die_kwargs = self._get_kwargs(kwarg_nodes, die_class)
        if self._use_limits:
            self._check_limits(die_class, die_params, die_kwargs)
        return die_class(*die_params, **die_kwargs)

    def _get_die_class(self, class_name):
        class_name = self._update_search_string(class_name)
        for die_class in self._classes.keys():
            test_against = self._update_search_string(die_class.__name__)
            if class_name == test_against:
                return die_class
        raise ParseError('Die class: <{}> not recognized by parser.'.format(class_name))

    def _update_search_string(self, search_str):
        if self.ignore_case:
            return search_str.lower()
        return search_str

    def _get_params(self, param_nodes, die_class):
        params = []
        param_types = self._classes[die_class]
        self._raise_error_for_missing_methods(param_types, die_class)
        for index, node in enumerate(param_nodes):
            type_key = param_types[index]
            conversion_method = self._param_types[type_key]
            params.append(conversion_method(node))
        return params

    def _raise_error_for_missing_methods(self, param_types, die_class):
        if any(type_key not in self._param_types for type_key in param_types):
            raise ParseError('Failed to create die: <{}> with param types: {}. One or more param types not recognized.'
                             .format(die_class.__name__, param_types))

    def _get_kwargs(self, kwarg_nodes, die_class):
        out = {}
        self._raise_error_for_kwargs_not_allowed(kwarg_nodes)
        self._raise_error_for_bad_kwarg(kwarg_nodes, die_class)
        for kwarg_node in kwarg_nodes:
            kwarg_name, value = self._get_kwarg_value(die_class, kwarg_node)
            out[kwarg_name] = value
        return out

    def _raise_error_for_kwargs_not_allowed(self, kwarg_nodes_list):
        if self.disable_kwargs and kwarg_nodes_list:
            raise ParseError('Tried to use kwargs on a Parser with disable_kwargs=True')

    def _raise_error_for_bad_kwarg(self, kwarg_nodes, die_class):
        die_kwargs = self._update_search_tuple(self._kwargs[die_class])
        if any(self._update_search_string(node.arg) not in die_kwargs for node in kwarg_nodes):
            raise ParseError('One or more kwargs not in kwarg_list: {} for die: <{}>'.format(
                die_kwargs, die_class.__name__))

    def _update_search_tuple(self, search_tuple):
        return tuple(map(self._update_search_string, search_tuple))

    def _get_kwarg_value(self, die_class, kwarg_node):
        kwarg_name_to_search_for = self._update_search_string(kwarg_node.arg)
        value_node = kwarg_node.value

        class_param_types = self._classes[die_class]
        true_kwarg_names = self._kwargs[die_class]
        kwarg_names_to_search = self._update_search_tuple(true_kwarg_names)

        index = kwarg_names_to_search.index(kwarg_name_to_search_for)

        kwarg_type = class_param_types[index]
        value = self._param_types[kwarg_type](value_node)

        true_kwarg_name = true_kwarg_names[index]
        return true_kwarg_name, value

    def _check_limits(self, die_class, die_params, die_kwargs):
        self._check_then_update_nested_calls()

        if issubclass(die_class, DicePool):
            self._update_then_check_dice_pool_calls()
            input_die = self._get_limits_params('input_die', die_class, die_params, die_kwargs)
            pool_size = self._get_limits_params('pool_size', die_class, die_params, die_kwargs)
            self._check_dice_pool(input_die, pool_size)

        size_param = self._get_limits_params('size', die_class, die_params, die_kwargs)
        explosions_param = self._get_limits_params('explosions', die_class, die_params, die_kwargs)
        explodes_on_param = self._get_limits_params('explodes_on', die_class, die_params, die_kwargs)
        self._check_die_size(size_param)
        self._check_explosions(explosions_param, explodes_on_param)

    def _check_then_update_nested_calls(self):
        if self._nested_dice_counter > self.max_nested_dice:
            msg = 'Max number of nested dice: {}'.format(self.max_nested_dice)
            raise LimitsError(msg)
        self._nested_dice_counter += 1

    def _update_then_check_dice_pool_calls(self):
        self._dice_pool_counter += 1
        if self._dice_pool_counter > self.max_dice_pool_calls:
            msg = 'Max number of DicePool objects: {}'.format(self.max_dice_pool_calls)
            raise LimitsError(msg)

    def _get_limits_params(self, param_types, die_class, die_params, die_kwargs):
        limits_kw_default = self._limits_values[param_types]
        class_kwargs = self._kwargs[die_class]
        for kwarg_name, default in limits_kw_default:
            if kwarg_name in class_kwargs:
                index = class_kwargs.index(kwarg_name)
                if len(die_params) > index:
                    return die_params[index]
                else:
                    return die_kwargs.get(kwarg_name, default)

        return None

    def _check_die_size(self, die_size_param):

        if die_size_param is None:
            return None

        if isinstance(die_size_param, int):
            size_value = die_size_param
        elif isinstance(die_size_param, dict):
            size_value = max(die_size_param.keys())
        else:
            msg = 'A kwarg declared as a "die size limit" is neither an int nor a dict of ints.'
            raise ValueError(msg)

        if size_value > self.max_size:
            msg = 'Max die_size: {}'.format(self.max_size)
            raise LimitsError(msg)

    def _check_explosions(self, explosions, explodes_on):
        explosions_value = 0
        if explosions is not None:
            if not isinstance(explosions, int):
                raise ValueError('A kwarg declared as an "explosions" is not an int.')
            explosions_value += explosions

        if explodes_on is not None:
            if not isinstance(explodes_on, (tuple, list)):
                raise ValueError('A kwarg declared as an "explodes_on" is not a tuple.')
            explosions_value += len(explodes_on)

        if explosions_value > self.max_explosions:
            msg = 'Max number of explosions + len(explodes_on): {}'.format(self.max_explosions)
            raise LimitsError(msg)

    def _check_dice_pool(self, input_die, pool_size):
        if not isinstance(input_die, ProtoDie):
            raise ValueError('A kwarg declared as an "input_die" does not inherit from ProtoDie.')
        if not isinstance(pool_size, int):
            raise ValueError('A kwarg declared as a "pool_size" is not an int.')

        dict_size = len(input_die.get_dict())
        pool_limit = 0
        for key, limit in sorted(self.max_dice_pool_combinations_per_dict_size.items()):
            if key > dict_size:
                break
            pool_limit = limit

        score = count_unique_combination_keys(input_die, pool_size)
        if score > pool_limit:
            max_pool_size = largest_permitted_pool_size(input_die, pool_limit)
            msg = '{!r} has a get_dict() of size: {}\n'.format(input_die, dict_size)
            explanation = 'For this die, the largest permitted pool_size is {}'.format(max_pool_size)
            raise LimitsError(msg + explanation)

    def add_class(self, class_, param_identifiers, auto_detect_kwargs=True, kwargs=()):
        """

        :param class_: the class you are adding
        :param param_identifiers: a tuple of param_types according to Parser().param_types. Defaults are:
            'int', 'die', 'int_dict', 'int_tuple'
        :param auto_detect_kwargs: will try to detect kwargs of __init__ function. overrides kwargs param
        :param kwargs: (optional) a tuple of the kwarg names for instantiation of the new class.
        """
        self._classes[class_] = param_identifiers
        if auto_detect_kwargs:
            kwargs = _get_kwargs_from_init(class_)
        self._kwargs[class_] = kwargs

    def add_param_type(self, param_type, creation_method):
        self._param_types[param_type] = creation_method

    def add_limits_kwarg(self, existing_key, new_key_word, default=None):
        """
        If there is a default value and you do not add it or you add the incorrect one,
        `parse_within_limits` will fail.

        current keys are:

        - 'size'
        - 'explosions'
        - 'explodes_on'
        - 'input_die'
        - 'pool_size'
        """
        if existing_key not in self._limits_values.keys():
            raise KeyError('key: "{}" not in self.limits_kwargs. Use add_limits_key.'.format(existing_key))
        self._limits_values[existing_key].append((new_key_word, default))

    def add_limits_key(self, new_key):
        if new_key in self._limits_values.keys():
            raise ValueError('Tried to add existing key to self.limits_kwargs.')
        self._limits_values[new_key] = []


def make_int_dict(dict_node):
    keys = make_int_list(dict_node.keys)
    values = make_int_list(dict_node.values)
    return dict(zip(keys, values))


def make_int_tuple(tuple_node):
    return tuple(make_int_list(tuple_node.elts))


def make_int_list(num_node_list):
    return [make_int(num_node) for num_node in num_node_list]


def make_int(num_node):
    if isinstance(num_node, ast.UnaryOp) and isinstance(num_node.op, ast.USub):
        return num_node.operand.n * -1
    return num_node.n


def _get_kwargs_from_init(class_):
    try:
        kwargs = class_.__init__.__code__.co_varnames
        return kwargs[1:]
    except AttributeError:
        raise AttributeError('could not find the code for __init__ function at class_.__init__.__code__')
