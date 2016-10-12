from ..constants import Constants
from ..units import Distance, Velocity, AngularVelocity
from .rigid_transform import RigidTransform


class DriveTrainKinematics:
    '''
        Provides forward and inverse kinematics equations for the robot modeling the
        wheelbase as a differential drive.
    '''
    kEpsilon = 1E-9
    constants = Constants()
    kScrubFactor = constants.drivetrain.scrub_factor
    kTrackEffectiveDiameter = Distance(constants.drivetrain.track_effective_diametere, Distance.inch)

    @classmethod
    def forward_kinematics(cls, left_delta, right_delta, rotation_delta=None):
        '''
            Forward kinematics using encoders and possibly gyro.
            if gyro is not used then rotation is implicit
        '''
        linear_velocity = (left_delta + right_delta) / 2
        if rotation_delta is None:
            delta_v = (left_delta - right_delta) / 2
            rotation_delta = delta_v * 2 * cls.kTrackScrubFactor / cls.kTrackEffectiveDiameter
        return RigidTransform.Delta(linear_velocity, Velocity(0, 1), Velocity(0, 1),
                                    rotation_delta, AngularVelocity(0, 1))

    @classmethod
    def integrate_forward_kinematics(cls, current_pose, left_delta, right_delta, current_heading):
        '''
            Append the result of forward kinematics to a previous pose.
        '''
        with_gyro = DriveTrainKinematics.forward_kinematics(left_delta, right_delta,
                                                            current_pose.get_rotation().inverse()
                                                            .rotate_by(current_heading).theta)
        return current_pose.transform_by(RigidTransform.from_delta_position(with_gyro))

    class DriveVelocity:
        def __init__(self, left, right):
            self.left = left
            self.right = right

    @classmethod
    def inverse_kinematics(cls, velocity):
        if(abs(velocity.dtheta) < DriveTrainKinematics.kEpsilon):
            return DriveTrainKinematics.DriveVelocity(velocity.dx, velocity.dx)
        delta_v = cls.kTrackEffectiveDiameter * velocity.dtheta / (2 * cls.kTrackScrubFactor)
        return DriveTrainKinematics.DriveVelocity(velocity.dx - delta_v, velocity.dx + delta_v)
