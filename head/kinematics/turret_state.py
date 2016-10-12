from math import atan2, sqrt, sin, cos
from .rotation import Rotation
from .translation import Translation
from .rigit_transform import RigidTransform
from .interpolatable import InterpolatingMap, InterpolatingDouble
from ..vision.target_tracker import TargetTracker
from ..units import Angle, Distance, Time
from ..constants import Constants


class TurretState:
    '''
        TurretState builds off of robot state and keeps track of the poses of various coordinate
        frames throughout the match. A coordinate frame is simply a point and direction in space
        that defines an (x,y) coordinate system. Transforms (or poses) keep track of the
        spatial relationship between different frames.

        Robot frames of interest (from parent to child):

        1. Turret fixed frame: origin is the center of the turret when the turret is
        at 0 degrees rotation relative to the vehicle frame (kept track of in `RobotState`)

        2. Turret rotating frame: origin is the center of the turret as it rotates

        3. Camera frame: origin is the center of the camera imager as it rotates with
        the turret

        6. target frame: origin is the center of the target (note that orientation in
        this frame is arbitrary). Also note that there can be multiple target frames.

        As a kinematic chain with 4 frames, there are 4 transforms of interest:

        1. Vehicle-to-turret-fixed: This is a constant.

        2. Vehicle-to-turret-rotating: This is a pure rotation, and is tracked over
        time using the turret encoder.

        3. Turret-rotating-to-camera: This is a constant.

        4. Camera-to-target: This is a pure translation, and is measured by the vision
        system.
    '''
    def __init__(self, robot_state=None, vehicle_to_turret=None, turret_rotating_to_camera=None):
        if robot_state is not None:
            self.robot_state = robot_state
        if vehicle_to_turret is not None:
            self.vehicle_to_turret = vehicle_to_turret
        if turret_rotating_to_camera is not None:
            self.turret_rotating_to_camera = turret_rotating_to_camera
        if not hasattr(self, 'instance'):
            self.reset(0, Rotation())
            constants = Constants()
            self.self.kObservationBufferSize = constants.constants.robot_state.observation_buffer_size
            # Camera
            self.kCameraPitchAngle = Angle(constants.constants.camera.frame.pitch_angle_degrees, Angle.degree)
            self.kCameraYawAngle = Angle(constants.constants.camera.frame.yaw_angle_degrees, Angle.degree)
            self.kCameraXOffset = Distance(constants.constants.camera.frame.x_offset_inches, Distance.inch)
            self.kCameraYOffset = Distance(constants.constants.camera.frame.y_offset_inches, Distance.inch)
            self.kCameraZOffset = Distance(constants.constants.camera.frame.z_offset_inches, Distance.inch)
            self.kCameraDeadband = constants.constants.camera.deadband

            # Turret
            self.kTurretXOffset = Distance(constants.constants.turret.frame.x_offset_inches, Distance.inch)
            self.kTurretYOffset = Distance(constants.constants.turret.frame.y_offset_inches, Distance.inch)
            self.kTurretAngleOffset = Angle(constants.constants.turret.frame.angle_offset_degrees, Angle.degree)

            self.kVehicleToTurretFixed = RigidTransform(Translation(self.kTurretXOffset, self.kTurretYOffset),
                                                        Rotation(self.kTurretAngleOffset))

            self.kTurretRotatingToCamera = RigidTransform(Translation(self.kCameraXOffset, self.kCameraYOffset),
                                                          Rotation())
            # Target Tracker
            self.kCenterOfTargetHeight = constants.constants.target_tracker.center_of_target_height_inches
            self.kMaxTargetAge = Time(constants.constants.target_tracker.max_target_age_seconds, Time.s)
        self.instance = True

    def reset(self, start_time, initial_turret_rotation):
        self.turret_rotation = InterpolatingMap(self.kObservationBufferSize)
        self.turret_rotation.put(InterpolatingDouble(start_time), initial_turret_rotation)
        self.target_tracker = TargetTracker()
        self.camera_pitch_correction = Rotation(-self.kCameraPitchAngleDegrees)
        self.camera_yaw_correction = Rotation(-self.kCameraYawAngleDegrees)
        self.differential_height = self.kCenterOfTargetHeight - self.kCameraZOffset

    def get_turret_rotation(self, timestamp):
        return self.turret_rotation.get_interpolated(InterpolatingDouble(timestamp))

    def get_latest_turret_rotation(self):
        return self.turret_rotation.last_entry()

    def get_field_to_turret_rotated(self, timestamp):
        return (self.robot_state.get_field_to_vehicle(timestamp)
                .transform_by(self.kVehicleToTurretFixed).
                transform_by(RigidTransform(Translation(),
                                            self.turret_rotation.get_interpolated(InterpolatingDouble(timestamp)))))

    def get_field_to_camera(self, timestamp):
        return self.get_field_to_turret_rotated(timestamp).transform_by(self.kTurretRotatingToCamera)

    def get_capture_time_field_to_target(self):
        rv = []
        for report in self.target_tracker.get_tracks():
            rv.append(RigidTransform(report.field_to_target, Rotation()))
        return rv

    def get_aiming_parameters(self, current_timestamp, comparator):
        rv = []
        reports = self.target_tracker.get_tracks()
        reports.sort(key=comparator)

        # turret fixed (latest) -> vehicle (latest) -> field
        latest_turret_fixed_to_field = self.robot_state.get_predicted_field_to_vehicle(
            self.kAutoAimPredictionTime).transform_by(self.kVehicleToTurretFixed).inverse()
        for report in reports:
            if current_timestamp - report.latest_timestamp > self.kMaxTargetAge:
                continue

            # turret fixed (latest) -> vehicle (latest) -> field -> targets
            latest_turret_fixed_to_target = latest_turret_fixed_to_field.transform_by(
                RigidTransform(report.field_to_target, Rotation()))

            # We can actually disregard the angular portion of this pose. It is
            # the bearing that we care about!
            rv.add(ShooterAimingParameters(latest_turret_fixed_to_target.get_translation().norm(),
                                           Rotation(latest_turret_fixed_to_target.get_translation().get_x(),
                                                    latest_turret_fixed_to_target.get_translation().get_y(), True),
                                           report.id))
        return rv

    def add_turret_rotation_observation(self, timestamp, observation):
        self.turret_rotation.put(InterpolatingDouble(timestamp), observation)

    def add_vision_update(self, timestamp, vision_update):
        field_to_targets = []
        field_to_camera = self.get_field_to_camera(timestamp)
        if vision_update is not None and len(vision_update) > 0:
            for target_info in vision_update:
                if target_info.get_y() > -self.kCameraDeadband and target_info.get_y() < self.kCameraDeadband:
                    ydeadband = 0
                else:
                    ydeadband = target_info.get_y()

                # Compensate for camera yaw
                xyaw = (target_info.get_x() * cos(self.camera_yaw_correction.to(Angle.radian)) +
                        ydeadband * sin(self.camera_yaw_correction.to(Angle.radian)))
                yyaw = (ydeadband * cos(self.camera_yaw_correction.to(Angle.radian)) -
                        target_info.get_x() * sin(self.camera_yaw_correction.to(Angle.radian)))
                zyaw = target_info.get_z()

                # Compensate for camera pitch
                xr = (zyaw * sin(self.camera_pitch_correction.to(Angle.radian)) +
                      xyaw * cos(self.camera_pitch_correction.to(Angle.radian)))
                yr = yyaw
                zr = (zyaw * cos(self.camera_pitch_correction.to(Angle.radian)) -
                      xyaw * sin(self.camera_pitch_correction.to(Angle.radian)))

                # find intersection with the target
                if zr > 0:
                    scaling = self.differential_height / zr
                    distance = sqrt(xr ** 2 + yr ** 2) * scaling
                    angle = Rotation(atan2(yr, xr))
                    field_to_targets.append(field_to_camera.transform_by(
                        RigidTransform(Translation(distance * cos(angle.to(Angle.radian)),
                                                   distance * sin(angle.to(Angle.radian))),
                                       Rotation())).get_translation())
        self.target_tracker.update(timestamp, field_to_targets)

    def reset_vision(self):
        self.target_tracker.reset()
