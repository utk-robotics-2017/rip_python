import math
from threading import Lock

from .drivetrain_physics import DrivetrainPhysics
from ..spine.appendages.four_wheel_drive import FourWheelDrive
from ..units import *

from ..spine.ourlogging import Logger

logger = Logger()


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

        self.x = Distance(config['simulation']['starting_x'], Distance.inch)
        self.y = Distance(config['simulation']['starting_y'], Distance.inch)
        self.angle = Angle(config['simulation']['starting_angle'], Angle.degree)

        self.config = config
        self.drivetrain_type = config['drivetrain']['type']
        wheelbase_width = Length(config['drivetrain']['wheelbase_width'], Length.inch)
        wheelbase_length = Length(config['drivetrain']['wheelbase_length'], Length.inch)
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
            if tm_diff > Time(0.010, Time.s):
                self.update_sim(now, tm_diff)
                self.last_tm = now

    def update_dependencies(self):
        for appendage in self.appendages.values:
            dependencies = appendage.get_dependency_update()
            if dependencies is not None:
                self.update_dependency(dependencies)

    def update_dependency(self, dependencies):
        for label in dependencies.keys():
            for key, value in iter(dependencies[label].items()):
                self.appendages[label].__dict__[key] = value
            dependency = self.appendages[label].get_dependency_update()
            if dependency is not None:
                self.update_dependency(dependency)

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
        self.update_dependencies()
        for appendage in self.appendages.values():
            appendage.sim_update(self.hal_data, tm_diff)
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

    def get_hal_data_update(self):
        hal_data = {}
        for label, appendage in iter(self.appendages.items()):
            hal_data[label] = appendage.get_hal_data()
        hal_data['robot']['x'] = self.x
        hal_data['robot']['y'] = self.y
        hal_data['robot']['angle'] = self.angle
        if hasattr(self, 'hal_data'):
            for label in self.hal_data.keys():
                del_list = []
                for sim_variable, sim_value in iter(hal_data[label].items()):
                    if self.hal_data[label][sim_variable] == sim_value:
                        del_list.append(sim_variable)
                for d in del_list:
                    del self.hal_data[label][d]
            del_list = []
            for label in self.hal_data.keys():
                if hal_data[label] is None:
                    del_list.append(label)
            for d in del_list:
                del hal_data[d]
            for label in hal_data:
                for sim_variable in hal_data[label]:
                    self.hal_data[label][sim_variable] = hal_data[label][sim_variable]
            return hal_data
        else:
            self.hal_data = hal_data
            return hal_data

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
        x = distance * Constant(math.cos(angle.to(Angle.radian)))
        y = distance * Constant(math.sin(angle.to(Angle.radian)))

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

        x = vx * Constant(math.sin(angle.to(Angle.radian))) + vy * Constant(math.cos(angle.to(Angle.radian)))
        y = vx * Constant(math.cos(angle.to(Angle.radian))) + vy * Constant(math.sin(angle.to(Angle.radian)))

        self._move(x, y, angle)

    def _move(self, x, y, angle):
        if self.navx is not None:
            self.navx.set_angle(angle)

        # x, y, and angle are all relative to the robot
        with self._lock:
            self.vx += x
            self.vy += y
            self.angle += angle
            c = Constant(math.cos(self.angle.to(Angle.radian)))
            s = Constant(math.sin(self.angle.to(Angle.radian)))

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
