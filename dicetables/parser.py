import ast

from dicetables.dieevents import Die, ModDie, Modifier, ModWeightedDie, WeightedDie, StrongDie, Exploding, ExplodingOn


class ParseError(ValueError):
    def __init__(self, *args):
        super(ParseError, self).__init__(*args)


class Parser(object):
    def __init__(self, ignore_case=False, disable_kwargs=False):
        self._classes = {Die: ('int',), ModDie: ('int', 'int'), Modifier: ('int',),
                         ModWeightedDie: ('int_dict', 'int'), WeightedDie: ('int_dict',),
                         StrongDie: ('die', 'int'), Exploding: ('die', 'int'),
                         ExplodingOn: ('die', 'int_tuple', 'int')}
        self._param_types = {'int': make_int, 'int_dict': make_int_dict,
                             'die': self.make_die, 'int_tuple': make_int_tuple}

        self._kwargs = {Die: ('die_size',), ModDie: ('die_size', 'modifier'), Modifier: ('modifier',),
                        ModWeightedDie: ('dictionary_input', 'modifier'), WeightedDie: ('dictionary_input',),
                        StrongDie: ('input_die', 'multiplier'), Exploding: ('input_die', 'explosions'),
                        ExplodingOn: ('input_die', 'explodes_on', 'explosions')}

        self.ignore_case = ignore_case
        self.disable_kwargs = disable_kwargs

    def get_param_types(self):
        return self._param_types.copy()

    def get_classes(self):
        return self._classes.copy()

    def get_kwargs(self):
        return self._kwargs.copy()

    def parse_die(self, die_string):
        ast_call_node = ast.parse(die_string).body[0].value
        return self.make_die(ast_call_node)

    def make_die(self, call_node):
        die_class_name = call_node.func.id
        param_nodes = call_node.args
        kwarg_nodes = call_node.keywords
        die_class = self._get_die_class(die_class_name)
        die_params = self._get_params(param_nodes, die_class)
        die_kwargs = self._get_kwargs(kwarg_nodes, die_class)
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
        search_kwarg_name = self._update_search_string(kwarg_node.arg)
        value_node = kwarg_node.value

        param_types = self._classes[die_class]
        true_kwarg_tuple = self._kwargs[die_class]
        search_kwarg_tuple = self._update_search_tuple(true_kwarg_tuple)

        index = search_kwarg_tuple.index(search_kwarg_name)

        param_key = param_types[index]
        value = self._param_types[param_key](value_node)

        true_kwarg_name = true_kwarg_tuple[index]
        return true_kwarg_name, value

    def add_class(self, klass, param_identifiers, kwargs=()):
        self._classes[klass] = param_identifiers
        self._kwargs[klass] = kwargs

    def add_param_type(self, param_type, creation_method):
        self._param_types[param_type] = creation_method


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
