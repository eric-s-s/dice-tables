"""
AdditiveEvents is the general case for DiceTable - an IntegerEvents that can combine with other IntegerEvents.
"""
from __future__ import absolute_import


from dicetables.factory.eventsfactory import EventsFactory
from dicetables.tools.dictcombiner import DictCombiner
from dicetables.eventsbases.integerevents import IntegerEvents


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
        dictionary = EventsDictCreator(self, events).create_using_combine_by_fastest(times)
        return EventsFactory.from_dictionary(self, dictionary)

    def combine_numpy(self, events, times=1):
        dictionary = EventsDictCreator(self, events).create_using_combine_by_numpy(times)
        return EventsFactory.from_dictionary(self, dictionary)

    def combine_by_flattened_list(self, events, times=1):
        """

        :WARNING - UNSAFE METHOD: len(flattened_list) = total occurrences of events.
            if this list is too big, it will raise MemoryError or OverflowError
        """
        dictionary = EventsDictCreator(self, events).create_using_combine_by_flattened_list(times)
        return EventsFactory.from_dictionary(self, dictionary)

    def combine_by_dictionary(self, events, times=1):
        dictionary = EventsDictCreator(self, events).create_using_combine_by_dictionary(times)
        return EventsFactory.from_dictionary(self, dictionary)

    def combine_by_indexed_values(self, events, times=1):
        dictionary = EventsDictCreator(self, events).create_using_combine_by_indexed_values(times)
        return EventsFactory.from_dictionary(self, dictionary)

    def remove(self, events, times=1):
        """

        :WARNING - UNSAFE METHOD: There is no record of what you added to an AdditiveEvents.
            If you remove what you haven't added, no error will be raised, but you will have bugs.
        """
        dictionary = EventsDictCreator(self, events).create_using_remove_by_tuple_list(times)
        return EventsFactory.from_dictionary(self, dictionary)


class EventsDictCreator(object):
    def __init__(self, primary_events, events_to_combine_with):
        self.combiner = DictCombiner(primary_events.get_dict())
        self.to_combine_with = events_to_combine_with.get_dict()

    def create_using_combine_by_fastest(self, times_to_combine):
        new_dict_combiner = self.combiner.combine_by_fastest(self.to_combine_with, times_to_combine)
        return new_dict_combiner.get_dict()

    def create_using_combine_by_numpy(self, times_to_combine):
        new_dict_combiner = self.combiner.combine_by_numpy(self.to_combine_with, times_to_combine)
        return new_dict_combiner.get_dict()

    def create_using_combine_by_dictionary(self, times_to_combine):
        new_dict_combiner = self.combiner.combine_by_dictionary(self.to_combine_with, times_to_combine)
        return new_dict_combiner.get_dict()

    def create_using_combine_by_flattened_list(self, times_to_combine):
        new_dict_combiner = self.combiner.combine_by_flattened_list(self.to_combine_with, times_to_combine)
        return new_dict_combiner.get_dict()

    def create_using_combine_by_indexed_values(self, times_to_combine):
        new_dict_combiner = self.combiner.combine_by_indexed_values(self.to_combine_with, times_to_combine)
        return new_dict_combiner.get_dict()

    def create_using_remove_by_tuple_list(self, times_to_remove):
        new_dict_combiner = self.combiner.remove_by_tuple_list(self.to_combine_with, times_to_remove)
        return new_dict_combiner.get_dict()
