from .component import Component
from ...units import Length


class Ultrasonic(Component):
    READ = "kReadUltrasonic"
    READ_RESULT = "kReadUltrasonic"

    def __init__(self, spine, devname, config, commands, sim):
        self.spine = spine
        self.devname = devname
        self.label = config['label']
        self.index = config['index']
        self.sim = sim

        if self.sim:
            self.distance = 0
        else:
            self.readIndex = commands[self.READ]
            self.readResultIndex = commands[self.READ_RESULT]

    def get_command_parameters(self):
        yield self.readIndex, [self.READ, "i"]
        yield self.readResult, [self.READ_RESULT, "i"]

    def set_distance(self, distance):
        if self.sim:
            self.distance = distance

    def read(self):
        '''
        Reads the ultrasonics
        :return: distance in specified unit
        '''
        if self.sim:
            return self.distance

        response = self.spine.send(self.devname, True, self.READ, self.index)

        if response == 0:
            response = float('inf')

        response = Length(float(response / 2.0 / 29.1), Length.cm)

        return response
