

from math import pi, exp
import time
import operator
import logging

from ArmKinematics import ArmKinematics
from Vec3d import Vec3d
from ..spine.ourlogging import setup_logging

setup_logging(__file__)
logger = logging.getLogger(__name__)


class get_arm_controller:

    def __init__(self, arm, **kwargs):
        self.arm = arm
        self.kwargs = kwargs

    def __enter__(self):
        self.arm_controller = ArmController(self.arm, **self.kwargs)
        return self.arm_controller

    def __exit__(self, type, value, traceback):
        self.arm.park()


class ArmController(object):

    WRIST_TO_CUP = 10  # Distance in centimeters from wrist center to cup tip

    # Servo configuration
    BASE_CENTER = 85  # more positive moves to the right
    BASE_RIGHT = BASE_CENTER + 85
    BASE_LEFT = BASE_CENTER - 85

    SHOULDER_CENTER = 95  # more positive moves backward
    SHOULDER_DOWN = SHOULDER_CENTER - 79

    ELBOW_CENTER = 126  # more positive moves down
    ELBOW_UP = ELBOW_CENTER - 90

    WRIST_CENTER = 112  # more positive flexes up
    WRIST_DOWN = WRIST_CENTER - 82

    # Probably no calibration needed
    WRIST_ROTATE_CENTER = 90
    SUCTION_CENTER = 90

    DOWN = 0
    CENTER = 1
    UP = 2
    LEFT = 0
    RIGHT = 2

    # Starts at base
    PARKED = [180, 170, 180, 60, 180]

    # CENTER is defined as 0 radians
    def __init__(self, arm, **kwargs):
        self.parked = kwargs.get('parked', self.PARKED)
        self.base = kwargs.get('base', [self.BASE_LEFT, self.BASE_CENTER, self.BASE_RIGHT])
        self.shoulder = kwargs.get('shoulder', [self.SHOULDER_DOWN, self.SHOULDER_CENTER, -1])
        self.elbow = kwargs.get('elbow', [-1, self.ELBOW_CENTER, self.ELBOW_UP])
        self.wrist = kwargs.get('wrist', [self.WRIST_DOWN, self.WRIST_CENTER, -1])
        self.wrist_rotate = kwargs.get('wrist_rotate', self.WRIST_ROTATE_CENTER)
        self.wrist_to_cup = kwargs.get('wrist_to_cup', self.WRIST_TO_CUP)

        self.servos = self.parked
        self.arm = arm

    def shoulder_r2p(self, r):
        return self.shoulder[self.CENTER] + (r / (pi / 2)) * (self.shoulder[self.DOWN] - self.shoulder[self.CENTER])

    def elbow_r2p(self, r):
        return self.elbow[self.CENTER] - (r / (pi / 2)) * (self.shoulder[self.DOWN] - self.shoulder[self.CENTER])

    def wrist_r2p(self, r):
        return self.wrist[self.CENTER] - (r / (pi / 2)) * (self.elbow[self.UP] - self.elbow[self.CENTER])

    # Wrist is the amount of up rotation, from straight down, in radians
    # cuppos assumes that wrist is set to 0 radians
    # This is a raw function - use move_to instead
    def set_pos(self, cuppos, wrist, wristrotate):
        self.servos = self._to_servos(cuppos, wrist, wristrotate)
        self.arm.set(self.servos)

    def set_servos(self, *args):
        self.servos = args
        self.arm.set(list(args))

    def move_to(self, cuppos, wrist, wristrotate, seconds=1, smoothing='sigmoid'):
        '''Wrist measurement is in radians!!!'''
        assert wrist < pi
        startargs = self.servos
        endargs = self._to_servos(cuppos, wrist, wristrotate)
        self._interpolate(lambda *args: self.set_servos(*args),
                          startargs, endargs, seconds, smoothing)

    def move_to_abs(self, servopos, seconds=1, smoothing='sigmoid'):
        startargs = self.servos
        endargs = servopos
        self._interpolate(lambda *args: self.set_servos(*args),
                          startargs, endargs, seconds, smoothing)

    def park(self, seconds=2):
        self.move_to_abs(self.parked, seconds)
        self.arm.detach()

    def interpolate(self, f, startargs, endargs, seconds, smoothing):
        def linear(x):
            return x

        def rawsigmoid(a, x):
            return 1 / (1 + exp(-(x - .5) / a))

        def sigmoid(a, x):
            return (rawsigmoid(a, x) - rawsigmoid(a, 0)) / (rawsigmoid(a, 1) - rawsigmoid(a, 0))
        start_time = time.time()
        difference = list(map(operator.sub, endargs, startargs))
        curr_time = time.time()
        iters = 0
        while (curr_time - start_time) < seconds:
            elapsed = curr_time - start_time
            fraction = elapsed / seconds
            if smoothing == 'linear':
                def sfunc(x):
                    return linear(x)
            elif smoothing == 'sigmoid':
                def sfunc(x):
                    return sigmoid(0.13, x)
            toadd = [v * sfunc(fraction) for v in difference]
            currargs = list(map(operator.add, startargs, toadd))
            f(*currargs)
            curr_time = time.time()
            iters += 1
        logger.info("Arm interpolation iterations: %d", iters)
        f(*endargs)

    def to_servos(self, cuppos, wrist, wristrotate):
        wristpos = cuppos + Vec3d(0, 0, self.wrist_to_cup)
        ak = ArmKinematics()
        rot = ak.revkin(wristpos)
        wrist += -pi / 2
        # If positive wrist flexes up, positive shoulder and elbow rotations will
        # add directly to wrist
        wrist += rot[1] + rot[2]
        servo = [self.base_r2p(rot[0]), self.shoulder_r2p(rot[1]), self.elbow_r2p(rot[2]),
                 self.wrist_r2p(wrist), wristrotate]
        servo = [max(int(round(p)), 0) for p in servo]
        # print servo
        return servo
