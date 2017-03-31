from .component import Component
from ...units import *


class PositionControlledMotor(Component):
    SET_VOLTAGE = "kSetPCMVoltage"
    SET_POSITION = "kSetPCMPosition"
    GET_POSITION = "kGetPCMPosition"
    GET_POSITION_RESULT = "kGetPCMPositionResult"
    STOP = "kStopPCM"

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
            self.getPositionIndex = commands[self.GET_POSITION]
            self.getPositionResultIndex = commands[self.GET_POSITION_RESULT]
            self.stopIndex = commands[self.STOP]

    def get_command_parameters(self):
        yield self.setVoltageIndex, [self.SET_VOLTAGE, "ii"]
        yield self.setPositionIndex, [self.SET_POSITION, "id"]
        yield self.getPositionIndex, [self.GET_POSITION, "i"]
        yield self.getPositionResultIndex, [self.GET_POSITION_RESULT, "d"]
        yield self.stopIndex, [self.STOP, "i"]

    def set_voltage(self, voltage):
        self.spine.send(self.devname, False, self.SET_VOLTAGE, self.index, voltage)

    def set_position(self, position):
        self.spine.send(self.devname, False, self.SET_POSITION, self.index, position)

    def get_position(self):
        response = self.spine.send(self.devname, True, self.GET_POSITION, self.index)
        return Angle(response[0], Angle.rev)

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
