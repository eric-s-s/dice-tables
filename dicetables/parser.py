import ast
from typing import Dict, Iterable, Type, Union
from inspect import signature, _empty, Signature

from dicetables.dicepool_collection import (
    BestOfDicePool,
    WorstOfDicePool,
    UpperMidOfDicePool,
    LowerMidOfDicePool,
)
from dicetables.dicepool import DicePool
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


DieOrPool = Union[Type[ProtoDie], Type[DicePool]]


class ParseError(ValueError):
    pass


class Parser(object):
    def __init__(
        self,
        ignore_case: bool = False,
        checker: AbstractLimitChecker = NoOpLimitChecker(),
    ):
        """

        :param ignore_case: False: Can the parser ignore case on die names and kwargs.
        :param checker: `dicetables.tools.limit_checker.NoOpLimitChecker`: How limits will be enforced
            for parsing.  This defaults to a limit checker that does not check limits.
        """
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
            DicePool,
        }
        self._param_types = {
            int: make_int,
            Dict[int, int]: make_int_dict,
            ProtoDie: self.make_die,
            Iterable[int]: make_int_tuple,
            DicePool: self.make_pool,
        }

    @classmethod
    def with_limits(
        cls,
        ignore_case: bool = False,
        max_size: int = 500,
        max_explosions: int = 10,
        max_dice: int = 6,
        max_dice_pools: int = 2,
    ) -> "Parser":
        """
        Creates a parser with a functioning limit checker from `dicetables.tools.limit_checker.LimitChecker`
        For explanation of how or why to change `max_dice_pool_combinations_per_dict_size`, and
        `max_dice_pool_calls`, see
        `Parser <http://dice-tables.readthedocs.io/en/latest/implementation_details/parser.html#limits-and-dicepool-objects>`_

        :param ignore_case: False: Can the parser ignore case on die names and kwargs.
        :param max_size: 500: The maximum allowed die size when :code:`parse_die_within_limits`
        :param max_explosions: 10: The maximum allowed (explosions + len(explodes_on)) when
            :code:`parse_die_within_limits`
        :param max_dice: 6: The maximum number of dice calls when :code:`parse`.
            Ex: :code:`StrongDie(Exploding(Die(5), 2), 3)` has 3 dice calls.
        :param max_dice_pools: 2: The maximum number of allowed dice_pool calls
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
        die_class = self._get_call_class(call_node)
        bound_args = self._get_bound_args(call_node, die_class)

        self.checker.assert_explosions_within_limits(bound_args)
        self.checker.assert_die_size_within_limits(bound_args)

        return die_class(*bound_args.args, **bound_args.kwargs)

    def make_pool(self, call_node: ast.Call):
        pool_class = self._get_call_class(call_node)
        bound_args = self._get_bound_args(call_node, pool_class)

        self.checker.assert_dice_pool_within_limits(bound_args)

        return pool_class(*bound_args.args, **bound_args.kwargs)

    def walk_dice_calls(self, call_node: ast.AST) -> Iterable[DieOrPool]:
        return (
            self._get_call_class(node)
            for node in ast.walk(call_node)
            if isinstance(node, ast.Call)
        )

    def _get_call_class(self, call_node: ast.AST):
        class_name = call_node.func.id
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

    def _get_bound_args(self, call_node: ast.Call, call_class: DieOrPool):
        call_signature = signature(call_class)
        args = self._get_params(call_node, call_signature)
        kwargs = self._get_kwargs(call_node, call_signature)
        try:
            bound_args = call_signature.bind(*args, **kwargs)
            bound_args.apply_defaults()
        except TypeError as e:
            msg = "{} for class: {}".format(e.args[0], call_node.func.id)
            raise ParseError(msg)
        return bound_args

    def _get_params(self, call_node: ast.Call, call_signature: Signature):
        signature_params = list(call_signature.parameters.values())
        param_nodes = call_node.args
        if len(param_nodes) > len(signature_params):
            raise ParseError("Too many parameters for class: {}".format(call_node.func.id))
        params = []
        for node, param in zip(param_nodes, signature_params):
            type_hint = param.annotation
            converter = self._param_types[type_hint]
            params.append(converter(node))
        return params

    def _raise_error_for_missing_type(self, call_signature: Signature):
        if any(
            param.annotation not in self._param_types
            for param in call_signature.parameters.values()
        ):
            raise ParseError(
                "The signature: {} has one or more un-recognized param types".format(
                    call_signature
                )
            )

    def _get_kwargs(self, call_node: ast.Call, call_signature: Signature):
        kwarg_nodes = call_node.keywords
        out = {}
        for kwarg_node in kwarg_nodes:
            kwarg_name, value = self._get_kwarg_value(call_signature, kwarg_node)
            out[kwarg_name] = value
        return out

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
        die_signature = signature(class_)
        self._raise_error_for_missing_annotation(die_signature)
        self._raise_error_for_missing_type(die_signature)
        self._classes.add(class_)

    @staticmethod
    def _raise_error_for_missing_annotation(die_signature: Signature):
        if any(
            param.annotation == _empty for param in die_signature.parameters.values()
        ):
            raise ParseError(
                "The signature: {} is missing type annotations".format(die_signature)
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
            if key != "kind":  # pragma no branch
                value = val
    if not isinstance(value, int):
        raise ValueError("Expected an integer, but got: {!r}".format(value))
    return value
