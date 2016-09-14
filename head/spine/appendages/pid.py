class pid:
    def __init__(self, spine, devname, label, index):
        self.spine = spine
        self.devname = devname
        self.label = label
        self.index = index

    def modify_constants(self, kp, ki, kd):
        response = self.spine.send(
            self.devname, "pc {} {} {} {}".format(self.index, kp, ki, kd))
        assert response == 'ok'

    def set(self, setpoint):
        response = self.spine.send(
            self.devname, "ps {} {}".format(self.index, setpoint))
        assert response == 'ok'

    def off(self):
        response = self.spine.send(self.devname, "poff {}".format(self.index))
        assert response == 'ok'

    def display(self):
        response = self.spine.send(self.devname, "pd {}".format(self.index))
        # TODO: break response up into parts
        return response

    #def test(self):
        # idk how do you test a pid?
