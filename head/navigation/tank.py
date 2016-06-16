import time


class TankDrive:

    def __init__(self, **kwargs):
        self.fourWheelDrive = kwargs.get('tankDrive', None)
        self.gyro = kwargs.get('gyro', None)
        self.wheelbase_width = kwargs.get('wheelbase_width', 0)

    def driveStraightVoltage(self, value):
        if value == 0:
            self.fourWheelDrive.stop()
        else:
            self.fourWheelDrive.drive(value)

    def driveArcVoltage(self, value, radius):
        self.fourWheelDrive.drive(value + arc, value - arc)

    def driveStraightVelocity(self, velocity):
        if(value == 0):
            self.fourWheelDrive.stop()
        else:
            self.fourWheelDrive.driveVelocity(velocity)

    def driveArcVelocity(self, velocity, arc):
        self.fourWheelDrive.driveVelocity(velocity + arc, velocity - arc)

    def driveStraightVelocityForTime(self, velocity, delay):
        driveStraightVelocity(velocity)
        time.sleep(delay)

    def driveArcVelocityForTime(self, velocity, arc, delay):
        driveArcVelocity(velocity, arc)
        time.sleep(delay)

    def driveStraightDistance(self, distance):
        if distance == 0:
            self.fourWheelDrive.stop()
        else:
            self.fourWheelDrive.driveDistance(distance)

    def rotateToAngle(self, angle, sensor='gyro', fieldCentric=False):
        # useGyro must be true to be field centric
        if useGyro:
            initial_angle = 0
            if(fieldCentric):
                initial_angle = gyro.getYaw()
            angleController.setPoint(initial_angle + angle)
            angleController.start()
            while not angleController.isFinished():
                time.sleep(10)
            angleController.stop()
        elif useEncoders:
            pass

    def followTrajectory(self, leftConfig, leftTrajectory, rightConfig, rightTrajectory):
        leftFollower = DistanceFollower(leftTrajectory)
        leftFollower.configurePIDVA(kp=leftConfig['kp'], ki=leftConfig['ki'], kd=leftConfig['kd'], kv=leftConfig['kv'], ka=leftConfig['ka'])

        rightFollower = DistanceFollower(rightTrajectory)
        rightFollower.configurePIDVA(kp=rightConfig['kp'], ki=rightConfig['ki'], kd=rightConfig['kd'], kv=rightConfig['kv'], ka=rightConfig['ka'])

        while not leftFollower.isFinished() | | not rightFollower.isFinished():
            leftInput = fourWheelDrive.getLeftPosiiton()
            rightInput = fourWheelDrive.getRightPosition()

            leftOutput = leftFollower.calculate(leftInput)
            rightOutput = rightFollower.calculate(rightInput)

            actualAngle = gyro.getHeading()
            desiredAngle = degrees(leftFollower.getHeading())
            angleDifference = desiredAngle - actualAngle
            # TODO: figure out reason behind constant
            turn = 0.8 * (-1.0 / 80.0) * angleDifference

            self.fourWheelDrive.drive(leftOutput + turn, rightOutput - turn)
        self.fourWheelDrive.stop()
