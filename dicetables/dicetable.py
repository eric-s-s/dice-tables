"""for all things dicey."""
from __future__ import absolute_import

from dicetables.baseevents import AdditiveEvents


class DiceRecordError(ValueError):
    def __init__(self, message='', *args, **kwargs):
        super(DiceRecordError, self).__init__(message, *args, **kwargs)


class DiceRecord(object):
    def __init__(self, die_number_dict):
        self._record = {}
        for die, number in die_number_dict.items():
            self._raise_error_for_negative_dice(number, die, 'init neg')
            if number:
                self._record[die] = number

    def get_record(self):
        return self._record.copy()

    def add_die(self, number, die):
        self._raise_error_for_negative_dice(number, die, 'added neg')
        new = self._record.copy()
        new[die] = number + new.get(die, 0)
        return DiceRecord(new)

    def remove_die(self, number, die):
        self._raise_error_for_negative_dice(number, die, 'removed neg')
        new = self._record.copy()
        new_count = new.get(die, 0) - number
        self._raise_error_for_negative_dice(new_count, die, 'removed too many')
        new[die] = new_count
        return DiceRecord(new)

    @staticmethod
    def _raise_error_for_negative_dice(number, die, message_key):
        messages = {'init neg': 'DiceRecord may not have negative dice.',
                    'added neg': 'May not add negative dice to DiceRecord.',
                    'removed neg': 'May not remove negative dice from DiceRecord.',
                    'removed too many': 'Removed too many dice from DiceRecord.'}
        if number < 0:
            raise DiceRecordError(messages[message_key] + ' Error at ({!r}, {})'.format(die, number))

    def __str__(self):
        str_list = [die.multiply_str(number) for die, number in sorted(self._record.items())]
        return '\n'.join(str_list)

    def get_details(self):
        output = ''
        for die, number in sorted(self._record.items()):
            output += format_die_info(die, number)
        return output.rstrip('\n')


def format_die_info(die, number):
    weight_info = die.weight_info()
    adjusted_info = weight_info.replace(str(die), die.multiply_str(number)) + '\n\n'
    return adjusted_info


class DiceTable(AdditiveEvents):
    """
    DiceTable() creates an empty table that dice can be added to and removed from
    """

    def __init__(self, input_dict, dice_list):
        super(DiceTable, self).__init__(input_dict)
        self._record = DiceRecord(dict(dice_list))

    @classmethod
    def new(cls):
        return cls({0: 1}, [])

    def get_list(self):
        """

        :return: sorted copy of dice list: [(die, number of dice), ...]
        """
        return sorted(self._record.get_record().items())

    def number_of_dice(self, query_die):
        return self._record.get_record().get(query_die, 0)

    def weights_info(self):
        """

        :return: str: complete info for all dice
        """
        return self._record.get_details()

    def __str__(self):
        return self._record.__str__()

    def add_die(self, number, die):
        """

        :param number: int>= 0
        :param die: Die, ModDie, WeightedDie, ModWeightedDie, StrongDie or new ProtoDie subclass
        """
        self._record = self._record.add_die(number, die)
        self.combine(number, die)

    def remove_die(self, number, die):
        """

        :param number: 0 <= int <= number of "die" in table
        :param die: Die, ModDie, WeightedDie, ModWeightedDie, StrongDie or new ProtoDie subclass
        """
        self._record = self._record.remove_die(number, die)
        self.remove(number, die)
