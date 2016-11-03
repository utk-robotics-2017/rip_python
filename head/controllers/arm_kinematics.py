from Vec3d import Vec3d
from math import atan2, pi, degrees, sqrt


class ArmKinematics:
    def __init__(self, s2e=4.75 * 2.54, e2w=5 * 2.54, s_pos=Vec3d(0, -4.6, 7)):
        # Shoulder to Elbow
        self.s2e = s2e

        # Elbow to Wrist
        self.e2w = e2w

        # Shoulder Position
        self.s_pos = s_pos

    def fwd_kin(self, rot):
        humerus = Vec3d(0, 0, self.s2e)
        forearm = Vec3d(0, self.e2w, 0)
        base_theta = rot[0]
        shoulder_theta = rot[1]
        elbow_theta = rot[2]
        pos = humerus.rotated_around_x(-degrees(shoulder_theta))
        pos += forearm.rotated_around_x(-degrees(elbow_theta + shoulder_theta))
        pos.rotate_around_z(-degrees(base_theta))
        pos += self.s_pos
        return pos

    def rev_kin(self, pos):
        npos = pos - self.s_pos
        # Atan2 parameters are in the reverse order from Mathematica
        base_theta = -(atan2(npos[1], npos[0]) - pi / 2)
        npos = npos.rotated_around_z(degrees(base_theta))
        y = npos[1]
        z = npos[2]

        shoulder_theta = atan2(
            (1 * (-(self.e2w ** 2 * self.s2e * y ** 2) + self.s2e ** 3 * y ** 2 + self.s2e * y ** 4 +
                  self.s2e * y ** 2 * z ** 2 - z *
                  sqrt(-(self.s2e ** 2 * y ** 2 * (self.e2w ** 4 + (-self.s2e ** 2 + y ** 2 + z ** 2) ** 2 -
                                                   2 * self.e2w ** 2 * (self.s2e ** 2 + y ** 2 +
                                                                        z ** 2)))))) / (self.s2e ** 2 * y *
                                                                                        (y ** 2 + z ** 2)),
            (1 * (-(self.e2w ** 2 * self.s2e * z) + self.s2e ** 3 * z + self.s2e * y ** 2 * z +
                  self.s2e * z ** 3 + sqrt(-(self.s2e ** 2 * y ** 2 *
                                             (self.e2w ** 4 + (-self.s2e ** 2 + y ** 2 + z ** 2) ** 2 -
                                              2 * self.e2w ** 2 * (self.s2e ** 2 + y ** 2 +
                                                                   z ** 2)))))) / (self.s2e ** 2 *
                                                                                   (y ** 2 + z ** 2)))
        elbow_theta = atan2(
            (self.e2w ** 2 + self.s2e ** 2 - y ** 2 - z ** 2) / (self.e2w * self.s2e),
            sqrt(-(self.s2e ** 2 * y ** 2 * (self.e2w ** 4 + (-self.s2e ** 2 + y ** 2 + z ** 2) ** 2 -
                                             2 * self.e2w ** 2 * (self.s2e ** 2 + y ** 2 + z ** 2)))) /
            (self.e2w * self.s2e ** 2 * y))

        return Vec3d(base_theta, shoulder_theta, elbow_theta)
