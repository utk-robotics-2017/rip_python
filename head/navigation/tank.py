import math
import logging

from ..controllers.pid_controller import PIDController
from .pathfinder_python.DistanceFollower import DistanceFollower
from ..spine.ourlogging import setup_logging
from ..units import Unit
from ..timer import Timer

setup_logging(__file__)
logger = logging.getLogger(__name__)


class TankDrive:

    def __init__(self, tank, gyro=None):
        self.tank = tank
        self.gyro = gyro
        self.timer = Timer()

    def drive_straight_voltage(self, value):
        if value == Unit(0, 1):
            self.tank.stop()
        else:
            self.tank.drive(value)

    def drive_arc_voltage(self, value, arc):
        self.tank.drive(value + arc, value - arc)

    def drive_voltage(self, left, right):
        self.tank.drive(left, right)

    def drive_straight_velocity(self, velocity):
        if(velocity == Unit(0, 1)):
            self.tank.stop()
        else:
            self.tank.drive_pid(velocity)

    def drive_arc_velocity(self, velocity, radius, cw):

        angular_velocity = velocity / radius

        if cw:
            right = angular_velocity * (radius - (self.tank.wheelbase_width / 2))
            left = angular_velocity * (radius - (self.tank.wheelbase / 2))
        else:
            left = angular_velocity * (radius - (self.tank.wheelbase_width / 2))
            right = angular_velocity * (radius - (self.tank.wheelbase_width / 2))

        self.drive_velocity(left, right)

    def drive_velocity(self, left, right):
        self.tank.drive_pid(left, right)

    def drive_straight_velocity_for_time(self, velocity, delay, stop=True):
        self.drive_straight_velocity(velocity)
        self.timer.sleep(delay)
        if stop:
            self.tank.stop()

    def drive_arc_velocity_for_time(self, velocity, radius, cw, delay, stop=True):
        self.drive_arc_velocity(velocity, radius, cw)
        self.timer.sleep(delay)
        if stop:
            self.tank.stop()

    def drive_straight_distance(self, distance, p, i, d):
        if distance == Unit(0, 1):
            self.tank.stop()
        else:
            self.tank.set_pid_type("distance")
            distance_controller = PIDController(kp=p, ki=i, kd=d,
                                                input_sources=self.tank,
                                                output_sources=self.tank)
            distance_controller.set_setpoint(distance)
            while not distance_controller.is_finnished():
                distance_controller.calculate()

    def rotate_at_angular_velocity(self, angular_velocity):
        self.tank.rotate_pid(angular_velocity, -angular_velocity)

    def rotate_at_angular_velocity_for_time(self, angular_velocity, delay, stop=True):
        self.rotate_at_angular_velocity(angular_velocity)
        self.timer.sleep(delay)
        if stop:
            self.tank.stop()

    def rotate_to_angle(self, angle, p, i, d):
        if self.gyro is not None:
            self.tank.set_pid_type("angle")
            angle_controller = PIDController(kp=p, ki=i, kd=d,
                                             input_sources=self.gyro,
                                             output_sources=self.tank)
            angle_controller.set_setpoint(angle)
            while not angle_controller.is_finished():
                angle_controller.calculate()
        elif self.tank.is_velocity_controlled():
            self.tank.set_pid_type("angle")
            angle_controller = PIDController(kp=p, ki=i, kd=d,
                                             input_sources=self.tank,
                                             output_sources=self.tank)
            angle_controller.set_setpoint(angle)
            while not angle_controller.is_finished():
                angle_controller.calculate()
        else:
            raise Exception("Can't run rotate_to_angle without sensors")
            logger.error("Can't run rotate_to_angle without sensors")

    def followTrajectory(self, left_config, left_trajectory, right_config, right_trajectory):
        left_follower = DistanceFollower(left_trajectory)
        left_follower.configurePIDVA(kp=left_config['kp'],
                                     ki=left_config['ki'],
                                     kd=left_config['kd'],
                                     kv=left_config['kv'],
                                     ka=left_config['ka'])

        right_follower = DistanceFollower(right_trajectory)
        right_follower.configurePIDVA(kp=right_config['kp'],
                                      ki=right_config['ki'],
                                      kd=right_config['kd'],
                                      kv=right_config['kv'],
                                      ka=right_config['ka'])

        while not left_follower.is_finished() or not right_follower.is_finished():
            left_input = self.tank.get_left_posiiton()
            right_input = self.tank.get_right_position()

            left_output = left_follower.calculate(left_input)
            right_output = right_follower.calculate(right_input)

            actual_angle = self.gyro.get_heading()
            desired_angle = math.degrees(left_follower.get_heading())
            angle_difference = desired_angle - actual_angle
            # TODO: figure out reason behind constant
            turn = 0.8 * (-1.0 / 80.0) * angle_difference

            self.tank.drive(left_output + turn, right_output - turn)
        self.tank.stop()
