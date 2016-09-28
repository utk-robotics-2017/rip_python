from .component import Component


class Ultrasonic(Component):
    READ = "kReadUltrasonic"
    READ_RESULT = "kReadUltrasonic"

    def __init__(self, spine, devname, config, commands):
        self.spine = spine
        self.devname = devname
        self.label = config['label']
        self.index = config['index']

        self.readIndex = commands[self.READ]
        self.readResultIndex = commands[self.READ_RESULT]

    def get_command_parameters(self):
        yield self.readIndex, [self.READ, "i"]
        yield self.readResult, [self.READ_RESULT, "i"]

    def read(self, unit):
        '''
        Reads the ultrasonics
        :return: distance in specified unit
        '''
        response = self.spine.send(self.devname, True, self.READ, self.index)
        assert unit in ['inch', 'cm']
        if unit == 'inch':
            response = float(response) / 2.0 / 73.746
        elif unit == 'cm':
            response = float(response) / 2.0 / 29.1

        if response == 0:
            response = float('inf')

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
