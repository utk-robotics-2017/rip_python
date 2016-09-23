from .component import Component


class Motor(Component):
    DRIVE = "kDriveMotor"
    STOP = "kStopMotor"

    def __init__(self, spine, devname, config, commands, sim):
        self.spine = spine
        self.devname = devname
        self.label = config['label']
        self.index = config['index']
        self.sim = sim

        if not sim:
            self.driveIndex = commands[self.DRIVE]
            self.stopIndex = commands[self.STOP]

    def get_command_parameters(self):
        yield self.driveIndex, [self.DRIVE, "ii"]
        yield self.stopIndex, [self.STOP, "i"]

    def drive(self, value):
        if self.sim:
            return

        if value == 0:
            self.stop()
            return
        self.spine.send(self.devname, False, self.DRIVE, self.index, value)

    def stop(self):
        if self.sim:
            return

        self.spine.send(self.devname, False, self.STOP, self.index)

    def pid_set(self, value):
        self.drive(value)
