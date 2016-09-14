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
        response = self.spine.send(self.devname, "ss %d %d" % (self.index, value))
        assert response == 'ok'

    def detach(self):
        response = self.spine.send(self.devname, "sd %d" % self.index)
        assert response == 'ok'

    def test(self):
        
        fail0 = 0
        print ("\nTesting servo\n")
        self.set(self, 0)
        query0 = raw_input("\nDid the servo set to 0? y/n\n")
        if query0 != 'y':
            print("Test 1 failed\n")
        fail0 = 1
        
        self.set(self, 255)
        query0 = raw_input("\nDid the servo set to 255? y/n\n")
        if query0 != 'y':
            print("Test 2 failed\n")
        fail0 = 1

        self.set(self, 90)
        query0 = raw_input("\nDid the servo set to 90? y/n\n")
        if query0 != 'y':
            print("Test 3 failed\n")
        fail0 = 1
        
        if fail0 == 1:
            return False
        else:
            return True
