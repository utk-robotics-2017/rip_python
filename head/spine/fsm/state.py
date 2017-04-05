class State:
    def __init__(self, name):
        self.name = name

    def run(self):
        raise NotImplemented("State run not implemented")

    def next(self):
        raise NotImplemented("State next not implemented")

    def __str__(self):
        return self.name

    __repr__ = __str__
