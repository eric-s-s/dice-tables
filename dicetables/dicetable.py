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
            self._raise_error_for_negative_dice(die, number, 'init neg')
            if number:
                self._record[die] = number

    @staticmethod
    def _raise_error_for_negative_dice(die, number, message_key):
        messages = {'init neg': 'DiceRecord may not have negative dice.',
                    'added neg': 'May not add negative dice to DiceRecord.',
                    'removed neg': 'May not remove negative dice from DiceRecord.',
                    'removed over': 'Removed too many dice from DiceRecord.'}
        if number < 0:
            raise DiceRecordError(messages[message_key] + ' Error at ({!r}, {})'.format(die, number))

    def get_record(self):
        return self._record.copy()

    def add_die(self, die, number):
        self._raise_error_for_negative_dice(die, number, 'added neg')
        new = self._record.copy()
        new[die] = number + new.get(die, 0)
        return DiceRecord(new)

    def remove_die(self, die, number):
        self._raise_error_for_negative_dice(die, number, 'removed neg')
        new = self._record.copy()
        new_count = new.get(die, 0) - number
        self._raise_error_for_negative_dice(die, new_count, 'removed over')
        new[die] = new_count
        return DiceRecord(new)

    def __str__(self):
        str_list = [die.multiply_str(number) for die, number in sorted(self._record.items())]
        return '\n'.join(str_list)

    def get_details(self):
        output = ''
        for die, number in sorted(self._record.items()):
            weight_info = die.weight_info()
            adjusted_info = weight_info.replace(str(die), die.multiply_str(number)) + '\n\n'
            output += adjusted_info
        return output.rstrip('\n')


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
        self._record = self._record.add_die(die, number)
        self.combine(number, die)

    def remove_die(self, number, die):
        """

        :param number: 0 <= int <= number of "die" in table
        :param die: Die, ModDie, WeightedDie, ModWeightedDie, StrongDie or new ProtoDie subclass
        """
        self._record = self._record.remove_die(die, number)
        self.remove(number, die)

"""
NEW                                         ORIGINAL

PROPERTIES
all_events                                  frequency_all()
events_range                                values_range()
events_keys                                 values()
total_occurrences                           total_frequency()
biggest_event                               frequency_highest()

METHODS
get_event(INT)                              frequency(INT)
get_range_of_events(INT, INT)               frequency_range(INT, INT)
                                            frequency_max()
                                            frequency_min()
mean()                                      mean()
stddev()                                    stddev()

add_die(INT, DIE)                           add_die(INT, DIE)
remove_die(IND, DIE)                        remove_die(IND, DIE)
get_list()                                  get_list()
weights_info()                              weights_info()

combine(INT, EVENTS)                        add(INT, EVENTS)
remove(INT, EVENTS)                         remove(INT, EVENTS)

get_dict()
3 * combine_by_<algorithm>(INT, EVENTS)


create_table




"""