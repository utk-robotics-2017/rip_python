import math
from ..timer import Timer
from .translation_2d import Translation2d
from ..units import Constant, Distance, Time
from ..constants import Constants


class TargetTrack:
    '''
        A class that is used to keep track of all goals detected by the vision
        system. As goals are detected/not detected anymore by the vision system,
        function calls will be made to create, destroy, or update a goal track.

        This helps in the goal ranking process that determines which goal to fire
        into, and helps to smooth measurements of the goal's location over time.
    '''
    constants = Constants()
    kMaxTrackerDistance = Distance(constants.constant.target_tracker.max_tracker_distance_inches, Distance.inch)
    kCameraFrameRate = constants.constants.camera.frame_rate
    kMaxGoalTrackAge = Time(constants.constants.target_tracker.max_goal_track_age_seconds, Time.s)

    def __init__(self):
        self.observed_positions = {}
        self.smoothed_position = None
        self.id = 0

    @staticmethod
    def make_new_track(timestamp, first_observation, id):
        '''
            Makes a new track based on the timestamp and the goal's coordinates (from vision)
        '''
        rv = TargetTrack()
        rv.observed_position[timestamp] = first_observation
        rv.id = id
        return rv

    def empty_update(self):
        self.prune_by_time()

    def try_update(self, timestamp, new_observation):
        '''
            Attempts to update the track with a new observation.

            :return True if the track was updated
        '''
        if not self.is_alive():
            return False
        distance = self.smoothed_position.inverse().translate_by(new_observation).norm()
        if(distance < self.kMaxTrackerDistance):
            self.observed_positions[timestamp] = new_observation
            self.prune_by_time()
            return True
        else:
            return False

    def is_alive(self):
        return len(self.observed_positions) > 0

    def prune_by_time(self):
        '''
            Removes the track if it is older than the set "age" described in the
            Constants file.
        '''
        delete_before = Timer.get() - self.kMaxGoalTrackAge
        delete_keys = []
        for key in self.observed_positions.keys():
            if key < delete_before:
                delete_keys.append(key)
        for key in delete_keys:
            del self.observed_positions[key]
        if len(self.observed_positions) > 0:
            self.smooth()
        else:
            self.smoothed_position = None

    def smooth(self):
        '''
            Averages out the observed positions based on an set of observed positions
        '''
        if self.is_alive():
            x = Constant(0)
            y = Constant(0)
            for value in self.observed_positions.values():
                x += value.get_x()
                y += value.get_y()
            x /= len(self.observed_positions)
            y /= len(self.observed_positions)
            self.smoothed_position = Translation2d(x, y)

    def get_smoothed_position(self):
        return self.smoothed_position

    def get_latest_timestamp(self):
        if len(self.observed_positions) > 0:
            rv = Constant(0.0)
            for key in self.observed_positions.keys():
                if key > rv:
                    rv = key
            return rv
        else:
            return Constant(0.0)

    def get_stability(self):
        return math.min(1.0, len(self.observed_positions) / (self.kCameraFrameRate * self.kMaxGoalTrackAge))

    def get_id(self):
        return self.id
