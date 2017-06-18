import re
from collections import namedtuple

from dicetables.dieevents import Die, ModDie, Modifier, ModWeightedDie, WeightedDie, StrongDie, Exploding, ExplodingOn
from dicetables.factory.factorytools import StaticDict


FunctionCall = namedtuple('FunctionCall', ['func', 'params'])
Group = namedtuple('Group', ['value'])
Value = namedtuple('Value', ['value'])


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


def make_die(function_tuple):
    return Parser.get_die_from_function_tuple(function_tuple)


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


class Parser2(object):

    def __init__(self, ignore_case=False):
        self.__base_classes = {Die: ('int',), ModDie: ('int', 'int'), Modifier: ('int',),
                               ModWeightedDie: ('int_dict', 'int'), WeightedDie: ('int_dict',),
                               StrongDie: ('die', 'int'), Exploding: ('die', 'int'),
                               ExplodingOn: ('die', 'int_tuple', 'int')}
        self.__base_methods = {'int': make_int, 'int_dict': make_int_dict,
                               'die': self.make_die, 'int_tuple': make_int_tuple}

        self.ignore_case = ignore_case
        self._classes = {}
        self._methods = {}
        self.reset()

    def parse_die(self, die_string):
        function_tuple = StringToParams.get_call_structure(die_string)[0]
        return self.make_die(function_tuple)

    def make_die(self, function_tuple):
        die_class_name = function_tuple.func
        die_param_strings = function_tuple.params
        die_class = self.get_die_class(die_class_name)
        die_params = self.get_params(die_param_strings, die_class)
        return die_class(*die_params)

    def get_die_class(self, class_name):
        if self.ignore_case:
            class_name = class_name.lower()
        for die_class in self._classes.keys():
            test_against = die_class.__name__
            if self.ignore_case:
                test_against = test_against.lower()
            if class_name == test_against:
                return die_class
        raise ValueError('Die class not in parser dictionary.')

    def get_params(self, param_strings, die_class):
        params = []
        method_names = self._classes.get(die_class)
        for index, param_str in enumerate(param_strings):
            method = self._methods.get(method_names[index])
            params.append(method(param_str))
        return params

    def reset(self):
        self._methods = self.__base_methods.copy()

        self._classes = self.__base_classes.copy()

    def add_die(self, klass, param_identifiers):
        self._raise_error_for_altering_existing_key(klass, 'die')
        self._classes[klass] = param_identifiers

    def add_param(self, param_name, creation_method):
        self._raise_error_for_altering_existing_key(param_name, 'param_type')
        self._methods[param_name] = creation_method

    def _raise_error_for_altering_existing_key(self, new_key, key_type_str):
        lookups = {'die': self._classes, 'param_type': self._methods }
        if new_key in lookups[key_type_str].keys():
            raise KeyError('Tried to overwrite a {} already assigned'.format(key_type_str))


class Parser(object):
    classes = StaticDict(
        {Die: ('int',), ModDie: ('int', 'int'), Modifier: ('int',), ModWeightedDie: ('int_dict', 'int'),
         WeightedDie: ('int_dict',), StrongDie: ('die', 'int'), Exploding: ('die', 'int'),
         ExplodingOn: ('die', 'int_tuple', 'int')}
    )

    methods = StaticDict({'int': make_int, 'int_dict': make_int_dict, 'die': make_die, 'int_tuple': make_int_tuple})

    @classmethod
    def parse_die(cls, die_string):
        function_tuple = StringToParams.get_call_structure(die_string)[0]
        return cls.get_die_from_function_tuple(function_tuple)

    @classmethod
    def get_die_from_function_tuple(cls, function_tuple):
        die_class_name = function_tuple.func
        die_param_strings = function_tuple.params
        die_class = cls.get_die_class(die_class_name)
        die_params = cls.get_params(die_param_strings, die_class)
        return die_class(*die_params)

    @classmethod
    def get_die_class(cls, class_name):
        for die_class in cls.classes.keys():
            if die_class.__name__ == class_name:
                return die_class

    @classmethod
    def get_params(cls, param_strings, die_class):
        params = []
        method_names = cls.classes.get(die_class)
        for index, param_str in enumerate(param_strings):
            method = cls.methods.get(method_names[index])
            params.append(method(param_str))
        return params

    @classmethod
    def reset(cls):
        cls.methods = StaticDict({'int': make_int, 'int_dict': make_int_dict, 'die': make_die,
                                  'int_tuple': make_int_tuple})

        cls.classes = StaticDict(
            {Die: ('int',), ModDie: ('int', 'int'), Modifier: ('int',), ModWeightedDie: ('int_dict', 'int'),
             WeightedDie: ('int_dict',), StrongDie: ('die', 'int'), Exploding: ('die', 'int'),
             ExplodingOn: ('die', 'int_tuple', 'int')}
        )

    @classmethod
    def add_die(cls, klass, param_identifiers):
        cls._raise_error_for_altering_existing_key(klass, 'die')
        cls.classes = cls.classes.set(klass, param_identifiers)

    @classmethod
    def add_param(cls, param_name, creation_method):
        cls._raise_error_for_altering_existing_key(param_name, 'param_type')
        cls.methods = cls.methods.set(param_name, creation_method)

    @classmethod
    def _raise_error_for_altering_existing_key(cls, new_key, key_type_str):
        lookups = {'die': cls.classes, 'param_type': cls.methods }
        if new_key in lookups[key_type_str].keys():
            raise KeyError('Tried to overwrite a {} already assigned'.format(key_type_str))
