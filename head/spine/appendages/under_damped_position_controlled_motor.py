from .component import Component
from ...units import *


class UnderDampedPositionControlledMotor(Component):
    SET_VOLTAGE = "kSetUDPCMVoltage"
    SET_POSITION = "kSetUDPCMPosition"
    SET_ALLOWED_DIRECTION = "UDPCMkSetAllowedDirection"
    GET_POSITION = "kGetUDPCMPosition"
    GET_POSITION_RESULT = "kGetUDPCMPositionResult"
    GET_VELOCITY = "kGetUDPCMVelocity"
    GET_VELOCITY_RESULT = "kGetUDPCMVelocityResult"
    STOP = "kStopUDPCM"

    # for allowed direction
    DIRECT = 0
    FORWARD = DIRECT
    REVERSE = 1

    def __init__(self, spine, devname, config, commands, sim):
        self.spine = spine
        self.devname = devname
        self.label = config['label']
        self.index = config['index']
        self.sim = sim
        self.motor = config['motor']
        self.encoder = config['encoder']
        self.pid = config['pid']

        if self.sim:
            self.sim_velocity = Constant(0)
            self.sim_position = Constant(0)
        if not self.sim:
            self.setVoltageIndex = commands[self.SET_VOLTAGE]
            self.setPositionIndex = commands[self.SET_POSITION]
            self.setAllowedDirectionIndex = commands[self.SET_ALLOWED_DIRECTION]
            self.getPositionIndex = commands[self.GET_POSITION]
            self.getPositionResultIndex = commands[self.GET_POSITION_RESULT]
            self.getVelocityIndex = commands[self.GET_VELOCITY]
            self.getVelocityResultIndex = commands[self.GET_VELOCITY_RESULT]
            self.stopIndex = commands[self.STOP]

    def get_command_parameters(self):
        yield self.setVoltageIndex, [self.SET_VOLTAGE, "ii"]
        yield self.setPositionIndex, [self.SET_POSITION, "id"]
        yield self.setAllowedDirectionIndex, [self.SET_ALLOWED_DIRECTION, "ii"]
        yield self.getPositionIndex, [self.GET_POSITION, "i"]
        yield self.getPositionResultIndex, [self.GET_POSITION_RESULT, "d"]
        yield self.getVelocityIndex, [self.GET_VELOCITY, "i"]
        yield self.getVelocityResultIndex, [self.GET_VELOCITY_RESULT, "d"]
        yield self.stopIndex, [self.STOP, "i"]

    def set_voltage(self, voltage):
        self.spine.send(self.devname, False, self.SET_VOLTAGE, self.index, voltage)

    def set_position(self, position):
        self.spine.send(self.devname, False, self.SET_POSITION, self.index, position)

    def set_allowed_direction(self, direction):
        self.spine.send(self.devname, False, self.SET_ALLOWED_DIRECTION, self.index, direction)

    def get_position(self):
        response = self.spine.send(self.devname, True, self.GET_POSITION, self.index)
        return Angle(response[0], Angle.rev)

    def get_velocity(self):
        response = self.spine.send(self.devname, True, self.GET_VELOCITY, self.index)
        return AngularVelocity(response[0], AngularVelocity.rpm)

    def stop(self):
        self.spine.send(self.devname, False, self.STOP, self.index)


'''
    def get_dependency_update(self):
        dependencies = {}
        dependencies[self.motor]['sim_velocity'] = self.sim_velocity
        dependencies[self.encoder]['sim_velocity'] = self.sim_velocity
        return dependencies

    def sim_update(self, tm_diff):
        self.sim_position += self.sim_velocity * tm_diff

    def get_hal_data(self):
        hal_data = {}
        hal_data['velocity'] = self.sim_velocity
        hal_data['position'] = self.sim_position
        return hal_data
'''
