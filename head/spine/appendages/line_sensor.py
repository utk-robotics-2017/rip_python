from .component import Component


class LineSensor(Component):
    READ_DIGITAL = "kReadDigitalLineSensor"
    READ_DIGITAL_RESULT = "kReadDigitalLineSensorResult"
    READ_ANALOG = "kReadAnalogLineSensor"
    READ_ANALOG_RESULT = "kReadAnalogLineSensorResult"

    def __init__(self, spine, devname, label, config, commands, sim):
        self.spine = spine
        self.devname = devname
        self.label = config['label']
        self.index = config['index']
        self.digital = config['digital']
        self.sim = sim

        if not self.sim:
            if self.READ_DIGITAL in commands:
                self.readDigitalIndex = commands[self.READ_DIGITAL]
                self.readDigitalResultIndex = commands[self.READ_DIGITAL_RESULT]

            if self.READ_ANALOG in commands:
                self.readAnalogIndex = commands[self.READ_ANALOG]
                self.readAnalogResultIndex = commands[self.READ_ANALOG_RESULT]

    def get_command_parameters(self):
        if hasattr(self, 'readDigitalIndex'):
            yield self.readDigitalIndex, [self.READ_DIGITAL, "i"]
            yield self.readDigitalResultIndex, [self.READ_DIGITAL_RESULT, "i"]

        if hasattr(self, 'readAnalogIndex'):
            yield self.readAnalogIndex, [self.READ_ANALOG, "i"]
            yield self.readAnalogResultIndex, [self.READ_ANALOG_RESULT, "i"]

    def read(self):
        if self.sim:
            return 0

        if self.digital:
            return self.spine.send(self.devname, True, self.READ_DIGITAL, self.index)
        else:
            return self.spine.send(self.devname, True, self.READ_ANALOG, self.index)
