"""for all things dicey."""
from __future__ import absolute_import
from sys import version_info

from dicetables.baseevents import AdditiveEvents
from dicetables.eventsinfo import EventsCalculations
from dicetables.factory.eventsfactory import EventsFactory
from dicetables.dieevents import ProtoDie
from dicetables.tools.eventerrors import DiceRecordError


class RecordVerifier(object):
    @staticmethod
    def check_types(die_input):
        int_types = int
        if version_info[0] < 3:
            int_types = (int, long)
        if any(not isinstance(die, ProtoDie) or not isinstance(num, int_types) for die, num in die_input.items()):
            raise DiceRecordError('input must be {ProtoDie: int, ...}')

    @staticmethod
    def check_negative(die_input):
        for key, val in die_input.items():
            if val < 0:
                raise DiceRecordError('Tried to create a DiceRecord with a negative value at {!r}: {}'.format(key, val))

    @staticmethod
    def check_number(num):
        if num < 0:
            raise DiceRecordError('Tried to add_die or remove_die with a negative number.')


def scrub_zeroes(input_dict):
    return {key: val for key, val in input_dict.items() if val}


class DiceRecord(object):
    def __init__(self, dice_number_dict):
        RecordVerifier.check_types(dice_number_dict)
        RecordVerifier.check_negative(dice_number_dict)
        self._record = scrub_zeroes(dice_number_dict)

    def get_dict(self):
        return self._record.copy()

    def get_number(self, query_die):
        return self._record.get(query_die, 0)

    def add_die(self, number, die):
        RecordVerifier.check_number(number)
        new = self._record.copy()
        new[die] = number + new.get(die, 0)
        return DiceRecord(new)

    def remove_die(self, number, die):
        RecordVerifier.check_number(number)
        new = self._record.copy()
        new[die] = new.get(die, 0) - number
        return DiceRecord(new)


class DiceTable(AdditiveEvents):

    def __init__(self, events_dict, dice_number_dict):
        self._record = DiceRecord(dice_number_dict)
        super(DiceTable, self).__init__(events_dict)

    def dice_data(self):
        return self._record.get_dict()

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

    def add_die(self, number, die):
        """

        :param number: int>= 0
        :param die: Die, ModDie, WeightedDie, ModWeightedDie, StrongDie or new ProtoDie subclass
        """
        dice_iterable = self._create_constructor_dice(number, die, method_str='add_die')
        dictionary = self._create_constructor_dict(number, die, method_str='combine')
        return EventsFactory.from_dictionary_and_dice(self, dictionary, dice_iterable)

    def remove_die(self, number, die):
        """

        :param number: 0 <= int <= number of "die" in table
        :param die: Die, ModDie, WeightedDie, ModWeightedDie, StrongDie or new ProtoDie subclass
        """
        dice_iterable = self._create_constructor_dice(number, die, method_str='remove_die')
        dictionary = self._create_constructor_dict(number, die, method_str='remove')
        return EventsFactory.from_dictionary_and_dice(self, dictionary, dice_iterable)

    def _create_constructor_dice(self, number, die, method_str):
        methods = {'add_die': self._record.add_die,
                   'remove_die': self._record.remove_die}
        new_record = methods[method_str](number, die)
        return new_record.get_dict()


def format_die_info(die, number):
    weight_info = die.weight_info()
    adjusted_info = weight_info.replace(str(die), die.multiply_str(number)) + '\n\n'
    return adjusted_info


class RichDiceTable(DiceTable):

    def __init__(self, events_dict, dice_number_dict, calc_includes_zeroes=True):
        super(RichDiceTable, self).__init__(events_dict, dice_number_dict)
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
        return EventsFactory.from_params(self, {'calc_bool': not self.calc_includes_zeroes})
