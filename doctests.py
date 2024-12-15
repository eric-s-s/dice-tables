import doctest
import unittest
import warnings
import os


# Note loader and ignore are required arguments for unittest even if unused.
def load_tests(loader, tests, ignore):
    excluded_dirs = ["venv", ".tox"]

    flags = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE | doctest.IGNORE_EXCEPTION_DETAIL
    for path, _, files in os.walk("."):
        if not any(excluded in path for excluded in excluded_dirs):
            for file in files:
                if file.endswith(".rst"):
                    name = os.path.join(path, file)
                    print("added file: ", name)
                    tests.addTests(doctest.DocFileSuite(name, optionflags=flags))
    return tests


if __name__ == "__main__":
    warnings.simplefilter("ignore")
    unittest.main()
