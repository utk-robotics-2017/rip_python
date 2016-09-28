class encoder:
    def __init__(self, spine, devname, label, index):
        self.spine = spine
        self.devname = devname
        self.label = label
        self.index = index

    def read(self):
        '''
        Read the encoder.
        '''
        return float(self.spine.send(self.devname, "re %d" % self.index))

    def zero(self):
        response = self.spine.send(self.devname, "ze %d" % self.index)
        assert response == 'ok'

    def pidGet(self):
        return self.read()

    def test(self):
        print("\nEncoder\n")

        init = self.read()
        print("Initial reading: " + init)
        print("Move the wheel manually")
        change = self.read()
        print("New reading: " + change)
        
        while True:
            f_query = raw_input("Is this correct? (y/n): ")
            if f_query == 'y' or f_query == 'n':
                break
