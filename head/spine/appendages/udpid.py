from .component import Component


class Udpid(Component):
    UDPID_CONSTANTS = "kUdpidConstants"
    UDPID_CONSTANTS_RESULT = "kUdpidConstantsResult"
    MODIFY_UDPID_CONSTANTS = "kModifyUdpidConstants"
    SET_UDPID_SETPOINT = "kSetUdpidSetpoint"
    UDPID_OFF = "kUdpidOff"
    UDPID_DISPLAY = "kUdpidDisplay"
    UDPID_DISPLAY_RESULT = "kUdpidDisplayResult"

    def __init__(self, spine, devname, config, commands, sim):
        self.spine = spine
        self.devname = devname
        self.label = config['label']
        self.index = config['index']
        self.sim = sim

        if not self.sim:
            self.udpidConstantsIndex = commands[self.UDPID_CONSTANTS]
            self.udpidConstantsResultIndex = commands[self.UDPID_CONSTANTS_RESULT]
            self.modifyUdpidConstantsIndex = commands[self.MODIFY_UDPID_CONSTANTS]
            self.setUdpidSetpointIndex = commands[self.SET_UDPID_SETPOINT]
            self.udpidOffIndex = commands[self.UDPID_OFF]
            self.udpidDisplayIndex = commands[self.UDPID_DISPLAY]
            self.udpidDisplayResultIndex = commands[self.UDPID_DISPLAY_RESULT]

    def get_command_parameters(self):
        yield self.udpidConstantsIndex, [self.UDPID_CONSTANTS, "i"]
        yield self.udpidConstantsResultIndex, [self.UDPID_CONSTANTS_RESULT, "ddd"]
        yield self.modifyUdpidConstantsIndex, [self.MODIFY_UDPID_CONSTANTS, "iddd"]
        yield self.setUdpidSetpointIndex, [self.SET_UDPID_SETPOINT, "id"]
        yield self.udpidOffIndex, [self.UDPID_OFF, "i"]
        yield self.udpidDisplayIndex, [self.UDPID_DISPLAY, "i"]
        yield self.udpidDisplayResultIndex, [self.UDPID_DISPLAY_RESULT, "ddd"]

    def constants(self):
        return self.spine.send(self.devname, True, self.UDPID_CONSTANTS, self.index)

    def modify_constants(self, kp, ki, kd):
        if self.sim:
            return

        self.spine.send(self.devname, False, self.MODIFY_UDPID_CONSTANTS, self.index, kp, ki, kd)

    def set(self, setpoint):
        if self.sim:
            return

        self.spine.send(self.devname, False, self.SET_UDPID_SETPOINT, self.index, setpoint)

    def off(self):
        if self.sim:
            return

        self.spine.send(self.devname, False, self.UDPID_OFF, self.index)

    def display(self):
        if self.sim:
            return 0

        response = self.spine.send(self.devname, True, self.UDPID_DISPLAY, self.index)
        return response

    def sim_update(self, tm_diff):
        pass

    def get_hal_data(self):
        return {}
