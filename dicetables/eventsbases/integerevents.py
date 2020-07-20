"""
The abstract class for sets of events that can be represented by integers.
"""
from typing import Dict

from dicetables.eventsbases.eventerrors import InvalidEventsError


class EventsVerifier(object):

    def verify_get_dict(self, events_dict):
        """

        :param events_dict: IntegerEvents.get_dict()
        :raises: InvalidEventsError
        """
        if not events_dict:
            raise InvalidEventsError('events may not be empty. a good alternative is the identity - {0: 1}.')
        if not self.is_all_ints(events_dict.keys()) or not self.is_all_ints(events_dict.values()):
            raise InvalidEventsError('all values must be ints')
        if any(occurrence <= 0 for occurrence in events_dict.values()):
            raise InvalidEventsError('no negative or zero occurrences in Events.get_dict()')

    @staticmethod
    def is_all_ints(iterable):
        return all(isinstance(value, int) for value in iterable)


class IntegerEvents(object):
    def __init__(self):
        super(IntegerEvents, self).__init__()
        EventsVerifier().verify_get_dict(self.get_dict())

    def get_dict(self) -> Dict[int, int]:
        """

        :return: {event: occurrences}
        """
        raise NotImplementedError(('get_dict() must return a dictionary\n'
                                   '{event: occurrences, ...} event=int, occurrence=int>0.'))

    def __eq__(self, other):
        return type(self) is type(other) and self.get_dict() == other.get_dict()

    def __ne__(self, other):
        return not self == other
