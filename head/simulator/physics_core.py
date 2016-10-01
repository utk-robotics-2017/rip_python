import math
import logging
from threading import Lock

from .drivetrain_physics import DrivetrainPhysics
from ..spine.appendages.four_wheel_drive import FourWheelDrive
from ..units import Unit, Length, Angular, Time

from ..spine.ourlogging import setup_logging

setup_logging(__file__)
logger = logging.getLogger(__name__)


class PhysicsEngine:
    '''
        An instance of this is passed to the constructor of your
        :class:`PhysicsEngine` object. This instance is used to communicate
        information to the simulation, such as moving the robot on the
        field displayed to the user.
    '''
    def __init__(self, config):
        self.vx = Unit(0, 1)
        self.vy = Unit(0, 1)

        self.x = Unit(config['simulation']['starting_x'], Length.inch)
        self.y = Unit(config['simulation']['starting_y'], Length.inch)
        self.angle = Unit(config['simulation']['starting_angle'], Angular.degree)

        self.config = config
        self.drivetrain_type = config['drivetrain']['type']
        wheelbase_width = Unit(config['drivetrain']['wheelbase_width'], Length.inch)
        wheelbase_length = Unit(config['drivetrain']['wheelbase_length'], Length.inch)
        self.drivetrain_physics = DrivetrainPhysics(wheelbase_width, wheelbase_length)

        self.navx = None

        self.last_tm = None
        self._lock = Lock()

    def _on_increment_time(self, now):
        last_tm = self.last_tm

        if last_tm is None:
            self.last_tm = now
        else:
            # When using time, always do it based on a differential! You may
            # not always be called at a constant rate
            tm_diff = now - last_tm

            # Don't run physics calculations more than 100hz
            if tm_diff > Unit(0.010, Time.s):
                self.update_sim(now, tm_diff)
                self.last_tm = now

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
        for appendage in self.appendages.values():
            appendage.sim_update(tm_diff)
            if isinstance(appendage, FourWheelDrive):
                if self.drivetrain_type.lower() == "tank":
                    fwd, rcw = self.drivetrain_physics.tank_drive(appendage.get_left_velocity(),
                                                                  appendage.get_right_velocity())
                    self.drive(fwd, rcw, tm_diff)
                elif self.drivetrain_type.lower() == "mecanum":
                    vx, vy, vw = self.drivetrain_physics.mecanum_drive(
                        appendage.get_left_front_velocity(),
                        appendage.get_right_front_velocity(),
                        appendage.get_left_back_velocity(),
                        appendage.get_right_back_velocity())
                    self.vector_drive(vx, vy, vw, tm_diff)

    def _set_starting_hal(self, appendages):
        self.appendages = appendages
        sim_appendages = self.config['simulation']['appendages']
        for label, sim_vars in iter(sim_appendages.items()):
            for sim_var_name, sim_var_start_value in iter(sim_vars.items()):
                self.appendages[label].__dict__[sim_var_name] = Unit(sim_var_start_value, 1)

    def add_navx(self, navx):
        self.navx = navx
        self.navs.set_yaw(self.angle)

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
        x = distance * Unit(math.cos(angle.to(Angular.radian)), 1)
        y = distance * Unit(math.sin(angle.to(Angular.radian)), 1)

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
        if self.navx is not None:
            self.navx.set_angle(angle)

        # x, y, and angle are all relative to the robot
        with self._lock:
            self.vx += x
            self.vy += y
            self.angle += angle
            c = Unit(math.cos(self.angle.to(Angular.radian)), 1)
            s = Unit(math.sin(self.angle.to(Angular.radian)), 1)

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
