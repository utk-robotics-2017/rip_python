from .component import Component
from ...units import Unit, Angular, AngularVelocity


class I2CEncoder(Component):
    POSITION = "kI2CEncoderPosition"
    POSITION_RESULT = "kI2CEncoderPositionResult"
    RAW_POSITION = "kI2CEncoderRawPosition"
    RAW_POSITION_RESULT = "kI2CEncoderRawPositionResult"
    SPEED = "kI2CEncoderSpeed"
    SPEED_RESULT = "kI2CEncoderSpeedResult"
    VELOCITY = "kI2CEncoderVelocity"
    VELOCITY_RESULT = "kI2CEncoderVelocityResult"
    ZERO = "kI2CEncoderZero"

    def __init__(self, spine, devname, config, commands, sim):
        self.spine = spine
        self.devname = devname
        self.label = config['label']
        self.index = config['index']
        self.pidSource = 'position'
        self.sim = sim

        if self.sim:
            self.sim_position = Unit(0, 1)
            self.sim_velocity = Unit(0, 1)
        else:
            self.positionIndex = commands[self.POSITION]
            self.positionResultIndex = commands[self.POSITION_RESULT]
            self.rawPositionIndex = commands[self.RAW_POSITION]
            self.rawPositionResultIndex = commands[self.RAW_POSITION_RESULT]
            self.speedIndex = commands[self.SPEED]
            self.speedResultIndex = commands[self.SPEED_RESULT]
            self.velocityIndex = commands[self.VELOCITY]
            self.velocityResultIndex = commands[self.VELOCITY_RESULT]
            self.zeroIndex = commands[self.ZERO]

    def get_commands_parameters(self):
        yield self.positionIndex, [self.POSITION, "i"]
        yield self.positionResultIndex, [self.POSITION_RESULT, "d"]
        yield self.rawPositionIndex, [self.RAW_POSITION, "i"]
        yield self.rawPostionResultIndex, [self.RAW_POSITION_RESULT, "d"]
        yield self.speedIndex, [self.SPEED, "i"]
        yield self.speedResultIndex, [self.SPEED_RESULT, "d"]
        yield self.velocityIndex, [self.VELOCITY, "i"]
        yield self.velocityResultIndex, [self.VELOCITY_RESULT, "d"]
        yield self.zeroIndex, [self.ZERO, "i"]

    def set_pid_source(self, source):
        self.pidSource = source

    def get_position(self):
        if self.sim:
            return self.sim_position

        response = self.spine.send(self.devname, True, self.POSITION, self.index)
        response = Unit(response[0], Angular.rev)
        return response

    def set_position(self, position):
        if self.sim:
            self.sim_position = position

    def raw_position(self):
        if self.sim:
            return 0

        return self.spine.send(self.devname, True, self.RAW_POSITION, self.index)[0]

    def get_speed(self):
        if self.sim:
            return abs(self.sim_velocity)

        response = self.spine.send(self.devname, True, self.SPEED, self.index)
        response = Unit(response[0], AngularVelocity.rpm)
        return response

    def set_velocity(self, velocity):
        if self.sim:
            self.sim_velocity = velocity

    def get_velocity(self):
        if self.sim:
            return self.sim_velocity

        response = self.spine.send(self.devname, True, self.VELOCITY, self.index)
        response = Unit(response[0], AngularVelocity.rpm)
        return response

    def zero(self):
        if self.sim:
            self.sim_position = 0
            self.sim_velocity = 0
            return

        self.spine.send(self.devname, False, self.ZERO, self.index)

    def pid_get(self):
        if self.pidSource == 'position':
            return self.position()
        elif self.pidSource == 'velocity':
            return self.velocity()

    def sim_update(self, tm_diff):
        self.sim_position += self.sim_velocity * tm_diff
