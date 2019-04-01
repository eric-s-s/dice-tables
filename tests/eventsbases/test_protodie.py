# pylint: disable=missing-docstring, invalid-name, too-many-public-methods
from __future__ import absolute_import

import unittest

from dicetables.eventsbases.protodie import ProtoDie


class DummyDie(ProtoDie):
    def __init__(self, size, weight, dictionary, repr_str):
        self.size = size
        self.weight = weight
        self.dictionary = dictionary
        self.repr_str = repr_str
        super(DummyDie, self).__init__()

    def get_dict(self):
        return self.dictionary

    def get_size(self):
        return self.size

    def get_weight(self):
        return self.weight

    def __repr__(self):
        return self.repr_str

    def __str__(self):
        return 'hi'

    def multiply_str(self, number):
        return str(number)

    def weight_info(self):
        return "OyVei! you're too thin. Es, bubelah."


class TestProtoDie(unittest.TestCase):

    def test_ProtoDie_not_implemented_errors(self):
        self.assertRaises(NotImplementedError, ProtoDie)

        class TestDie(ProtoDie):
            def get_dict(self):
                return {1: 1}

        test = TestDie()
        self.assertRaises(NotImplementedError, test.get_size)
        self.assertRaises(NotImplementedError, test.get_weight)
        self.assertRaises(NotImplementedError, test.weight_info)
        self.assertRaises(NotImplementedError, test.multiply_str, 3)
        self.assertRaises(NotImplementedError, test.__str__)
        self.assertRaises(NotImplementedError, test.__repr__)

    # rich comparison testing
    def test_ProtoDie_equality_true(self):
        first = DummyDie(2, 3, {2: 2}, 'b')
        second = DummyDie(2, 3, {2: 2}, 'b')
        self.assertTrue(first == second)

    def test_ProtoDie_equality_false_if_different_types_eval_the_same(self):
        class NewDummyDie(DummyDie):
            def __init__(self, size, weight, dictionary, repr_str):
                super(NewDummyDie, self).__init__(size, weight, dictionary, repr_str)

        first = DummyDie(2, 3, {2: 2}, 'b')
        second = NewDummyDie(2, 3, {2: 2}, 'b')
        self.assertFalse(first == second)

    def test_ProtoDie_equality_false_by_size(self):
        first = DummyDie(2, 3, {2: 2}, 'b')
        second = DummyDie(100, 3, {2: 2}, 'b')
        self.assertFalse(first == second)

    def test_ProtoDie_equality_false_by_weight(self):
        first = DummyDie(2, 3, {2: 2}, 'b')
        second = DummyDie(2, 100, {2: 2}, 'b')
        self.assertFalse(first == second)

    def test_ProtoDie_equality_false_by_get_dict(self):
        first = DummyDie(2, 3, {200: 200}, 'b')
        second = DummyDie(2, 3, {2: 2}, 'b')
        self.assertFalse(first == second)

    def test_ProtoDie_equality_false_by_get_repr(self):
        first = DummyDie(2, 3, {2: 2}, 'b')
        second = DummyDie(2, 3, {2: 2}, 'different repr')
        self.assertFalse(first == second)

    def test_ProtoDie_equality_false_by_not_a_proto_die(self):
        self.assertFalse(DummyDie(2, 3, {2: 2}, 'b') == 2)

    def test_lt_false_if_equal(self):
        first = DummyDie(2, 3, {2: 2}, 'a')
        second = DummyDie(2, 3, {2: 2}, 'a')
        self.assertFalse(first < second)
        self.assertFalse(second < first)

    def test_ProtoDie_lt_by_size(self):
        first = DummyDie(2, 3, {2: 2}, 'b')
        second = DummyDie(20, 3, {2: 2}, 'b')
        self.assertTrue(first < second)

    def test_ProtoDie_lt_by_weight(self):
        first = DummyDie(2, 3, {2: 2}, 'b')
        second = DummyDie(2, 30, {2: 2}, 'b')
        self.assertTrue(first < second)

    def test_ProtoDie_lt_by_sorted_get_dict(self):
        first = DummyDie(2, 3, {2: 200, 20: 200}, 'b')
        second = DummyDie(2, 3, {20: 2}, 'b')
        third = DummyDie(2, 3, {20: 20}, 'b')
        self.assertTrue(first < second)
        self.assertTrue(first < third)
        self.assertTrue(second < third)

    def test_ProtoDie_lt_by_repr(self):
        first = DummyDie(2, 3, {2: 2}, 'a')
        second = DummyDie(2, 3, {2: 2}, 'b')
        self.assertTrue(first < second)

    def test_ProtoDie_lt_by_size_is_most_important(self):
        first = DummyDie(2, 30, {20: 20}, 'b')
        second = DummyDie(20, 3, {2: 2}, 'a')
        self.assertTrue(first < second)

    def test_ProtoDie_lt_by_weight_is_second_most_important(self):
        first = DummyDie(2, 3, {20: 20}, 'b')
        second = DummyDie(2, 30, {2: 2}, 'a')
        self.assertTrue(first < second)

    def test_ProtoDie_lt_by_sorted_get_dict_is_third_most_important_and_so_repr_is_last(self):
        first = DummyDie(2, 3, {2: 2}, 'b')
        second = DummyDie(2, 3, {20: 20}, 'a')
        self.assertTrue(first < second)

    def test_ProtoDie_not_equal_true(self):
        first = DummyDie(20, 3, {2: 2}, 'a')
        second = DummyDie(2, 3, {2: 2}, 'a')
        self.assertTrue(first != second)
        self.assertFalse(first == second)

    def test_ProtoDie_not_equal_false(self):
        first = DummyDie(2, 3, {2: 2}, 'a')
        second = DummyDie(2, 3, {2: 2}, 'a')
        self.assertTrue(first == second)
        self.assertFalse(first != second)

    def test_ProtoDie_gt_true(self):
        first = DummyDie(20, 3, {2: 2}, 'a')
        second = DummyDie(2, 3, {2: 2}, 'a')
        self.assertTrue(first > second)

    def test_ProtoDie_gt_false(self):
        first = DummyDie(20, 3, {2: 2}, 'a')
        second = DummyDie(2, 3, {2: 2}, 'a')
        self.assertFalse(second > first)
        self.assertFalse(first > first)

    def test_ProtoDie_le_true(self):
        first = DummyDie(2, 3, {2: 2}, 'a')
        second = DummyDie(20, 3, {2: 2}, 'a')
        self.assertTrue(first <= second)
        self.assertTrue(first <= first)

    def test_ProtoDie_le_false(self):
        first = DummyDie(2, 3, {2: 2}, 'a')
        second = DummyDie(20, 3, {2: 2}, 'a')
        self.assertFalse(second <= first)

    def test_ProtoDie_ge_true(self):
        first = DummyDie(20, 3, {2: 2}, 'a')
        second = DummyDie(2, 3, {2: 2}, 'a')
        self.assertTrue(first >= second)
        self.assertTrue(first >= first)

    def test_ProtoDie_ge_false(self):
        first = DummyDie(20, 3, {2: 2}, 'a')
        second = DummyDie(2, 3, {2: 2}, 'a')
        self.assertFalse(second >= first)

    def test_ProtoDie_hash(self):
        hash_str = 'hash of REPR, 2, 3, {4: 5}'
        self.assertEqual(hash(DummyDie(2, 3, {4: 5}, 'REPR')), hash(hash_str))


if __name__ == '__main__':
    unittest.main()
