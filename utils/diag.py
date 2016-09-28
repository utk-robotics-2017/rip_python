# Python modules
import logging
from collections import OrderedDict

# Local modules
from ..head.spine.core import get_spine
from ..head.spine.ourlogging import setup_logging

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
PASS_TEST = 0
FAILED_TEST = 1

#set up command line arguemnts
#ap = argparse.ArgumentParser()
#ap.add_argument("-i", "--input", required=True, help="Path to json config file for what is connected to the Arduino.")
#args = vars(ap.parse_args())

#open input file for reading
#try:
#    fi = open(args["input"], "r")
#except IOError:
#    print "Fool! Your config file does not exist. Please enter a valid path to the file."

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
