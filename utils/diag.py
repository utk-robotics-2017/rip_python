# Python modules
import logging
from collections import OrderedDict

# Local modules
from ..head.spine.core import get_spine
from ..head.spine.ourlogging import setup_logging

setup_logging(__file__)
logger = logging.getLogger(__name__)
PASS_TEST = 0
FAILED_TEST = 1

with get_spine() as s:
    appendages = s.get_appendage_dict()
    sorted_appendages = OrderedDict(sorted(appendages.items(), key=lambda e: e.__class__))
    for label, appendage in iter(sorted_appendages.items()):
        while True:
            print("\n--------------------------\n")
            ans = input("Should we run the tests for {0:s}? (y/n)".format(label))

            if ans.lower() in ['yes', 'y']:
                result = appendage.run_tests()
                if result == FAILED_TEST:
                    appendage.show_suggestions()
                    break
                else:
                    ans = input("Should we run the tests for {0:s} again? (y/n)".format(label))
                    if ans.lower in ['yes', 'y']:
                        continue
                    else:
                        break
            elif ans.lower() in ['no', 'n']:
                print("Skipping tests for {0:s}...".format(label))
                break
        if result == FAILED_TEST:
            break
