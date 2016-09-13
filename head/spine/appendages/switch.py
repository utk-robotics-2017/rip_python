class switch:
    def __init__(self, spine, devname, label, index):
        self.spine = spine
        self.devname = devname
        self.label = label
        self.index = index

    def read(self):
        response = self.spine.send(self.devname, "rs {}".format(self.index))
        return {'1': True, '0': False}[response]

    def test(self):
        print("\nSwitch\n")

        # first test
        raw_input("Make sure no one is touching the switch.  Press enter when ready")
        response = self.read()
        print("State: " + (response == '1') ? "true" : "false")

        while True:
            f_query = raw_input("Is this correct? (y/n): ")
            if f_query == 'y' or f_query == 'n':
                break

        # second test
        raw_input("Press the button or flip the switch.  Press enter when ready")
        response = self.read()
        print("State: " + (response == '1') ? "true" : "false")

        while True:
            s_query = raw_input("Is this correct? (y/n): ")
            if s_query == 'y' or s_query == 'n':
                break

        # pass/fail
        if f_query == 'n' or s_query == 'n':
            return False
        else:
            return True
