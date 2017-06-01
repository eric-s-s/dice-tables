import doctest
import unittest
import warnings


# Note loader and ignore are required arguments for unittest even if unused.
def load_tests(loader, tests, ignore):

    flags = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE | doctest.IGNORE_EXCEPTION_DETAIL

    tests.addTests(doctest.DocFileSuite("README.rst", optionflags=flags))
    return tests


if __name__ == '__main__':
    warnings.simplefilter("ignore")
    unittest.main()
