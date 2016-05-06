# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
from multiprocessing import Process


class PiVideoStream:
    def __init__(self, **kwargs):
        # initialize the camera and stream
        self.camera = PiCamera()
        self.camera.resolution = kwargs.get('resolution', (320, 240))
        self.camera.framerate = kwargs.get('framerate', 32)
        self.camera.sharpness = kwargs.get('sharpness', 0)
        self.camera.contrast = kwargs.get('contrast', 0)
        self.camera.brightness = kwargs.get('brightness', 50)
        self.camera.saturation = kwargs.get('saturation', 0)
        self.camera.ISO = kwargs.get('ISO', 0)
        self.camera.video_stabilization = kwargs.get('video_stabilization', False)
        self.camera.exposure_compensation = kwargs.get('exposure_compensation', 0)
        self.camera.exposure_mode = kwargs.get('exposure_mode', 'auto')
        self.camera.meter_mode = kwargs.get('meter_mode', 'average')
        self.camera.awb_mode = kwargs.get('awb_mode', 'auto')
        self.camera.image_effect = kwargs.get('image_effect', 'none')
        self.camera.color_effects = kwargs.get('color_effects', None)
        self.camera.rotation = kwargs.get('rotation', 0)
        self.camera.hflip = kwargs.get('hflip', False)
        self.camera.vflip = kwargs.get('vflip', False)
        self.camera.crop = kwargs.get('crop', (0.0, 0.0, 1.0, 1.0))

        self.rawCapture = PiRGBArray(self.camera, size=self.camera.resolution)
        self.stream = self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True)

        # initialize the frame and the variable used to indicate
        # if the thread should be stopped
        self.frame = None
        self.stopped = False

    def start(self):
        # start the process to read frames from the video stream
        p = Process(target=self.update, args=())
        p.start()
        return self

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

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True
