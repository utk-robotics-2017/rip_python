from math import sqrt, sin, cos
import copy
from ..units import Distance


class Translation:
    '''
        A translation in a 3d coordinate frame. Translations are simply shifts in an
        (x, y) plane.
    '''
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def norm(self):
        return sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    def translate_by(self, other):
        '''
            We can compose Translation's by adding together the x, y, and z shifts.

            :param other The other translation to add.

            :return The combined effect of translating by this object and the other.
        '''
        return Translation(self.x + other.x, self.y + other.y, self.z + other.z)

    def rotate_by(self, rotation):
        '''
            We can also rotate Translation's. See:
                https://en.wikipedia.org/wiki/Rotation_matrix

            :param rotation The rotation to apply.

            :return This translation rotated by rotation.
        '''
        x = self.x
        y = self.y
        z = self.z
        theta = rotation.theta
        phi = rotation.phi

        x_prime = x * cos(phi) - y * sin(phi)
        y_prime = x * cos(theta) * sin(phi) + y * cos(theta) * cos(phi) - z * sin(theta)
        z_prime = x * sin(theta) * sin(phi) + y * sin(theta) * cos(phi) + z * cos(theta)
        return Translation(x_prime, y_prime, z_prime)

    def inverse(self):
        '''
            The inverse simply means a Translation that "undoes" this object.

            :return Translation by -x, -y, -z.
        '''
        return Translation(-self.x, -self.y, -self.z)

    def interpolate(self, other, x):
        if x <= 0:
            return copy.deepcopy(self)
        elif x >= 1:
            return copy.deepcopy(other)

        return Translation(x * (other.x - self.x) + self.x,
                           x * (other.y - self.y) + self.y,
                           x * (other.z - self.x) + self.z)

    def extrapolate(self, other, x):
        return Translation(x * (other.x - self.x) + self.x,
                           x * (other.y - self.y) + self.y,
                           x * (other.z - self.z) + self.z)

    def __add__(self, other):
        return Translation(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Translation(self.x - other.x, self.y - other.y, self.z - other.z)

    def __iadd__(self, other):
        return Translation(self.x + other.x, self.y + other.y, self.z + other.z)

    def __isub__(self, other):
        return Translation(self.x - other.x, self.y - other.y, self.z - other.z)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __ne__(self, other):
        return self.x != other.x or self.y != other.y or self.z != other.z

    def __str__(self):
        return "(x: {0:0.0000f} in, y: {1:0.0000f} in, z: {2:0.0000f} in)".format(self.x.to(Distance.inch),
                                                                                  self.y.to(Distance.inch),
                                                                                  self.z.to(Distance.inch))

    __repr__ = __str__
