
class DrivetrainPhysics:
    def __init__(sefl, wheelbase_width, wheelbase_length):
        sefl.wheelbase_width = wheelbase_width
        sefl.wheelbase_length = wheelbase_length

    def tank_drive(sefl, l, r):
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

        fwd = (l + r) * 0.5
        rcw = (l - r) / sefl.wheelbase_width

        return fwd, rcw

    def mecanum_drive(self, fl, fr, bl, br):
        '''
            Four motors, each with a mechanum wheel attached to it.

            :returns: Speed of robot in x (ft/s), Speed of robot in y (ft/s),
                      clockwise rotation of robot (radians/s)
        '''
        # From http://www.chiefdelphi.com/media/papers/download/2722 pp7-9
        # [F] [omega](r) = [V]
        #
        # F is
        # .25  .25  .25 .25
        # -.25 .25 -.25 .25
        # -.25k -.25k .25k .25k
        #
        # omega is
        # [fl bl br fr]

        # Calculate K
        k = abs(self.wheelbase_width / 2) + abs(self.wheelbase_length / 2)

        # Calculate resulting motion
        Vy = .25 * (fl + bl + br + fr)
        Vx = .25 * (fl + -bl + br + -fr)
        Vw = (.25 / k) * (fl + bl + -br + -fr)

        return Vx, Vy, Vw
