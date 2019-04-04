from collections import namedtuple

Alias = namedtuple('Alias', ['primary', 'alternate', 'primary_height'])


class AliasTable(object):
    """

    here is
    `a nice explanation of alias tables: <http://www.keithschwarz.com/darts-dice-coins/>`_

    `Vose's algorithm <https://web.archive.org/web/20131029203736/http://web.eecs.utk.edu/~vose/Publications/random.pdf>`_

    """

    def __init__(self, input_dict):
        self._height = sum(input_dict.values())
        self._length = len(input_dict)
        self._aliases = self._create_aliases(input_dict)

    def _create_aliases(self, input_dict):
        big_heights, small_heights = self._get_height_sorted_lists(input_dict)

        alias_list = []
        while small_heights:
            primary, primary_height = small_heights.pop()
            alternate, alternate_height = big_heights.pop()
            alias_list.append(Alias(primary=primary, alternate=alternate, primary_height=primary_height))
            new_alternate_height = alternate_height - (self._height - primary_height)
            self._update_sorting_lists(alternate, new_alternate_height, big_heights, small_heights)

        while big_heights:
            primary, _ = big_heights.pop()
            alias_list.append(Alias(primary=primary, alternate=primary, primary_height=self._height))

        return alias_list

    def _update_sorting_lists(self, event, event_height, big_heights, small_heights):
        if event_height < self._height:
            small_heights.append((event, event_height))
        else:
            big_heights.append((event, event_height))

    def _get_height_sorted_lists(self, input_dict):
        less_than_height = []
        greater_than_or_equal_height = []
        for event, frequency in sorted(input_dict.items()):
            event_height = self._length * frequency
            self._update_sorting_lists(event, event_height, greater_than_or_equal_height, less_than_height)
        return greater_than_or_equal_height, less_than_height

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
        if height >= alias.primary_height:
            return alias.alternate
        return alias.primary
