import numpy as np
import cv2
import math
from datetime import datetime

from videostream import VideoStream


class Target:

    def __init__(self, contour, cx, cy, width, height, hAngle, vAngle, distance):
        self.contour = contour
        self.cx = cx
        self.cy = cy
        self.width = width
        self.height = height
        self.hAngle = hAngle
        self.vAngle = vAngle
        self.distance = distance


class TargetTracker:

    def __init__(self, **kwargs):
        self.fov = kwargs.get('fov', 60)

        lowerTemp = kwargs.get('lowerRange', (0, 0, 0))
        self.lowerRange = np.array([lowerTemp[0], lowerTemp[1], lowerTemp[2]])
        upperTemp = kwargs.get('upperRange', (180, 255, 255))
        self.upperRange = np.array([upperTemp[0], upperTemp[1], upperTemp[2]])
        self.shape = kwargs.get('shape', -1)

        self.targetWidth = kwargs.get('targetWidth', 0)
        self.targetHeight = kwargs.get('targetHeight', 0)
        self.targetElevation = kwargs.get('targetElevation', 0)

        self.cameraElevation = kwargs.get('cameraElevation', 0)
        self.cameraAngle = kwargs.get('cameraAngle', 0)

        self.resolution = kwargs.get('resolution', (320, 240))
        self.fl = self.resolution[0] / (2 * math.tan(self.fov / 2.0))
        self.videostream = VideoStream(**kwargs)
        self.cx = self.resolution[0] / 2.0 - 0.5
        self.cy = self.resolution[1] / 2.0 - 0.5

        self.minArea = kwargs.get('minArea', -1)
        self.maxArea = kwargs.get('maxArea', -1)
        self.minSolidarity = kwargs.get('minSolidarity', -1)
        self.maxSolidarity = kwargs.get('maxSolidarity', -1)

        self.saveLocation = kwargs.get('saveLocation', '')

    def setCameraParams(self, **kwargs):
        self.fov = kwargs.get('fov', self.fov)
        self.cameraElevation = kwargs.get('cameraElevation', self.cameraElevation)
        self.cameraAngle = kwargs.get('cameraAngle', self.cameraAngle)

        self.resolution = kwargs.get('resolution', self.resolution)
        self.fl = self.resolution[0] / (2 * math.tan(self.fov / 2.0))
        self.videostream.stop()
        self.videostream = VideoStream(kwargs)

        self.cx = self.resolution[0] / 2.0 - 0.5
        self.cy = self.resolution[1] / 2.0 - 0.5

    def setTargetParams(self, **kwargs):
        self.lowerHSV = kwargs.get('lowerHSV', self.lowerHSV)
        self.upperHSV = kwargs.get('upperHSV', self.upperHSV)
        self.shape = kwargs.get('shape', self.shape)

        self.targetWidth = kwargs.get('targetWidth', self.targetWidth)
        self.targetHeight = kwargs.get('targetHeight', self.targetHeight)
        self.targetElevation = kwargs.get('targetElevation', self.targetElevation)

    def setFilterParams(self, **kwargs):
        self.minArea = kwargs.get('minArea', self.minArea)
        self.maxArea = kwargs.get('maxArea', self.maxArea)
        self.minSolidarity = kwargs.get('minSolidarity', self.minSolidarity)
        self.maxSolidarity = kwargs.get('maxSolidarity', self.maxSolidarity)

    def setSaveLocation(self, saveLocation):
        self.saveLocation = saveLocation

    def startVideoStream(self):
        self.videostream.start()

    def stopVideoStream(self):
        self.videostream.stop()

    def calculate(self, image=None, display=False, save=False):
        if image is None:
            image = self.videostream.read()
        elif isinstance(image, str):
            image = cv2.imread(image)

        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        hsv = cv2.medianBlur(hsv, 5)
        mask = cv2.inRange(hsv, self.lowerRange, self.upperRange)
        if display or save:
            res = cv2.bitwise_and(image, image, mask=mask)
            ranged = res.copy()
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        print len(contours)
        if display or save:
            cv2.drawContours(res, contours, -1, (0, 0, 255), -1)
        targets = []

        keptContours = []
        for contour in contours:
            area = cv2.contourArea(contour)

            # Filter by area
            if (self.maxArea != -1 and area > self.maxArea) or (self.minArea != -1 and area < self.minArea):
                continue

            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.1 * perimeter, True)

            # Filter by Shape
            if self.shape != -1 and len(approx) != self.shape:
                continue

            hull = cv2.convexHull(contour)
            hullArea = cv2.contourArea(hull)
            solidarity = area / hullArea

            # Filter by Solidarity
            if (self.maxSolidarity != -1 and solidarity > self.maxSolidarity) or (self.minSolidarity != -1 and solidarity < self.minSolidarity):
                continue

            keptContours.append(contour)

            M = cv2.moments(contour)
            u = int(M['m10'] / M['m00'])
            v = int(M['m01'] / M['m00'])

            x, y, w, h = cv2.boundingRect(contour)

            hAngle = math.degrees(math.atan((u - self.cx) / self.fl))
            vAngle = math.degrees(math.atan((v - self.cy) / self.fl))
            distance = 0  # TODO: Determine Distance based on camera physical parameters and target physical parameters

            if display or save:
                cv2.circle(res, (u, v), 5, (255, 0, 0), 5)
                cv2.putText(res, "CX: %d" % (u), (u + 20, v - 70),
                            cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 0, 0))
                cv2.putText(res, "CY: %d" % (v), (u + 20, v - 50),
                            cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 0, 0))
                cv2.putText(res, "Width: %d" % (w), (u + 20, v - 30),
                            cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 0, 0))
                cv2.putText(res, "Height: %d" % (h), (u + 20, v - 10),
                            cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 0, 0))
                cv2.putText(res, "H Angle: %f" % (hAngle), (u + 20, v + 10),
                            cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 0, 0))
                cv2.putText(res, "V Angle: %f" % (vAngle), (u + 20, v + 30),
                            cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 0, 0))
                cv2.putText(res, "Distance: %d" % (distance), (u + 20, v + 50),
                            cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 0, 0))
            targets.append(Target(contour, u, v, w, h, hAngle, vAngle, distance))

        if display or save:
            cv2.drawContours(res, keptContours, -1, (0, 255, 0), 3)
            both = np.hstack((image, res))
            both2 = np.hstack((ranged, image))
            three = np.vstack((both, both2))
            if display:
                cv2.imshow("Target", three)

            if save:
                cv2.imwrite(self.saveLocation + "%s-Target.jpg" % datetime.now(), three)

        return targets
