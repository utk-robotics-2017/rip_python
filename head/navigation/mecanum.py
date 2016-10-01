import math
import logging
from ..spine.ourlogging import setup_logging
from ..units import Unit, Angular, Velocity, AngularVelocity

setup_logging(__file__)
logger = logging.getLogger(__name__)

class MecanumDrive:

    def __init__(self, fwd, max_velocity, gyro=None):
        self.fwd = fwd
        self.gyro = gyro
        self.max_velocity = max_velocity

    def drive_voltage_cartesian(self, x, y, rotation, fieldCentric=False):
        """Drive method for Mecanum wheeled robots.
        A method for driving with Mecanum wheeled robots. There are 4 wheels
        on the robot, arranged so that the front and back wheels are toed in
        45 degrees.  When looking at the wheels from the top, the roller
        axles should form an X across the robot.
        This is designed to be directly driven by joystick axes.
        :param x: The speed that the robot should drive in the X direction.
        :param y: The speed that the robot should drive in the Y direction.
        :param rotation: The rate of rotation for the robot that is
            completely independent of the translation.
        :param fieldCentric: whether to use the gyro (gyro must have been
        included when initialized) in calculating a field centric control
        """
        xIn = x
        yIn = y
        if fieldCentric and self.gyro is not None:
            # Compenstate for gyro angle.
            xIn, yIn = MecanumDrive.rotate_vector(xIn, yIn, self.gyro.getYaw())

        lf = xIn + yIn + rotation
        rf = -xIn + yIn - rotation
        lb = -xIn + yIn + rotation
        rb = xIn + yIn - rotation

        lf, rf, lb, rb = MecanumDrive.normalize(
            lf, rf, lb, rb)
        self.fwd.drive(lf, rf, lb, rb)

    def drive_voltage_polar(self, magnitude, direction, rotation):
        """Drive method for Mecanum wheeled robots.
        A method for driving with Mecanum wheeled robots. There are 4 wheels
        on the robot, arranged so that the front and back wheels are toed in
        45 degrees.  When looking at the wheels from the top, the roller
        axles should form an X across the robot.
        :param magnitude: The speed that the robot should drive in a given
            direction.
        :param direction: The direction the robot should drive in degrees.
            The direction and maginitute are independent of the rotation rate.
        :param rotation: The rate of rotation for the robot that is completely
            independent of the magnitude or direction.
        """
        magnitude = max(min(magnitude, 1023), -1023)

        # The rollers are at 45 degree angles.
        dirInRad = math.radians(direction + 45.0)
        cosD = math.cos(dirInRad)
        sinD = math.sin(dirInRad)

        lf = sinD * magnitude + rotation
        rf = cosD * magnitude - rotation
        lb = cosD * magnitude + rotation
        rb = sinD * magnitude - rotation

        lf, rf, lb, rb = MecanumDrive.normalize(
            lf, rf, lb, rb)
        self.fwd.drive(lf, rf, lb, rb)

    def drive_velocity_cartesian(self, x, y, rotation, fieldCentric=False):
        """Drive method for Mecanum wheeled robots.
        A method for driving with Mecanum wheeled robots. There are 4 wheels
        on the robot, arranged so that the front and back wheels are toed in
        45 degrees.  When looking at the wheels from the top, the roller
        axles should form an X across the robot.
        This is designed to be directly driven by joystick axes.
        :param x: The speed that the robot should drive in the X direction.
        :param y: The speed that the robot should drive in the Y direction.
        :param rotation: The rate of rotation for the robot that is
            completely independent of the translation.
        :param fieldCentric: whether to use the gyro (gyro must have been
        included when initialized) in calculating a field centric control
        """
        xIn = x
        yIn = y
        logger.info("xIn: {0:f} yIn: {1:f} rot {2:f}".format(xIn.to(Velocity.inch_s), yIn.to(Velocity.inch_s), rotation.to(AngularVelocity.rpm)))
        if fieldCentric and self.gyro is not None:
            # Compenstate for gyro angle.
            xIn, yIn = MecanumDrive.rotate_vector(xIn, yIn, self.gyro.getYaw())

        lf = xIn + yIn + rotation
        rf = -xIn + yIn - rotation
        lb = -xIn + yIn + rotation
        rb = xIn + yIn - rotation

        logger.info("lf {0:f} rf {1:f} lb {2:f} rb {3:f}".format(lf.to(Velocity.inch_s), rf.to(Velocity.inch_s), lb.to(Velocity.inch_s), rb.to(Velocity.inch_s)))

        if self.max_velocity is not None:
            lf, rf, lb, rb = MecanumDrive.normalize_velocity(
                lf, rf, lb, rb, self.max_velocity)
        logger.info("lf {0:f} rf {1:f} lb {2:f} rb {3:f}".format(lf.to(Velocity.inch_s), rf.to(Velocity.inch_s), lb.to(Velocity.inch_s), rb.to(Velocity.inch_s)))
        self.fwd.drive_pid(lf, rf, lb, rb)

    def drive_velocity_polar(self, magnitude, direction, rotation):
        """Drive method for Mecanum wheeled robots.
        A method for driving with Mecanum wheeled robots. There are 4 wheels
        on the robot, arranged so that the front and back wheels are toed in
        45 degrees.  When looking at the wheels from the top, the roller
        axles should form an X across the robot.
        :param magnitude: The speed that the robot should drive in a given
            direction.
        :param direction: The direction the robot should drive in degrees.
            The direction and maginitute are independent of the rotation rate.
        :param rotation: The rate of rotation for the robot that is completely
            independent of the magnitude or direction.
        """
        if self.maxVelocity is not None:
            magnitude = max(min(magnitude, self.maxVelocity), -self.maxVelocity)

        # The rollers are at 45 degree angles.
        dirInRad = math.radians(direction.to(Angular.degree) + 45.0)
        cosD = math.cos(dirInRad)
        sinD = math.sin(dirInRad)

        lf = Unit(sinD, 1) * magnitude + rotation
        rf = Unit(cosD, 1) * magnitude - rotation
        lb = Unit(cosD, 1) * magnitude + rotation
        rb = Unit(sinD, 1) * magnitude - rotation

        if self.maxVelocity is not None:
            lf, rf, lb, rb = MecanumDrive.normalize_velocity(
                lf, rf, lb, rb, self.maxVelocity)
        self.fwd.drive_pid(lf, rf, lb, rb)

    @staticmethod
    def normalize(lf, rf, lb, rb):
        """Normalize all wheel speeds if the magnitude of any wheel is greater
        than 1023.
        """
        wheel_speeds = [lf, rf, lb, rb]
        maxMagnitude = max(abs(x) for x in wheel_speeds)
        if maxMagnitude > 1023:
            for i in range(len(wheel_speeds)):
                wheel_speeds[i] = wheel_speeds[i] / maxMagnitude
        return wheel_speeds[0], wheel_speeds[1], wheel_speeds[2], wheel_speeds[3]

    @staticmethod
    def normalize_velocity(lf, rf, lb, rb, max_velocity):
        """Normalize all wheel speeds if the magnitude of any wheel is greater
        than `the max_velocity`.
        """
        wheel_speeds = [lf, rf, lb, rb]
        max_magnitude = max(abs(x) for x in wheel_speeds)
        if max_magnitude > max_velocity:
            for i in range(len(wheel_speeds)):
                wheel_speeds[i] = wheel_speeds[i] / max_magnitude
        return wheel_speeds[0], wheel_speeds[1], wheel_speeds[2], wheel_speeds[3]

    @staticmethod
    def rotate_vector(x, y, angle):
        """Rotate a vector in Cartesian space."""
        angle = math.radians(angle.to(Angular.degree))
        cosA = math.cos(angle)
        sinA = math.sin(angle)
        return (x * Unit(cosA, 1) - y * Unit(sinA, 1)), (x * Unit(sinA, 1) + y * Unit(cosA, 1))
