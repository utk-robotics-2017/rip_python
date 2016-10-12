import time
from .simulator.sim_time import SimTime
from .units import Time


class Timer:
    # Singleton
    class __Timer:
        def __init__(self, sim=False):
            if sim:
                self.sim_time = SimTime()
            else:
                self.sim_time = None

            self.timeout = None
            self.timeout_start = None

        def get(self):
            if self.sim_time is not None:
                return self.sim_time.get()
            else:
                return Time(time.time(), Time.s)

        def time(self):
            return self.get()

        def sleep(self, t):
            if self.sim_time is not None:
                self.sim_time.increment_time_by(t)
            else:
                time.sleep(t.to(Time.s))

        def delay(self, t):
            self.sleep(t)

        def set_timeout(self, timeout):
            self.timeout = timeout
            if self.sim_time is not None:
                self.timeout_start = self.sim_time.get()
            else:
                self.timeout_start = Time(time.time(), Time.s)

        def timeout_finished(self):
            if self.timeout is None:
                raise Exception("No timeout set")

            if self.sim_time is not None:
                now = Time(self.sim_time.get(), Time.s)
            else:
                now = Time(time.time(), Time.s)

            '''
            # Should we do this?
            if now - self.timeout_start > self.timeout:
                self.timeout = None
                return True
            return False
            '''

            return now - self.timeout_start > self.timeout

    instance = None

    def __init__(self, sim=False):
        if not Timer.instance:
            Timer.instance = Timer.__Timer(sim)

    def __getattr__(self, name):
        return getattr(self.instance, name)
