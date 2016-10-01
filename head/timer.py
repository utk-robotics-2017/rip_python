import time
from .simulator.sim_time import SimTime
from .units import Unit, Time


class Timer:
    def __init__(self, sim=False):
        if sim:
            self.sim_time = SimTime()
        else:
            self.sim_time = None

        self.timeout = None
        self.timeout_start = None

    def get(self):
        if self.sim_time is not None:
            return Unit(self.sim_time.get(), Time.s)
        else:
            return Unit(time.time(), Time.s)

    def time(self):
        return self.get()

    def sleep(self, secs):
        if self.sim_time is not None:
            self.sim_time.increment_time_by(secs.to(Time.s))
        else:
            time.sleep(secs.to(Time.s))

    def delay(self, secs):
        self.sleep(secs)

    def set_timeout(self, timeout):
        self.timeout = timeout
        if self.sim_time is not None:
            self.timeout_start = Unit(self.sim_time.get(), Time.s)
        else:
            self.timeout_start = Unit(time.time(), Time.s)

    def timeout_finished(self):
        if self.timeout is None:
            raise Exception("No timeout set")

        if self.sim_time is not None:
            now = Unit(self.sim_time.get(), Time.s)
        else:
            now = Unit(time.time(), Time.s)

        '''
        # Should we do this?
        if now - self.timeout_start > self.timeout:
            self.timeout = None
            return True
        return False
        '''

        return now - self.timeout_start > self.timeout
