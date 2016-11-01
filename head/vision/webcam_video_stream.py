# import the necessary packages
from threading import Thread
import cv2
import scanf
from ..misc.timer import Timer
import logging
from ..spine.ourlogging import setup_logging
setup_logging(__file__)
logger = logging.getLogger(__name__)


class WebcamVideoStream:
    def __init__(self, **kwargs):
        # initialize the video camera stream and read the first frame
        # from the stream
        if 'src' in kwargs:
            try:
                src_int = int(kwargs['src'])
                src = src_int
            except:
                logger.error("Unknown option for `src`")
                raise Exception("Unknown option for `src`")
        else:
            src = 0

        self.stream = cv2.VideoCapture(src)

        if 'resolution' in kwargs:
            try:
                w, h = scanf.sscanf(kwargs['resolution'], "(%d, %d)")
            except:
                logger.error("Unknown option for `resolution`. Format should be (w, h)")
                raise Exception("Unknown option for `resolution`. Format should be (w, h)")
        else:
            self.resolution = (320, 240)
        self.stream.set(3, self.resolution[0])
        self.stream.set(4, self.resolution[1])
        (grabbed, self.frame) = self.stream.read()
        self.timer = Timer()

        # initialize the variable used to indicate if the thread should
        # be stopped
        self.stopped = False

    def start(self):
        # start the process to read frames from the video stream
        self.t = Thread(target=self.update, name="Webcam")
        self.t.start()

    def update(self):
        # keep looping infinitely until the thread is stopped
        while not self.stopped:
            # otherwise, read the next frame from the stream
            self.timestamp = timer.time()
            (grabbed, self.frame) = self.stream.read()
            if not grabbed:
                logger.e("Camera didn't grab an image")

    def read(self):
        # return the frame most recently read
        return (self.timestamp, self.frame)

    def free(self):
        self.stop()

        self.t.join(5)
        if self.t.is_alive():
            self.t.termintate()

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True
