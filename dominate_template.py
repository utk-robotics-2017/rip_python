# Python modules
# import time
import logging
# import argparse
import json
import time
from threading import Thread

# Local modules
from head.spine.core import get_spine
from head.spine.ourlogging import setup_logging
from head.spine.simulation.physics_core import PhysicsInterface
from head.spine.simulation.physics_core import PhysicsEngine
from head.spine.simulation.sim_time import SimTime

setup_logging(__file__)
logger = logging.getLogger(__name__)


class get_robot:
    def __init__(self, sim=False):
        self.sim = sim

    def __enter__(self):
        self.gs = get_spine(sim=self.sim)
        self.r = Robot(self.gs.__enter__(), self.sim)
        return self.r

    def __exit__(self, type, value, traceback):
        self.gs.__exit__(type, value, traceback)
        self.r.finish()


class Robot:
    def __init__(self, s, sim):
        self.s = s
        self.sim = sim
        self.sim_time = SimTime()

        if sim:
            with open("/Robot/robot.json") as robot_json:
                robot_sim_config = json.loads(robot_json)
            self.physics_interface = PhysicsInterface(robot_sim_config)
            self.physics_engine = PhysicsEngine(self.physics_interface)
            appendage_dict = self.s.get_appendages()
            self.physics_interface._set_starting_hal(appendage_dict)
            self.sim_thread = Thread(target=self.simulate, name="Simulation Thread", args=())
            self.sim_thread.start()

    def start(self):
        pass

    def simulate(self):
        self.sim_stopped = False
        while(True):
            self.physics_interface._on_increment_time(self.sim_time.get())
            time.sleep(0.01)

    def sim_stop(self):
        self.sim_stopped = True

    def finish(self):
        if self.sim:
            self.sim_stop()
            self.sim_thread.join(5)
            if self.sim_thread.is_alive():
                self.sim_thread.terminate()

if __name__ == "__main__":
    with get_robot(True) as bot:
        bot.start()
