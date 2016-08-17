class stepper:
    def __init__(self, spine, devname, label, index):
        self.spine = spine
        self.devname = devname
        self.label = label
        self.index = index

    def setSpeed(self, value):
        '''
        Set speed for a stepper motor.
        :param value:
            Speed for the stepper to turn at
        :type value: ``int``
        '''
        response = self.spine.send(self.devname, "sssp %d %d" % (self.index, value))
        assert response == 'ok'

    def step(self, value):
        '''
        Step the motor forward value amount

        :param value:
            Number of steps the motor will turn
        :type value: ``int``
        '''
        response = self.spine.send(self.devname, "sss %d %d" % (self.index, value))
        assert response == 'ok'