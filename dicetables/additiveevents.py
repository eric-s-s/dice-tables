"""
AdditiveEvents is the general case for DiceTable - an IntegerEvents that can combine with other IntegerEvents.
"""
from typing import TypeVar, Type, Dict

from dicetables.eventsbases.integerevents import IntegerEvents
from dicetables.factory.eventsfactory import EventsFactory
from dicetables.tools.dictcombiner import DictCombiner


def scrub_zeroes(dictionary):
    return {key: val for key, val in dictionary.items() if val}


T = TypeVar('T', bound='AdditiveEvents')


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
    def new(cls: Type[T]) -> T:
        return EventsFactory.new(cls)

    def get_dict(self) -> Dict[int, int]:
        return self._table.copy()

    def __str__(self):
        min_event = min(self._table.keys())
        max_event = max(self._table.keys())
        return 'table from {} to {}'.format(min_event, max_event)

    def combine(self: T, events: IntegerEvents, times: int = 1) -> T:
        dictionary = DictCombiner(self.get_dict()).combine_by_fastest(events.get_dict(), times)
        return EventsFactory.from_dictionary(self, dictionary)

    def combine_by_flattened_list(self: T, events: IntegerEvents, times: int = 1) -> T:
        """

        :WARNING - UNSAFE METHOD: len(flattened_list) = total occurrences of events.
            if this list is too big, it will raise MemoryError or OverflowError
        """
        dictionary = DictCombiner(self.get_dict()).combine_by_flattened_list(events.get_dict(), times)
        return EventsFactory.from_dictionary(self, dictionary)

    def combine_by_dictionary(self: T, events: IntegerEvents, times: int = 1) -> T:
        dictionary = DictCombiner(self.get_dict()).combine_by_dictionary(events.get_dict(), times)
        return EventsFactory.from_dictionary(self, dictionary)

    def combine_by_indexed_values(self: T, events: IntegerEvents, times: int = 1) -> T:
        dictionary = DictCombiner(self.get_dict()).combine_by_indexed_values(events.get_dict(), times)
        return EventsFactory.from_dictionary(self, dictionary)

    def remove(self: T, events: IntegerEvents, times: int = 1) -> T:
        """

        :WARNING - UNSAFE METHOD: There is no record of what you added to an AdditiveEvents.
            If you remove what you haven't added, no error will be raised, but you will have bugs.
        """
        dictionary = DictCombiner(self.get_dict()).remove_by_tuple_list(events.get_dict(), times)
        return EventsFactory.from_dictionary(self, dictionary)
