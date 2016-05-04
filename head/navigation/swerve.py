class Swerve:
    def __init__(self, **kwargs):
        self.leftWheels = []
        self.lfdm = kwargs.get('leftFrontDriveMotor', None)
        self.rfdm = kwargs.get('rightFrontDriveMotor', None)
        self.lbdm = kwargs.get('leftBackDriveMotor', None)
        self.rbdm = kwargs.get('rightBackDriveMotor', None)
        self.lfde = kwargs.get('leftFrontDriveEncoder', None)
        self.rfde = kwargs.get('rightFrontDriveEncoder', None)
        self.lbde = kwargs.get('leftBackDriveEncoder', None)
        self.rbde = kwargs.get('rightBackDriveEncoder', None)

        self.lftm = kwargs.get('leftFrontTurnMotor', None)
        self.rftm = kwargs.get('rightFrontTurnMotor', None)
        self.lbtm = kwargs.get('leftBackTurnMotor', None)
        self.rbtm = kwargs.get('rightBackTurnMotor', None)
        self.lfte = kwargs.get('leftFrontTurnEncoder', None)
        self.rfte = kwargs.get('rightFrontTurnEncoder', None)
        self.lbte = kwargs.get('leftBackTurnEncoder', None)
        self.rbte = kwargs.get('rightBackTurnEncoder', None)

        self.gyro = kwargs.get('gyro', None)

    def driveVoltage(self, linear, rot=0):
        return

    def driveVelocity(self, linear, rot=0):
        return

    def driveDistance(self, linear, rot=0):
        return
