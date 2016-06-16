import math


class Mecanum:

    def __init__(self, **kwargs):
        self.fourWheelDrive = kwargs.get('mecanumDrive', None)
        self.gyro = kwargs.get('gyro', None)
        self.maxVelocity = kwargs.get('maxVelocity', None)

    def driveVoltage_Cartesian(self, x, y, rotation, fieldCentric):
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
            xIn, yIn = Mecanum.rotateVector(xIn, yIn, self.gyro.getYaw())

        frontLeft = xIn + yIn + rotation
        frontRight = -xIn + yIn - rotation
        backLeft = -xIn + yIn + rotation
        backRight = xIn + yIn - rotation

        frontLeft, frontRight, backLeft, backRight = Mecanum.normalize(
            frontLeft, frontRight, backLeft, backRight)
        self.fourWheelDrive.drive(frontLeft, frontRight, backLeft, backRight)

    def driveVoltage_Polar(self, magnitude, direction, rotation):
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

        frontLeft = sinD * magnitude + rotation
        frontRight = cosD * magnitude - rotation
        backLeft = cosD * magnitude + rotation
        backRight = sinD * magnitude - rotation

        frontLeft, frontRight, backLeft, backRight = Mecanum.normalize(
            frontLeft, frontRight, backLeft, backRight)
        self.fourWheelDrive.drive(frontLeft, frontRight, backLeft, backRight)

    def driveVelocity_Cartesian(self, x, y, rotation, fieldCentric):
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
            xIn, yIn = Mecanum.rotateVector(xIn, yIn, self.gyro.getYaw())

        frontLeft = xIn + yIn + rotation
        frontRight = -xIn + yIn - rotation
        backLeft = -xIn + yIn + rotation
        backRight = xIn + yIn - rotation

        if self.maxVelocity is not None:
            frontLeft, frontRight, backLeft, backRight = Mecanum.normalizeVelocity(
                frontLeft, frontRight, backLeft, backRight, self.maxVelocity)
        self.fourWheelDrive.driveVelocity(frontLeft, frontRight, backLeft, backRight)

    def driveVelocity_Polar(self, magnitude, direction, rotation):
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

        frontLeft = sinD * magnitude + rotation
        frontRight = cosD * magnitude - rotation
        backLeft = cosD * magnitude + rotation
        backRight = sinD * magnitude - rotation

        if self.maxVelocity is not None:
            frontLeft, frontRight, backLeft, backRight = Mecanum.normalizeVelocity(
                frontLeft, frontRight, backLeft, backRight, self.maxVelocity)
        self.fourWheelDrive.driveVelocity(frontLeft, frontRight, backLeft, backRight)

    @staticmethod
    def normalize(frontLeft, frontRight, backLeft, backRight):
        """Normalize all wheel speeds if the magnitude of any wheel is greater
        than 1023.
        """
        wheelSpeeds = [frontLeft, frontRight, backLeft, backRight]
        maxMagnitude = max(abs(x) for x in wheelSpeeds)
        if maxMagnitude > 1023:
            for i in range(len(wheelSpeeds)):
                wheelSpeeds[i] = wheelSpeeds[i] / maxMagnitude
        return wheelSpeeds[0], wheelSpeeds[1], wheelSpeeds[2], wheelSpeeds[3]

    @staticmethod
    def normalizeVelocity(frontLeft, frontRight, backLeft, backRight, maxVelocity):
        """Normalize all wheel speeds if the magnitude of any wheel is greater
        than 1023.
        """
        wheelSpeeds = [frontLeft, frontRight, backLeft, backRight]
        maxMagnitude = max(abs(x) for x in wheelSpeeds)
        if maxMagnitude > maxVelocity:
            for i in range(len(wheelSpeeds)):
                wheelSpeeds[i] = wheelSpeeds[i] / maxMagnitude
        return wheelSpeeds[0], wheelSpeeds[1], wheelSpeeds[2], wheelSpeeds[3]

    @staticmethod
    def rotateVector(x, y, angle):
        """Rotate a vector in Cartesian space."""
        angle = math.radians(angle)
        cosA = math.cos(angle)
        sinA = math.sin(angle)
        return (x * cosA - y * sinA), (x * sinA + y * cosA)
