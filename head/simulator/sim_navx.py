from ..units import *


class SimNavX:
    def __init__(self):
        self.start = False

        self.last_time_stamp = Constant(0)
        self.yaw = Constant(0)
        self.pitch = Constant(0)
        self.roll = Constant(0)
        self.compass_heading = Constant(0)

        # Linear Acceleration
        self.linear_acceleration_x = Constant(0)
        self.linear_acceleration_y = Constant(0)
        self.linear_acceleration_z = Constant(0)

        self.barometric_pressure = Constant(0)
        self.altitude = Constant(0)
        self.fused_heading = Constant(0)

        # Quaternion
        self.quaternion_w = Constant(0)
        self.quaternion_x = Constant(0)
        self.quaternion_y = Constant(0)
        self.quaternion_z = Constant(0)

        # Velocity
        self.velocity_x = Constant(0)
        self.velocity_y = Constant(0)
        self.velocity_z = Constant(0)

        # Displacement
        self.displacement_x = Constant(0)
        self.displacement_y = Constant(0)
        self.displacement_z = Constant(0)

        self.temp = Constant(0)

    def start(self):
        self.start = True

    def stop(self):
        self.start = False

    def free(self):
        self.stop()

    def get_list_time_stamp(self):
        return self.last_time_stamp

    def get_yaw(self):
        return self.yaw

    def get_pitch(self):
        return self.pitch

    def get_roll(self):
        return self.roll

    def get_compass_heading(self):
        return self.compass_heading

    def zero_yaw(self):
        self.yaw = Constant(0)

    def is_calibrating(self):
        return False

    def is_connected(self):
        return False

    def get_world_linear_accel_x(self):
        return self.linear_acceleration_x

    def get_world_linear_accel_y(self):
        return self.linear_acceleration_y

    def get_world_linear_accel_z(self):
        return self.linear_acceleration_z

    def is_moving(self):
        motion_threshold = Acceleration(0.02, Acceleration.G)
        return (self.linear_acceleration_x > motion_threshold or
                self.linear_acceleration_y > motion_threshold or
                self.linear_acceleration_z > motion_threshold)

    def is_rotating(self):
        return self.yaw_rate > Constant(0)

    def get_barometric_pressure(self):
        return self.barometric_pressure

    def get_altitude(self):
        return self.altitude

    def is_altitude_valid(self):
        return False

    def get_fused_heading(self):
        return self.fused_heading

    def is_magnetic_disturbance(self):
        return True

    def is_magnetometer_calibrated(self):
        return False

    def get_quaternion_w(self):
        return self.quaternion_w

    def get_quaternion_x(self):
        return self.quaternion_x

    def get_quaternion_y(self):
        return self.quaternion_y

    def get_quaternion_z(self):
        return self.quaternion_z

    def reset_displacement(self):
        self.displacement_x = Constant(0)
        self.displacement_y = Constant(0)
        self.displacement_z = Constant(0)

    def get_velocity_x(self):
        return self.velocity_x

    def get_velocity_y(self):
        return self.velocity_y

    def get_velocity_z(self):
        return self.velocity_z

    def get_displacement_x(self):
        return self.displacement_x

    def get_displacement_y(self):
        return self.displacement_y

    def get_displacement_z(self):
        return self.displacement_z

    def get_temp(self):
        return self.temp
