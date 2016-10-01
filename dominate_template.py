# Python modules
# import time
import logging
# import argparse
import json
import time
import socket
from threading import Thread
# from smbus import SMBus

# Local modules
from head.spine.core import get_spine
from head.spine.ourlogging import setup_logging
from head.simulator.physics_core import PhysicsEngine
from head.timer import Timer
# from head.navigation.navx_python.navx import get_navx
from head.units import Unit, Velocity, Length, Angular, AngularVelocity, Time
from head.navigation.tank import TankDrive
from head.navigation.mecanum import MecanumDrive

setup_logging(__file__)
logger = logging.getLogger(__name__)


class get_robot:
    def __init__(self, sim=False):
        self.sim = sim

    def __enter__(self):
        self.gs = get_spine(devices=["fakearduino"], sim=self.sim)
        self.r = Robot(self.gs.__enter__(), self.sim)
        return self.r

    def __exit__(self, type, value, traceback):
        self.gs.__exit__(type, value, traceback)
        self.r.finish()


class Robot:
    def __init__(self, s, sim):
        self.s = s
        self.sim = sim
        self.timer = Timer(sim)

        with open("/Robot/robot.json") as robot_json:
            self.robot_config = json.loads(robot_json.read())

        # Check if navx is connected and create object if it exists
        # bus = SMBus(1)

        self.navx = None
        '''
        try:
            bus.write_quick(0x32)
            self.navx = get_navx()
        except:
            pass
        '''
        if sim:
            self.sim_init()

    def sim_init(self):
        self.physics_interface = PhysicsEngine(self.robot_config)
        appendage_dict = self.s.get_appendage_dict()
        self.physics_interface._set_starting_hal(appendage_dict)
        if self.navx is not None:
            self.physics_interface.add_navx(self.navx)
        self.sim_thread = Thread(target=self.simulate, name="Simulation Thread", args=())
        self.sim_thread.start()

    def start(self):
        fwd = self.s.get_appendage("fwd")
        tank = TankDrive(fwd)
        tank.rotate_at_angular_velocity_for_time(Unit(1, AngularVelocity.rps), Unit(4, Time.s))
        # mecanum = MecanumDrive(fwd, Unit(self.robot_config['dynamics']['max_velocity'], Velocity.inch_s))
        # mecanum.drive_velocity_cartesian(Unit(0, Velocity.inch_s), Unit(0, Velocity.inch_s), Unit(1, AngularVelocity.rps))
        # self.timer.sleep(Unit(4, Time.s))

    def simulate(self):
        self.sim_stopped = False
        # Set up the sockets
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(socket.gethostname(), 5000)
        self.sock.listen(1)

        client,addr = self.sock.accept()

        while(not self.sim_stopped):
            self.physics_interface._on_increment_time(self.timer.get())
            x, y, angle = self.physics_interface.get_position()
            print("X: {0:f} Y: {1:f} angle: {2:f}".format(x.to(Length.inch), y.to(Length.inch),
                                                          angle.to(Angular.rev)))
            time.sleep(0.01)

    def sim_stop(self):
        self.sim_stopped = True

    def finish(self):
        if self.sim:
            self.sim_stop()
            self.sim_thread.join(5)

if __name__ == "__main__":
    with get_robot(True) as bot:
        bot.start()
