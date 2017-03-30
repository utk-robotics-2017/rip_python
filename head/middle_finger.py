class MiddleFinger(Exception):
    def __str__(self):
        with open('middle_finger.txt') as f:
            print(f.read())
    __repr__ = __str__
