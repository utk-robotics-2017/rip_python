# Global
import time
import os
import signal
import logging
import json
import sys
from multiprocessing import Lock
from subprocess import Popen, PIPE
import importlib

# Third-party
import serial

from ourlogging import setup_logging

setup_logging(__file__)
logger = logging.getLogger(__name__)

CURRENT_ARDUINO_CODE_DIR = "/currentArduinoCode"

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

    def __enter__(self, devices=""):
        if devices == "":
            self.s = Spine()
        else:
            self.s = Spine(devices=devices)
        #self.s.startup()
        return self.s

    def __exit__(self, type, value, traceback):
        for i in range(2):
            for device in self.s.devices:
                self.s.ser[device].flushOutput()
                self.s.ser[device].flushInput()
            time.sleep(0.1)
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
        self.ser = {}
        self.use_lock = kwargs.get('use_lock', True)
        self.lock_dir = kwargs.get('lock_dir', '/var/lock/')

        self.devices = devices = kwargs.get('devices', self.grab_connected_devices())

        first = True
        config = {}
        indices = {}
        for device in devices:
            if self.use_lock:
                lockfn = '%s%s.lck' % (self.lock_dir, device)
                if os.path.isfile(lockfn):
                    self.close()
                    print "Lockfile %s exists. It's possible that someone is using this serial port. If not, remove this lock file. Closing and raising error." % lockfn
                    sys.exit()

            logger.info('Connecting to /dev/%s.' % device)
            self.ser[device] = serial.Serial("/dev/%s" % device, 115200, timeout=t_out)
            if self.use_lock:
                with open(lockfn, 'w') as f:
                    f.write('-1')
                logger.info('Created lock at %s.' % lockfn)
            if first:
                first = False
            else:
                logger.info('Waiting for connection to stabilize.')
                time.sleep(1)
            config_file = open("%s/%s/%s.json" % (CURRENT_ARDUINO_CODE_DIR, device, device))
            config[device] = json.loads(config_file.read())

            indices_file = open("%s/%s/%s_indices.json" % (CURRENT_ARDUINO_CODE_DIR, device, device))
            indices[device] = json.loads(indices_file.read())
        self.configure_arduino(config, indices)
        self.delim = delim
        self.sendMutex = Lock()

    def grab_connected_devices(self):
        deviceOptions = [d for d in os.listdir(CURRENT_ARDUINO_CODE_DIR) if os.path.isdir("%s/%s" % (CURRENT_ARDUINO_CODE_DIR, d)) and not d == ".git" and os.path.exists("%s/%s/%s.json" % (CURRENT_ARDUINO_CODE_DIR, d, d))]

        connectedDeviceOptions = [d for d in deviceOptions if os.path.exists("/dev/%s" % d)]
        return connectedDeviceOptions
    
    def stop(self):
        ''' Stop all motors '''
        pass

    def close(self):
        '''Close all serial connections and remove locks.

        Failing to call this when you are done with the Spine object will force 
        others to manually remove the locks that you created.

        :note:
            If you are using a :func:`get_spine` environment, this method will
            get called automatically during cleanup.
        '''
        for devname in self.ser.keys():
            if self.use_lock:
                lockfn = '%s%s.lck' % (self.lock_dir, devname)
            self.ser[devname].close()
            logger.info('Closed serial connection %s.' % self.ser[devname].port)
            if self.use_lock:
                os.remove(lockfn)
                logger.info('Removed lock at %s.' % lockfn)


    def send(self, devname, command):
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
        logger.debug("Sending %s to '%s'" % (repr(command), devname))
        with DelayedKeyboardInterrupt():
            self.ser[devname].write(command + self.delim)
            echo = self.ser[devname].readline()
            response = self.ser[devname].readline()
        try:
            assert echo == '> ' + command + '\r\n'
        except AssertionError:
            logger.warning('Echo error to %s.' % repr(devname))
            logger.warning('Actual echo was %s.' % repr(echo))
            logger.warning('Command was %s.' % repr(command))
            raise
        logger.debug("Response: %s" % repr(response[:-2]))
        # Be sure to chop off newline. We don't need it.
        self.sendMutex.release()
        return response[:-2]

    def ping(self):
        '''Send a ping command to all devices and assert success.
        This is called automatically by :func:`startup()`.
        '''
        for devname in self.ser.keys():
            response = self.send(devname, 'ping')
            assert response == 'ok'

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
        command = 'le ' + ('on' if status else 'off')
        response = self.send(devname, command)
        assert response == 'ok'

    def configure_arduino(self, config, indices):
        '''
        '''
        self.appendages = dict()

        for devname, arduino in config.iteritems():
            for appendage in arduino:
                
                if appendage['type'].lower() == 'limit_switch' or appendage['type'].lower() == 'button':
                    appendage['type'] = 'switch'
        
                if appendage['type'].lower() == 'monstermotomotor':
                    appendage['type'] = 'motor'
                elif appendage['type'].lower() == 'roverfivemotor':
                    appendage['type'] = 'motor'

                # Magic voodoo that imports a class from the appendages folder with the specific type and instantiates it
                # http://stackoverflow.com/questions/4821104/python-dynamic-instantiation-from-string-name-of-a-class-in-dynamically-imported
                module = importlib.import_module("head.spine.appendages.%s" % (appendage['type']))
                class_ = getattr(module, appendage['type'])

                self.appendages[appendage['label']] = class_(self, devname, appendage['label'], indices[devname][appendage['label'])
    
    def get_appendage(self, label):
        return self.appendages[label]
    
    def print_appendages(self):
        print self.appendages
