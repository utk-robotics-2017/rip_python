import time

class motor:
    def __init__(self, spine, devname, label, index):
        self.spine = spine
        self.devname = devname
        self.label = label
        self.index = index

    def drive(self, value):
        if value == 0:
            self.stop()
            return
        response = self.spine.send(self.devname, "mod %d %d", (self.index, value))
        assert response == 'ok'

    def stop(self):
        response = self.spine.send(self.devname, "mod %d", self.index)
        assert response == 'ok'

    def pidSet(self, value):
        self.drive(value)

    def test(self):
        print("\nMotor\n")

        # first test
        print("The motor should not be moving.  The motor will turn for five seconds.")
        self.drive(420) # blaze it
        time.sleep(5)
        self.stop()

        while True:
            f_query = raw_input("Did it turn (y/n): ")
            if f_query == 'y' or f_query == 'n':
                break

        #second test
        print("The motor should not be moving.  The motor will turn the opposite direction for five seconds.")
        self.drive(-420) # unblaze it
        time.sleep(5)
        self.stop()

        while True:
            s_query = raw_input("Did it turn (y/n): ")
            if s_query == 'y' or s_query == 'n':
                break

        # pass/fail
        if f_query == 'n' or s_query == 'n':
            return False
        else:
            return True
