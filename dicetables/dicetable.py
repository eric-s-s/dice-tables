"""
DiceTable and DetailedDiceTable compute combination of Die events
"""

from typing import TypeVar

from dicetables import DiceRecord
from dicetables.additiveevents import AdditiveEvents
from dicetables.eventsbases.protodie import ProtoDie
from dicetables.eventsinfo import EventsCalculations, EventsInformation
from dicetables.factory.eventsfactory import EventsFactory
from dicetables.tools.dictcombiner import DictCombiner

T = TypeVar('T', bound='DiceTable')


class DiceTable(AdditiveEvents):
    def __init__(self, events_dict: dict, dice_record: DiceRecord):
        self._record = dice_record
        super(DiceTable, self).__init__(events_dict)

    def dice_data(self) -> DiceRecord:
        return self._record

    def get_list(self):
        """

        :return: sorted copy of dice list: [(die, number of dice), ...]
        """
        return sorted(self._record.get_dict().items())

    def number_of_dice(self, query_die: ProtoDie) -> int:
        return self._record.get_number(query_die)

    def weights_info(self):
        """

        :return: str: complete info for all dice
        """
        output = ''
        for die, number in self.get_list():
            output += format_die_info(die, number)
        return output.rstrip('\n')

    def __str__(self):
        str_list = [die.multiply_str(number) for die, number in self.get_list()]
        return '\n'.join(str_list)

    def __repr__(self):
        class_name = self.__class__.__name__
        dice = str(self).replace('\n', ', ')
        return '<{} containing [{}]>'.format(class_name, dice)

    def add_die(self: T, die: ProtoDie, times: int = 1) -> T:
        """

        :param die: any subclass of ProtoDie: Die, ModDie, WeightedDie, ModWeightedDie, Modifier,
            StrongDie, Exploding, ExplodingOn
        :param times: int>= 0
        """
        dice_data = self._record.add_die(die, times)
        dictionary = DictCombiner(self.get_dict()).combine_by_fastest(die.get_dict(), times)
        return EventsFactory.from_dictionary_and_dice(self, dictionary, dice_data)

    def remove_die(self: T, die: ProtoDie, times=1) -> T:
        """

        :param die: any subclass of ProtoDie: Die, ModDie, WeightedDie, ModWeightedDie, Modifier,
            StrongDie, Exploding, ExplodingOn
        :param times: 0 <= int <= number of "die" in table
        """
        dice_data = self._record.remove_die(die, times)
        dictionary = DictCombiner(self.get_dict()).remove_by_tuple_list(die.get_dict(), times)
        return EventsFactory.from_dictionary_and_dice(self, dictionary, dice_data)

    def __eq__(self, other):
        return super(DiceTable, self).__eq__(other) and self.dice_data() == other.dice_data()


def format_die_info(die, number):
    weight_info = die.weight_info()
    adjusted_info = weight_info.replace(str(die), die.multiply_str(number)) + '\n\n'
    return adjusted_info


class DetailedDiceTable(DiceTable):
    def __init__(self, events_dict: dict, dice_record: DiceRecord, calc_includes_zeroes: bool = True):
        super(DetailedDiceTable, self).__init__(events_dict, dice_record)
        self._calc = EventsCalculations(self, calc_includes_zeroes)

    @property
    def info(self) -> EventsInformation:
        return self._calc.info

    @property
    def calc(self) -> EventsCalculations:
        return self._calc

    @property
    def calc_includes_zeroes(self) -> bool:
        return self._calc.include_zeroes

    def switch_boolean(self: T) -> T:
        """

        :return: a new DetailedDiceTable with the `calc_includes_zeroes` boolean switched
        """
        return EventsFactory.from_params(self, {'calc_includes_zeroes': not self.calc_includes_zeroes})

    def __eq__(self, other):
        return super(DetailedDiceTable, self).__eq__(other) and self.calc_includes_zeroes == other.calc_includes_zeroes
