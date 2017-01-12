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
        response = self.spine.send(self.devname, "rs {}".format(self.index))
        return {'1': True, '0': False}[response]

    def test(self):
        print("\nSwitch\n")

        # first test
        raw_input("Make sure no one is touching the switch.  Press enter when ready")
        response = self.read()
        print("State: " + (response == '1') ? "true" : "false")

        while True:
            f_query = raw_input("Is this correct? (y/n): ")
            if f_query == 'y' or f_query == 'n':
                break

        # second test
        raw_input("Press the button or flip the switch.  Press enter when ready")
        response = self.read()
        print("State: " + (response == '1') ? "true" : "false")

        while True:
            s_query = raw_input("Is this correct? (y/n): ")
            if s_query == 'y' or s_query == 'n':
                break

        # pass/fail
        if f_query == 'n' or s_query == 'n':
            return False
        else:
            return True

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
