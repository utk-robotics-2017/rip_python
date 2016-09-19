# import the necessary packages
from multiprocessing import Process, Pipe
import time

from webcam_video_stream import WebcamVideoStream


class VideoStream:
    def __init__(self, **kwargs):
        # check to see if the picamera module should be used
        if kwargs.get('usePiCamera', False):
            # only import the picamera packages unless we are
            # explicity told to do so -- this helps remove the
            # requirement of `picamera[array]` from desktops or
            # laptops that still want to use the `imutils` package
            from pi_video_stream import PiVideoStream

            # initialize the picamera stream and allow the camera
            # sensor to warmup
            self.stream = PiVideoStream(**kwargs)

        # otherwise, we are using OpenCV so initialize the webcam
        # stream
        else:
            self.stream = WebcamVideoStream(**kwargs)

    def start(self):
        self.parent_conn, child_conn = Pipe()
        self.p = Process(target=self.respond, name="Video", args=(child_conn))
        self.p.start()

    def respond(self, child_conn):
        self.stream.start()

        while True:
            if child_conn.poll():
                cmd = child_conn.recv()
                if cmd == 'r':
                    child_conn.send(self.stream.read())
                elif cmd == 'f':
                    self.stream.free()
                    break
                elif cmd == 's':
                    self.stream.stop()
                    break
            else:
                time.sleep(0.1)

    def free(self):
        self.parent_conn.send('f')

        self.p.join(5)
        if self.p.is_alive():
            self.p.terminate()

    def read(self):
        # return the current frame
        self.parent_conn.send('r')
        return self.parent_conn.recv()

    def stop(self):
        # stop the thread and release any resources
        self.parent_conn.send('s')
