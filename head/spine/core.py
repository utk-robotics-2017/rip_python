# Global
import time
import os
import signal
import logging
from multiprocessing import Lock
# import json
from subprocess import Popen, PIPE

# Third-party
import serial

from ourlogging import setup_logging
from appendages.encoder import encoder
from appendages.i2cencoder import i2cencoder
from appendages.linesensor import linesensor
from appendages.linesensor_array import linesensor_array
from appendages.switch import switch
from appendages.ultrasonic import ultrasonic
from appendages.servo import servo
from appendages.motor import motor
from appendages.arm import arm


setup_logging(__file__)
logger = logging.getLogger(__name__)

DEF_PORTS = {
    'mega': '/dev/mega',
}


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

    def __enter__(self, ports=dict(), config=dict()):
        self.s = Spine(ports, config)
        self.s.startup()
        return self.s

    def __exit__(self, type, value, traceback):
        for i in range(2):
            for devname, port in self.s.ports.iteritems():
                self.s.ser[devname].flushOutput()
                self.s.ser[devname].flushInput()
            time.sleep(0.1)

        self.s.stop()
        for i in range(2):
            self.s.stop_loader_motor(i)
        self.s.stop_width_motor()
        self.s.stop_lift_motor()
        self.s.detach_loader_servos()
        self.s.set_release_suction(False)
        self.s.set_suction(False)
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
        self.ports = kwargs.get('ports', DEF_PORTS)
        config = kwargs.get('config', dict())
        first = True
        for devname, port in self.ports.iteritems():
            if self.use_lock:
                fndevname = port.split('/dev/')[1]
                lockfn = '%sLCK..%s' % (self.lock_dir, fndevname)
                if os.path.isfile(lockfn):
                    self.close()
                    raise SerialLockException(
                        "Lockfile %s exists. It's possible that someone is using this serial port. If not, remove this lock file. Closing and raising error." % lockfn)
            logger.info('Connecting to %s.' % port)
            self.ser[devname] = serial.Serial(port, 115200, timeout=t_out)
            if self.use_lock:
                with open(lockfn, 'w') as f:
                    f.write('-1')
                logger.info('Created lock at %s.' % lockfn)
            if first:
                first = False
            else:
                logger.info('Waiting for connection to stabilize.')
                time.sleep(1)
        self.configure_arduino(config)
        self.delim = delim
        self.wsServer = Popen(['wsServer', '9000'], stdout=PIPE, stdin=PIPE)
        self.sendMutex = Lock()

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

    def configure_arduino(self, arduino_config):
        '''
        '''
        self.appendages = dict()
        encoders = 0
        i2cencoders = 0
        linesensors = 0
        linesensor_arrays = 0
        switches = 0
        ultrasonics = 0
        servos = 0
        motors = 0
        arms = 0
        steppers = 0
        for arduino in arduino_config:
            devname = arduino['devname']
            for appendage in arduino:
                if appendage['type'] == 'encoder':
                    self.appendages[appendage['label']] = encoder(self, devname, appendage['label'], encoders)
                    encoders ++
                elif appendage['type'] == 'i2cencoder':
                    self.appendages[appendage['label']] = i2cencoder(self, devname, appendage['label'], i2cencoders)
                    i2cencoders ++
                elif appendage['type'] == 'linesensor':
                    self.appendages[appendage['label']] = linesensor(self, devname, appendage['label'], linesensors, appendage['analog'])
                    linesensors ++
                elif appendage['type'] == 'linesensor_array':
                    self.appendages[appendage['label']] = linesensor_array(self, devname, appendage['label'], linesensor_arrays, appendage['analog'])
                    linesensor_arrays ++
                elif appendage['type'] == 'switch':
                    self.appendages[appendage['label']] = switch(self, devname, appendage['label'], encoders)
                    switches ++
                elif appendage['type'] == 'ultrasonic':
                    self.appendages[appendage['label']] = ultrasonic(self, devname, appendage['label'], ultrasonics)
                    ultrasonics ++
                elif appendage['type'] == 'servo':
                    self.appendages[appendage['label']] = servo(self, devname, appendage['label'], servos)
                    servos ++
                elif appendage['type'] == 'motor':
                    self.appendages[appendage['label']] = motor(self, devname, appendage['label'], motors)
                    motors ++
                elif appendage['type'] == 'arm':
                    self.appendages[appendage['label']] = arm(self, devname, appendage['label'], arms)
                    arms ++
                elif appendage['type'] == 'stepper':
                    self.appendages[appendage['label']] = stepper(self, devname, appendage['label'], steppers)
                else:
                    logging.e("Unknown appendage")

    def get_appendage(self, label):
        return self.appendages[label]
