import time
from simulator.sim_time import SimTime


class Timer:
    def __init__(self, sim=False):
        if sim:
            self.sim_time = SimTime()
        else:
            self.sim_time = None

        self.timeout = None
        self.timeout_start = None

    def sleep(self, secs):
        if self.sim_time is not None:
            self.sim_time.increment_time_by(secs)
        else:
            time.sleep(secs)

    def delay(self, secs):
        self.sleep(secs)

    def set_timeout(self, timeout):
        self.timeout = timeout
        if self.sim_time is not None:
            self.timeout_start = self.sim_time.get()
        else:
            self.timeout_start = time.time()

    def timeout_finished(self):
        if self.timeout is None:
            raise Exception("No timeout set")

        if self.sim_time is not None:
            now = self.sim_time.get()
        else:
            now = time.time()

        '''
        # Should we do this?
        if now - self.timeout_start > self.timeout:
            self.timeout = None
            return True
        return False
        '''

        return now - self.timeout_start > self.timeout
