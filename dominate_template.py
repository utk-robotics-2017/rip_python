# Python modules
# import time
import logging
# import argparse
import json
import time
# import socket
from threading import Thread
# from smbus import SMBus

# Local modules
from head.spine.core import get_spine
from head.spine.ourlogging import setup_logging
from head.simulator.physics_engine import PhysicsEngine
from head.simulator.sim_navx import SimNavX
from head.simulator.sim_camera import SimCamera
from head.timer import Timer
from head.navigation.navx_python.navx import get_navx
from head.units import *
from head.navigation.tank import TankDrive
# from head.navigation.mecanum import MecanumDrive

setup_logging(__file__)
logger = logging.getLogger(__name__)


class get_robot:
    def __init__(self, sim=False, navx=False, camera=False):
        self.sim = sim
        self.navx = navx
        self.camera = camera

    def __enter__(self):
        self.gs = get_spine(devices=["fakearduino"], sim=self.sim)
        self.r = Robot(s=self.gs.__enter__(), sim=self.sim, navx=navx, camera=camera)
        return self.r

    def __exit__(self, type, value, traceback):
        self.gs.__exit__(type, value, traceback)
        self.r.finish()


class Robot:
    def __init__(self, s, sim, navx, camera):
        self.s = s
        self.sim = sim
        self.timer = Timer(sim)

        with open("/Robot/robot.json") as robot_json:
            self.robot_config = json.loads(robot_json.read())

        # Check if navx is connected and create object if it exists
        # bus = SMBus(1)

        self.navx = None
        if navx:
            if sim:
                self.navx = SimNavX()
            else:
                try:
                    bus.write_quick(0x32)
                    self.navx = get_navx()
                except:
                    logger.error("NavX not found on I2C")
                    raise Exception("NavX not found on I2C")

        self.camera = None
        if camera:
            camera_options = {}
            for option in camera.split(';'):
                parameter_split = option.split("=")
                camera_options[parameter_split[0]] = parameter_split[1]
            if sim:
                self.camera = SimCamera(**camera_options)
            else:
                self.camera = VideoStream(**camera_options)

        if sim:
            self.sim_init()

    def sim_init(self):
        self.physics_engine = PhysicsEngine(self.robot_config)
        appendage_dict = self.s.get_appendage_dict()
        self.physics_engine._set_starting_hal(appendage_dict)
        if self.navx is not None:
            self.physics_engine.add_navx(self.navx)
        '''
        if self.camera is not None:
            self.physics_engine.add_camera(self.camera)
        '''
        self.sim_thread = Thread(target=self.simulate, name="Simulation Thread", args=())
        self.sim_thread.start()

    def start(self):
        fwd = self.s.get_appendage("fwd")
        tank = TankDrive(fwd)
        tank.rotate_at_angular_velocity_for_time(AngularVelocity(1, AngularVelocity.rps), Time(4, Time.s))
        # mecanum = MecanumDrive(fwd, Unit(self.robot_config['dynamics']['max_velocity'], Velocity.inch_s))
        # mecanum.drive_velocity_cartesian(Unit(0, Velocity.inch_s), Unit(0, Velocity.inch_s),
        #                                  Unit(1, AngularVelocity.rps))
        # self.timer.sleep(Unit(4, Time.s))

    def simulate(self):
        self.sim_stopped = False

        '''
        # Set up the sockets
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((socket.gethostname(), 5000))
        self.sock.listen(1)

        client, addr = self.sock.accept()
        '''
        while(not self.sim_stopped):
            t = self.timer.get()
            self.physics_engine._on_increment_time(t)
            x, y, theta = self.physics_engine.get_position()
            print("T: {0:f}, X: {1:f}, Y: {2:f}, Theta: {3:f}".format(t.to(Time.s),
                                                                      x.to(Length.inch),
                                                                      y.to(Length.inch),
                                                                      theta.to(Angle.degree)))
            # hal_data_update = self.physics_engine.get_hal_data_update()
            # client.write(json.dumps(hal_data_update) + "\n")
            time.sleep(0.01)

    def sim_stop(self):
        self.sim_stopped = True

    def finish(self):
        if self.sim:
            self.sim_stop()
            self.sim_thread.join(5)

if __name__ == "__main__":
    # Collect command line arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-s", "--simulate", required=False, action="store_true",
                    help="Turns on simulation mode")
    ap.add_argument("-n", "--navx", required=False, action="store_true",
                    help="Turns on attempting to use navx")
    ap.add_argment("-c", "--camera", required=False,
                   help="Turns on attempting to use Camera")
    args = vars(ap.parse_args())

    if 'camera' is not args:
        args['camera'] = False

    with get_robot(sim=args['simulate'], navx=args['navx'], camera=args['camera']) as bot:
        bot.start()
