class servo:
    def __init__(self, spine, devname, label, index):
        self.spine = spine
        self.devname = devname
        self.label = label
        self.index = index

    def set(self, value):
        '''
        Set each servo to a position.
        Programming with this command can be tricky since often the servos are
        reverse to each other and they can also fight against each other when
        they are set to different positions.
        :param value:
            Position from 0 to 255 of the servo.
        :type value: ``int``
        '''
        assert 0 <= value <= 255
        response = self.spine.send(self.devname, "ss {} {}".format(self.index, value))
        assert response == 'ok'

    def detach(self):
        response = self.spine.send(self.devname, "sd {}".format(self.index))
        assert response == 'ok'
    def test(self):
        #TEST SOME SHIT I DON'T KNOW
        print("\nservo\n")
        
        #First test
        print("RE
