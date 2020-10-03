import ast
from typing import Dict, Tuple, get_type_hints, List, Iterable
from inspect import signature, _empty, BoundArguments, Signature

from dicetables.bestworstmid import DicePool, BestOfDicePool, WorstOfDicePool, UpperMidOfDicePool, LowerMidOfDicePool
from dicetables.dieevents import Die, ModDie, Modifier, ModWeightedDie, WeightedDie, StrongDie, Exploding, ExplodingOn
from dicetables.eventsbases.protodie import ProtoDie
from dicetables.tools.limit_checker import AbstractLimitChecker, NoOpLimitChecker
from dicetables.tools.orderedcombinations import count_unique_combination_keys, largest_permitted_pool_size

from dicetables.parser import ParseError, LimitsError



# TODO



class NewParser(object):
    def __init__(self, ignore_case=False, checker: AbstractLimitChecker=NoOpLimitChecker()):
        pass
    @classmethod
    def with_limits(cls, ignore_case=False, max_size=500, max_explosions=10, max_nested_dice=5):
        """

        :param ignore_case: False: Can the parser ignore case on die names and kwargs.
        :param max_size: 500: The maximum allowed die size when :code:`parse_die_within_limits`
        :param max_explosions: 10: The maximum allowed (explosions + len(explodes_on)) when
            :code:`parse_die_within_limits`
        :param max_nested_dice: 5: The maximum number of nested dice beyond first when :code:`parse_die_within_limits`.
            Ex: :code:`StrongDie(Exploding(Die(5), 2), 3)` has 2 nested dice.

        For explanation of how or why to change `max_dice_pool_combinations_per_dict_size`, and
        `max_dice_pool_calls`, see
        `Parser <http://dice-tables.readthedocs.io/en/latest/implementation_details/parser.html#limits-and-dicepool-objects>`_
        """
        self._classes = {Die, ModDie, Modifier,
                         ModWeightedDie, WeightedDie,
                         StrongDie, Exploding,
                         ExplodingOn, BestOfDicePool,
                         WorstOfDicePool, UpperMidOfDicePool,
                         LowerMidOfDicePool}
        self._param_types = {int: make_int, Dict[int, int]: make_int_dict,
                             ProtoDie: self.make_die, Iterable[int]: make_int_tuple}

        self._limits_kwargs = {'size': ['die_size', 'dictionary_input'],
                               'explosions': ['explosions'],
                               'explodes_on': ['explodes_on'],
                               'input_die': ['input_die'],
                               'pool_size': ['pool_size']}
        self.ignore_case = ignore_case

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

    def make_die(self, call_node: ast.Call):
        die_class_name = call_node.func.id
        param_nodes = call_node.args
        kwarg_nodes = call_node.keywords
        die_class = self._get_die_class(die_class_name)

        instance_for_signature = die_class.__new__(die_class)
        die_signature = signature(instance_for_signature.__init__)

        self._raise_error_for_missing_type(die_signature)
        die_params = self._get_params(param_nodes, die_signature)
        die_kwargs = self._get_kwargs(kwarg_nodes, die_signature)

        bound_args = die_signature.bind(*die_params, **die_kwargs)
        bound_args.apply_defaults()

        if self._use_limits:
            self._check_limits(die_class, bound_args)
        return die_class(*die_params, **die_kwargs)

    def walk_dice_calls(self, call_node: ast.AST):
        return (self._get_die_class(node.func.id) for node in ast.walk(call_node) if isinstance(node, ast.Call))

    def _get_die_class(self, class_name):
        class_name = self._update_search_string(class_name)
        for die_class in self._classes:
            test_against = self._update_search_string(die_class.__name__)
            if class_name == test_against:
                return die_class
        raise ParseError('Die class: <{}> not recognized by parser.'.format(class_name))

    def _update_search_string(self, search_str):
        if self.ignore_case:
            return search_str.lower()
        return search_str

    def _get_params(self, param_nodes, die_signature: Signature):
        params = []
        for node, param in zip(param_nodes, die_signature.parameters.values()):
            type_hint = param.annotation
            converter = self._param_types[type_hint]
            params.append(converter(node))
        return params

    def _raise_error_for_missing_type(self, die_signature: Signature):
        if any(param.annotation not in self._param_types for param in die_signature.parameters.values()):
            raise ParseError('The signature: {} has one or more un-recognized param types'
                             .format(die_signature))

    def _get_kwargs(self, kwarg_nodes, die_signature):
        out = {}
        for kwarg_node in kwarg_nodes:
            kwarg_name, value = self._get_kwarg_value(die_signature, kwarg_node)
            out[kwarg_name] = value
        return out

    def _update_search_tuple(self, search_tuple):
        return tuple(map(self._update_search_string, search_tuple))

    def _get_kwarg_value(self, die_signature, kwarg_node):
        kwarg_name_to_search_for = self._update_search_string(kwarg_node.arg)
        value_node = kwarg_node.value

        class_params = die_signature.parameters
        param_mapping = {self._update_search_string(key): value for key, value in class_params.items()}

        try:
            param = param_mapping[kwarg_name_to_search_for]
        except KeyError:
            raise ParseError("The keyword: {} is not in the die signature: {}".format(kwarg_node.arg, die_signature))
        converter = self._param_types[param.annotation]

        return param.name, converter(value_node)

    def _check_limits(self, die_class, bound_args: BoundArguments):
        self._check_then_update_nested_calls()
        self._update_then_check_dice_pool_calls(die_class)

        input_die = self._get_limits_params('input_die', bound_args)
        pool_size = self._get_limits_params('pool_size', bound_args)
        size_or_dict = self._get_limits_params('size', bound_args)
        explosions = self._get_limits_params('explosions', bound_args)
        explodes_on = self._get_limits_params('explodes_on', bound_args)

        self._check_dice_pool(input_die, pool_size)
        self._check_die_size(size_or_dict)
        self._check_explosions(explosions, explodes_on)

    def _check_then_update_nested_calls(self):
        if self._nested_dice_counter > self.max_nested_dice:
            msg = 'Max number of nested dice: {}'.format(self.max_nested_dice)
            raise LimitsError(msg)
        self._nested_dice_counter += 1

    def _update_then_check_dice_pool_calls(self, die_class):
        if issubclass(die_class, DicePool):
            self._dice_pool_counter += 1
            if self._dice_pool_counter > self.max_dice_pool_calls:
                msg = 'Max number of DicePool objects: {}'.format(self.max_dice_pool_calls)
                raise LimitsError(msg)

    def _get_limits_params(self, param_types, bound_args: BoundArguments):
        limit_keywords = self._limits_kwargs[param_types]
        arguments = bound_args.arguments
        for kwarg_name in limit_keywords:
            if kwarg_name in arguments:
                return arguments[kwarg_name]

        return None

    def _check_die_size(self, size_or_dict):

        if size_or_dict is None:
            return None

        if isinstance(size_or_dict, int):
            size_value = size_or_dict
        elif isinstance(size_or_dict, dict):
            size_value = max(size_or_dict.keys())
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
        if input_die is None or pool_size is None:
            return None

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

    def add_class(self, class_: object):
        """

        :param class_: the class you are adding
        """
        new_instance = class_.__new__(class_)
        die_signature = signature(new_instance.__init__)
        self._raise_error_for_missing_annotation(die_signature)
        self._raise_error_for_missing_type(die_signature)
        self._classes.add(class_)

    @staticmethod
    def _raise_error_for_missing_annotation(die_signature: Signature):
        if any(param.annotation == _empty for param in die_signature.parameters.values()):
            raise ParseError(f"The signature: {die_signature} is missing type annotations")

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
        if existing_key not in self._limits_kwargs.keys():
            raise KeyError('key: "{}" not in self.limits_kwargs. Use add_limits_key.'.format(existing_key))
        self._limits_kwargs[existing_key].append((new_key_word, default))

    def add_limits_key(self, new_key):
        if new_key in self._limits_kwargs.keys():
            raise ValueError('Tried to add existing key to self.limits_kwargs.')
        self._limits_kwargs[new_key] = []


def make_int_dict(dict_node):
    keys = _make_int_list(dict_node.keys)
    values = _make_int_list(dict_node.values)
    return dict(zip(keys, values))


def make_int_tuple(tuple_node):
    return tuple(_make_int_list(tuple_node.elts))


def _make_int_list(num_node_list):
    return [make_int(num_node) for num_node in num_node_list]


def make_int(num_node):
    if isinstance(num_node, ast.UnaryOp) and isinstance(num_node.op, ast.USub):
        value = num_node.operand.n * -1
    else:
        value = None
        for key, val in ast.iter_fields(num_node):
            if key != 'kind':
                value = val
    if not isinstance(value, int):
        raise ValueError(f"Expected an integer, but got: {value!r}")
    return value


def _get_kwargs_from_init(class_):
    try:
        kwargs = class_.__init__.__code__.co_varnames
        return kwargs[1:]
    except AttributeError:
        raise AttributeError('could not find the code for __init__ function at class_.__init__.__code__')
