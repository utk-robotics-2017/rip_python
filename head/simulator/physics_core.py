import math
import sys
import os
from drivetrain_physics import DrivetrainPhysics
sys.path.append(("/").join(os.path.abspath(__file__).split("/")[:-3]))
from head.units import Unit, Length, Velocity
from ..spine.appendage.four_wheel_drive import FourWheelDrive

class PhysicsEngine:

    '''
        An instance of this is passed to the constructor of your
        :class:`PhysicsEngine` object. This instance is used to communicate
        information to the simulation, such as moving the robot on the
        field displayed to the user.
    '''
    def __init__(self, config):
        self.vx = 0
        self.vy = 0

        self.x = config['simulation']['starting_x']
        self.y = config['simulation']['starting_y']
        self.angle = config['simulation']['starting_angle']

        self.config = config
        self.drivetrain_type = config['drivetrain']['type']
        wheelbase_width = config['drivetrain']['wheelbase_width']
        wheelbase_length = config['drivetrain']['wheelbase_length']
        self.drivetrain_physics = DrivetrainPhysics(wheelbase_width, wheelbase_length)

    def update_sim(self, hal_data, now, tm_diff):
        '''
            Called when the simulation parameters for the program need to be
            updated.

            :param hal_data: A giant dictionary that has all data about the robot.

            :param now: The current time
            :type  now: float

            :param tm_diff: The amount of time that has passed since the last
                            time that this function was called
            :type  tm_diff: float
        '''

        # setup
        left = hal_data['fwd']['right_velocity']
        right = hal_data['fwd']['left_velocity']

        # drive simulator
        f_vel, a_vel = self.drivetrain_physics.tank_drive(left, right)
        self.drive(f_vel, a_vel, tm_diff)

        pass

    def _on_increment_time(self, now):
        last_tm = self.last_tm

        if last_tm is None:
            self.last_tm = now
        else:
            # When using time, always do it based on a differential! You may
            # not always be called at a constant rate
            tm_diff = now - last_tm

            self.engine._collect_hal()

            # Don't run physics calculations more than 100hz
            if tm_diff > 0.010:
                self.engine.update_sim(self.hal_data, now, tm_diff)

    def update_sim(self, now, tm_diff):
        '''
            Called when the simulation parameters for the program need to be
            updated.

            :param now: The current time
            :type  now: float

            :param tm_diff: The amount of time that has passed since the last
                            time that this function was called
            :type  tm_diff: float
        '''
        pass

    def _set_starting_hal(self, appendages):
        self.appendages = appendages
        sim_appendages = self.config['simulation']['appendages']
        for label, sim_vars in iter(sim_appendages.items()):
            for sim_var_name, sim_var_start_value in iter(sim_vars.items()):
                self.appendages[label].__dict__[sim_var_name] = Unit(sim_var_start_value, 1)

    def drive(self, speed, rotation_speed, tm_diff):
        '''
            Call this from your :func:`PhysicsEngine.update_sim` function.
            Will update the robot's position on the simulation course.

            You can either calculate the speed & rotation manually, or you
            can use the predefined functions in :class:`DrivetrainPhysics`.

            .. note:: The simulator currently only allows 2D motion

            :param speed:           Speed of robot in ft/s
            :param rotation_speed:  Clockwise rotational speed in radians/s
            :param tm_diff:         Amount of time speed was traveled (this is the
                                    same value that was passed to update_sim)
        '''
        distance = speed * tm_diff
        angle = rotation_speed * tm_diff

        x = distance * math.cos(angle)
        y = distance * math.sin(angle)

        self._move(x, y, angle)

    def vector_drive(self, vx, vy, vw, tm_diff):
        '''
            Call this from your :func:`PhysicsEngine.update_sim` function.
            Will update the robot's position on the simulation course.

            This moves the robot using a vector relative to the robot
            instead of by speed/rotation speed.

            :param vx: Speed in x direction relative to robot in ft/s
            :param vy: Speed in y direction relative to robot in ft/s
            :param vw: Clockwise rotational speed in rad/s
            :param tm_diff:         Amount of time speed was traveled
        '''

        angle = vw * tm_diff
        vx = (vx * tm_diff)
        vy = (vy * tm_diff)

        x = vx * math.sin(angle) + vy * math.cos(angle)
        y = vx * math.cos(angle) + vy * math.sin(angle)

        self._move(x, y, angle)

    def _move(self, x, y, angle):
        # x, y, and angle are all relative to the robot
        with self._lock:
            self.vx += x
            self.vy += y
            self.angle += angle

            c = math.cos(self.angle)
            s = math.sin(self.angle)

            self.x += (x * c - y * s)
            self.y += (x * s + y * c)

    def get_position(self):
        '''
            :returns: Robot's current position on the course as `(x,y,angle)`.
                      `x` and `y` are specified in feet, `angle` is in radians
        '''
        with self._lock:
            return self.x, self.y, self.angle

    def _get_vector(self):
        '''
            :returns: The sum of all movement vectors, not very useful
                      except for getting the difference of them
        '''
        return self.vx, self.vy, self.angle
