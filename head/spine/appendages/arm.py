class arm:
    def __init__(self, spine, devname, label, index):
        self.spine = spine
        self.devname = devname
        self.label = label
        self.index = index

    def set(self, base, shoulder, elbow, wrist, wrist_rotate):
        self.spine.send(self.devname, "sa %d %d %d %d %d %d" % (self.index, base, shoulder, elbow, wrist, wrist_rotate))

    def detach(self):
        self.spine.send(self.devname, "das %d" % self.index)
