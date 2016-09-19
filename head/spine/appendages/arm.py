class Arm:
    SET = "kSetArm"
    DETACH = "kDetachArm"

    def __init__(self, spine, devname, config, commands):
        self.spine = spine
        self.devname = devname
        self.label = config['label']
        self.index = config['index']

        self.setIndex = commands[self.SET]
        self.detachIndex = commands[self.DETACH]

    def get_command_parameters(self):
        yield self.setIndex, [self.SET, "i", "i", "i", "i", "i", "i"]
        yield self.detachIndex, [self.DETACH, "i"]

    def set(self, rot):
        '''
        Move the arm to a position given in raw servo values.
        :warning:
            You probably do not want to call this method directly. Please see
            the documentation on the Arm class which can greatly simplify the
            process of programming for the arm. It can help with the translation
            between cartesian coordinates and servo values, and it can also
            handle the interpolation between arm positions.
        :param rot:
            A tuple of length 5 with values between 1 and 180 that specify the
            amount of rotation for each servo in the arm. The servo order is
            (base, shoulder, elbow, wrist, wristrotate).
        :type rot: ``tuple``
        '''
        assert len(rot) == 5
        for r in rot:
            assert 0 <= r <= 180
        self.spine.send(self.devname, False, self.SET, self.index, tuple(rot))

    def detach(self):
        self.spine.send(self.devname, False, self.DETACH, self.index)
