"""for all things dicey."""
from __future__ import absolute_import
from sys import version_info

from dicetables.baseevents import AdditiveEvents
from dicetables.eventsinfo import EventsCalculations
from dicetables.factory.eventsfactory import EventsFactory
from dicetables.dieevents import ProtoDie
from dicetables.tools.eventerrors import DiceRecordError

if version_info[0] < 3:
    from dicetables.tools.py2funcs import is_int
else:
    from dicetables.tools.py3funcs import is_int


class RecordVerifier(object):
    @staticmethod
    def check_types(die_input):
        if any(not isinstance(die, ProtoDie) or not is_int(num) for die, num in die_input.items()):
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

    def add_die(self, die, times):
        RecordVerifier.check_number(times)
        new = self._record.copy()
        new[die] = times + new.get(die, 0)
        return DiceRecord(new)

    def remove_die(self, die, times):
        RecordVerifier.check_number(times)
        new = self._record.copy()
        new[die] = new.get(die, 0) - times
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

    def add_die(self, die, times=1):
        """

        :param times: int>= 0
        :param die: Die, ModDie, WeightedDie, ModWeightedDie, StrongDie or new ProtoDie subclass
        """
        dice_iterable = self._create_constructor_dice(die, times, method_str='add_die')
        dictionary = self._create_constructor_dict(die, times, method_str='combine')
        return EventsFactory.from_dictionary_and_dice(self, dictionary, dice_iterable)

    def remove_die(self, die, times=1):
        """

        :param times: 0 <= int <= number of "die" in table
        :param die: Die, ModDie, WeightedDie, ModWeightedDie, StrongDie or new ProtoDie subclass
        """
        dice_iterable = self._create_constructor_dice(die, times, method_str='remove_die')
        dictionary = self._create_constructor_dict(die, times, method_str='remove')
        return EventsFactory.from_dictionary_and_dice(self, dictionary, dice_iterable)

    def _create_constructor_dice(self, die, times, method_str):
        methods = {'add_die': self._record.add_die,
                   'remove_die': self._record.remove_die}
        new_record = methods[method_str](die, times)
        return new_record.get_dict()


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
        return EventsFactory.from_params(self, {'calc_bool': not self.calc_includes_zeroes})
