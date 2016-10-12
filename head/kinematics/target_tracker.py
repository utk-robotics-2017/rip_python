from .target_track import TargetTrack


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
            self.field_to_goal = track.get_smoothed_position()
            self.latest_timestamp = track.get_latest_timestamp()

            # The percentage of the target tracking time during which this goal has
            # been observed (0 to 1)
            self.stability = track.get_stability()
            self.id = track.get_id()

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
