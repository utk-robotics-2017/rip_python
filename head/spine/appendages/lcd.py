import logging
from .component import Component

from ..ourlogging import setup_logging

setup_logging(__file__)
logger = logging.getLogger(__name__)


class Lcd(Component):
    WRITE = "kPrintLCD"
    CLEAR = "kClearLCD"
    SETPOS = "kSetCursorLCD"

    def __init__(self, spine, devname, config, commands, sim, rows=2, cols=16):
        self.spine = spine
        self.devname = devname
        self.label = config['label']
        self.index = config['index']
        self.sim = sim
        self.rows = rows
        self.cols = cols
        # lines is an array for keeping track of what is on each line.
        # contains char lists for each line/row.
        self.lines = []
        # self.cursor: (row, col)
        # keeps track of where the cursor is.
        self.cursor = (0, 0)

        if self.sim:
            for i in range(0, self.rows):
                self.lines.append(list("Sim Line " + str(i)))
        else:
            self.writeLCD = commands[self.WRITE]
            self.clearLCD = commands[self.CLEAR]
            self.setposLCD = commands[self.SETPOS]
            # The display is initially empty.
            for i in range(0, self.rows):
                self.lines.append(list(" " * cols))

    def get_command_parameters(self):
        yield self.writeLCD, [self.WRITE, "is"]
        yield self.clearLCD, [self.CLEAR, "i"]
        yield self.setposLCD, [self.SETPOS, "iii"]

    def write(self, message):
        '''write(str message)
        Writes a message to the LCD display at the current position.
        :return: nothing
        '''

        logger.info("Trying to set LCD message: " + message)

        if not self.sim:
            self.spine.send(self.devname, False, self.WRITE, self.index, message)
            logger.info("Written: \"" + message + "\" to the LCD #" + str(self.index))
        else:
            logger.info("Written: \"" + message + "\" to the LCD #" + str(self.index))

        self.lines[self.cursor[0]] = list(message)

        return

    def clear(self):
        '''clear()
        Clears the LCD display of all text.
        :return: nothing
        '''

        if not self.sim:
            self.spine.send(self.devname, False, self.CLEAR, self.index)
        logger.info("Cleared LCD display #" + str(self.index))

        for row in range(0, self.rows):
            self.lines[row] = list(" " * self.cols)

        return

    def setpos(self, vertical, horizontal):
        '''setpos(int vertical, int horizontal)
        Sets the cursor position for the LCD display.
        :return: nothing
        '''

        self.cursor = (vertical, horizontal)

        if not self.sim:
            self.spine.send(self.devname, False, self.SETPOS, self.index, vertical, horizontal)

        logger.info("Set cursor position for LCD #" + str(self.index))

        return

    def get_message(self):
        '''get_message()
        Returns a representation of what the display was last set to.
        :return: multi-line string, newline at end of each line
        '''
        return_message = ""

        for linelist in self.lines:
            return_message += "".join(linelist)
            return_message += "\n"

        return return_message

    def get_hal_data(self):
        hal_data = {}
        hal_data['message'] = self.message
        return hal_data
