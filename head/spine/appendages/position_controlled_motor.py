from .component import Component
from ...units import *


class PositionControlledMotor(Component):
    SET_VOLTAGE = "kSetPCMVoltage"
    STOP = "kStopPCM"
    POSITION = "kGetPCMPosition"
    POSITION_RESULT = "kGetPCMPositionResult"
    SET = "kSetPCMPosition"

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
            self.sim_position = Constant(0)
        if not self.sim:
            self.setVoltageIndex = commands[self.SET_VOLTAGE]
            self.stopIndex = commands[self.STOP]
            self.positionIndex = commands[self.POSITION]
            self.positionResultIndex = commands[self.POSITION_RESULT]
            self.setIndex = commands[self.SET]

    def get_command_parameters(self):
        yield self.setVoltageIndex, [self.SET_VOLTAGE, "ii"]
        yield self.stopIndex, [self.STOP, "i"]
        yield self.positionIndex, [self.POSITION, "i"]
        yield self.positionResultIndex, [self.POSITION_RESULT, "d"]
        yield self.setIndex, [self.SET, "id"]

    def set_voltage(self, value):
        if self.sim:
            # TODO: update sim_velocity based on sim_motor
            return

        self.spine.send(self.devname, False, self.SET_VOLTAGE, self.index, value)

    def stop(self):
        if self.sim:
            self.sim_velocity = Constant(0)
            return

        self.spine.send(self.devname, False, self.STOP, self.index)

    def get_position(self):
        if self.sim:
            return self.sim_position

        response = self.spine.send(self.devname, True, self.POSITION, self.index)
        response = Angle(response[0], Angle.rev)
        return response

    def set_position(self, position):
        if self.sim:
            self.sim_position = position
            return

        self.spine.send(self.devname, False, self.SET, self.index, position.to(Angle.degree))

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
