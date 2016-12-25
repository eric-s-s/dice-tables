""" this module contains the class LongIntTable and longintmath that the table
needs to deal with it's BFN"""
from __future__ import absolute_import

from sys import version_info

from dicetables.factory.eventsfactory import EventsFactory
from dicetables.tools.dictcombiner import DictCombiner
from dicetables.tools.eventerrors import InvalidEventsError

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


def scrub_zeroes(dictionary):
    return {key: val for key, val in dictionary.items() if val}


class AdditiveEvents(IntegerEvents):

    def __init__(self, events_dict):
        """

        :param events_dict: {event: occurrences}\n
            event=int. occurrences=int >=0
            total occurrences > 0
        """
        self._table = scrub_zeroes(events_dict)
        super(AdditiveEvents, self).__init__()
        EventsFactory.check(self.__class__)

    @classmethod
    def new(cls):
        return EventsFactory.new(cls)

    def get_dict(self):
        return self._table.copy()

    def __str__(self):
        min_event = min(self._table.keys())
        max_event = max(self._table.keys())
        return 'table from {} to {}'.format(min_event, max_event)

    def combine(self, events, times=1):
        dictionary = self._create_constructor_dict(events, times, method_str='combine')
        return EventsFactory.from_dictionary(self, dictionary)

    def combine_by_flattened_list(self, events, times=1):
        """

        :WARNING - UNSAFE METHOD: len(flattened_list) = total occurrences of events.
            if this list is too big, it will raise MemoryError or OverflowError
        """
        dictionary = self._create_constructor_dict(events, times, method_str='combine_by_flattened_list')
        return EventsFactory.from_dictionary(self, dictionary)

    def combine_by_dictionary(self, events, times=1):
        dictionary = self._create_constructor_dict(events, times, method_str='combine_by_dictionary')
        return EventsFactory.from_dictionary(self, dictionary)

    def combine_by_indexed_values(self, events, times=1):
        dictionary = self._create_constructor_dict(events, times, method_str='combine_by_indexed_values')
        return EventsFactory.from_dictionary(self, dictionary)

    def remove(self, events, times=1):
        """

        :WARNING - UNSAFE METHOD: There is no record of what you added to an AdditiveEvents.
            If you remove what you haven't added, no error will be raised, but you will have bugs.
        """
        dictionary = self._create_constructor_dict(events, times, method_str='remove')
        return EventsFactory.from_dictionary(self, dictionary)

    def _create_constructor_dict(self, events, times, method_str):
        combiner = DictCombiner(self.get_dict())
        methods = {'combine': combiner.combine_by_fastest,
                   'combine_by_flattened_list': combiner.combine_by_flattened_list,
                   'combine_by_dictionary': combiner.combine_by_dictionary,
                   'combine_by_indexed_values': combiner.combine_by_indexed_values,
                   'remove': combiner.remove_by_tuple_list}
        new_combiner = methods[method_str](events.get_dict(), times)
        return new_combiner.get_dict()
