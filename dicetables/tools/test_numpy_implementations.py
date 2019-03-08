import unittest

import numpy as np
from numpy.testing import assert_array_equal


class NumpyIndexedArray(object):
    def __init__(self, array: np.ndarray, start_index: int):
        self.array = array
        self.start_index = start_index

    @classmethod
    def from_dict(cls, input_dict):
        start = min(input_dict)
        end = max(input_dict)
        array = np.zeros(end - start + 1, dtype=object)
        for key, value in input_dict.items():
            array[key - start] = value
        return cls(array, start)

    def to_dict(self):
        return {index + self.start_index: value for index, value in enumerate(self.array) if value}

    def combine_with_dict(self, input_dict, times):
        current = self
        dict_key_min = min(input_dict)
        dict_key_max = max(input_dict)
        for _ in range(times):
            current = current.combine_once_with_dict(input_dict, dict_key_min, dict_key_max)
        return current

    def combine_once_with_dict(self, input_dict, dict_key_min, dict_key_max):
        added_size = dict_key_max - dict_key_min
        answer_array = np.zeros(self.array.size + added_size, dtype=object)

        new_start_index = dict_key_min + self.start_index
        for index, multiplier in input_dict.items():
            to_add = self.array
            if multiplier != 1:
                to_add = self.array * multiplier
            insertion_point = index - dict_key_min
            answer_array[insertion_point: insertion_point + to_add.size] += to_add
        return NumpyIndexedArray(answer_array, new_start_index)


class TestNumpyImplementation(unittest.TestCase):

    def test_numpy_indexed_array_init(self):
        np_indexed = NumpyIndexedArray(np.array([1, 2, 3]), 3)
        assert_array_equal(np_indexed.array, np.array([1, 2, 3]))
        self.assertEqual(np_indexed.start_index, 3)

    def test_numpy_indexed_array_from_dict(self):
        test_dict = {1: 1, 2: 3}
        indexed = NumpyIndexedArray.from_dict(test_dict)
        assert_array_equal(indexed.array, np.array([1, 3]))
        self.assertEqual(indexed.start_index, 1)

    def test_numpy_indexed_array_from_dict_with_spaces(self):
        test_dict = {2: 1, 4: 2}
        indexed = NumpyIndexedArray.from_dict(test_dict)
        assert_array_equal(indexed.array, np.array([1, 0, 2]))
        self.assertEqual(indexed.start_index, 2)

    def test_numpy_indexed_array_to_dict(self):
        test_dict = {2: 1, 4: 2}
        result = NumpyIndexedArray.from_dict(test_dict).to_dict()
        self.assertEqual(test_dict, result)

    def test_combine_with_dict_once(self):
        d_two = {1: 1, 2: 1}
        two_d_two = {2: 1, 3: 2, 4: 1}
        array_combiner = NumpyIndexedArray.from_dict(d_two)
        answer = array_combiner.combine_with_dict(d_two, times=1)
        self.assertEqual(answer.to_dict(), two_d_two)

    def test_combine_with_dict_twice(self):
        d_two = {1: 1, 2: 1}
        three_d_two = {3: 1, 4: 3, 5: 3, 6: 1}
        array_combiner = NumpyIndexedArray.from_dict(d_two)
        answer = array_combiner.combine_with_dict(d_two, times=2)
        self.assertEqual(answer.to_dict(), three_d_two)

    def test_combine_with_dict_large_numbers_in_indexed_array(self):
        current = {1: 10 ** 1000, 2: 10 ** 1000}
        array_combiner = NumpyIndexedArray.from_dict(current)
        combined_d_two = {2: 10 ** 1000, 3: 2 * 10 ** 1000, 4: 10 ** 1000}
        answer = array_combiner.combine_with_dict({1: 1, 2: 1}, 1)
        self.assertEqual(answer.to_dict(), combined_d_two)

    def test_combine_with_dict_large_numbers_in_dictionary(self):
        current = {1: 1, 2: 1}
        array_combiner = NumpyIndexedArray.from_dict(current)
        combined_d_two = {2: 10 ** 1000, 3: 2 * 10 ** 1000, 4: 10 ** 1000}
        answer = array_combiner.combine_with_dict({1: 10 ** 1000, 2: 10 ** 1000}, 1)
        self.assertEqual(answer.to_dict(), combined_d_two)
