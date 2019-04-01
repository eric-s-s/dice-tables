from bisect import insort
from collections import namedtuple

Alias = namedtuple('Alias', ['primary', 'alternate', 'primary_max'])


class AliasTable(object):
    def __init__(self, input_dict):
        self._height = sum(input_dict.values())
        self._length = len(input_dict)
        self._aliases = self._create_aliases(input_dict)

    def _create_aliases(self, input_dict):
        frequency_event = sorted(((frequency * self._length, event) for event, frequency in input_dict.items()))
        alias_list = []
        for _ in range(self._length - 1):
            max_event, max_frequency, new_alias = _get_next_alias(frequency_event)

            alias_list.append(new_alias)

            new_max_frequency = max_frequency - (self._height - new_alias.primary_max)
            _update_frequency_event_list(frequency_event, new_max_frequency, max_event)

        final_alias = _get_final_alias(frequency_event)
        alias_list.append(final_alias)

        return alias_list

    @property
    def height(self):
        return self._height

    @property
    def length(self):
        return self._length

    def to_list(self):
        return self._aliases[:]

    def get(self, length, height):
        alias = self._aliases[length]
        if height >= alias.primary_max:
            return alias.alternate
        return alias.primary


def _update_frequency_event_list(frequency_event, new_frequency, new_event):
    if new_frequency > 0:
        insort(frequency_event, (new_frequency, new_event))


def _get_next_alias(frequency_event):
    min_frequency, min_event = frequency_event.pop(0)
    max_frequency, max_event = frequency_event.pop()
    new_alias = Alias(primary=min_event, alternate=max_event, primary_max=min_frequency)
    return max_event, max_frequency, new_alias


def _get_final_alias(frequency_event):
    final_min_frequency, final_min_event = frequency_event.pop(0)
    try:
        final_max_event = frequency_event.pop()[1]
    except IndexError:
        final_max_event = final_min_event
    alias = Alias(primary=final_min_event, alternate=final_max_event, primary_max=final_min_frequency)
    return alias
