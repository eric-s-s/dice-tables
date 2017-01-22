from sys import version_info

from dicetables.eventsbases.protodie import ProtoDie
from dicetables.eventsbases.eventerrors import DiceRecordError


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

    @classmethod
    def new(cls):
        return cls({})

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

    def __eq__(self, other):
        if not isinstance(other, DiceRecord):
            return False
        return self.get_dict() == other.get_dict()

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return 'DiceRecord({!r})'.format(self._record)
