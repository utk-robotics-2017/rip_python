from .component import Component


class Motor(Component):
    DRIVE = "kDriveMotor"
    STOP = "kStopMotor"

    def __init__(self, spine, devname, config, commands):
        self.spine = spine
        self.devname = devname
        self.label = config['label']
        self.index = config['index']

        self.driveIndex = commands[self.DRIVE]
        self.stopIndex = commands[self.STOP]

    def get_command_parameters(self):
        yield self.driveIndex, [self.DRIVE, "ii"]
        yield self.stopIndex, [self.STOP, "i"]

    def drive(self, value):
        if value == 0:
            self.stop()
            return
        self.spine.send(self.devname, False, self.DRIVE, self.index, value)

    def stop(self):
        self.spine.send(self.devname, False, self.STOP, self.index)

    def pid_set(self, value):
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
        print "The motor should not be moving.  The motor will turn the opposite direction for five seconds."
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
