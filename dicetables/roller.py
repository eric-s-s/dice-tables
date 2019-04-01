import random

from dicetables.tools.alias_table import AliasTable


class Roller(object):
    def __init__(self, events, random_generator=None):
        """

        :param events: any IntegerEvents
        :param random_generator: any instance of random.Random. defaults to python default random instance
        """
        self._alias_table = AliasTable(events.get_dict())
        self._random_generator = random_generator
        if not self._random_generator:
            self._random_generator = random

    @property
    def alias_table(self):
        """
        here is
        `a nice explanation of alias tables: <http://www.keithschwarz.com/darts-dice-coins/>`_

        :return: dicetables.tools.AliasTable
        """
        return self._alias_table

    @property
    def random_generator(self):
        return self._random_generator

    def roll(self):
        length = self._random_generator.randrange(self._alias_table.length)
        height = self._random_generator.randrange(self._alias_table.height)
        return self._alias_table.get(length, height)

    def roll_many(self, times):
        return [self.roll() for _ in range(times)]
