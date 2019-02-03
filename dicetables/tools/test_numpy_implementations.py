import numpy as np

import unittest


class TestNumpyImplementation(unittest.TestCase):

    def test_dict_to_array(self):
        test_dict = {x: 2*x for x in range(5)}
        expected = np.array([[0, 1, 2, 3, 4], [0, 2, 4, 6, 8]])


