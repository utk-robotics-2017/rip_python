class vpid:

    def __init__(self, spine, devname, label, index):
        self.spine = spine
        self.devname = devname
        self.label = label
        self.index = index

    def modify_constants(self, kp, ki, kd):
        response = self.spine.send(
            self.devname, "vpc {} {} {} {}".format(self.index, kp, ki, kd))
        assert response == 'ok'

    def set(self, setpoint):
        response = self.spine.send(
            self.devname, "vps {} {}".format(self.index, setpoint))
        assert response == 'ok'

    def off(self):
        response = self.spine.send(self.devname, "vpoff {}".format(self.index))
        assert response == 'ok'

    def display(self):
        response = self.spine.send(self.devname, "vpd {}".format(self.index))
        # TODO: break response up into parts
        return response
