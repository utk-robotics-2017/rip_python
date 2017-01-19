from .component import Component


class Magnetometer(Component):
    READ_X = "kReadX"
    READ_X_RESULT = "kReadXResult"
    READ_Y = "kReadY"
    READ_Y_RESULT = "kReadYResult"
    READ_Z = "kReadZ"
    READ_Z_RESULT = "kReadZResult"

    def __init__(self, spine, devname, config, commands, sim):
        self.spine = spine
        self.devname = devname
        self.label = config['label']

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
        yield self.readXIndex, [self.READ_X, '']
        yield self.readXResultIndex, [self.READ_X_RESULT, 'i']
        yield self.readYIndex, [self.READ_Y, '']
        yield self.readYResultIndex, [self.READ_Y_RESULT, 'i']
        yield self.readZIndex, [self.READ_Z, '']
        yield self.readZResultIndex, [self.READ_Z_RESULT, 'i']

    def read_x(self):
        result = self.spine.send(self.devname, True, self.READ_X)
        return result[0]

    def read_y(self):
        result = self.spine.send(self.devname, True, self.READ_Y)
        return result[0]

    def read_z(self):
        result = self.spine.send(self.devname, True, self.READ_Z)
        return result[0]
