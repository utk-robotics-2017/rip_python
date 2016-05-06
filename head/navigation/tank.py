from enum import Enum
import time


class DriveType(Enum):
    Voltage = 0
    Velocity = 1
    Distance = 2


class TankDrive:
    def __init__(self, **kwargs):
        self.leftDriveMotors = kwargs.get('leftDriveMotors', [])
        self.rightDriveMotors = kwargs.get('rightDriveMotors', [])

        self.leftDistanceController = kwargs.get('leftDistanceController', None)
        self.rightDistanceController = kwargs.get('rightDistanceController', None)
        self.angleController = kwargs.get('angleController', None)

        self.leftVelocityControllers = kwargs.get('leftVelocityControllers', [])
        self.rightVelocityControllers = kwargs.get('rightVelocityControllers', [])

        self.wheelbase_width = kwargs.get('wheelbase_width', 8.0)
        self.wheelsize = kwargs.get('wheelsize', 4.0)
        self.distanceTolerance = kwargs.get('distanceTolerance', 1.0)
        self.angleTolerance = kwargs.get('angleTolerance', 1.0)

        self.gyro = kwargs.get('gyro', None)

    def driveStraight(self, value, driveType):
        if(driveType == DriveType.Voltage):
            self.driveStraightVoltage(value)
        elif(driveType == DriveType.Velocity):
            self.driveStraightVelocity(value)
        elif(driveType == DriveType.Distance):
            self.driveStraightDistance(value)

    def driveStraightVoltage(self, value):
        if leftValue == 0 and rightValue == 0:
            for i in range(len(self.leftDriveMotors)):
                self.leftDriveMotors[i].stop()
                self.rightDriveMotors[i].stop()
        else:
            for i in range(len(self.leftDriveMotors)):
                self.leftDriveMotors[i].drive(value)
                self.rightDriveMotors[i].drive(value)

    def driveStraightVelocity(self, velocity):
        if velocity == 0:
            for i in range(len(self.leftVelocityControllers)):
                self.leftVelocityControllers.stop()
                self.rightVelocityControllers.stop()

            for i in range(len(self.leftDriveMotors)):
                self.leftDriveMotors[i].stop()
                self.rightDriveMotors[i].stop()
        else:
            for i in range(len(self.leftVelocityControllers)):
                self.leftVelocityControllers.setPoint(velocity)
                self.leftVelocityControllers.start()
                self.rightVelocityControllers.setPoint(velocity)
                self.rightVelocityControllers.start()

    def driveStraightVelocityForTime(self, velocity, delay):
        if velocity == 0:
            for i in range(len(self.leftVelocityControllers)):
                self.leftVelocityControllers.stop()
                self.rightVelocityControllers.stop()

            for i in range(len(self.leftDriveMotors)):
                self.leftDriveMotors[i].stop()
                self.rightDriveMotors[i].stop()
            times.sleep(delay)
        else:
            for i in range(len(self.leftVelocityControllers)):
                self.leftVelocityControllers.setPoint(velocity)
                self.leftVelocityControllers.start()
                self.rightVelocityControllers.setPoint(velocity)
                self.rightVelocityControllers.start()
            time.sleep(delay)
            for i in range(len(self.leftVelocityControllers)):
                self.leftVelocityControllers.stop()
                self.rightVelocityControllers.stop()


    def driveStraightDistance(self, distance):
        if distance == 0:
            self.leftDistanceController.stop()
            self.rightDistanceController.stop()
            for i in range(len(self.leftDriveMotors)):
                self.leftDriveMotors[i].stop()
                self.rightDriveMotors[i].stop()

        else:
            self.leftDistanceController.setPoint(distance)
            self.rightDistanceController.setPoint(distance)
            self.leftDistanceController.start()
            self.rightDistanceController.start()
            while not self.leftDistanceController.isFinished() and not self.rightDistanceController.isFinished():
                time.sleep(10)
            self.leftDistanceController.stop()
            self.rightDistanceController.stop()
            

    def rotateToAngle(self, angle, useGyro=True, fieldCentric=False,  useEncoders=False):
        initial_angle = 0

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

    def followTrajectory(self, trajectory):
        return

    def followTrajectoryFile(self, trajectoryFilename):
        return
