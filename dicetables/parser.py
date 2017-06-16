from dicetables.dieevents import Die, ModDie, Modifier, ModWeightedDie, WeightedDie, StrongDie, Exploding, ExplodingOn
from dicetables.factory.factorytools import StaticDict


class ParseFactory(object):
    pass


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
                if remainder.startswith(name):
                    answer[name] = []
                    remainder = remainder.lstrip(name)
            if remainder.startswith('('):
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


