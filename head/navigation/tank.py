class Tank:
    def __init__(self, **kwargs):
        self.numDriveMotors = kwargs.get('numDriveMotors', 4)
        self.leftDriveMotors = []
        self.rightDriveMotors = []
        self.leftDriveEncoders = []
        self.rightDriveEncoders = []
        for i in range(self.numDriveMotors / 2):
            self.leftDriveMotors.append(kwargs.get('leftDriveMotor' + (i + 1), None))
            self.rightDriveMotors.append(kwargs.get('rightDriveMotor' + (i + 1), None))
            self.leftDriveEncoders.append(kwargs.get('leftDriveEncoder' + (i + 1), None))
            self.rightDriveEncoders.append(kwargs.get('rightDriveEncoder' + (i + 1), None))
        self.leftDriveMotors = filter(None, self.leftDriveMotors)
        self.rightDriveMotors = filter(None, self.rightDriveMotors)
        self.leftDriveEncoders = filter(None, self.leftDriveEncoders)
        self.rightDriveEncoders = filter(None, self.rightDriveEncoders)

        self.gyro = kwargs.get('gyro', None)

    def driveVoltage(self, linear, rot=0):
        if linear == 0 and rot == 0:
            for i in range(len(self.leftDriveMotors)):
                self.leftDriveMotors[i].stop()
                self.rightDriveMotors[i].stop()
        else:
            return

    def driveVelocity(self, linear, rot=0, units='inch'):
        if linear == 0 and rot == 0:
            for i in range(len(self.leftDriveMotors)):
                self.leftDriveMotors[i].stop()
                self.rightDriveMotors[i].stop()
        else:
            return

    def driveDistance(self, linear, rot=0, units='inch'):
        if linear == 0 and rot == 0:
            for i in range(len(self.leftDriveMotors)):
                self.leftDriveMotors[i].stop()
                self.rightDriveMotors[i].stop()
        else:
            return

    def followTrajectory(self, trajectoryFilename):
        return
