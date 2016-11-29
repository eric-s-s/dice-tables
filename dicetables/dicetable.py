"""for all things dicey."""
from __future__ import absolute_import

from dicetables.baseevents import AdditiveEvents
from dicetables.eventsinfo import EventsCalculations, EventsInformation


class DiceRecordError(ValueError):
    def __init__(self, message='', *args, **kwargs):
        super(DiceRecordError, self).__init__(message, *args, **kwargs)


class DiceRecord(object):
    def __init__(self, die_number_iterable, init_error_msg='init neg'):
        self._record = {}
        for die, number in die_number_iterable:
            self._raise_error_for_negative_dice(number, die, init_error_msg)
            if number:
                self._record[die] = number

    def get_items(self):
        return self._record.items()

    def get_record(self):
        return self._record.copy()

    def get_number(self, query_die):
        return self._record.get(query_die, 0)

    def add_die(self, number, die):
        self._raise_error_for_negative_dice(number, die, 'added neg')
        new = self._record.copy()
        new[die] = number + new.get(die, 0)
        return DiceRecord(new.items())

    def remove_die(self, number, die):
        self._raise_error_for_negative_dice(number, die, 'removed neg')
        new = self._record.copy()
        new[die] = new.get(die, 0) - number
        return DiceRecord(new.items(), init_error_msg='removed too many')

    @staticmethod
    def _raise_error_for_negative_dice(number, die, message_key):
        messages = {'init neg': 'DiceRecord may not have negative dice.',
                    'added neg': 'May not add negative dice to DiceRecord.',
                    'removed neg': 'May not remove negative dice from DiceRecord.',
                    'removed too many': 'Removed too many dice from DiceRecord.'}
        if number < 0:
            raise DiceRecordError(messages[message_key] + ' Error at ({!r}, {})'.format(die, number))


def format_die_info(die, number):
    weight_info = die.weight_info()
    adjusted_info = weight_info.replace(str(die), die.multiply_str(number)) + '\n\n'
    return adjusted_info


class DiceTable(AdditiveEvents):
    def __init__(self, input_dict, dice_list):
        super(DiceTable, self).__init__(input_dict)
        self._record = DiceRecord(dice_list)
        self._constructor_dice_iterable = []

    @classmethod
    def new(cls):
        return cls({0: 1}, [])

    def get_list(self):
        """

        :return: sorted copy of dice list: [(die, number of dice), ...]
        """
        return sorted(self._record.get_items())

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
        self._create_constructor_dice_iterable(number, die, method_str='add_die')
        self._create_constructor_dict(number, die, method_str='combine')
        return self._construct_by_dictionary_and_dice_iterable()

    def remove_die(self, number, die):
        """

        :param number: 0 <= int <= number of "die" in table
        :param die: Die, ModDie, WeightedDie, ModWeightedDie, StrongDie or new ProtoDie subclass
        """
        self._create_constructor_dice_iterable(number, die, method_str='remove_die')
        self._create_constructor_dict(number, die, method_str='remove')
        return self._construct_by_dictionary_and_dice_iterable()

    def _create_constructor_dice_iterable(self, number, die, method_str):
        methods = {'add_die': self._record.add_die,
                   'remove_die': self._record.remove_die}
        new_record = methods[method_str](number, die)
        self._constructor_dice_iterable = new_record.get_items()

    def _construct_by_dictionary(self):
        new_dice_table = DiceTable(self._constructor_dict, self._record.get_items())
        self._reset_constructors()
        return new_dice_table

    def _construct_by_dictionary_and_dice_iterable(self):
        new_dice_table = DiceTable(self._constructor_dict, self._constructor_dice_iterable)
        self._reset_constructors()
        return new_dice_table

    def _reset_constructors(self):
        super(DiceTable, self)._reset_constructors()
        self._constructor_dice_iterable = []


class RichDiceTable(DiceTable):

    def __init__(self, input_dict, dice_list, calc_includes_zeroes=True):
        super(RichDiceTable, self).__init__(input_dict, dice_list)
        self._zeroes_bool = calc_includes_zeroes

    @property
    def info(self):
        return EventsInformation(self)

    @property
    def calc(self):
        return EventsCalculations(self, self.calc_includes_zeroes)

    @property
    def calc_includes_zeroes(self):
        return self._zeroes_bool

    @classmethod
    def new(cls):
        return cls({0: 1}, [], True)

    def switch_boolean(self):
        return RichDiceTable(self.get_dict(), self._record.get_items(), not self.calc_includes_zeroes)

    def _construct_by_dictionary(self):
        new_rich_dice_table = RichDiceTable(self._constructor_dict,
                                            self._record.get_items(),
                                            self.calc_includes_zeroes)
        self._reset_constructors()
        return new_rich_dice_table

    def _construct_by_dictionary_and_dice_iterable(self):
        new_rich_dice_table = RichDiceTable(self._constructor_dict,
                                            self._constructor_dice_iterable,
                                            self.calc_includes_zeroes)
        self._reset_constructors()
        return new_rich_dice_table
