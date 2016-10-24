from multiprocessing import Process, Pipe, Lock as PLock
from threading import Thread, Lock as TLock
from ..misc.timer import Timer


class Looper:
    kDefaultLoopTime = Time(0.1, Time.s)
    def __init__(self):
        self.running = False
        self.timer = Timer()

    def set_loop_time(self, loop_time):
        self.loop_time = loop_time

    def tstart(self):
        self.t = Threading(target=self.tloop)
        self.t.start()
        self.tlock = TLock()

    def pstart(self):
        self.pipe, other_pipe = Pipe()
        self.p = Processing(target=self.ploop, args=(other_pipe,))
        self.plock = PLock()

    def tloop(self):
        self.running = True
        self.on_tstart()
        while self.running:
            start_time = timer.get()
            self.on_tloop()
            end_time = timer.get()
            delta_time = end_time - start_time
            if self.kDefaultLoopTime - delta_time > Time(0, 1):
                timer.sleep(self.kDefaultLoopTime - delta_time)

    def ploop(self, pipe):
        self.running = True
        self.on_pstart()
        while self.running:
            message = pipe.recv()
            if message == "stop":
                self.stop()
            self.on_ploop(message)

    def on_tstart(self):
        pass

    def on_tloop(self):
        raise NotImplementedError("on_tloop")

    def on_pstart(self):
        pass

    def on_ploop(self, message):
        raise NotImplementedError("on_ploop")

    def stop(self):
        self.running = False
        if hasattr(self, 't'):
            self.t.join(timeout=5)
        if hasattr(self, 'p'):
            self.pipe.send("stop")
            self.p.join(timeout=5)
            if self.p.is_alive():
                self.p.terminate()
