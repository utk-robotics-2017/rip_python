from .component import Component


class Lcd(Component):
    WRITE = "kPrintLCD"

    def __init__(self, spine, devname, config, commands, sim):
        self.spine = spine
        self.devname = devname
        self.label = config['label']
        self.index = config['index']
        self.sim = sim
        self.message = ""

        if self.sim:
            self.write
        else:
            self.writeLCD = commands[self.WRITE]

    def get_command_parameters(self):
        yield self.writeLCD, [self.WRITE, "is"]

    def write(self, message):
        '''
        Writes a message to the LCD display.
        :return: nothing
        '''

        self.message = message
        print("Trying to set LCD message: " + self.message)
        response = self.spine.send(self.devname, False, self.WRITE, self.index, self.message)
        # TODO Debugging
        print("Written: \"" + message + "\" to the LCD #" + str(self.index) +
              ", spine.send response: " + str(response))

        return

    def get_hal_data(self):
        hal_data = {}
        hal_data['message'] = self.message
        return hal_data
