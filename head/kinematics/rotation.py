import copy
from ..units import Angle


class Rotation:
    '''
        A rotation in a 2d coordinate frame represented a point on the unit circle
        (cosine and sine).

        Inspired by Sophus (https://github.com/strasdat/Sophus/tree/master/sophus)
    '''
    kEpsilon = 1E-9

    def __init__(self, theta, phi=Angle(0, Angle.degrees)):
        self.theta = theta
        self.phi = phi

    def rotate_by(self, other):
        '''
            We can rotate this Rotation by adding together the effects of it and
            another rotation.

            :param other The other rotation. See:
                    https://en.wikipedia.org/wiki/Rotation_matrix
            :return This rotation rotated by other.
        '''
        self.theta += other.theta
        self.phi += other.phi

    def inverse(self):
        '''
            The inverse of a Rotation2d "undoes" the effect of this rotation.

            :return The opposite of this rotation.
        '''
        return Rotation(-self.theta, -self.phi)

    def interpolate(self, other, x):
        if x <= 0:
            return copy.deepcopy(self)
        elif x >= 1:
            return copy.deepcopy(other)

        theta_diff = other.theta - self.theta
        phi_diff = other.phi - self.phi
        return Rotation(theta_diff * x + self.theta, phi_diff * x + self.phi)

    def __add__(self, other):
        return Rotation(self.theta + other.theta, self.phi + other.phi)

    def __sub__(self, other):
        return Rotation(self.theta - other.theta, self.theta - other.phi)

    def __eq__(self, other):
        return self.theta == other.theta and self.phi == other.phi

    def __ne__(self, other):
        return self.theta != other.theta or self.phi != other.phi

    def __iadd__(self, other):
        return Rotation(self.theta + other.theta, self.phi + other.phi)

    def __isub__(self, other):
        return Rotation(self.theta - other.theta, self.theta - other.phi)

    def __str__(self):
        return "(theta: {0:0.000f} deg, phi: {1:0.000f} deg)".format(self.theta.to(Angle.degree),
                                                                     self.phi.to(Angle.degree))

    __repr__ = __str__
