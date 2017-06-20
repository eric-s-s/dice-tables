import ast

from dicetables.dieevents import Die, ModDie, Modifier, ModWeightedDie, WeightedDie, StrongDie, Exploding, ExplodingOn


class ParseError(ValueError):
    def __init__(self, *args):
        super(ParseError, self).__init__(*args)


class Parser(object):
    def __init__(self, ignore_case=False):
        self._classes = {Die: ('int',), ModDie: ('int', 'int'), Modifier: ('int',),
                         ModWeightedDie: ('int_dict', 'int'), WeightedDie: ('int_dict',),
                         StrongDie: ('die', 'int'), Exploding: ('die', 'int'),
                         ExplodingOn: ('die', 'int_tuple', 'int')}
        self._param_types = {'int': make_int, 'int_dict': make_int_dict,
                             'die': self.make_die, 'int_tuple': make_int_tuple}

        self.ignore_case = ignore_case

    def get_param_types(self):
        return self._param_types.copy()

    def get_classes(self):
        return self._classes.copy()

    def parse_die(self, die_string):
        ast_call_node = ast.parse(die_string).body[0].value
        return self.make_die(ast_call_node)

    def make_die(self, call_node):
        die_class_name = call_node.func.id
        param_nodes = call_node.args
        die_class = self._get_die_class(die_class_name)
        die_params = self._get_params(param_nodes, die_class)
        return die_class(*die_params)

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

    def add_class(self, klass, param_identifiers):
        self._classes[klass] = param_identifiers

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
