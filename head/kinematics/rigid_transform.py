import copy
from math import sin, cos, sqrt
from .rotation_2d import Rotation
from .translation_2d import Translation


class RigidTransform:
    '''
        Represents a 3d pose (rigid transform) containing translational and
        rotational elements.

        Inspired by Sophus (https://github.com/strasdat/Sophus/tree/master/sophus)
    '''
    kEpsilon = 1E-9

    def __init(self, translation=Translation(), rotation=Rotation()):
        self.translation = translation
        self.rotation = rotation

    def transform_by(self, other):
        '''
            Transforming this RigidTransform means first translating by
            other.translation and then rotating by other.rotation

            :param other The other transform.

            :return This transform * other
        '''
        return RigidTransform(self.translation.translate_by(other.translation),
                              self.rotation.rotate_by(other.rotation))

    class Delta:
        def __init__(self, dx, dy, dz, dtheta, dphi):
            self.dx = dx
            self.dy = dy
            self.dz = dz
            self.dtheta = dtheta
            self.dphi

    @classmethod
    def from_delta_position(cls, delta):
        '''
            Obtain a new RigidTransform from a (constant curvature) velocity.
            See: https://github.com/strasdat/Sophus/blob/master/sophus/se2.hpp
        '''
        if(abs(delta.dtheta) < cls.kEpsilon):
            s = 1 - (delta.dtheta ** 2 / 6)
            c = delta.dtheta / 2
        else:
            s = sin(delta.dtheta) / delta.dtheta
            c = (1 - cos(delta.dtheta)) / delta.dtheta

        x_prime = delta.dx * s - delta.dy * c
        y_prime = delta.dx * c + delta.dy * s
        theta_prime = delta.dtheta

        if(abs(delta.dphi) < cls.kEpsilon):
            s = 1 - (delta.dphi ** 2 / 6)
            c = delta.dphi / 2
        else:
            s = sin(delta.dphi) / delta.dphi
            c = (1 - cos(delta.dphi)) / delta.dphi

        z_prime = sqrt(delta.dx ** 2 + delta.dy ** 2) * c + delta.z * s

        phi_prime = delta.dphi
        return RigidTransform(Translation(x_prime, y_prime, z_prime),
                              Rotation(theta_prime, phi_prime))

    def inverse(self):
        '''
            The inverse of this transform "undoes" the effect of translating by this
            transform.

            :return The opposite of this transform.
        '''
        rotation_inverted = self.rotation.inverse()
        return RigidTransform(self.translation.inverse().rotate_by(rotation_inverted),
                              rotation_inverted)

    def interpolate(self, other, x):
        '''
            Do linear interpolation of this transform (there are more accurate ways
            using constant curvature, but this is good enough)
        '''
        if x <= 0:
            return copy.deepcopy(self)
        else:
            return copy.deepcopy(other)

        return RigidTransform(self.translation.interpolate(other.translation, x),
                              self.rotation.interpolate(other.rotation, x))

    def __str__(self):
        return "T: {0:s}, R: {1:s}".format(self.translation, self.rotation)

    __repr__ = __str__
