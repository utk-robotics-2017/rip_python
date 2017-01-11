from .component import Component


class Magnetometer(Component):
    READ_X = "kReadX"
    READ_X_RESULT = "kReadXResult"
    READ_Y = "kReadY"
    READ_Y_RESULT = "KReadYResult"
    READ_Z = "kReadZ"
    READ_Z_RESULT = "kReadZResult"

    def __init__(self, spine, devname, config, commands, sim):
        self.spine = spine
        self.devname = devname
        self.label = config['label']
        self.index = config['index']

        self.sim = sim
        if sim:
            pass
        else:
            self.readXIndex = commands[self.READ_X]
            self.readXResultIndex = commands[self.READ_X_RESULT]
            self.readYIndex = commands[self.READ_Y]
            self.readYResultIndex = commands[self.READ_Y_RESULT]
            self.readZIndex = commands[self.READ_Z]
            self.readZResultIndex = commands[self.READ_Z_RESULT]

    def get_command_parameters(self):
        yield self.readXIndex, []
        yield self.readXResultIndex, ['i']
        yield self.readYIndex, []
        yield self.readYResultIndex, ['i']
        yield self.readZIndex, []
        yield self.readZResultIndex, ['i']

    def read_x(self):
        result = self.spine.send(self.devname, True, self.READ_X, [])
        return result

    def read_y(self):
        result = self.spine.send(self.devname, True, self.READ_Y, [])
        return result

    def read_z(self):
        result = self.spine.send(self.devname, True, self.READ_Z, [])
        return result
