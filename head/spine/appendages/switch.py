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
            self.state = False
        else:
            self.readIndex = commands[self.READ]
            self.readResultIndex = commands[self.READ_RESULT]

    def get_command_parameters(self):
        yield self.readIndex, [self.READ, "i"]
        yield self.readResultIndex, [self.READ_RESULT, "?"]

    def set_state(self, state):
        if self.sim:
            self.state = state

    def read(self):
        if self.sim:
            return self.state

        response = self.spine.send(self.devname, True, self.READ, self.index)
        return response
