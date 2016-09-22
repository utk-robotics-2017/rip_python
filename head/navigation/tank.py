import time
import logging
import math
from ..spine.ourlogging import setup_logging
from Pathfinder_Python.DistanceFollower import DistanceFollower

setup_logging(__file__)
log = logging.getLogger(__name__)


class TankDrive:

    def __init__(self, drivebase, wheelbase_width, gyro=None):
        self.drivebase = drivebase
        self.gyro = gyro
        self.wheelbase_width = wheelbase_width

    def driveStraightVoltage(self, value):
        if value == 0:
            self.drivebase.stop()
        else:
            self.drivebase.drive(value)

    def driveArcVoltage(self, value, radius):
        self.drivebase.drive(value + radius, value - radius)

    def driveStraightVelocity(self, velocity):
        if(velocity == 0):
            self.drivebase.stop()
        else:
            self.drivebase.driveVelocity(velocity)

    def driveArcVelocity(self, velocity, arc):
        self.drivebase.driveVelocity(velocity + arc, velocity - arc)

    def driveStraightVelocityForTime(self, velocity, delay, stop=False):
        self.driveStraightVelocity(velocity)
        time.sleep(delay)
        if stop:
            self.drivebase.stop()

    def driveArcVelocityForTime(self, velocity, arc, delay, stop=False):
        self.driveArcVelocity(velocity, arc)
        time.sleep(delay)
        if stop:
            self.drivebase.stop()

    def driveStraightDistance(self, distance):
        if distance == 0:
            self.drivebase.stop()
        else:
            self.drivebase.driveDistance(distance)

    def rotateToAngle(self, angle, sensor='gyro'):
        if sensor == 'gyro':
            pass
        elif sensor == 'encoder':
            pass
        else:
            log.error("Unknown sensor to use for rotating: {0:s}".format(sensor))
            raise Exception("Unknown sensor to use for rotating {0:s}".format(sensor))

    def followTrajectory(self, leftConfig, leftTrajectory, rightConfig, rightTrajectory):
        leftFollower = DistanceFollower(leftTrajectory)
        leftFollower.configurePIDVA(kp=leftConfig['kp'], ki=leftConfig['ki'],
                                    kd=leftConfig['kd'], kv=leftConfig['kv'],
                                    ka=leftConfig['ka'])

        rightFollower = DistanceFollower(rightTrajectory)
        rightFollower.configurePIDVA(kp=rightConfig['kp'], ki=rightConfig['ki'],
                                     kd=rightConfig['kd'], kv=rightConfig['kv'],
                                     ka=rightConfig['ka'])

        while not leftFollower.isFinished() or not rightFollower.isFinished():
            leftInput = self.drivebase.getLeftPosiiton()
            rightInput = self.drivebase.getRightPosition()

            leftOutput = leftFollower.calculate(leftInput)
            rightOutput = rightFollower.calculate(rightInput)

            actualAngle = self.gyro.getHeading()
            desiredAngle = math.degrees(leftFollower.getHeading())
            angleDifference = desiredAngle - actualAngle
            # TODO: figure out reason behind constant
            turn = 0.8 * (-1.0 / 80.0) * angleDifference

            self.drivebase.drive(leftOutput + turn, rightOutput - turn)
        self.drivebase.stop()
