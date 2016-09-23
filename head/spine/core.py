import time
import os
import signal
import logging
import json
import sys
from multiprocessing import Lock
import importlib

# Third-party
from .ourlogging import setup_logging
from .PyCmdMessenger.PyCmdMessenger.PyCmdMessenger import CmdMessenger
from .PyCmdMessenger.PyCmdMessenger.arduino import ArduinoBoard

setup_logging(__file__)
logger = logging.getLogger(__name__)

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


class get_spine:
    '''A controlled execution environment for Spine.
    This controlled execution environment will provide a reference to a spine
    object in addition to cleanly handling execution completion, keyboard
    interrupts, and other unexpected interruptions such as exceptions. What does
    this mean practically? Whenever your code stops running, this environment
    will make sure that the main robot motors stop and that the serial ports get
    properly closed. Because this environment offers an easy way to avoid
    common issues, it is recommended to use this environment rather than by
    instantiating a Spine object directly.
    For more information on controlled execution environments and Python's
    `with` statement, please see
    `this article <http://effbot.org/zone/python-with-statement.htm>`_.
    '''

    def __init__(self, devices=None, sim=False):
        if devices is not None:
            self.devices = devices
        self.sim = sim

    def __enter__(self):
        if hasattr(self, 'devices'):
            self.s = Spine(devices=self.devices, sim=self.sim)
        else:
            self.s = Spine(sim=self.sim)
        self.s.startup()
        return self.s

    def __exit__(self, type, value, traceback):
        self.s.stop()
        self.s.close()


class Spine:
    '''Provides a simple interface to the robot's peripherals.
    This class should probably not be instantiated directly. Please see
    :func:`get_spine`, which provides safe error and interrupt handling, which
    this class does not directly provide.
    There is no need to create more than one Spine object. In fact, it is not
    possible due to serial port locking.
    Note that typically commands will assert a successful response from one of
    the micros even if there is no return value.
    :param t_out:
        The serial timeout. Probably should not change
    :type t_out: ``int``
    :param delim:
        The line delimeter for serial communications. Probably should not
        change.
    :type delim: ``string``
    :Keyword Arguments:
        * **use_lock** (``bool``) --
          Whether to respect and create the lock files in ``/var/lock``. Should
          probably always be true, the default.
        * **lock_dir** (``str``) --
          Location of the lock files. Defaults to ``/var/lock/``.
        * **ports** (``dict``) --
          A dictionary of the ports and serial devices they are connected to.
          See DEF_PORTS in the module `head.spine.core` for the default and an
          example of a valid setting.
    '''

    def __init__(self, t_out=1, delim='\n', **kwargs):
        self.arduinos = {}
        self.messengers = {}
        self.use_lock = kwargs.get('use_lock', True)
        self.lock_dir = kwargs.get('lock_dir', '/var/lock/')

        self.devices = devices = kwargs.get('devices', self.grab_connected_devices())

        self.sim = kwargs.get('sim', False)

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
                                                     timeout=t_out)
                if self.use_lock:
                    with open(lockfn, 'w') as f:
                        f.write('RIP Core')
                    os.chmod(lockfn, 0o777)
                    logger.info('Created lock at {0:s}.'.format(lockfn))
            config_file = open("{0:s}/{1:s}/{1:s}_core.json".format(CURRENT_ARDUINO_CODE_DIR, device))
            config[device] = json.loads(config_file.read())
            self.configure_arduino(config)
        self.delim = delim
        self.sendMutex = Lock()

    def grab_connected_devices(self):
        deviceOptions = [d for d in os.listdir(CURRENT_ARDUINO_CODE_DIR)
                         if os.path.isdir("{0:s}/{1:s}".format(CURRENT_ARDUINO_CODE_DIR, d)) and
                         not d == ".git" and os.path.exists("{0:s}/{1:s}/{1:s}.json"
                                                            .format(CURRENT_ARDUINO_CODE_DIR, d))]

        connectedDeviceOptions = [d for d in deviceOptions if os.path.exists("/dev/{0:s}".format(d))]
        return connectedDeviceOptions

    def startup(self):
        '''
        Ping Arduino boards and turn on their LEDs.
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

    def stop(self):
        if self.sim:
            return

        for appendage in self.appendages.values():
            if hasattr(appendage, 'stop'):
                appendage.stop()

    def close(self):
        '''Close all serial connections and remove locks.

        Failing to call this when you are done with the Spine object will force
        others to manually remove the locks that you created.

        :note:
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

    def send(self, devname, has_response, command, *args):
        '''Send a command to a device and return the result.
        This is an internal method and should not be used directly. This is
        only for testing new commands that do not yet have specific Spine
        methods written for them. This method is used internally by the other
        Spine methods.
        :param devname:
            The device name to send the command to.
        :type devname: ``string``
        :param command:
            The command to send. Do not include the newline at the end.
            Information on these serial commands can be gathered through looking
            at the Spine source or the source of the various microcontrollers
            directly.
        :type command: ``string``
        :return: The string response of the command, without the newline.
        '''
        self.sendMutex.acquire()
        logger.debug("Sending {0:s} to '{1:s}'".format(command, devname))
        with DelayedKeyboardInterrupt():
            self.messengers[devname].send(command, *args)
            acknowledgement = self.messengers[devname].receive()
            if has_response:
                response = self.messengers[devname].receive()
        try:
            assert (acknowledgement[0] == "kAcknowledge" and
                    self.command_map[devname][acknowledgement[1][0]] == command)
        except AssertionError:
            logger.warning("Acknowledgement error to {0:s}.".format(devname))
            logger.warning("Actual response was {}.".format(repr(acknowledgement)))
            logger.warning("Acknowledged Command was {0:s}.".format(self.command_map[devname][acknowledgement[1][0]]))
            logger.warning("Command was {0:s}.".format(command))
            raise
        if has_response:
            try:
                assert (response[0][:-6] == command and
                        response[0][-6:] == "Result")
            except AssertionError:
                logger.warning("Response error to {0:s}.".format(devname))
                logger.warning("Actual response command was {}".format(repr(response)))
                logger.warning("Command was {0:s}.".format(command))
        self.sendMutex.release()
        if has_response:
            return response[1]

    def ping(self):
        '''Send a ping command to all devices and assert success.
        This is called automatically by :func:`startup()`.
        '''
        if self.sim:
            return

        for devname in self.messengers.keys():
            response = self.send(devname, True, "kPing")
            assert self.command_map[devname][response[0]] == "kPong"

    def set_led(self, devname, status):
        '''Turns the debug LED on or off for certain devices.
        This is typically only used for debug purposes. LEDs are flashed three
        times on all devices during the :func:`startup()` call.
        :param devname:
            The device to direct the LED setting to.
        :type devname: ``string``
        :param status:
            True for on, False for off.
        :type status: ``bool``
        '''
        if self.sim:
            return

        self.send(devname, False, "kSetLed", status)

    def configure_arduino(self, config):
        '''Sets up the appendages dictionary with all the objects that are
        connected to each Arduino. Also sets up the `CmdMessengers` as well
        as the command map
        :param config
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
                # Magic voodoo that imports a class from the appendages folder with the specific
                # type and instantiates it
                # http://stackoverflow.com/questions/4821104/python-dynamic-instantiation-from-string-name-of-a-class-in-dynamically-imported
                module = importlib.import_module("{0:s}appendages.{1:s}"
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

    def get_appendage(self, label):
        return self.appendages[label]

    def print_appendages(self):
        print(self.appendages)
