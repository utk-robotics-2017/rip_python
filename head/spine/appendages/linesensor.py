class linesensor:
    def __init__(self, spine, devname, label, index, analog):
        self.spine = spine
        self.devname = devname
        self.label = label
        self.index = index
        self.analog = analog

    def read(self):        
        if self.analog:
            return self.spine.send(self.devname, "rals {}".format(self.index))
        else:
            return self.spine.send(self.devname, "rdls {}".format(self.index))

    def test(self):
        print("\nLine sensor\n")

        # first test
        raw_input("Make sure nothing is obstructing the sensor.  Press enter when ready")
        response = self.read()
        print("Result: %d " % response)

        while True:
            f_query = raw_input("Is this correct? (y/n): ")
            if f_query == 'y' or f_query == 'n':
                break

        # second test
        raw_input("Obstruct the sensor (put your hand over it or something).  Press enter when ready")
        response = self.read()
        print("Result: %d " % response)

        while True:
            s_query = raw_input("Is this correct? (y/n): ")
            if s_query == 'y' or s_query == 'n':
                break

        # pass/fail
        if f_query == 'n' or s_query == 'n':
            return False
        else:
            return True
