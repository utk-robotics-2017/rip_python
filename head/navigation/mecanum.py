import math


class MecanumDrive:

    def __init__(self, fwd, gyro=None):
        self.fwd = fwd
        self.gyro = gyro

    def drive_voltage_cartesian(self, x, y, rotation, fieldCentric):
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
            xIn, yIn = MecanumDrive.rotateVector(xIn, yIn, self.gyro.getYaw())

        fl = xIn + yIn + rotation
        fr = -xIn + yIn - rotation
        bl = -xIn + yIn + rotation
        br = xIn + yIn - rotation

        fl, fr, bl, br = MecanumDrive.normalize(
            fl, fr, bl, br)
        self.fwd.drive(fl, fr, bl, br)

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

        fl = sinD * magnitude + rotation
        fr = cosD * magnitude - rotation
        bl = cosD * magnitude + rotation
        br = sinD * magnitude - rotation

        fl, fr, bl, br = MecanumDrive.normalize(
            fl, fr, bl, br)
        self.fwd.drive(fl, fr, bl, br)

    def drive_velocity_cartesian(self, x, y, rotation, fieldCentric):
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
            xIn, yIn = MecanumDrive.rotateVector(xIn, yIn, self.gyro.getYaw())

        fl = xIn + yIn + rotation
        fr = -xIn + yIn - rotation
        bl = -xIn + yIn + rotation
        br = xIn + yIn - rotation

        if self.maxVelocity is not None:
            fl, fr, bl, br = MecanumDrive.normalizeVelocity(
                fl, fr, bl, br, self.maxVelocity)
        self.fwd.drive_velocity(fl, fr, bl, br)

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
        dirInRad = math.radians(direction + 45.0)
        cosD = math.cos(dirInRad)
        sinD = math.sin(dirInRad)

        fl = sinD * magnitude + rotation
        fr = cosD * magnitude - rotation
        bl = cosD * magnitude + rotation
        br = sinD * magnitude - rotation

        if self.maxVelocity is not None:
            fl, fr, bl, br = MecanumDrive.normalizeVelocity(
                fl, fr, bl, br, self.maxVelocity)
        self.fwd.drive_velocity(fl, fr, bl, br)

    @staticmethod
    def normalize(fl, fr, bl, br):
        """Normalize all wheel speeds if the magnitude of any wheel is greater
        than 1023.
        """
        wheel_speeds = [fl, fr, bl, br]
        maxMagnitude = max(abs(x) for x in wheel_speeds)
        if maxMagnitude > 1023:
            for i in range(len(wheel_speeds)):
                wheel_speeds[i] = wheel_speeds[i] / maxMagnitude
        return wheel_speeds[0], wheel_speeds[1], wheel_speeds[2], wheel_speeds[3]

    @staticmethod
    def normalize_velocity(fl, fr, bl, br, max_velocity):
        """Normalize all wheel speeds if the magnitude of any wheel is greater
        than `the max_velocity`.
        """
        wheel_speeds = [fl, fr, bl, br]
        max_magnitude = max(abs(x) for x in wheel_speeds)
        if max_magnitude > max_velocity:
            for i in range(len(wheel_speeds)):
                wheel_speeds[i] = wheel_speeds[i] / max_magnitude
        return wheel_speeds[0], wheel_speeds[1], wheel_speeds[2], wheel_speeds[3]

    @staticmethod
    def rotateVector(x, y, angle):
        """Rotate a vector in Cartesian space."""
        angle = math.radians(angle)
        cosA = math.cos(angle)
        sinA = math.sin(angle)
        return (x * cosA - y * sinA), (x * sinA + y * cosA)
