from .component import Component


class Switch(Component):
    READ = "kReadSwitch"
    READ_RESULT = "kReadSwitchResult"

    def __init__(self, spine, devname, config, commands, sim):
        self.spine = spine
        self.devname = devname
        self.label = config['label']
        self.index = config['index']
        self.sim = sim

        if self.sim:
            self.sim_state = False
        else:
            self.readIndex = commands[self.READ]
            self.readResultIndex = commands[self.READ_RESULT]

    def get_command_parameters(self):
        yield self.readIndex, [self.READ, "i"]
        yield self.readResultIndex, [self.READ_RESULT, "i"]

    def set_state(self, state):
        if self.sim:
            self.sim_state = state

    def read(self):
        if self.sim:
            return self.sim_state

        response = self.spine.send(self.devname, True, self.READ, self.index)
        return [False, True][response[0]]

    def sim_update(self, tm_diff):
        pass

    def get_hal_data(self):
        hal_data = {}
        hal_data['state'] = self.sim_state
        return hal_data
