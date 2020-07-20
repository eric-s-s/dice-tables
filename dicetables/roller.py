import random
from typing import Optional, List

from dicetables.tools.alias_table import AliasTable


class Roller(object):
    def __init__(self, events, random_generator: Optional[random.Random] = None):
        """

        :param events: any IntegerEvents
        :param random_generator: any instance of random.Random. defaults to python default random instance
        """
        self._alias_table = AliasTable(events.get_dict())
        self._random_generator = random_generator
        if not self._random_generator:
            self._random_generator = random.Random()

    @property
    def alias_table(self) -> AliasTable:
        """
        here is
        `a nice explanation of alias tables: <http://www.keithschwarz.com/darts-dice-coins/>`_

        :return: dicetables.tools.AliasTable
        """
        return self._alias_table

    @property
    def random_generator(self) -> random.Random:
        return self._random_generator

    def roll(self) -> int:
        length = self._random_generator.randrange(self._alias_table.length)
        height = self._random_generator.randrange(self._alias_table.height)
        return self._alias_table.get(length, height)

    def roll_many(self, times) -> List[int]:
        """

        :param times: int - how many times to roll
        :return: [int,..] - the value of each roll
        """
        return [self.roll() for _ in range(times)]
