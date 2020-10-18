import ast
from typing import Dict, Iterable, Type
from inspect import signature, _empty, Signature

from dicetables.bestworstmid import (
    BestOfDicePool,
    WorstOfDicePool,
    UpperMidOfDicePool,
    LowerMidOfDicePool,
)
from dicetables.dieevents import (
    Die,
    ModDie,
    Modifier,
    ModWeightedDie,
    WeightedDie,
    StrongDie,
    Exploding,
    ExplodingOn,
)
from dicetables.eventsbases.protodie import ProtoDie
from dicetables.tools.limit_checker import (
    AbstractLimitChecker,
    NoOpLimitChecker,
    LimitChecker,
)

from dicetables.parser import ParseError


class NewParser(object):
    def __init__(
        self,
        ignore_case: bool = False,
        checker: AbstractLimitChecker = NoOpLimitChecker(),
    ):
        self.checker = checker
        self.ignore_case = ignore_case

        self._classes = {
            Die,
            ModDie,
            Modifier,
            ModWeightedDie,
            WeightedDie,
            StrongDie,
            Exploding,
            ExplodingOn,
            BestOfDicePool,
            WorstOfDicePool,
            UpperMidOfDicePool,
            LowerMidOfDicePool,
        }
        self._param_types = {
            int: make_int,
            Dict[int, int]: make_int_dict,
            ProtoDie: self.make_die,
            Iterable[int]: make_int_tuple,
        }

    @classmethod
    def with_limits(
        cls,
        ignore_case: bool = False,
        max_size: int = 500,
        max_explosions: int = 10,
        max_dice: int = 6,
        max_dice_pools: int = 2,
    ) -> "NewParser":
        """

        :param ignore_case: False: Can the parser ignore case on die names and kwargs.
        :param max_size: 500: The maximum allowed die size when :code:`parse_die_within_limits`
        :param max_explosions: 10: The maximum allowed (explosions + len(explodes_on)) when
            :code:`parse_die_within_limits`
        :param max_dice: 6: The maximum number of dice calls when :code:`parse`.
            Ex: :code:`StrongDie(Exploding(Die(5), 2), 3)` has 3 dice calls.
        :param max_dice_pools: 2: The maximum number of allowed dice_pool calls

        For explanation of how or why to change `max_dice_pool_combinations_per_dict_size`, and
        `max_dice_pool_calls`, see
        `Parser <http://dice-tables.readthedocs.io/en/latest/implementation_details/parser.html#limits-and-dicepool-objects>`_
        """
        checker = LimitChecker(
            max_dice_pools=max_dice_pools,
            max_dice=max_dice,
            max_explosions=max_explosions,
            max_size=max_size,
        )
        return cls(ignore_case=ignore_case, checker=checker)

    @property
    def param_types(self):
        return self._param_types.copy()

    @property
    def classes(self):
        return self._classes.copy()

    def parse_die(self, die_string):
        die_string = die_string.strip()
        ast_call_node = ast.parse(die_string).body[0].value

        self.checker.assert_numbers_of_calls_within_limits(
            self.walk_dice_calls(ast_call_node)
        )

        return self.make_die(ast_call_node)

    def make_die(self, call_node: ast.Call):
        die_class_name = call_node.func.id
        param_nodes = call_node.args
        kwarg_nodes = call_node.keywords
        die_class = self._get_die_class(die_class_name)

        instance_for_signature = die_class.__new__(die_class)
        die_signature = signature(instance_for_signature.__init__)

        die_params = self._get_params(param_nodes, die_signature)
        die_kwargs = self._get_kwargs(kwarg_nodes, die_signature)

        bound_args = die_signature.bind(*die_params, **die_kwargs)
        bound_args.apply_defaults()

        self.checker.assert_explosions_within_limits(bound_args)
        self.checker.assert_dice_pool_within_limits(bound_args)
        self.checker.assert_die_size_within_limits(bound_args)

        return die_class(*die_params, **die_kwargs)

    def walk_dice_calls(self, call_node: ast.AST) -> Iterable[Type[ProtoDie]]:
        return (
            self._get_die_class(node.func.id)
            for node in ast.walk(call_node)
            if isinstance(node, ast.Call)
        )

    def _get_die_class(self, class_name):
        class_name = self._update_search_string(class_name)
        for die_class in self._classes:
            test_against = self._update_search_string(die_class.__name__)
            if class_name == test_against:
                return die_class
        raise ParseError("Die class: <{}> not recognized by parser.".format(class_name))

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
        if any(
            param.annotation not in self._param_types
            for param in die_signature.parameters.values()
        ):
            raise ParseError(
                "The signature: {} has one or more un-recognized param types".format(
                    die_signature
                )
            )

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
        param_mapping = {
            self._update_search_string(key): value
            for key, value in class_params.items()
        }

        try:
            param = param_mapping[kwarg_name_to_search_for]
        except KeyError:
            raise ParseError(
                "The keyword: {} is not in the die signature: {}".format(
                    kwarg_node.arg, die_signature
                )
            )
        converter = self._param_types[param.annotation]

        return param.name, converter(value_node)

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
        if any(
            param.annotation == _empty for param in die_signature.parameters.values()
        ):
            raise ParseError(
                f"The signature: {die_signature} is missing type annotations"
            )

    def add_param_type(self, param_type, creation_method):
        self._param_types[param_type] = creation_method


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
            if key != "kind":
                value = val
    if not isinstance(value, int):
        raise ValueError(f"Expected an integer, but got: {value!r}")
    return value


def _get_kwargs_from_init(class_):
    try:
        kwargs = class_.__init__.__code__.co_varnames
        return kwargs[1:]
    except AttributeError:
        raise AttributeError(
            "could not find the code for __init__ function at class_.__init__.__code__"
        )
