class velocitycontrolledmotor:
    def __init__(self, spine, devname, label, index):
        self.spine = spine
        self.devname = devname
        self.label = label
        self.index = index

    def drive(self, value):
        response = self.spine.send(self.devname, "vcmd %d %d", (self.index, value))
        assert response == 'ok'

    def set(self, value):
        response = self.spine.send(self.devname, "vcdsv %d %f", (self.index, value))
        assert response == 'ok'

    def getVelocity(self):
        response = self.spine.send(self.devname, "vcdgv %d", (self.index))
        return response

    def getPosition(self):
        response = self.spine.send(self.devname, "vcdgp %d", (self.index))
        return response

    def stop(self):
        response = self.spine.send(self.devname, "vcms %d", (self.index))
        assert response == 'ok'

    def test(self):
        '''
        Method:
        Set a hard coded velocity (probably)
        Check the velocity with getVelocity
        See if they are the same
        '''
