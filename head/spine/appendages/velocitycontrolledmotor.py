class velocitycontrolledmotor:
    def __init__(self, spine, devname, label, index):
        self.spine = spine
        self.devname = devname
        self.label = label
        self.index = index

    def drive(self, value):
        response = self.spine.send(self.devname, "vcmd {} {}".format(self.index, value))
        assert response == 'ok'

    def set(self, value):
        response = self.spine.send(self.devname, "vcdsv {} {}".format(self.index, value))
        assert response == 'ok'

    def getVelocity(self):
        response = self.spine.send(self.devname, "vcdgv {}".format(self.index))
        return response

    def getPosition(self):
        response = self.spine.send(self.devname, "vcdgp {}".format(self.index))
        return response

    def stop(self):
        response = self.spine.send(self.devname, "vcms {}".format(self.index))
        assert response == 'ok'

    def test(self):
        '''
        Method:
        Set a hard coded velocity (probably)
        Check the velocity with getVelocity
        See if they are the same
        '''
