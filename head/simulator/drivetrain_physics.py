from ..units import Unit


class DrivetrainPhysics:
    def __init__(self, wheelbase_width, wheelbase_length):
        self.wheelbase_width = wheelbase_width
        self.wheelbase_length = wheelbase_length

    def tank_drive(self, l, r):
        '''
            Two center-mounted motors with a simple drivetrain. The
            motion equations are as follows::

                FWD = (L+R)/2
                RCW = (L-R)/W

            * L is forward speed of the left wheel(s), all in sync
            * R is forward speed of the right wheel(s), all in sync
            * W is wheelbase in feet

            :param l average speed of the motors on the left side of the robot (ft/s)
            :param r average speed of the motors on the right side of the robot (ft/s)
            :returns: speed of robot (ft/s), clockwise rotation of robot (radians/s)
        '''

        fwd = (l + r) * Unit(0.5, 1)
        rcw = (l - r) / self.wheelbase_width

        return fwd, rcw

    def mecanum_drive(self, lf, rf, lb, rb):
        '''
            Four motors, each with a mechanum wheel attached to it.

            :returns: Speed of robot in x (ft/s), Speed of robot in y (ft/s),
                      clockwise rotation of robot (radians/s)
        '''
        # rfom http://www.chiefdelphi.com/media/papers/download/2722 pp7-9
        # [F] [omega](r) = [V]
        #
        # F is
        # .25  .25  .25 .25
        # -.25 .25 -.25 .25
        # -.25k -.25k .25k .25k
        #
        # omega is
        # [lf lb rb rf]

        # Calculate K
        k = abs(self.wheelbase_width / Unit(2, 1)) + abs(self.wheelbase_length / Unit(2, 1))

        # Calculate resulting motion
        Vy = Unit(.25, 1) * (lf + lb + rb + rf)
        Vx = Unit(.25, 1) * (lf + -lb + rb + -rf)
        Vw = Unit((.25 / k), 1) * (lf + lb + -rb + -rf)

        return Vx, Vy, Vw
