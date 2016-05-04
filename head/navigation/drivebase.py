from enum import Enum
from swerve import Swerve
from mecanum import Mecanum
from tank import Tank


class DriveBaseTypes(Enum):
    TANK = 'tank'
    MECANUM = 'mecanum'
    SWERVE = 'swerve'


class DriveBase:
    def __init__(self, **kwargs):
        self.drivebase_type = kwargs.get('drivebase_type', 'tank')
        if self.drivebase_type == DriveBaseTypes.TANK:
            self.drivebase = Tank(**kwargs)
        elif self.drivebase_type == DriveBaseTypes.MECANUM:
            self.drivebase = Mecanum(**kwargs)
        elif self.drivebase_type == DriveBaseTypes.SWERVE:
            self.drivebase = Swerve(**kwargs)

        #  Inches
        self.wheelsize = kwargs.get('wheelsize', 4.0)
        self.wheelbase_width = kwargs.get('wheelbase_width', 8.0)
        self.wheelbase_length = kwargs.get('wheelbase_length', 8.0)

    def driveVoltage(self, x, y=0, rot=0):
        '''
            +x is the forward direction (based on trajectory planner)
            +y is to the right
            +rot is rotating towards the right
        '''

        return

    def driveVelocity(self, x, y=0, rot=0, units='inch'):
        '''
            +x is the forward direction (based on trajectory planner)
            +y is to the right
            +rot is rotating towards the right
        '''
        return

    def driveDistance(self, x, y=0, units='inch'):
        '''
            +x is the forward direction (based on trajectory planner)
            +y is to the right
            +rot is rotating towards the right
        '''
        return

    def rotateToAngle(self, angle):
        # + is rotating towards the right

        return

    def followTrajectory(self, trajectoryFilename):
        return
