import ast

from dicetables.dieevents import Die, ModDie, Modifier, ModWeightedDie, WeightedDie, StrongDie, Exploding, ExplodingOn


class ParseError(ValueError):
    def __init__(self, *args):
        super(ParseError, self).__init__(*args)


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
        """
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

        self._size_limit_kwargs = ['die_size', 'dictionary_input']
        self._explosions_limit_kwargs = ['explosions', 'explodes_on']

        self.ignore_case = ignore_case
        self.disable_kwargs = disable_kwargs
        self.max_size = max_size
        self.max_explosions = max_explosions
        self.max_nested_dice = max_nested_dice

        self._nested_dice_counter = 0
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
        return {'explosions_limits': self._explosions_limit_kwargs[:],
                'die_size_limits': self._size_limit_kwargs[:]}

    def parse_die(self, die_string):
        ast_call_node = ast.parse(die_string).body[0].value
        return self.make_die(ast_call_node)

    def parse_die_within_limits(self, die_string):
        """
        Checks to see if limits are exceeded. If not, parses string. This only works with die classes that contain the
        following key-word arguments:

        - die_size
        - dictionary_input
        - explosions
        - explodes_on

        If your die classes use different kwargs to describe size or number of explosions, they will
        be parsed as if there were no limits.
        """
        ast_call_node = ast.parse(die_string).body[0].value

        self._use_limits = True
        self._nested_dice_counter = 0

        die = self.make_die(ast_call_node)

        self._use_limits = False

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
            self._nested_dice_counter += 1
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
        self._check_nested_calls()

        class_kwargs = self._kwargs[die_class]
        size_params = [find_value(key_word, class_kwargs, die_params, die_kwargs)
                       for key_word in self._size_limit_kwargs]
        explosions_params = [find_value(key_word, class_kwargs, die_params, die_kwargs)
                             for key_word in self._explosions_limit_kwargs]

        self._check_die_size(size_params)
        self._check_explosions(explosions_params)

    def _check_nested_calls(self):
        if self._nested_dice_counter > self.max_nested_dice:
            msg = 'LIMITS EXCEEDED. Max number of nested dice: {}'.format(self.max_nested_dice)
            raise ParseError(msg)

    def _check_die_size(self, die_size_params):
        msg = 'LIMITS EXCEEDED. Max die_size: {}'.format(self.max_size)
        for param in die_size_params:
            if param is None:
                continue

            if isinstance(param, int):
                size = param
            elif isinstance(param, dict):
                size = max(param.keys())
            else:
                msg = 'A kwarg declared as a "die size limit" is neither an int nor a dict of ints.'
                raise ValueError(msg)

            if size > self.max_size:
                raise ParseError(msg)

    def _check_explosions(self, explosions_params):
        msg = 'LIMITS EXCEEDED. Max number of explosions + len(explodes_on): {}'.format(self.max_explosions)
        explosions = 0
        for param in explosions_params:
            if param is None:
                continue

            if isinstance(param, int):
                explosions += param
            elif isinstance(param, (tuple, list)):
                explosions += len(param)
            else:
                msg = 'A kwarg declared as an "explosions limit" is neither an int nor a tuple/list of ints.'
                raise ValueError(msg)

            if explosions > self.max_explosions:
                raise ParseError(msg)

    def add_class(self, class_, param_identifiers, auto_detect_kwargs=True, kwargs=()):
        """

        :param class_: the class you are adding
        :param param_identifiers: a tuple of param_types according to Parser().param_types()
        :param auto_detect_kwargs: will try to detect kwargs of __init__ function. overrides kwargs param
        :param kwargs: (optional) a tuple of the kwarg names for instantiation of the new class.
        """
        self._classes[class_] = param_identifiers
        if auto_detect_kwargs:
            kwargs = _get_kwargs_from_init(class_)
        self._kwargs[class_] = kwargs

    def add_param_type(self, param_type, creation_method):
        self._param_types[param_type] = creation_method

    def add_die_size_limit_kwarg(self, new_key_word):
        self._size_limit_kwargs.append(new_key_word)

    def add_explosions_limit_kwarg(self, new_key_word):
        self._explosions_limit_kwargs.append(new_key_word)


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


def find_value(key_word, class_kwargs, die_params, die_kwargs):
    if key_word not in class_kwargs:
        return None

    index = list(class_kwargs).index(key_word)
    if len(die_params) > index:
        return die_params[index]
    else:
        return die_kwargs[key_word]
