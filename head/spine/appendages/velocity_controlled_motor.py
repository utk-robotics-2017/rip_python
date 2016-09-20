from .component import Component


class VelocityControlledMotor(Component):
    DRIVE = "kSetVCMVoltage"
    SET = "kSetVCMVelocity"
    STOP = "kStopVCM"
    VELOCITY = "kGetVCMVelocity"
    VELOCITY_RESULT = "kGetVCMVelocityResult"
    POSITION = "kGetVCMPosition"
    POSITION_RESULT = "kGetVCMPositionResult"

    def __init__(self, spine, devname, config, commands):
        self.spine = spine
        self.devname = devname
        self.label = config['label']
        self.index = config['index']

        self.driveIndex = commands[self.DRIVE]
        self.setIndex = commands[self.SET]
        self.stopIndex = commands[self.STOP]
        self.velocityIndex = commands[self.VELOCITY]
        self.velocityResultIndex = commands[self.VELOCITY_RESULT]
        self.positionIndex = commands[self.POSITION]
        self.positionResultIndex = commands[self.POSITION_RESULT]

    def get_command_parameters(self):
        yield self.driveIndex, [self.DRIVE, "ii"]
        yield self.setIndex, [self.SET, "id"]
        yield self.stopIndex, [self.STOP, "i"]
        yield self.velocityIndex, [self.VELOCITY, "i"]
        yield self.velocityResultIndex, [self.VELOCITY_RESULT, "d"]
        yield self.positionIndex, [self.POSITION, "i"]
        yield self.positionResultIndex, [self.POSITION_RESULT, "d"]

    def drive(self, value):
        self.spine.send(self.devname, False, self.DRIVE, self.index, value)

    def set(self, value):
        self.spine.send(self.devname, False, self.SET, self.index, value)

    def getVelocity(self):
        response = self.spine.send(self.devname, True, self.VELOCITY, self.index)
        return response

    def getPosition(self):
        response = self.spine.send(self.devname, True, self.POSITION, self.index)
        return response

    def stop(self):
        self.spine.send(self.devname, False, self.STOP, self.index)
