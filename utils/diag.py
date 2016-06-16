# Python modules
import time
import logging
import cv2
import os

# Local modules
from head.spine.core import get_spine
from head.spine.Vec3d import Vec3d
from head.spine.ourlogging import setup_logging

setup_logging(__file__)
logger = logging.getLogger(__name__)

with get_spine() as s:
    def test(f, prompt):
        while True:
            print ''
            print '----------------------------'
            print ''
            print("Starting the '%s' test." % (f.__name__))
            print("Prompt will be '%s'." % prompt)
            ans = ''
            while ans not in ['y', 'n']:
                ans = raw_input("Should we run the '%s' test? (y/n) " % (f.__name__))

            if ans == 'n':
                return False

            f()
            ans = ''
            while ans not in ['y', 'n', 'rerun']:
                ans = raw_input("%s (y/n/rerun) " % (prompt))
            if ans == 'y':
                return False
            if ans == 'n':
                return False
