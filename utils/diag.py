# Python modules
import time
import logging
import cv2
import os
import json
import argparse
import sys

#wild shot in the dark to get these imports to fucking work
sys.path.append("/home/kevin/general_robot_platform")

# Local modules
from head.spine.core import get_spine
import head.spine.core
from head.spine.ourlogging import setup_logging

#sensors
#from head.spine.appendages import ultrasonic
#from head.spine.appendages import linesensor
#from head.spine.appendages import linesensor_array
#from head.spine.appendages import i2cencoder
#from head.spine.appendages import encoder
#from head.spine.appendages import switch

#actuator
#from head.spine.appendages import servo
#from head.spine.appendages import motor
#from head.spine.appendages import stepper

#control
#from head.spine.appendages import pid

#system
#from head.spine.appendages import arm
#from head.spine.appendages import velocitycontrolledmotor
#from head.spine.appendages import fourwheeldrivebase

setup_logging(__file__)
logger = logging.getLogger(__name__)

#set up command line arguemnts
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input", required=True, help="Path to json config file for what is connected to the Arduino.")
args = vars(ap.parse_args())

#open input file for reading
try:
    fi = open(args["input"], "r")
except IOError:
    print "Fool! Your config file does not exist. Please enter a valid path to the file."

#read in config file given on command line
#Jokes on you, turns out core handles this
'''file_text= ""
for line in fi:
    file_text = file_text + line
#json_data is a dictionary
json_data = json.loads(file_text)'''

#create dictionary of device classes
'''device_type = {
    'ultrasonic' : ultrasonic,
    'linesensor' : linesensor,
    'i2cencoder' : i2cencoder,
    'encoder' : encoder,
    'switch' : switch,
    'arm' : arm,
    'pid' : pid,
    'servo' : servo,
    'motor' : motor,
    'linesensor_array' : linesensor_array,
    'stepper' : stepper,
    'velocityControlledMotor' : velocitycontrolledmotor,
#    'fourWheelDriveBase' : fourwheeldrivebase
}'''

with get_spine() as s:
    s.print_appendages()
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
            f.test();
            ans = ''
            while ans not in ['y', 'n', 'rerun']:
                ans = raw_input("%s (y/n/rerun) " % (prompt))
            if ans == 'y':
                return False
            if ans == 'n':
                return False
    for label, appendage in s.appendages.iteritems():
        test(appendage, label)
