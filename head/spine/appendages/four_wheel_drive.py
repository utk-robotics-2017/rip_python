import logging

from .component import Component
from ...units import Unit, Length, Angular, AngularVelocity
from ..ourlogging import setup_logging

setup_logging(__file__)
logger = logging.getLogger(__name__)


class FourWheelDrive(Component):
    DRIVE = "kDriveFWD"
    STOP = "kStopFWD"
    DRIVE_PID = "kDriveFWD_PID"
    LEFT_VELOCITY = "kGetFWDLeftVelocity"
    LEFT_VELOCITY_RESULT = "kGetFWDLeftVelocityResult"
    RIGHT_VELOCITY = "kGetFWDRightVelocity"
    RIGHT_VELOCITY_RESULT = "kGetFWDRightVelocityResult"
    RIGHT_FRONT_VELOCITY = "kGetFWDRightFrontVelocity"
    RIGHT_FRONT_VELOCITY_RESULT = "kGetFWDRightFrontVelocityResult"
    LEFT_FRONT_VELOCITY = "kGetFWDLeftFrontVelocity"
    LEFT_FRONT_VELOCITY_RESULT = "kGetFWDLeftFrontVelocityResult"
    RIGHT_BACK_VELOCITY = "kGetFWDRightBackVelocity"
    RIGHT_BACK_VELOCITY_RESULT = "kGetFWRightBackVelocityResult"
    LEFT_BACK_VELOCITY = "kGetFWDLeftBackVelocity"
    LEFT_BACK_VELOCITY_RESULT = "kGetFWDLeftBackVelocityResult"
    LEFT_POSTIION = "kGetFWDLeftPosition"
    LEFT_POSITION_RESULT = "kGetFWDLeftPositionResult"
    RIGHT_POSITION = "kGetFWDRightPosition"
    RIGHT_POSITION_RESULT = "kGetFWDRightPositionResult"

    def __init__(self, spine, devname, config, commands, sim):
        self.spine = spine
        self.devname = devname
        self.label = config['label']
        self.index = config['index']
        self.wheel_diameter = Unit(config['wheel_diameter'], Length.inch)

        self.sim = sim
        if self.sim:
            self.sim_left_velocity = Unit(0, 0)
            self.sim_left_position = Unit(0, 0)
            self.sim_right_velocity = Unit(0, 0)
            self.sim_right_position = Unit(0, 0)
            self.sim_left_front_velocity = Unit(0, 0)
            self.sim_left_back_velocity = Unit(0, 0)
            self.sim_right_front_velocity = Unit(0, 0)
            self.sim_right_back_velocity = Unit(0, 0)
        else:
            self.driveIndex = commands[self.DRIVE]
            self.stopIndex = commands[self.STOP]
            self.drivePIDIndex = commands[self.DRIVE_PID]
            self.leftVelocityIndex = commands[self.LEFT_VELOCITY]
            self.leftVelocityResultIndex = commands[self.LEFT_VELOCITY_RESULT]
            self.rightVelocityIndex = commands[self.RIGHT_VELOCITY]
            self.rightVelocityResultIndex = commands[self.RIGHT_VELOCITY_RESULT]
            self.rightFrontVelocityIndex = commands[self.RIGHT_FRONT_VELOCITY]
            self.rightFrontVelocityResultIndex = commands[self.RIGHT_FRONT_VELOCITY_RESULT]
            self.rightBackVelocityIndex = commands[self.RIGHT_BACK_VELOCITY]
            self.rightBackVelocityResultIndex = commands[self.RIGHT_BACK_VELOCITY_RESULT]
            self.leftFrontVelocityIndex = commands[self.LEFT_FRONT_VELOCITY]
            self.leftFrontVelocityResultIndex = commands[self.LEFT_FRONT_VELOCITY_RESULT]
            self.leftBackVelocityIndex = commands[self.LEFT_BACK_VELOCITY]
            self.leftBackVelocityResultIndex = commands[self.LEFT_BACK_VELOCITY_RESULT]
            self.leftPositionIndex = commands[self.LEFT_POSITION]
            self.leftPositionResultIndex = commands[self.LEFT_POSITION_RESULT]
            self.rightPositionIndex = commands[self.RIGHT_POSITION]
            self.rightPositionResultIndex = commands[self.RIGHT_POSITION_RESULT]

    def get_command_parameters(self):
        yield self.driveIndex, [self.DRIVE, "iiiii"]
        yield self.stopIndex, [self.STOP, "i"]
        yield self.drivePIDIndex, [self.DRIVE_PID, "iffff"]
        yield self.leftVelocityIndex, [self.LEFT_VELOCITY, "i"]
        yield self.leftVelocityResultIndex, [self.LEFT_VELOCITY_RESULT, "f"]
        yield self.rightVelocityIndex, [self.RIGHT_VELOCITY, "i"]
        yield self.rightVelocityResultIndex, [self.RIGHT_VELOCITY_RESULT, "f"]
        yield self.rightFrontVelocityIndex, [self.RIGHT_FRONT_VELOCITY, "i"]
        yield self.rightFrontVelocityResultIndex, [self.RIGHT_FRONT_VELOCITY_RESULT, "f"]
        yield self.rightBackVelocityIndex, [self.RIGHT_BACK_VELOCITY, "i"]
        yield self.rightBackVelocityResultIndex, [self.RIGHT_BACK_VELOCITY_RESULT, "f"]
        yield self.leftFrontVelocityIndex, [self.LEFT_FRONT_VELOCITY, "i"]
        yield self.leftFrontVelocityResultIndex, [self.LEFT_FRONT_VELOCITY_RESULT, "f"]
        yield self.leftBackVelocityIndex, [self.LEFT_BACK_VELOCITY, "i"]
        yield self.leftBackVelocityResultIndex, [self.LEFT_BACK_VELOCITY_RESULT, "f"]
        yield self.leftPositionIndex, [self.LEFT_POSITION, "i"]
        yield self.leftPositionResultIndex, [self.LEFT_POSITION_RESULT, "f"]
        yield self.rightPositionIndex, [self.RIGHT_POSITION, "i"]
        yield self.rightPositionResultIndex, [self.RIGHT_POSITION_RESULT, "f"]

    def drive(self, *args):
        # Parameter order: lf_value, rf_value, lb_value, rb_value
        if len(args) == 1:
            values = [args[0]] * 4
        elif len(args) == 2:
            values = [args[0], args[1], args[0], args[1]]
        elif len(args) == 4:
            values = list(args)
        else:
            logger.error("Wrong number of arguments in drive")
            raise Exception("Wrong number of arguments in drive")

        if self.sim:
            # TODO: get speed from sim_motor
            pass
        else:
            self.spine.send(self.devname, False, self.DRIVE, self.index, *values)

    def stop(self):
        if self.sim:
            self.sim_left_velocity = Unit(0, 0)
            self.sim_right_velocity = Unit(0, 0)
            self.sim_left_front_velocity = Unit(0, 0)
            self.sim_left_back_velocity = Unit(0, 0)
            self.sim_right_front_velocity = Unit(0, 0)
            self.sim_right_back_velocity = Unit(0, 0)
        else:
            self.spine.send(self.devname, False, self.STOP, self.index)

    def drive_pid(self, *args):
        # Parameter order: lf_value, rf_value, lb_value, rb_value
        if len(args) == 1:
            values = [args[0]] * 4
        elif len(args) == 2:
            values = [args[0], args[1], args[0], args[1]]
        elif len(args) == 4:
            values = list(args)
        else:
            logger.error("Wrong number of arguments in drive_pid")
            raise Exception("Wrong number of arguments in drive_pid")

        for i in range(len(values)):
            values[i] = values[i] / self.wheel_diameter

        if self.sim:
            self.sim_left_front_velocity = values[0]
            self.sim_left_back_velocity = values[2]
            self.sim_right_front_velocity = values[1]
            self.sim_right_back_velocity = values[3]

            self.sim_left_velocity = (values[0] + values[2]) / Unit(2.0, 1)
            self.sim_right_velocity = (values[1] + values[3]) / Unit(2.0, 1)
        else:
            self.spine.send(self.devname, False, self.DRIVE_PID, self.index, *values)

    def get_left_velocity(self):
        if self.sim:
            return self.sim_left_velocity * self.wheel_diameter
        response = self.spine.send(self.devname, True, self.LEFT_VELOCITY, self.index)
        response = Unit(response[0], AngularVelocity.rpm)
        return response

    def get_right_velocity(self):
        if self.sim:
            return self.sim_right_velocity * self.wheel_diameter
        response = self.spine.send(self.devname, True, self.RIGHT_VELOCITY, self.index)
        response = Unit(response[0], AngularVelocity.rpm)
        return response

    def get_left_front_velocity(self):
        if self.sim:
            return self.sim_left_front_velocity * self.wheel_diameter
        response = self.spine.send(self.devname, True, self.LEFT_FRONT_VELOCITY, self.index)
        return response

    def get_left_back_velocity(self):
        if self.sim:
            return self.sim_left_back_velocity * self.wheel_diameter
        response = self.spine.send(self.devname, True, self.LEFT_BACK_VELOCITY, self.index)
        return response

    def get_right_front_velocity(self):
        if self.sim:
            return self.sim_right_front_velocity * self.wheel_diameter
        response = self.spine.send(self.devname, True, self.RIGHT_FRONT_VELOCITY, self.index)
        return response

    def get_right_back_velocity(self):
        if self.sim:
            return self.sim_right_back_velocity * self.wheel_diameter
        response = self.spine.send(self.devname, True, self.RIGHT_BACK_VELOCITY, self.index)
        return response

    def get_left_position(self):
        if self.sim:
            return self.sim_left_position * self.wheel_diameter
        response = self.spine.send(self.devname, True, self.LEFT_POSITION, self.index)
        response = Unit(response[0], Angular.rev)
        return response

    def get_right_position(self):
        if self.sim:
            return self.sim_right_position * self.wheel_diameter
        response = self.spine.send(self.devname, True, self.RIGHT_POSITION, self.index)
        response = Unit(response[0], Angular.rev)
        return response

    def set_pid_type(self, type):
        self.pid_type = type

    def pid_get(self):
        if not hasattr(self, "pid_type") or self.pid_type == "distance":
            return (self.get_left_position() + self.get_right_position()) / 2
        elif self.pid_type == "angle":
            return self.get_left_position() - self.get_right_position()

    def pid_set(self, value):
        if not hasattr(self, "pid_type") or self.pid_type == "distance":
            self.drive_PID(value)
        elif self.pid_type == "angle":
            self.drive_PID(value, -value)

    def sim_update(self, tm_diff):
        self.sim_left_position += self.sim_left_velocity * tm_diff
        self.sim_right_position += self.sim_right_velocity * tm_diff
        '''
        self.sim_left_front_position += self.sim_left_front_velocity * tm_diff
        self.sim_left_back_position += self.sim_left_back_velocity * tm_diff
        self.sim_right_front_position += self.sim_right_front_velocity * tm_diff
        self.sim_right_back_position += self.sim_right_back_velocity * tm_diff
        '''
