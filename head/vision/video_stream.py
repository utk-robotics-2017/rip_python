# import the necessary packages
from multiprocessing import Process, Pipe
import time
import logging

from .webcam_video_stream import WebcamVideoStream
from .pi_video_stream import PiVideoStream
from ..spine.ourlogging import setup_logging

setup_logging(__file__)
logger = logging.getLogger(__name__)


class VideoStream:
    def __init__(self, **kwargs):
        # check to see if the picamera module should be used
        use_pi_camera = kwargs.get('use_pi_camera', False)
        if isinstance(use_pi_camera, str):
            if use_pi_camera.lower() == "true":
                use_pi_camera = True
            elif use_pi_camera.lower() == "false":
                use_pi_camera = False
            else:
                logger.error("Unknown option for `use_pi_camera`")
                raise Exception("Unknown option for `use_pi_camera`")
        if kwargs.get('use_pi_camera', False):
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
