class Mecanum:
    def __init__(self, **kwargs):
        self.lfm = kwargs.get('leftFrontDriveMotor', None)
        self.rfm = kwargs.get('rightFrontDriveMotor', None)
        self.lbm = kwargs.get('leftBackDriveMotor', None)
        self.rbm = kwargs.get('rightBackDriveMotor', None)
        self.lfe = kwargs.get('leftFrontEncoder', None)
        self.rfe = kwargs.get('rightFrontEncoder', None)
        self.lbe = kwargs.get('leftBackEncoder', None)
        self.rbe = kwargs.get('rightBackEncoder', None)

        self.gyro = kwargs.get('gyro', None)

    def driveVoltage(self, linear, rot=0):
        return

    def driveVelocity(self, linear, rot=0):
        return

    def driveDistance(self, linear, rot=0):
        return
