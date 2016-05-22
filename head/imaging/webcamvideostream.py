# import the necessary packages
#from threading import Thread
from multiprocessing import Process
import cv2


class WebcamVideoStream:
    def __init__(self, **kwargs):
        # initialize the video camera stream and read the first frame
        # from the stream
        src = kwargs.get('src', 0)
        self.stream = cv2.VideoCapture(src)
        self.resolution = kwargs.get('resolution', (320, 240))
        self.stream.set(3, self.resolution[0])
        self.stream.set(4, self.resolution[1])
        (self.grabbed, self.frame) = self.stream.read()

        # initialize the variable used to indicate if the thread should
        # be stopped
        self.stopped = False

    def start(self):
        # start the process to read frames from the video stream
        p = Process(target=self.update, args=())
        p.start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                return

            # otherwise, read the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        # return the frame most recently read
        return self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True
