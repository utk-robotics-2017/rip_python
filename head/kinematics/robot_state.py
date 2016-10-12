from .rigid_transform import RigidTransform
from .rotation import Rotation
from .interpolatable import InterpolatingMap, InterpolatingDouble
from .drivetrain_kinematics import DriveTrainKinematics
from ..singleton import Singleton
from ..constants import Constants
from ..units import Velocity, AngularVelocity


class RobotState(Singleton):
    '''
        RobotState keeps track of the poses of various coordinate frames throughout
        the match. A coordinate frame is simply a point and direction in space that
        defines an (x,y) coordinate system. Transforms (or poses) keep track of the
        spatial relationship between different frames.

        Robot frames of interest (from parent to child):

        1. Field frame: origin is where the robot is turned on

        2. Vehicle frame: origin is the center of the robot wheelbase, facing
        forwards

        As a kinematic chain with 2 frames, there is 1 transform of interest:

        1. Field-to-vehicle: This is tracked over time by integrating encoder and
        gyro measurements. It will inevitably drift, but is usually accurate over
        short time periods.
    '''
    _shared_state = {}

    def __init__(self):
        self.__dict__ = self.shared_state
        if not hasattr(self, 'instance'):
            self.field_to_vehicle = None
            self.vehicle_velocity = None
            constants = Constants()
            self.kObservationBufferSize = constants.constants.robot_state.observation_buffer_size
            self.reset(0, RigidTransform(), Rotation())
        self.instance = True

    def reset(self, start_time, initial_field_to_vehicle):
        self.field_to_vehicle = InterpolatingMap(self.kObservationBufferSize)
        self.field_to_vehicle.put(InterpolatingDouble(start_time), initial_field_to_vehicle)
        self.vehicle_velocity = RigidTransform.Delta(Velocity(0, 1), Velocity(0, 1), Velocity(0, 1),
                                                     AngularVelocity(0, 1), AngularVelocity(0, 0))

    def get_field_to_vehicle(self, timestamp):
        self.field_to_vehicle.get_interpolated(InterpolatingDouble(timestamp))

    def get_latest_field_to_vehicle(self):
        return self.field_to_vehicle.last_entry()

    def get_predicted_field_to_vehicle(self, lookahead_time):
        return self.get_latest_field_to_vehicle[1].transform_by(
            RigidTransform.fromVelocity(
                RigidTransform.Delta(self.vehicle_velocity.dx * lookahead_time,
                                     self.vehicle_velocity.dy * lookahead_time,
                                     0,
                                     self.vehicle_velocity.dtheta * lookahead_time,
                                     0)))

    def add_field_to_vehicle_observation(self, timestamp, observation):
        self.field_to_vehicle.put(InterpolatingDouble(timestamp), observation)

    def generate_odometry_from_sensors(self, left_encoder_delta, right_encoder_delta, gyro_angle):
        last_measurement = self.get_latest_field_to_vehicle()[1]
        return DriveTrainKinematics.integrate_forward_kinematics(last_measurement,
                                                                 left_encoder_delta,
                                                                 right_encoder_delta,
                                                                 gyro_angle)
