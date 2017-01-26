"""
The abstract class for sets of events that can be represented by integers.
"""
from __future__ import absolute_import

from sys import version_info

from dicetables.eventsbases.eventerrors import InvalidEventsError

if version_info[0] < 3:
    from dicetables.tools.py2funcs import is_int
else:
    from dicetables.tools.py3funcs import is_int


class EventsVerifier(object):
    def __init__(self):
        self._type_str = 'ints'
        if version_info[0] < 3:
            self._type_str += ' or longs'

    def verify_get_dict(self, events_dict):
        """

        :param events_dict: IntegerEvents.get_dict()
        :raises: InvalidEventsError
        """
        if not events_dict:
            raise InvalidEventsError('events may not be empty. a good alternative is the identity - {0: 1}.')
        if not self.is_all_ints(events_dict.keys()) or not self.is_all_ints(events_dict.values()):
            raise InvalidEventsError('all values must be {}'.format(self._type_str))
        if any(occurrence <= 0 for occurrence in events_dict.values()):
            raise InvalidEventsError('no negative or zero occurrences in Events.get_dict()')

    @staticmethod
    def is_all_ints(iterable):
        return all(is_int(value) for value in iterable)


class IntegerEvents(object):
    def __init__(self):
        super(IntegerEvents, self).__init__()
        EventsVerifier().verify_get_dict(self.get_dict())

    def get_dict(self):
        """

        :return: {event: occurrences}
        """
        message = ('get_dict() must return a dictionary\n' +
                   '{event: occurrences, ...} event=int, occurrence=int>0.')
        raise NotImplementedError(message)