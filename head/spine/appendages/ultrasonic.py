from .component import Component
from ... import units


class Ultrasonic(Component):
    READ = "kReadUltrasonic"
    READ_RESULT = "kReadUltrasonicResult"

    def __init__(self, spine, devname, config, commands, sim):
        self.spine = spine
        self.devname = devname
        self.label = config['label']
        self.index = config['index']
        self.sim = sim

        if self.sim:
            self.sim_distance = units.Constant(0)
        else:
            self.readIndex = commands[self.READ]
            self.readResultIndex = commands[self.READ_RESULT]

    def get_command_parameters(self):
        yield self.readIndex, [self.READ, "i"]
        yield self.readResultIndex, [self.READ_RESULT, "L"]

    def set_distance(self, distance):
        if self.sim:
            self.sim_distance = distance

    def read(self):
        '''
        Reads the ultrasonics
        :return: distance in specified unit
        '''
        if self.sim:
            return self.sim_distance

        response = self.spine.send(self.devname, True, self.READ, self.index)

        if response == 0:
            response = float('inf')

        converted_response = units.Length(float(response[0]), units.Length.cm)

        return converted_response

    def sim_update(self, tm_diff):
        pass

    def get_hal_data(self):
        hal_data = {}
        hal_data['distance'] = self.sim_distance
        return hal_data
