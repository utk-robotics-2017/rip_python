from .component import Component


class Pid(Component):
    PID_MODIFY_CONSTANT = "kModifyPidConstants"
    PID_SET = "kSetPidSetpoint"
    PID_OFF = "kPidOff"
    PID_DISPLAY = "kPidDisplay"
    PID_DISPLAY_RESULT = "kPidDisplayResult"

    VPID_MODIFY_CONSTANT = "kModifyVpidConstants"
    VPID_SET = "kSetVpidSetpoint"
    VPID_OFF = "kVpidOff"
    VPID_DISPLAY = "kVpidDisplay"
    VPID_DISPLAY_RESULT = "kVpidDisplayResult"

    def __init__(self, spine, devname, config, commands, sim):
        self.spine = spine
        self.devname = devname
        self.label = config['label']
        self.index = config['index']
        self.vpid = config['vpid']
        self.sim = sim

        if not self.sim:
            if not self.vpid:
                self.modifyConstantsIndex = commands[self.PID_MODIFY_CONSTANTS]
                self.setIndex = commands[self.PID_SET]
                self.offIndex = commands[self.PID_OFF]
                self.displayIndex = commands[self.PID_DISPLAY]
                self.displayResultIndex = commands[self.PID_DISPLAY_RESULT]

                self.MODIFY_CONSTANTS = self.PID_MODIFY_CONSTANTS
                self.SET = self.PID_SET
                self.OFF = self.PID_OFF
                self.DISPLAY = self.PID_DISPLAY
                self.DISPLAY_RESULT = self.PID_DISPLAY_RESULT
            else:
                self.modifyConstantsIndex = commands[self.VPID_MODIFY_CONSTANTS]
                self.setIndex = commands[self.VPID_SET]
                self.offIndex = commands[self.VPID_OFF]
                self.displayIndex = commands[self.VPID_DISPLAY]
                self.displayResultIndex = commands[self.VPID_DISPLAY_RESULT]

                self.MODIFY_CONSTANTS = self.VPID_MODIFY_CONSTANTS
                self.SET = self.VPID_SET
                self.OFF = self.VPID_OFF
                self.DISPLAY = self.VPID_DISPLAY
                self.DISPLAY_RESULT = self.VPID_DISPLAY_RESULT

    def get_command_parameters(self):
        yield self.modifyConstantsIndex, [self.MODIFY_CONSTANTS, "iddd"]
        yield self.setIndex, [self.SET, "id"]
        yield self.offIndex, [self.OFF, "i"]
        yield self.displayIndex, [self.DISPLAY, "i"]
        yield self.displayResultIndex, [self.DISPLAY_RESULT, "iddd"]

    def modify_constants(self, kp, ki, kd):
        if self.sim:
            return

        self.spine.send(self.devname, False, self.MODIFY_CONSTANTS, self.index, kp, ki, kd)

    def set(self, setpoint):
        if self.sim:
            return

        self.spine.send(self.devname, False, self.SET, self.index, setpoint)

    def off(self):
        if self.sim:
            return

        self.spine.send(self.devname, False, self.OFF, self.index)

    def display(self):
        if self.sim:
            return 0

        response = self.spine.send(self.devname, True, self.DISPLAY, self.index)
        return response

    def sim_update(self, tm_diff):
        pass

    def get_hal_data(self):
        return {}
