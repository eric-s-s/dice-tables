import re
from collections import namedtuple

from dicetables.dieevents import Die, ModDie, Modifier, ModWeightedDie, WeightedDie, StrongDie, Exploding, ExplodingOn


FunctionCall = namedtuple('FunctionCall', ['func', 'params'])
Group = namedtuple('Group', ['value'])
Value = namedtuple('Value', ['value'])


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
        function_tuple = StringToParams.get_call_structure(die_string)[0]
        return self.make_die(function_tuple)

    def make_die(self, function_tuple):
        die_class_name = function_tuple.func
        param_values = function_tuple.params
        die_class = self._get_die_class(die_class_name)
        die_params = self._get_params(param_values, die_class)
        return die_class(*die_params)

    def _get_die_class(self, class_name):
        class_name = self._update_search_string(class_name)
        for die_class in self._classes.keys():
            test_against = self._update_search_string(die_class.__name__)
            if class_name == test_against:
                return die_class
        raise ParseError('Die class: {} not recognized by parser.'.format(class_name))

    def _update_search_string(self, search_str):
        if self.ignore_case:
            return search_str.lower()
        return search_str

    def _get_params(self, param_values, die_class):
        params = []
        param_types = self._classes[die_class]
        self._raise_error_for_missing_methods(param_types, die_class)
        for index, value in enumerate(param_values):
            type_key = param_types[index]
            conversion_method = self._param_types[type_key]
            params.append(conversion_method(value))
        return params

    def _raise_error_for_missing_methods(self, param_types, die_class):
        if any(type_key not in self._param_types for type_key in param_types):
            raise ParseError('Failed to create die: {} with param types: {}. One or more param types not recognized.'
                             .format(die_class.__name__, param_types))

    def add_class(self, klass, param_identifiers):
        self._classes[klass] = param_identifiers

    def add_param_type(self, param_type, creation_method):
        self._param_types[param_type] = creation_method


def make_int_dict(group_tuple):
    no_braces = group_tuple.value.strip()[1: -1]
    if no_braces.strip() == '':
        return {}
    pairs = no_braces.split(',')
    key_vals = [pair.split(':') for pair in pairs]
    return {int(key): int(val) for key, val in key_vals}


def make_int_tuple(group_tuple):
    no_paren = group_tuple.value.strip()[1:-1]
    str_values = no_paren.split(',')
    return tuple([int(str_val) for str_val in str_values if str_val.strip()])


def make_int(value_tuple):
    return int(value_tuple.value)


class StringToParams(object):

    @staticmethod
    def get_call_structure(input_str):
        no_whitespace = input_str.strip()
        out_put = []
        while no_whitespace:
            if StringToParams.starts_with_function_call(no_whitespace):
                func_name, params, remainder = StringToParams.get_function_call(no_whitespace)
                param = FunctionCall(func=func_name, params=StringToParams.get_call_structure(params))
            elif StringToParams.starts_with_group(no_whitespace):
                gp_name, remainder = StringToParams.get_group(no_whitespace)
                param = Group(value=gp_name)
            else:
                val_name, remainder = StringToParams.get_param(no_whitespace)
                param = Value(value=val_name)
            out_put.append(param)
            no_whitespace = remainder
        return out_put

    @staticmethod
    def starts_with_function_call(input_str):
        to_test = input_str.strip()
        test = re.match('[A-Za-z_][A-Za-z0-9_]*\(', to_test)
        return test is not None

    @staticmethod
    def starts_with_group(input_str):
        no_whitespace = input_str.lstrip()
        collection_starts = ['(', '{', '[']
        return no_whitespace[0] in collection_starts

    @staticmethod
    def get_function_call(input_str):
        no_whitespace = input_str.strip()
        func_name, groups = no_whitespace.split('(', 1)
        groups = '(' + groups
        func_params, remainder = StringToParams.get_group(groups)
        without_parens = func_params[1:-1]
        return func_name, without_parens, remainder

    @staticmethod
    def get_group(input_str):
        no_whitespace = input_str.strip()
        start_of_remainder = StringToParams.find_end_of_first_group(no_whitespace) + 1
        first_group = no_whitespace[:start_of_remainder]
        remainder = no_whitespace[start_of_remainder:].lstrip().lstrip(',').lstrip(' ')
        return first_group, remainder

    @staticmethod
    def find_end_of_first_group(stripped_str):
        starts_and_ends = {'[': ']', '{': '}', '(': ')'}
        start_char = stripped_str[0]
        if start_char not in starts_and_ends:
            raise ValueError('String did not start with "[", "(" or "{"')
        end_char = starts_and_ends[start_char]
        brackets = 1
        for index in range(1, len(stripped_str)):
            if stripped_str[index] == start_char:
                brackets += 1
            if stripped_str[index] == end_char:
                brackets -= 1

            if brackets == 0:
                return index
        raise ValueError('String had no end of group')

    @staticmethod
    def get_param(input_str):
        if ',' not in input_str:
            return input_str.strip(), ''
        base_param, base_remainder = input_str.split(',', 1)
        return base_param.strip(), base_remainder.strip()
