from videostream import videostream
import numpy as np
import cv2
import math
from datetime import datetime


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

        self.lowerHSV = kwargs.get('lowerHSV', (0, 0, 0))
        self.upperHSV = kwargs.get('upperHSV', (180, 255, 255))
        self.shape = kwargs.get('shape', -1)

        self.targetWidth = kwargs.get('targetWidth', 0)
        self.targetHeight = kwargs.get('targetHeight', 0)
        self.targetElevation = kwargs.get('targetElevation', 0)

        self.cameraElevation = kwargs.get('cameraElevation', 0)
        self.cameraAngle = kwargs.get('cameraAngle', 0)

        self.resolution = kwargs.get('resolution', (320, 240))
        self.fl = self.resolution[0] / (2 * math.tan(self.fov / 2.0))
        self.videostream = videostream(kwargs)
        self.videostream.start()
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
        self.videostream = videostream(kwargs)
        self.videostream.start()

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

    def calculate(self, display=False, save=False):
        image = self.videostream.read()
        hsv = cv2.convertColor(image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lowerHSV, self.upperHSV)
        if display or save:
            res = cv2.bitwise_and(image, image, mask=mask)
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        if display or save:
            cv2.drawContours(res, contours, -1, (0, 0, 0), 3)

        targets = []
        keptContours = []
        for contour in contours:
            area = cv2.contourArea(contour)

            # Filter by area
            if (self.maxArea != -1 and area > self.maxArea) or (self.minArea != -1 or area < self.minArea):
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

            if self.shape == 4:
                x, y, w, h = cv2.boundingRect(contour)
            elif self.shape == 0:
                (x, y), radius = cv2.minEnclosingCircle(contour)
                radius = int(radius)
                w = radius * 2
                h = radius * 2

            hAngle = math.atan((u - self.cx) / self.fl)
            vAngle = math.atan((v - self.cy) / self.fl)
            distance = 0  # TODO

            if display or save:
                cv2.putText(res, "CX: %d\nCY: %d\nWidth: %d\nHeight: %d\nH Angel: %f\nV Angel: %f\nDistance: %f" % (u, v, w, h, hAngle, vAngle, display), (u + 20, v + 20), cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 0, 0))

            targets.append(Target(contour, u, v, w, h, hAngle, vAngle, distance))
        if display or save:
            cv2.drawContours(res, keptContours, -1, (0, 255, 0), 3)
            both = np.hstack((image, res))
            if display:
                cv2.imshow("Target", both)

            if save:
                cv2.imwrite(self.saveLocation + "%s-Target.jpg" % datetime.now(), both)

        return targets
