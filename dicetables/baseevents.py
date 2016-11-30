""" this module contains the class LongIntTable and longintmath that the table
needs to deal with it's BFN"""
from __future__ import absolute_import

from sys import version_info

from dicetables.tools.dictcombiner import DictCombiner
from dicetables.eventsfactory import EventsFactory


class InvalidEventsError(ValueError):
    def __init__(self, message='', *args, **kwargs):
        super(InvalidEventsError, self).__init__(message, *args, **kwargs)
        

class InputVerifier(object):
    def __init__(self):
        self._int_tuple = (int,)
        self._type_str = 'ints'
        if version_info[0] < 3:
            self._int_tuple += (long, )
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

    def is_int(self, number):
        return isinstance(number, self._int_tuple)

    def is_all_ints(self, iterable):
        return all(self.is_int(value) for value in iterable)


class IntegerEvents(object):
    def __init__(self):
        InputVerifier().verify_get_dict(self.get_dict())

    def get_dict(self):
        """

        :return: {event: occurrences}
        """
        message = ('get_dict() must return a dictionary\n' +
                   '{event: occurrences, ...} event=int, occurrence=int>0.')
        raise NotImplementedError(message)


def scrub_zeroes(dictionary):
    return dict(item for item in dictionary.items() if item[1])


class AdditiveEvents(IntegerEvents):

    must_do = ['_construct_by_dictionary']

    def __init__(self, events_dictionary):
        """

        :param events_dictionary: {event: occurrences}\n
            event=int. occurrences=int >=0
            total occurrences > 0
        """
        # self._check_overriders()
        self._table = scrub_zeroes(events_dictionary)
        super(AdditiveEvents, self).__init__()

    @classmethod
    def new(cls):
        return EventsFactory.new(cls)

    @classmethod
    def _check_overriders(cls):
        for method in cls.must_do:
            if method not in cls.__dict__:
                raise TypeError('must over ride method: {}'.format(method))

    def get_dict(self):
        return self._table.copy()

    def __str__(self):
        min_event = min(self._table.keys())
        max_event = max(self._table.keys())
        return 'table from {} to {}'.format(min_event, max_event)

    def combine(self, times, events):
        dictionary = self._create_constructor_dict(times, events, method_str='combine')
        return EventsFactory.from_dictionary(self, dictionary)

    def combine_by_flattened_list(self, times, events):
        """

        :WARNING - UNSAFE METHOD: len(flattened_list) = total occurrences of events.
            if this list is too big, it will raise MemoryError or OverflowError
        """
        dictionary = self._create_constructor_dict(times, events, method_str='combine_by_flattened_list')
        return EventsFactory.from_dictionary(self, dictionary)

    def combine_by_dictionary(self, times, events):
        dictionary = self._create_constructor_dict(times, events, method_str='combine_by_dictionary')
        return EventsFactory.from_dictionary(self, dictionary)

    def combine_by_indexed_values(self, times, events):
        dictionary = self._create_constructor_dict(times, events, method_str='combine_by_indexed_values')
        return EventsFactory.from_dictionary(self, dictionary)

    def remove(self, times, events):
        """

        :WARNING - UNSAFE METHOD: There is no record of what you added to an AdditiveEvents.
            If you remove what you haven't added, no error will be raised, but you will have bugs.
        """
        dictionary = self._create_constructor_dict(times, events, method_str='remove')
        return EventsFactory.from_dictionary(self, dictionary)

    def _create_constructor_dict(self, times, events, method_str):
        combiner = DictCombiner(self.get_dict())
        methods = {'combine': combiner.combine_by_fastest,
                   'combine_by_flattened_list': combiner.combine_by_flattened_list,
                   'combine_by_dictionary': combiner.combine_by_dictionary,
                   'combine_by_indexed_values': combiner.combine_by_indexed_values,
                   'remove': combiner.remove_by_tuple_list}
        new_combiner = methods[method_str](times, events.get_dict())
        return new_combiner.get_dict()


