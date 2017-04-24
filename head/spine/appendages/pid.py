from .component import Component


class Pid(Component):
    GET_PID_CONSTANTS = "kGetPidConstants"
    GET_PID_CONSTANTS_RESULT = "kGetPidConstantsResult"
    SET_PID_CONSTANTS = "kSetPidConstants"
    SET_PID_SETPOINT = "kSetPidSetpoint"
    GET_PID_VALUES = "kGetPidValues"
    GET_PID_VALUES_RESULT = "kGetPidValuesResult"
    PID_OFF = "kPidOff"

    def __init__(self, spine, devname, config, commands, sim):
        self.spine = spine
        self.devname = devname
        self.label = config['label']
        self.index = config['index']
        self.sim = sim

        if not self.sim:
            self.getPidConstantsIndex = commands[self.GET_PID_CONSTANTS]
            self.getPidConstantsResultIndex = commands[self.GET_PID_CONSTANTS_RESULT]
            self.setPidConstantsIndex = commands[self.SET_PID_CONSTANTS]
            self.setPidSetpointIndex = commands[self.SET_PID_SETPOINT]
            self.getPidValuesIndex = commands[self.GET_PID_VALUES]
            self.getPidValuesResultIndex = commands[self.GET_PID_VALUES_RESULT]
            self.pidOffIndex = commands[self.PID_OFF]

    def get_command_parameters(self):
        yield self.getPidConstantsIndex, [self.GET_PID_CONSTANTS, "i"]
        yield self.getPidConstantsResultIndex, [self.GET_PID_CONSTANTS_RESULT, "ddd"]
        yield self.setPidConstantsIndex, [self.SET_PID_CONSTANTS, "iddd"]
        yield self.setPidSetpointIndex, [self.SET_PID_SETPOINT, "id"]
        yield self.getPidValuesIndex, [self.GET_PID_VALUES, "i"]
        yield self.getPidValuesResultIndex, [self.GET_PID_VALUES_RESULT, "ddd"]
        yield self.pidOffIndex, [self.PID_OFF, "i"]

    def get_constants(self):
        if self.sim:
            return

        return self.spine.send(self.devname, True, self.GET_PID_CONSTANTS, self.index)

    def set_constants(self, kp, ki, kd):
        if self.sim:
            return

        self.spine.send(self.devname, False, self.SET_PID_CONSTANTS, self.index, kp, ki, kd)

    def set_setpoint(self, setpoint):
        if self.sim:
            return

        self.spine.send(self.devname, False, self.SET_PID_SETPOINT, self.index, setpoint)

    def get_values(self):
        if self.sim:
            return

        return self.spine.send(self.devname, True, self.GET_PID_VALUES, self.index)

    def off(self):
        if self.sim:
            return

        self.spine.send(self.devname, False, self.PID_OFF, self.index)

    def sim_update(self, tm_diff):
        pass

    def get_hal_data(self):
        return {}
