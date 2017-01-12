from .component import Component
from ...units import *


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
            self.sim_distance = Constant(0)
        else:
            self.readIndex = commands[self.READ]
            self.readResultIndex = commands[self.READ_RESULT]

    def get_command_parameters(self):
        yield self.readIndex, [self.READ, "i"]
        yield self.readResult, [self.READ_RESULT, "i"]

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

        response = Length(float(response / 2.0 / 29.1), Length.cm)

        return response

    def test(self):
        unit = 'cm'

        print("\nUltrasonic\n")

        time_end = time.time() + 5
        while time.time() < time_end:
            print("%d" % self.read(unit) + unit)
        
        # correctness test
        while True:
            query = raw_input("Is this correct? (y/n): ")
            if query == 'y' or query == 'n':
                break

        # pass/fail
        if query == 'n':
            return False
        else:
            return True
    def sim_update(self, tm_diff):
        pass

    def get_hal_data(self):
        hal_data = {}
        hal_data['distance'] = self.sim_distance
        return hal_data
