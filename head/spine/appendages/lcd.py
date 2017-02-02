import logging
from .component import Component

from ..ourlogging import setup_logging

setup_logging(__file__)
logger = logging.getLogger(__name__)


class Lcd(Component):
    WRITE = "kPrintLCD"
    CLEAR = "kClearLCD"
    SETPOS = "kSetCursorLCD"

    def __init__(self, spine, devname, config, commands, sim):
        self.spine = spine
        self.devname = devname
        self.label = config['label']
        self.index = config['index']
        self.sim = sim
        self.message = ""

        if self.sim:
            pass
            # No need for a display in sim?
        else:
            self.writeLCD = commands[self.WRITE]
            self.clearLCD = commands[self.CLEAR]
            self.setposLCD = commands[self.SETPOS]

    def get_command_parameters(self):
        yield self.writeLCD, [self.WRITE, "is"]
        yield self.clearLCD, [self.CLEAR, "i"]
        yield self.setposLCD, [self.SETPOS, "iii"]

    def write(self, message):
        '''write(str message)
        Writes a message to the LCD display.
        :return: nothing
        '''

        self.message = message
        logger.info("Trying to set LCD message: " + self.message)
        response = self.spine.send(self.devname, False, self.WRITE, self.index, self.message)
        logger.info("Written: \"" + message + "\" to the LCD #" + str(self.index) +
                    ", spine.send response: " + str(response))

        return

    def clear(self):
        '''clear()
        Clears the LCD display of all text.
        :return: nothing
        '''

        response = self.spine.send(self.devname, False, self.CLEAR, self.index)
        logger.info("Cleared LCD display: #" + str(self.index) + ", response: " + str(response))

        return

    def setpos(self, horizontal, vertical):
        '''setpos(int horizontal, int vertical)
        Sets the cursor position for the LCD display.
        :return: nothing
        '''

        reponse = self.spine.send(self.devname, False, self.SETPOS, self.index, horizontal, vertical)
        logger.info("Set cursor position for LCD #" + str(self.index) + ", reponse: " + str(reponse))

        return

    def get_hal_data(self):
        hal_data = {}
        hal_data['message'] = self.message
        return hal_data
