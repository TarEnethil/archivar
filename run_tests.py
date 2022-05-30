#!/usr/bin/env python3

import argparse
import unittest
import sys

from tests.models import suite as model_suite
from tests.helpers import suite as helper_suite
from tests.smoke import suite as smoke_suite


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("tests", help="which tests to run", choices=["all", "models", "helpers", "smoke"],
                        default="all", const="all", nargs="?")  # use "all" when nothing is supplied
    parser.add_argument("-v", "--verbosity", help="how verbose pythons testrunner is",
                        type=int, choices=[0, 1, 2], default=2)
    parser.add_argument("-f", "--failfast", action="store_true", help="stop suite on first failed test")
    parser.add_argument("-i", "--ignore-rc", action="store_true", help="always return 0")
    args = parser.parse_args()

    runner = unittest.TextTestRunner(verbosity=args.verbosity, failfast=args.failfast, descriptions=False)

    successfulTests = True

    if args.tests == "all" or args.tests == "models":
        print("running model tests")
        successfulTests = successfulTests and runner.run(model_suite()).wasSuccessful()

    if args.tests == "all" or args.tests == "helpers":
        print("running helper tests")
        successfulTests = successfulTests and runner.run(helper_suite()).wasSuccessful()

    if args.tests == "all" or args.tests == "smoke":
        print("running smoke tests")
        successfulTests = successfulTests and runner.run(smoke_suite()).wasSuccessful()

    if args.ignore_rc:
        sys.exit(0)

    sys.exit(0 if successfulTests else 1)
