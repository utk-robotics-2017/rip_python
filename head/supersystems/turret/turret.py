from ...vision.target_tracker_vision import TargetTrackerVision


class Turret(Looper):
    SCANNING_MODE_INCREASING = 0
    SCANNING_MODE_DECREASING = 1

    def __init__(self, turret_com, turret_state, camera):
        Looper.__init__(self)
        self.turret_com = turret_com
        self.turret_state = turret_state
        self.target_tracker = TargetTracker()
        self.vision = TargetTargetVision(camera)
        self.has_fired = False

    def set_pitch(self, pitch):
        pass

    def set_yaw(self, yaw):
        pass

    def fire(self):
        if hasattr(self, 'p'):
            self.pipe.send('fire')
            return

        if self.kInstantFire:
            self.turret_com.fire()
            self.has_fired = True
        else:
            self.has_fired = False
            self.wants_to_fire = True

    def on_tloop(self):
        pass

    def on_pstart(self):
        self.tstart()

    def on_ploop(self, message):
        if message == 'fire':
            self.fire()

    def auto_aim(self, now, allow_changing_tracks):
        aiming_parameters = self.get_current_aiming_parameters(now)
        if(len(aiming_parameters) == 0 and (allow_changing_tracks or self.turret_manual_setpoint is None)):
            # Manual search
            if self.turret_manual_setpoint is not None:
                self.turret_com.set_yaw(self.turret_manual_setpoint.get_turret_yaw())
                self.turret_com.set_pitch(self.turret_manual_setpoint.get_turret_pitch())
            else:
                # scanning mode
                current_yaw = self.turret_com.get_yaw()
                if self.scanning_mode == self.SCANNING_MODE_INCREASING:
                    desired_yaw = current_yaw + self.kTurretScanningOffset
                    if desired_yaw > self.kSoftMaxTurretAngle:
                        desired_yaw = self.kSoftMaxTurretAngle
                        self.scanning_mode = self.SCANNING_MODE_DECREASING
                else:
                    desired_yaw = current_yaw - self.kTurretScanningOffset
                    if desired_yaw < self.kSoftMinTurretAngle:
                        desired_yaw = self.kSoftMinTurretAngle
                        self.scanning_mode = self.SCANNING_MODE_INCREASING
                self.turret_com.set_yaw(desired_yaw)
                self.turret_com.set_pitch(self.kTurretCenterPitch)
        else:
            # Pick the target to aim at
            has_target = False
            for param in aiming_parameters:
                turret_angle = param.get_turret_angle()
                if(turret_angle >= self.kSoftMinTurretAngle and
                   turret_angle <= self.kSoftMaxTurretAngle and
                   param.get_range() >= self.kAutoAimMinRange and
                   param.get_range() <= self.kAutoAimMaxRange and
                   (allow_changing_tracks or self.current_track_id == param.get_track_id())):
                    # This target works
                    self.turret_com.set_flywheel(param.get_turret_speed())
                    self.turret_com.set_pitch(param.get_turret_pitch())
                    self.turret_com.set_yaw(param.get_turret_yaw())
                    self.current_track_id = param.get_track_id()
                    has_target = True
                    break
            if not has_target:
                self.current_track_id = -1

    def ready_to_fire(self, now):
        if self.turret_com.on_target():
            self.consecutive_cycles_on_target += 1
        else:
            self.consecutive_cycles_on_target = 0
        return self.consecutive_cycles_on_target > self.kAutoAimMinConsecutiveCyclesOnTarget
