import unittest

from dicetables.tools.alias_table import AliasTable, Alias


class TestAliasTable(unittest.TestCase):
    def test_alias(self):
        primary = 1
        alternate = 2
        primary_max = 3
        alias = Alias(primary=primary, alternate=alternate, primary_max=primary_max)
        self.assertEqual(alias.primary, primary)
        self.assertEqual(alias.alternate, alternate)
        self.assertEqual(alias.primary_max, primary_max)

    def assert_alias_table_has_expected_counts(self, alias_table, expected_counts):
        actual_counts = dict.fromkeys(expected_counts.keys(), 0)
        for length_val in range(alias_table.length):
            for height_val in range(alias_table.height):
                actual_counts[alias_table.get(length_val, height_val)] += 1

        self.assertEqual(expected_counts, actual_counts)

        actual_primaries = {alias.primary for alias in alias_table.to_list()}
        expected_primaries = set(expected_counts.keys())
        self.assertEqual(actual_primaries, expected_primaries)

    def test_alias_table(self):
        input_dict = {1: 1, 3: 4, 5: 2}
        expected_height = 1 + 4 + 2
        expected_length = 3

        alias_table = AliasTable(input_dict)

        self.assertEqual(alias_table.height, expected_height)
        self.assertEqual(alias_table.length, expected_length)

        expected_counts = {1: 3, 3: 12, 5: 6}

        self.assert_alias_table_has_expected_counts(alias_table, expected_counts)

    def test_even_alias_table_even_number(self):
        input_dict = {1: 2, 2: 2, 3: 2, 4: 2}
        expected_counts = {1: 8, 2: 8, 3: 8, 4: 8}

        alias_table = AliasTable(input_dict)
        self.assertEqual(alias_table.length, 4)
        self.assertEqual(alias_table.height, 8)

        self.assert_alias_table_has_expected_counts(alias_table, expected_counts)

    def test_even_alias_table_odd_number(self):
        input_dict = {1: 2, 2: 2, 4: 2}
        expected_counts = {1: 6, 2: 6, 4: 6}

        alias_table = AliasTable(input_dict)
        self.assertEqual(alias_table.length, 3)
        self.assertEqual(alias_table.height, 6)
        self.assert_alias_table_has_expected_counts(alias_table, expected_counts)

    def test_alias_table_to_list(self):
        input_dict = {1: 1, 2: 2, 3: 2, 4: 3}
        alias_table = AliasTable(input_dict)
        expected_list = [
            Alias(primary=1, alternate=4, primary_max=4),
            Alias(primary=2, alternate=4, primary_max=8),
            Alias(primary=3, alternate=4, primary_max=8),
            Alias(primary=4, alternate=4, primary_max=8)
        ]
        self.assertEqual(alias_table.to_list(), expected_list)

    def test_alias_table_to_list_silly_test_so_that_i_can_visualize_algorithm_better(self):
        input_dict = {1: 1, 2: 3, 3: 4, 4: 6, 5: 7}
        alias_table = AliasTable(input_dict)
        self.assertEqual(alias_table.height, 21)
        self.assert_alias_table_has_expected_counts(alias_table, {1: 5, 2: 15, 3: 20, 4: 30, 5: 35})

        expected_list = [
            Alias(primary=1, alternate=5, primary_max=5),  # {2: 15, 3: 20, 4: 30, 5: 19 (35-16)}
            Alias(primary=2, alternate=4, primary_max=15),  # {3: 20, 4: 24 (30-6), 5: 19}
            Alias(primary=5, alternate=4, primary_max=19),  # {3: 20, 4: 24-2, 5: 19}
            Alias(primary=3, alternate=4, primary_max=20),  # {3: 20, 4: 22}
            Alias(primary=4, alternate=4, primary_max=21)
        ]
        self.assertEqual(alias_table.to_list(), expected_list)

    def test_alias_table_to_list_does_not_mutate_alias_table(self):
        input_dict = {1: 1}
        alias_table = AliasTable(input_dict)

        alias_list = alias_table.to_list()
        alias_list[0] = Alias(2, 2, 2)
        self.assertNotEqual(alias_table.to_list(), alias_list)

        expected = [Alias(1, 1, 1)]
        self.assertEqual(alias_table.to_list(), expected)
