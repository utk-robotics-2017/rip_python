from .target_track import TargetTrack
from ...misc.constants import Constants

class TargetTracker:
    '''
        This is used in the event that multiple targets are detected to judge all goals
        based on timestamp, stability, and continuation of previous targets (i.e. if a
        target was detected earlier and has changed locations). This allows the robot
        to make consistent decisions about which target to aim at and to smooth out
        jitter from vibration of the camera.
    '''
    class TrackReport:
        '''
            Track reports contain all of the relevant information about a given target
            track.
        '''


        def __init__(self, track):
            self.field_to_goal = track.smoothed_position
            self.latest_timestamp = track.get_latest_timestamp()

            # The percentage of the target tracking time during which this goal has
            # been observed (0 to 1)
            self.stability = track.get_stability()
            self.id = track.id

    class TrackReportComparator:
        constants = Constants()
        kStabilityWeight = constants.constants.target_tracker.track_report_comparator.stability_weight
        kAgeWeight = constants.constants.target_tracker.track_report_comparator.age_weight
        kSwitchingWeight = constants.constants.target_tracker.track_report_comparator.switching_weight
        kMaxGoalTrackAge = Time(constants.constants.target_tracker.max_goal_track_age_seconds, Time.s)
        def init(self, current_timestamp, last_track_id, track_report):
            self.score = self.kStabilityWeight * track_report.stability
            if track_report.id != last_track_id:
                self.score += self.kSwitchingWeight
            self.score += self.kAgeWeight * max(0, (self.kMaxGoalTrackAge - (current_timestamp - report.latest_timestamp)) / self.kMaxGoalTrackAge)

        def __gt__(self, other):
            return self.score > other.score

        def __lt__(self, other):
            return self.score < other.score

        def __ge__(self, other):
            return self.score >= other.score

        def __le__(self, other):
            return self.score <= other.score

        def __eq__(self, other):
            return self.score == other.score

        def __ne__(self, other):
            return self.score != other.score

    def __init__(self):
        self.current_tracks = []
        self.next_id = 0

    def reset(self):
        self.current_tracks = []

    def update(self, timestamp, field_to_goals):
        has_updated_track = False
        # Try to update existing tracks
        for target in field_to_goals:
            for track in self.current_tracks:
                if not has_updated_track:
                    if track.try_update(timestamp, target):
                        has_updated_track = True
                else:
                    track.empty_update()
        # Prune any tracks that have died
        self.current_tracks = [track for track in self.current_tracks if track.is_alive()]
        if len(self.current_tracks) == 0:
            for target in field_to_goals:
                self.current_tracks.append(TargetTrack.make_new_track(timestamp, target, self.next_id))
                self.next_id += 1

    def has_tracks(self):
        return len(self.current_tracks) > 0

    def get_tracks(self):
        rv = []
        for track in self.current_tracks:
            rv.append(TargetTracker.TrackReport(track))
        return rv
