# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
from threading import Thread
import scanf
import logging
from ..spine.ourlogging import setup_logging
setup_logging(__file__)
logger = logging.getLogger(__name__)


class PiVideoStream:
    def __init__(self, **kwargs):
        # initialize the camera and stream
        self.camera = PiCamera()
        if 'resolution' in kwargs:
            try:
                w, h = scanf.sscanf(kwargs['resolution'], "(%d, %d)")
                self.camera.resolution((w, h))
            except:
                logger.error("Unknown option for `resolution`. Format should be (w, h)")
                raise Exception("Unknown option for `resolution`. Format should be (w, h)")
        else:
            self.camera.resolution = (320, 240)

        opt_default = {'framerate': 32, 'sharpness': 0, 'contrast': 0, 'brightness': 50,
                       'saturation': 0, 'ISO': 0, 'exposure_compensation': 0, 'rotation': 0}

        for opt in ['framerate', 'sharpness', 'contrast', 'brightness', 'saturation', 'ISO',
                    'exposure_compensation', 'rotation']:
            if opt in kwargs:
                try:
                    opt_int = int(kwargs[opt])
                    self.camera.__dict__[opt] = opt_int
                except:
                    logger.error("Unknown option for `{0:s}`".format(opt))
                    raise Exception("Unknown option for `{0:s}`".format(opt))
            else:
                self.camera.__dict__[opt] = opt_default[opt]

        for opt in ['video_stabilization', 'hflip', 'vflip']:
            if opt in kwargs:
                if kwargs[opt].lower() == "true":
                    opt_bool = True
                elif kwargs[opt].lower() == "false":
                    opt_bool = False
                else:
                    logger.error("Unknown option for `{0:s}`".format(opt))
                    raise Exception("Unknown option for `{0:s}`".format(opt))
                self.camera.__dict__[opt] = opt_bool
            else:
                self.camera.__dict__[opt] = False

        opt_default = {'exposure_mode': 'auto', 'meter_mode': 'average', 'awb_mode': 'auto',
                       'image_effect': 'none'}

        for opt in ['exposure_mode', 'meter_mode', 'awb_mode', 'image_effect']:
            if opt in kwargs:
                self.camera.__dict__[opt] = kwargs[opt]
            else:
                self.camera.__dict__[opt] = opt_default[opt]

        if 'color_effects' in kwargs:
            self.camera.color_effects = kwargs['color_effects']
        else:
            self.camera.color_effects = None

        if 'crop' in kwargs:
            try:
                crop = scanf.sscanf(kwargs['crop'], "(%f, %f, %f, %f)")
                self.camera.crop = crop
            except:
                logger.error("Unknown option for `crop`. Format is (x0, y0, x1, y1) as a percentage")
                raise Exception("Unknown option for `crop`. Format is (x0, y0, x1, y1) as a percentage")
        else:
            self.camera.crop = (0.0, 0.0, 1.0, 1.0)

        self.rawCapture = PiRGBArray(self.camera, size=self.camera.resolution)
        self.stream = self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True)

        # initialize the frame and the variable used to indicate
        # if the thread should be stopped
        self.frame = None
        self.stopped = False

    def start(self):
        # start the process to read frames from the video stream
        self.t = Thread(target=self.update, name="PiCam")
        self.t.start()

    def update(self):
        # keep looping infinitely until the thread is stopped
        for f in self.stream:
            # grab the frame from the stream and clear the stream in
            # preparation for the next frame
            self.frame = f.array
            self.rawCapture.truncate(0)

            # if the thread indicator variable is set, stop the thread
            # and resource camera resources
            if self.stopped:
                self.stream.close()
                self.rawCapture.close()
                self.camera.close()
                return

    def read(self):
        # return the frame most recently read
        return self.frame

    def free(self):
        self.stop()

        self.t.join(5)

        if self.t.is_alive():
            self.t.terminate()

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True
