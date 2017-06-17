import re
from collections import namedtuple

from dicetables.dieevents import Die, ModDie, Modifier, ModWeightedDie, WeightedDie, StrongDie, Exploding, ExplodingOn
from dicetables.factory.factorytools import StaticDict


FunctionCall = namedtuple('FunctionCall', ['func', 'params'])


class StringPrep(object):

    @staticmethod
    def get_params(input_str):
        no_whitespace = input_str.strip()
        out_put = []
        while no_whitespace:
            if StringPrep.starts_with_function_call(no_whitespace):
                param, remainder = StringPrep.get_function_call(no_whitespace)
            elif StringPrep.starts_with_group(no_whitespace):
                param, remainder = StringPrep.get_first_group(no_whitespace)
            else:
                param, remainder = StringPrep.get_next_param(no_whitespace)
            out_put.append(param)
            no_whitespace = remainder
        return out_put

    @staticmethod
    def starts_with_function_call(input_str):
        to_test = input_str.strip()
        test = re.match('[A-Z,a-z]+\(', to_test)
        return test is not None

    @staticmethod
    def starts_with_group(input_str):
        collection_starts = ['(', '{', '[']
        return input_str[0] in collection_starts

    @staticmethod
    def get_function_call(input_str):
        no_whitespace = input_str.strip()
        func_name, groups = no_whitespace.split('(', 1)
        groups = '(' + groups
        func_params, remainder = StringPrep.get_first_group(groups)
        without_parens = func_params[1:-1]
        return FunctionCall(func=func_name, params=StringPrep.get_params(without_parens)), remainder

    @staticmethod
    def get_first_group(input_str):
        no_whitespace = input_str.strip()
        start_of_remainder = StringPrep.find_end_of_first_group(no_whitespace) + 1
        first_group = no_whitespace[:start_of_remainder]
        remainder = no_whitespace[start_of_remainder:].strip().lstrip(',').lstrip(' ')
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
    def get_next_param(input_str):
        if ',' not in input_str:
            return input_str.strip(), ''
        base_param, base_remainder = input_str.split(',', 1)
        return base_param.strip(), base_remainder.strip()

    # @staticmethod
    # def split_first_el(big_str):
    #     big_str = big_str.strip()
    #     if ',' not in big_str:
    #         return big_str, ''
    #
    #     if big_str.startswith('[') or big_str.startswith('(') or big_str.startswith('{'):
    #         collection_end = StringPrep.find_collection_end(big_str)
    #         raw_index = big_str[collection_end:].find(',')
    #         if raw_index == -1:
    #             raw_index = 1
    #         index = raw_index + collection_end
    #     else:
    #         index = big_str.find(',')
    #     return big_str[:index], big_str[index + 1:]
    #
    # @staticmethod
    # def find_collection_end(list_string):
    #     starts_and_ends = {'[': ']', '{': '}', '(': ')'}
    #     start_char = list_string[0]
    #     end_char = starts_and_ends[start_char]
    #     brackets = 1
    #     index = 1
    #     while brackets:
    #         if list_string[index] == start_char:
    #             brackets += 1
    #         if list_string[index] == end_char:
    #             brackets -= 1
    #         index += 1
    #     return index - 1


class NodeCreator(object):
    def __init__(self, big_string):
        self.die_names = ['Die', 'ModDie', 'WeightedDie', 'ModWeightedDie', 'StrongDie', 'Modifier', 'Exploding',
                          'ExplodingOn']
        self.big_string = big_string

    def to_dict(self):
        answer = {}
        remainder = self.big_string
        while remainder:
            for name in self.die_names:
                if remainder.startswith(name + '('):
                    answer[name] = []
                    remainder = remainder.lstrip(name)
            if remainder.startswith('('):
                return answer
            print(remainder)
        return answer


class Parser(object):
    classes = StaticDict(
        {Die: ('int',), ModDie: ('int', 'int'), Modifier: ('int',), ModWeightedDie: ('int_dict', 'int'),
         WeightedDie: ('int_dict',), StrongDie: ('die', 'int'), Exploding: ('die', 'int'),
         ExplodingOn: ('die', 'int_tuple', 'int')}
    )

    methods = StaticDict({})

    @classmethod
    def parse(cls, die_string):
        if die_string == 'die(6)':
            return Die(6)
        return Die(7)

    @classmethod
    def add_die(cls, klass, params):
        pass

    @classmethod
    def add_param(cls, param_name, creation_method):
        pass


