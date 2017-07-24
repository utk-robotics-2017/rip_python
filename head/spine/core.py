import time
import os
import serial
import signal
import logging
import json
import sys
import atexit
from threading import Lock as TLock
from multiprocessing import Lock as PLock
import importlib

from .appendages.utils.logger import Logger
from .appendages.utils.decorators import attr_check, type_check, void, singleton
# Third-party
from .py_cmd_messenger.src.py_cmd_messenger import CmdMessenger
from .py_cmd_messenger.src.arduino import ArduinoBoard

logger = Logger()

CURRENT_ARDUINO_CODE_DIR = "/Robot/CurrentArduinoCode"


class DelayedKeyboardInterrupt(object):
    def __enter__(self):
        self.signal_received = False
        self.old_handler = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, self.handler)

    def handler(self, signal, frame):
        self.signal_received = (signal, frame)
        logging.info('SIGINT received. Delaying KeyboardInterrupt.')

    def __exit__(self, type, value, traceback):
        signal.signal(signal.SIGINT, self.old_handler)
        if self.signal_received:
            self.old_handler(*self.signal_received)


class SerialLockException(Exception):
    '''Raised when attempting to access a locked serial device.
    This happens when a lockfile already exists in the lock location, usually
    in ``/var/lock``. It's possible that someone is using this serial port. If
    not, the fix is to simply remove the lock using `rm`.
    '''
    pass


@singleton
@attr_check
class Spine:
    '''Provides a simple interface to the robot's peripherals.
    There is no need to create more than one Spine object. In fact, it is not
    possible due to serial port locking.
    Note that typically commands will assert a successful response from one of
    the micros even if there is no return value.
    '''
    arduinos = dict
    messengers = dict
    use_lock = bool
    lock_dir = str
    sim = bool
    devices = list
    tlock = TLock
    plock = PLock

    def __new__(cls):
        return object.__new__(cls)

    @type_check
    def __init__(self, timeout: float=1.0, **kwargs):
        '''
            Parameters
            ----------
            timeout: float
                The serial timeout. Probably should not change

            Keyword Arguments
            -----------------
            use_lock: bool
                Whether to respect and create the lock files in ``/var/lock``. Should
                probably always be true, the default.
            lock_dir: str
                Location of the lock files. Defaults to ``/var/lock/``.
            ports: dict
                A dictionary of the ports and serial devices they are connected to.
                See DEF_PORTS in the module `head.spine.core` for the default and an
                example of a valid setting.
        '''
        self.arduinos = {}
        self.messengers = {}
        self.use_lock = kwargs.get('use_lock', True)
        self.lock_dir = kwargs.get('lock_dir', '/var/lock/')

        self.sim = kwargs.get('sim', False)
        self.devices = devices = kwargs.get('devices', self.grab_connected_devices())

        self.tlock = TLock()
        self.plock = PLock()

        config = {}
        for device in devices:
            if not self.sim:
                if self.use_lock:
                    lockfn = "{0:s}{1:s}.lck".format(self.lock_dir, device)
                    if os.path.isfile(lockfn):
                        self.close()
                        print(("Lockfile {0:s} exists. It's possible that someone is using this " +
                               "serial port. If not, remove this lock file. Closing and raising " +
                               "error.").format(lockfn))
                        sys.exit()

                logger.info("Connecting to /dev/{0:s}.".format(device))

                self.arduinos[device] = ArduinoBoard("/dev/{0:s}".format(device), baud_rate=115200,
                                                     timeout=timeout)
                if self.use_lock:
                    with open(lockfn, 'w') as f:
                        f.write('RIP Core')
                    os.chmod(lockfn, 0o777)
                    logger.info('Created lock at {0:s}.'.format(lockfn))
            config_file = open("{0:s}/{1:s}/{1:s}_core.json".format(CURRENT_ARDUINO_CODE_DIR, device))
            config[device] = json.loads(config_file.read())
            self.configure_arduino(config)
        self.serial_timeout = timeout

    @type_check
    def grab_connected_devices(self) -> list:
        ''' Collects a list of the connected Microcontrollers

            Returns
            -------
                list A list of the names of the connected microcontrollers
        '''
        device_options = []
        # Loop through the Current Arduino Code Directory
        for d in os.listdir(CURRENT_ARDUINO_CODE_DIR):
            # If there is a directory (that isn't the hidden git directory) and it contains a config file
            # then add its name to the list 
            if(os.path.isdir("{0:s}/{1:s}".format(CURRENT_ARDUINO_CODE_DIR, d)) and d != ".git" and
               os.path.exists("{0:s}/{1:s}/{1:s}.json".format(CURRENT_ARDUINO_CODE_DIR, d))):
                device_options.append(d)

        # Simulation assumes that all arduinos are connected
        if self.sim:
            return deviceOptions
        # Filter by the devices that are connected
        else:
            connectedDeviceOptions = [d for d in deviceOptions if os.path.exists("/dev/{0:s}".format(d))]
            return connectedDeviceOptions

    @type_check
    def startup(self) -> void:
        ''' Ping Arduino boards and turn on their LEDs.
            This command is useful to run at the beginning of scripts to test each
            Arduino board all at once. Since we have multiple microcontroller
            boards, it is possible for them to encounter their own problems. This
            command will cause the script to fail early.
        '''
        if self.sim:
            return

        time.sleep(2)

        self.ping()

        for devname in self.messengers.keys():
            self.set_led(devname, True)

    @type_check
    def stop(self) -> void:
        ''' Stop as many appendages as possible'''
        if self.sim:
            return

        for appendage in self.appendages.values():
            if hasattr(appendage, 'stop'):
                appendage.stop()

    @type_check
    def close(self):
        ''' Close all serial connections and remove locks.

            Failing to call this when you are done with the Spine object will force
            others to manually remove the locks that you created.

            Note
            ----
            If you are using a :func:`get_spine` environment, this method will
            get called automatically during cleanup.
        '''
        if self.sim:
            return

        for devname in self.messengers.keys():
            self.set_led(devname, False)
            if self.use_lock:
                lockfn = "{0:s}{1:s}.lck".format(self.lock_dir, devname)
            self.arduinos[devname].close()
            logger.info("Closed serial connection to {0:s}.".format(devname))
            if self.use_lock:
                os.remove(lockfn)
                logger.info("Removed lock at {0:s}.".format(lockfn))

    @atexit.register
    def exit(self):
        '''A destructor of sorts'''
        self.stop()
        self.close()

    @type_check
    def send(self, devname: str, has_response: bool, command: str, *args, **kwargs):
        ''' Send a command to a device and return the result. This is a method that
            should be used by the appendages and not directly by anything else.

            Parameters
            ----------
            devname: str
                The device name to send the command to.
            has_response: bool
                Whether the command constitutes a response from the Arduino (aside from the acknowledgement)
            command: str
                The command to send.

            *args:
                Any arguments needed with the command

            Keyword Arguments:
                timeout: float
                    The timeout if this particular command needs a different timeout
        '''

        if 'timeout' in kwargs:
            default_timeout = self.arduinos[devname].comm.timeout
            self.arduinos[devname].comm.timeout = kwargs['timeout']

        self.tlock.acquire()
        self.plock.acquire()
        logger.info("Sending {0:s} to '{1:s}'".format(command, devname))

        # delay any keyboard interrupt until communication has completed
        with DelayedKeyboardInterrupt():
            # 3 tries
            for fails in range(3):
                try:
                    self.messengers[devname].send(command, *args)
                except serial.SerialTimeoutException as t:
                    # Socket connection with the arduino has timedout
                    pass
                except serial.SerialException as e:
                    self.reset_connection(devname)
                finally:
                    break
            # Reset has failed
            else:  #(means that the loop has completed)
                self.reset_system()

            acknowledgement = self.messengers[devname].receive()
            if has_response:
                response = self.messengers[devname].receive()
        # Check if command acknowledged correctly
        try:
            assert (acknowledgement[0] == "kAcknowledge" and
                    self.command_map[devname][acknowledgement[1][0]] == command)
        except AssertionError:
            logger.warning("Acknowledgement error to {0:s}.".format(devname))
            logger.warning("Actual response was {}.".format(repr(acknowledgement)))
            logger.warning("Acknowledged Command was {0:s}.".format(self.command_map[devname][acknowledgement[1][0]]))
            logger.warning("Command was {0:s}.".format(command))
            raise

        # Check if the response (if there is supposed to be a response) is to this command
        if has_response:
            try:
                assert (response[0][:-6] == command and
                        response[0][-6:] == "Result")
            except AssertionError:
                logger.warning("Response error to {0:s}.".format(devname))
                logger.warning("Actual response command was {}".format(repr(response)))
                logger.warning("Command was {0:s}.".format(command))

        if 'timeout' in kwargs:
            self.arduinos[devname].comm.timeout = default_timeout

        self.tlock.release()
        self.plock.release()

        if has_response:
            return response[1]

    @type_check
    def ping(self) -> void:
        ''' Send a ping command to all devices and assert success.
            This is called automatically by :func:`startup()`.
        '''
        if self.sim:
            return

        for devname in self.messengers.keys():
            response = self.send(devname, True, "kPing")
            assert self.command_map[devname][response[0]] == "kPong"

    @type_check
    def set_led(self, devname: str, status: bool) -> void:
        ''' Turns the debug LED on or off for certain devices.
            This is typically only used for debug purposes. LEDs are flashed three
            times on all devices during the :func:`startup()` call.

            Parameters
            ----------
            devname: str
                The device to direct the LED setting to.
            status: bool
                True for on, False for off.
        '''
        if self.sim:
            return

        self.send(devname, False, "kSetLed", status)

    @type_check
    def reset_system(self) -> void:
        '''Reboot the system'''
        self.stop()
        os.system('sudo reboot')

    @type_check
    def reset_connection(self, devname: str) -> void:
        ''' Reset the connection to a specific device

            Parameters
            ----------
            devname: str
                The name of the device to reset
        '''
        # TODO
        # Turn off usb hub
        # Turn on usb hub
        time.sleep(1)
        arduinos = self.grab_connected_devices()

        if devname in arduinos:
            self.arduinos[devname] = ArduinoBoard("/dev/{0:s}".format(devname), baud_rate=115200,
                                                  timeout=self.serial_timeout)

    @type_check
    def configure_arduino(self, config: dict) -> void:
        ''' Sets up the appendages dictionary with all the objects that are
            connected to each Arduino. Also sets up the `CmdMessengers` as well
            as the command map

            Parameters
            ----------
            config: dict
                The dict with all the appendage information needed to setup
        '''
        self.appendages = dict()
        if not self.sim:
            self.command_map = dict()
        for devname, arduino in iter(config.items()):
            appendages = arduino['appendages']
            if self.sim:
                commands_config = None
            else:
                commands_config = arduino['commands']

                commands = [None] * len(commands_config)
                commands[0] = ["kAcknowledge", "i"]
                commands[1] = ["kError", "i"]
                commands[2] = ["kUnknown", ""]
                commands[3] = ["kSetLed", "?"]
                commands[4] = ["kPing", ""]
                commands[5] = ["kPingResult", "i"]
                commands[6] = ["kPong", ""]

                self.command_map[devname] = {}
                self.command_map[devname][0] = "kAcknowledge"
                self.command_map[devname][1] = "kError"
                self.command_map[devname][2] = "kUnknown"
                self.command_map[devname][3] = "kSetLed"
                self.command_map[devname][4] = "kPing"
                self.command_map[devname][5] = "kPingResult"
                self.command_map[devname][6] = "kPong"

            m = self.__module__[:-4]
            for appendage in appendages:
                ''' Magic voodoo that imports a class from the appendages folder with the specific
                    type and instantiates it
                    
                    In reality use the name of the appendage to find the module that contains it (based on the appendage name)
                    and then get the class from the module (also based on the appendage name)

                    Reference
                    ---------
                    http://stackoverflow.com/questions/4821104/python-dynamic-instantiation-from-string-name-of-a-class-in-dynamically-imported
                '''
                module = importlib.import_module("{0:s}appendages.rip.{1:s}"
                                                 .format(m, appendage['type']).lower().replace(' ', '_'))
                class_ = getattr(module, appendage['type'].title().replace(' ', ''))

                self.appendages[appendage['label']] = class_(self, devname, appendage, commands_config, self.sim)
                if not self.sim:
                    for i, command in self.appendages[appendage['label']].get_command_parameters():
                        if commands[i] is None:
                            commands[i] = command
                            self.command_map[devname][i] = commands[i][0]
            if not self.sim:
                self.messengers[devname] = CmdMessenger(self.arduinos[devname], commands)

    @type_check
    def get_appendage(self, label: str):
        ''' Returns the appendage with the specified label'''
        return self.appendages[label]

    @type_check
    def get_appendage_dict(self) -> dict:
        ''' Returns the entire appendage dict '''
        return self.appendages

    @type_check
    def print_appendages(self) -> void:
        ''' Prints the appendage dict '''
        print(self.appendages)
