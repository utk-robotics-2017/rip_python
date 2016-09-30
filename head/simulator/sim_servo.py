class VexServo:
    def __init__(self):
        self.max_angle = 100

    def get_position(self, value):
        return self.max_angle * (value / 255)
