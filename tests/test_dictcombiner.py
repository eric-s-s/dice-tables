import unittest
from dicetables.baseevents import AdditiveEvents
from tools.dictcombiner import flatten_events_tuples, get_best_key, get_current_size_cutoff, DictCombiner

# TODO test every set of keys in dict for fastest method.  how fucking embarrassing


class TestDictCombiner(unittest.TestCase):
    def setUp(self):
        self.identity_combiner = DictCombiner({0: 1})

    def tearDown(self):
        del self.identity_combiner

    """
    the next several tests show how AdditiveEvents.get_fastest_method works.  The edge cases to choose between
    methods were determined empirically.  To see how they were derived see time_trials/flattenedlist_timetrials.py
    and time_trials/indexedvalues_timetrials.py.  Those modules require numpy and matplotlib where the actual
    project does not.  Before running either one, under "if __name__ == '__main__':" make sure to comment in
    the UI you wish to use.  The full data set for determining whether to use indexed_values is this:
        {
        2: {10: (250, 500), 50: (100, 200), 500: (1, 1)},
        3: {4: (500, 500), 10: (50, 100), 20: (10, 50), 50: (1, 10), 100: (1, 1)},
        4: {2: (500, 100), 4: (50, 100), 20: (1, 50), 50: (1, 1)},
        6: {2: (500, 500), 4: (10, 50), 20: (1, 1)},
        8: {1: (500, 1000), 2: {200, 200}, 5: (50, 50), 10: (1, 1)},
        20: {1: (50, 100), 3: (1, 50), 4: (1, 1)},
        50: {1: (50, 100), 3: (1, 1)}
        }
    data_dict = {new_event size: {times: (current_events_size_choices), ...}, ...}
    (current_events_size_choices)  is minimum size of AdditiveEvents to use with 'indexed_values'
    by ('flattened_list', 'tuple_list') methods.
    """
    def test_DictCombiner_get_fastest_method_one_current_events_and_one_times_never_picks_indexed_values(self):
        accepted_choices = ('tuple_list', 'flattened_list')
        for power_of_two in range(10):
            """
            events are:
            len(events) = 2**power_of_two (start =1, end = about 10**3)
            single = 1 occurrence
            some = 1, 2, 3 occurrences
            high = 1 + 2 ** event value
            """
            single_occurrence, some_occurrence, high_occurrence = next(events_generator())
            self.assertIn(self.identity_combiner.get_fastest_combine_method(1, single_occurrence), accepted_choices)
            self.assertIn(self.identity_combiner.get_fastest_combine_method(1, some_occurrence), accepted_choices)
            self.assertIn(self.identity_combiner.get_fastest_combine_method(1, high_occurrence), accepted_choices)

    def test_DictCombiner_get_fastest_method_tuple_vs_flattened_by_total_occurrences_min(self):
        events = AdditiveEvents({1: 1})
        self.assertEqual(self.identity_combiner.get_fastest_combine_method(1, events), 'flattened_list')

    def test_DictCombiner_get_fastest_method_tuple_vs_flattened_by_total_occurrences_mid(self):
        events = AdditiveEvents(dict.fromkeys(range(100), 1))
        self.assertEqual(self.identity_combiner.get_fastest_combine_method(1, events), 'flattened_list')

    def test_DictCombiner_get_fastest_method_tuple_vs_flattened_by_total_occurrences_edge(self):
        events = AdditiveEvents(dict.fromkeys(range(9999), 1))
        self.assertEqual(self.identity_combiner.get_fastest_combine_method(1, events), 'flattened_list')

    def test_DictCombiner_get_fastest_method_tuple_vs_flattened_by_total_occurrences_over_edge(self):
        """
        this cutoff is not for speed but for safety.  as the next test will demonstrate
        """
        events = AdditiveEvents(dict.fromkeys(range(10000), 1))
        self.assertEqual(self.identity_combiner.get_fastest_combine_method(1, events), 'tuple_list')

    def test_DictCombiner_demonstrate_why_there_is_cutoff_for_flattened_list(self):
        ok_events = [(1, 10 ** 4)]
        self.assertEqual(flatten_events_tuples(ok_events), [1] * 10 ** 4)
        bad_events = [(1, 10 ** 20)]
        self.assertRaises((OverflowError, MemoryError), flatten_events_tuples, bad_events)

    def test_DictCombiner_get_fastest_method_tuple_vs_flattened_by_ratio_under(self):
        events = AdditiveEvents({1: 1, 2: 1, 3: 2, 4: 1})
        ratio = events.total_occurrences / float(len(events.event_keys))
        self.assertEqual(ratio, 1.25)
        self.assertEqual(self.identity_combiner.get_fastest_combine_method(1, events), 'flattened_list')

    def test_DictCombiner_get_fastest_method_tuple_vs_flattened_by_ratio_edge(self):
        events = AdditiveEvents({0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 10: 4})
        ratio = events.total_occurrences / float(len(events.event_keys))
        self.assertEqual(ratio, 1.3)
        self.assertEqual(self.identity_combiner.get_fastest_combine_method(1, events), 'flattened_list')

    def test_DictCombiner_get_fastest_method_tuple_vs_flattened_by_ratio_over_edge(self):
        events_dict = dict.fromkeys(range(99), 1)
        events_dict[100] = 32
        events = AdditiveEvents(events_dict)
        ratio = events.total_occurrences / float(len(events.event_keys))
        self.assertEqual(ratio, 1.31)
        self.assertEqual(self.identity_combiner.get_fastest_combine_method(1, events), 'tuple_list')

    def test_DictCombiner_get_fastest_method_part_get_best_key_below_min(self):
        test_dict = {1: 1, 3: 1, 5: 1}
        self.assertEqual(get_best_key(-1, test_dict), 1)

    def test_DictCombiner_get_fastest_method_part_get_best_key_above_max(self):
        test_dict = {1: 1, 3: 1, 5: 1}
        self.assertEqual(get_best_key(1001, test_dict), 5)

    def test_DictCombiner_get_fastest_method_part_get_best_key_at_value(self):
        test_dict = {1: 1, 3: 1, 5: 1}
        self.assertEqual(get_best_key(3, test_dict), 3)

    def test_DictCombiner_get_fastest_method_part_get_best_key_between_values(self):
        test_dict = {1: 1, 3: 1, 5: 1}
        self.assertEqual(get_best_key(4, test_dict), 3)

    def test_DictCombiner_get_fastest_method_part_get_current_size_cutoff_method_variable(self):
        """
        data used for get_current_size
        {new_event_size: {times: (current_events_size_choices), ...}, ...}
        {4: {2: (500, 100), 4: (50, 100), 20: (1, 50), 50: (1, 1)},
        """
        self.assertEqual(get_current_size_cutoff('flattened_list', 20, 4), 1)
        self.assertEqual(get_current_size_cutoff('tuple_list', 20, 4), 50)

    def test_DictCombiner_get_fastest_method_part_get_current_size_cutoff_uses_get_best_key(self):
        """
        2: {10: (250, 500), 50: (100, 200), 500: (1, 1)},
        4: {2: (500, 100), 4: (50, 100), 20: (1, 50), 50: (1, 1)},
        6: ...
        """
        self.assertEqual(get_current_size_cutoff('tuple_list', 20, 4), 50)
        self.assertEqual(get_current_size_cutoff('tuple_list', 39, 4), 50)
        self.assertEqual(get_current_size_cutoff('tuple_list', 20, 5), 50)
        self.assertEqual(get_current_size_cutoff('tuple_list', 1, 1), 500)
        self.assertEqual(get_current_size_cutoff('tuple_list', 10000, 100000), 1)

    def test_DictCombiner_get_fastest_method_uses_size_cutoff_to_choose_size_of_one_indexed(self):
        """4: {2: (500, 100), 4: (50, 100), 20: (1, 50), 50: (1, 1)},"""
        sized_twenty = AdditiveEvents(dict.fromkeys(range(20), 1))
        self.assertEqual(get_current_size_cutoff('flattened_list', 20, 4), 1)
        self.assertEqual(self.identity_combiner.get_fastest_combine_method(4, sized_twenty),
                         'indexed_values')

    def test_DictCombiner_get_fastest_method_uses_size_cutoff_to_choose_size_of_one_other(self):
        """4: {2: (500, 100), 4: (50, 100), 20: (1, 50), 50: (1, 1)},"""
        sized_four = AdditiveEvents(dict.fromkeys(range(4), 2))
        self.assertEqual(get_current_size_cutoff('tuple_list', 20, 4), 50)
        self.assertEqual(self.identity_combiner.get_fastest_combine_method(4, sized_four), 'tuple_list')

    def test_DictCombiner_get_fastest_method_uses_size_cutoff_to_choose_below_cutoff(self):
        """4: {2: (500, 100), 4: (50, 100), 20: (1, 50), 50: (1, 1)},"""
        sized_four = AdditiveEvents(dict.fromkeys(range(4), 2))
        current_size_five = DictCombiner(dict.fromkeys(range(5), 1))
        self.assertEqual(get_current_size_cutoff('tuple_list', 20, 4), 50)
        self.assertEqual(current_size_five.get_fastest_combine_method(20, sized_four),
                         'tuple_list')

    def test_DictCombiner_get_fastest_method_uses_size_cutoff_to_choose_at_cutoff(self):
        """4: {2: (500, 100), 4: (50, 100), 20: (1, 50), 50: (1, 1)},"""
        sized_four = AdditiveEvents(dict.fromkeys(range(4), 2))
        current_size_fifty = DictCombiner(dict.fromkeys(range(50), 1))
        self.assertEqual(get_current_size_cutoff('tuple_list', 20, 4), 50)
        self.assertEqual(current_size_fifty.get_fastest_combine_method(20, sized_four),
                         'indexed_values')

    def test_DictCombiner_get_fastest_method_uses_size_cutoff_to_choose_above_cutoff(self):
        """4: {2: (500, 100), 4: (50, 100), 20: (1, 50), 50: (1, 1)},"""
        sized_four = AdditiveEvents(dict.fromkeys(range(4), 2))
        current_size_fifty_one = DictCombiner(dict.fromkeys(range(51), 1))
        self.assertEqual(get_current_size_cutoff('tuple_list', 20, 4), 50)
        self.assertEqual(current_size_fifty_one.get_fastest_combine_method(20, sized_four),
                         'indexed_values')


def events_generator():
    step_by_power_of_two = 1
    while True:
        single_occurrence = dict([(event, 1) for event in range(step_by_power_of_two)])
        middle_occurrences = dict([(event, 1 + event % 3) for event in range(step_by_power_of_two)])
        high_occurrences = dict([(event, 1 + 2 * event) for event in range(step_by_power_of_two)])
        step_by_power_of_two *= 2
        yield (AdditiveEvents(single_occurrence),
               AdditiveEvents(middle_occurrences),
               AdditiveEvents(high_occurrences))
