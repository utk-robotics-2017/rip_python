from targettracker import TargetTracker
import cv2

tracker = TargetTracker(lowerRange=(165, 150, 0),
                        upperRange=(180, 255, 255),
                        targetElevation=9.5,
                        targetWidth=8,
                        targetHeight=8,
                        cameraElevation=9,
                        minArea=800)
tracker.startVideoStream()
while True:
    targets = tracker.calculate(display=True)

    #print len(targets)
    cv2.waitKey(1)
