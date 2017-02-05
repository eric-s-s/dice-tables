"""
DiceTable and DetailedDiceTable compute combination of Die events
"""
from __future__ import absolute_import


from dicetables.additiveevents import AdditiveEvents, EventsDictCreator
from dicetables.eventsinfo import EventsCalculations
from dicetables.factory.eventsfactory import EventsFactory


class DiceTable(AdditiveEvents):
    def __init__(self, events_dict, dice_record):
        self._record = dice_record
        super(DiceTable, self).__init__(events_dict)

    def dice_data(self):
        return self._record

    def get_list(self):
        """

        :return: sorted copy of dice list: [(die, number of dice), ...]
        """
        return sorted(self._record.get_dict().items())

    def number_of_dice(self, query_die):
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

    def add_die(self, die, times=1):
        """

        :param times: int>= 0
        :param die: Die, ModDie, WeightedDie, ModWeightedDie, StrongDie or new ProtoDie subclass
        """
        dice_data = self._record.add_die(die, times)
        dictionary = EventsDictCreator(self, die).create_using_combine_by_fastest(times)
        return EventsFactory.from_dictionary_and_dice(self, dictionary, dice_data)

    def remove_die(self, die, times=1):
        """

        :param times: 0 <= int <= number of "die" in table
        :param die: Die, ModDie, WeightedDie, ModWeightedDie, StrongDie or new ProtoDie subclass
        """
        dice_data = self._record.remove_die(die, times)
        dictionary = EventsDictCreator(self, die).create_using_remove_by_tuple_list(times)
        return EventsFactory.from_dictionary_and_dice(self, dictionary, dice_data)

    def __eq__(self, other):
        return super(DiceTable, self).__eq__(other) and self.dice_data() == other.dice_data()


def format_die_info(die, number):
    weight_info = die.weight_info()
    adjusted_info = weight_info.replace(str(die), die.multiply_str(number)) + '\n\n'
    return adjusted_info


class DetailedDiceTable(DiceTable):
    def __init__(self, events_dict, dice_number_dict, calc_includes_zeroes=True):
        super(DetailedDiceTable, self).__init__(events_dict, dice_number_dict)
        self._calc = EventsCalculations(self, calc_includes_zeroes)

    @property
    def info(self):
        return self._calc.info

    @property
    def calc(self):
        return self._calc

    @property
    def calc_includes_zeroes(self):
        return self._calc.include_zeroes

    def switch_boolean(self):
        return EventsFactory.from_params(self, {'calc_includes_zeroes': not self.calc_includes_zeroes})

    def __eq__(self, other):
        return super(DetailedDiceTable, self).__eq__(other) and self.calc_includes_zeroes == other.calc_includes_zeroes
