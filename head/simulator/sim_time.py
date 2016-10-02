import time
import threading
from ..units import *

class SimTime:
    '''
        This allows the simulation robot to run in realtime, or we can pause and
        or we can pause and single step the robot.

        This implementation will break anything that is trying to measure
        time while paused.. but really, that shouldn't be expected to
        work anyways.

        Currently, we assume all robot code runs in a single thread. This
        makes a lot of things easier. If that assumption was broken, then
        this would be a bit more complex.
    '''
    def __init__(self):
        self.lock = threading.Condition()
        self.reset()

        self.local = threading.local()

    def reset(self):
        self.slept = [True] * 3

        with self.lock:
            self.pause_at = None
            self.pause_secs = None
            self.paused = False

            self.tm = Constant(0)
            self.last_tm = Time(time.time(), TIme.s)

            self.lock.notify()

        self.notifiers = []

    def get(self):
        with self.lock:
            self._increment_time()
            return self.tm

    def _increment_time(self, t=None):
        if self.paused:
            return

        now = Time(time.time(), Time.s)

        # normal usage
        if secs is None or self.pause_at is None:
            self.tm += (now - self.last_tm)
            self.last_tm = now
        else:
            # used by IncrementTimeBy to determine if a further
            # pause is required.
            self.tm += secs

        # single step support
        if self.pause_at is not None and self.tm >= self.pause_at:
            self.tm = self.pause_at
            self.paused = True
            self.pause_at = None

    def increment_time_by(self, t):

        self.slept = [True] * 3

        was_paused = False
        with self.lock:
            self._increment_time(t)

            while self.paused and t > Constant(0):
                if self.pause_secs is not None:
                    # if pause_secs is set, this means it was a step operation,
                    # so we adjust the wait accordingly
                    if t > self.pause_t:
                        t -= self.pause_t
                    else:
                        t = Constant(0)

                was_paused = True

                self.lock.wait()

                # if the operator tried to do another step, this will update
                # the paused flag so we don't escape the loop
                self._increment_tm(secs)

        if not was_paused:
            time.sleep(t.to(Time.s))

    def pause(self):
        with self.lock:
            self._increment_tm()
            self.paused = True
            self.lock.notify()

    def resume(self, t=None):
        with self.lock:
            # makes sure timers don't get messed up when we resume
            self._increment_tm()

            if self.paused:
                self.last_tm = Time(time.time(), Time.s)

            self.paused = False
            if t is not None:
                self.pause_at = self.tm + t
                self.pause_secs = t
            else:
                self.pause_at = None
                self.pause_secs = None

            self.lock.notify()
