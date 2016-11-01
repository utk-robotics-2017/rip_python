from ...vision.target_detector import TargetDetector
from .target_tracker import TargetTracker


class TurretController(Looper):
    SCANNING_MODE_INCREASING = 0
    SCANNING_MODE_DECREASING = 1

    constants = Constants()
    kScanningOffset = Angle(constants.constants.turret.scanning_offset, Angle.deg)
    kSoftMinYawAngle = Angle(constants.constants.turret.soft_min_yaw_degrees, Angle.deg)
    kSoftMaxYawAngle = Angle(constants.constants.turret.soft_max_yaw_degrees, Angle.deg)
    kCenterPitch = Angle(constants.constants.turret.pitch_center_degrees, Angle.deg)
    kAutoAimMinRange = Distance(constants.constants.turret.auto_min_range_inches, Distance.inch)
    kAutoAimMaxRange = Angle(constants.constants.turret.auto_min_range_inches, Distance.inch)

    def __init__(self, turret, robot_state, camera):
        Looper.__init__(self)
        self.turret = turret
        self.turret_state = TurretState(robot_state)
        self.target_tracker = TargetTracker()
        self.vision = TargetDetector(camera)
        self.has_fired = False
        self.turret_manual_setpoint = None

    def start(self):
        self.pstart()

    def set_manual(self, yaw=None, pitch=None, speed=None):
        if hasattr(self, 'p'):
            self.pipe.send({'yaw': yaw, 'pitch': pitch, 'speed': speed})
            return
        self.turret_manual_setpoint = {'yaw': yaw, 'pitch': pitch, 'speed': speed}

    def fire(self, continuous=False):
        if hasattr(self, 'p'):
            if continuous:
                self.pipe.send('continuous_fire')
            else:
                self.pipe.send('fire')
            return

        self.continuous = continuous
        if self.kInstantFire:
            while True:
                self.turret.fire()
        else:
            self.wants_to_fire = True

    def on_tloop(self):
        timestamp, targets = self.vision.process_image()
        vision_update = []
        for target in targets:
            # Coordinate frame:
            # +x is out the camera's optical axis
            # +y is to the left of the image
            # +z is to the top of the image
            # We assume the x component of all targets is +1.0 (since this is homogeneous)
            vision_update.append({'x': 1,
                                  'y': -(target['cx'] - self.kCenterColumn) / self.kFocalLengthPixels,
                                  'z': (target['cy'] - self.kCenterRow) / self.kFocalLengthPixels})
        self.turret_state.add_vision_update(timestamp, vision_update)
        self.auto_aim(self.timer.get(), True)
        if self.ready_to_fire() and self.wants_to_fire:
            self.turret.fire()
            if not self.continuous:
                self.wants_to_fire = False

    def on_pstart(self):
        self.tstart()

    def on_ploop(self, message):
        if message == 'fire':
            self.fire()
        elif message == 'continuous_fire':
            self.fire(True)
        elif isinstance(message, dict):
            if 'yaw' in message:
                self.set_manual(yaw=message['yaw'], pitch=message['pitch'], speed=message['speed'])

    def auto_aim(self, now, allow_changing_tracks):
        aiming_parameters = self.turret_state.get_current_aiming_parameters(now, self.current_track_id)
        if(len(aiming_parameters) == 0 and (allow_changing_tracks or self.turret_manual_setpoint is None)):
            # Manual Position setting
            if self.turret_manual_setpoint is not None:
                self.turret.set(yaw=self.turret_manual_setpoint['yaw'],
                                pitch=self.turret_manual_setpoint['pitch'],
                                speed=self.turret_manual_setpoint['speed'])
            else:
                # Scanning mode
                current_yaw = self.turret.get_yaw()
                if self.scanning_mode == self.SCANNING_MODE_INCREASING:
                    desired_yaw = current_yaw + self.kScanningOffset
                    if desired_yaw >= self.kSoftMaxTurretAngle:
                        desired_yaw = self.kSoftMaxTurretAngle
                        self.scanning_mode = self.SCANNING_MODE_DECREASING
                else:
                    desired_yaw = current_yaw - self.kScanningOffset
                    if desired_yaw <= self.kSoftMinTurretAngle:
                        desired_yaw = self.kSoftMinTurretAngle
                        self.scanning_mode = self.SCANNING_MODE_INCREASING
                self.turret.set(yaw=desired_yaw, pitch=self.kCenterPitch)
        else:
            # Pick the target to aim at
            has_target = False
            for param in aiming_parameters:
                if(param['yaw'] >= self.kSoftMinTurretAngle and
                   param['yaw'] <= self.kSoftMaxTurretAngle and
                   param['range'] >= self.kAutoAimMinRange and
                   param['range'] <= self.kAutoAimMaxRange and
                   (allow_changing_tracks or self.current_track_id == param['track_id'])):
                    # This target works
                    self.turret.set(yaw=param['yaw'], pitch=param['pitch'], speed=['speed'])
                    self.current_track_id = param['track_id']
                    has_target = True
                    break
            if not has_target:
                self.current_track_id = -1

    def ready_to_fire(self, now):
        if self.turret.on_target():
            self.consecutive_cycles_on_target += 1
        else:
            self.consecutive_cycles_on_target = 0
        return self.consecutive_cycles_on_target > self.kAutoAimMinConsecutiveCyclesOnTarget
