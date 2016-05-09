import numpy as np
import cv2
import math
from datetime import datetime

#from head.spine.ourlogging import setup_logging
from convience import resize
from videostream import VideoStream

#setup_logging(__file__)
#logger = logging.getLogger(__name__)


class Block:
    def __init__(self, color, length, width, cx, cy):
        self.color = color
        self.length = length
        self.width = width
        self.cx = cx
        self.cy = cy


DEF_COLORS = [{'name': 'red', 'lowerRange': (0, 100, 0), 'upperRange': (5, 255, 255), 'lowerRange2': (165, 100, 0), 'upperRange2': (180, 255, 255), 'display': (0, 0, 255)},
              {'name': 'orange', 'lowerRange': (5, 100, 0), 'upperRange': (15, 255, 255), 'display': (0, 127, 255)},
              {'name': 'blue', 'lowerRange': (105, 100, 0), 'upperRange': (135, 255, 255), 'display': (255, 0, 0)},
              {'name': 'green', 'lowerRange': (45, 100, 0), 'upperRange': (75, 255, 255), 'display': (0, 255, 0)},
              {'name': 'yellow', 'lowerRange': (15, 100, 0), 'upperRange': (45, 255, 255), 'display': (0, 255, 255)}]

DEF_LENGTHS = [2.5, 5, 7.5]  # in inches


class BlockDetector:
    def __init__(self, **kwargs):

        self.colorOptions = kwargs.get('colorOptions', DEF_COLORS)
        self.lengthOptions = kwargs.get('lengthOptions', DEF_LENGTHS)

        self.blocksElevation = kwargs.get('blocksElevation', 0)
        self.cameraElevation = kwargs.get('cameraElevation', 0)
        self.cameraAngle = kwargs.get('cameraAngle', 0)

        self.fov = kwargs.get('fov', 60)
        self.resolution = kwargs.get('resolution', (320, 240))
        self.fl = self.resolution[0] / (2 * math.tan(self.fov / 2.0))
        self.videostream = VideoStream(**kwargs)

        self.approximate = kwargs.get('approximate', False)
        self.checkRectangle = kwargs.get('checkRectangle', False)
        self.box = kwargs.get('box', False)
        self.minArea = kwargs.get('minArea', -1)
        self.maxArea = kwargs.get('maxArea', -1)

        self.saveLocation = kwargs.get('saveLocation', '')

    def startVideoStream(self):
        self.videostream.start()

    def stopVideoStream(self):
        self.videostream.stop()

    def calculate(self, image=None, display=False, save=False):
        if image is None:
            image = self.videostream.read()
        elif isinstance(image, str):
            image = resize(image=cv2.imread(image), width=self.resolution[0], height=self.resolution[1])
        else:
            image = resize(image=image, width=self.resolution[0], height=self.resolution[1])

        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        sobely = np.absolute(sobely)
        sobely = np.uint8(sobely)
        ret, sobely = cv2.threshold(sobely, 40, 255, cv2.THRESH_BINARY_INV)

        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobelx = np.absolute(sobelx)
        sobelx = np.uint8(sobelx)
        ret, sobelx = cv2.threshold(sobelx, 40, 255, cv2.THRESH_BINARY_INV)

        sobelxy = cv2.bitwise_and(sobelx, sobely)

        hsv = cv2.bitwise_and(hsv, hsv, mask=sobelxy)

        colorContours = []
        blocks = []

        if display or save:
            displayImage = image.copy()
            contourImage = image.copy()

        for color in self.colorOptions:
            colorMask = cv2.inRange(hsv, color['lowerRange'], color['upperRange'])
            if 'lowerRange2' in color:
                colorMask2 = cv2.inRange(hsv, color['lowerRange2'], color['upperRange2'])
                colorMask = cv2.bitwise_or(colorMask, colorMask2)
            contours, hierarchy = cv2.findContours(colorMask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
            #cv2.drawContours(contourImage, contours, -1, color['display'], 3)
            filtered_contours = []
            displayContours = []
            for contour in contours:
                area = cv2.contourArea(contour)
                # Filter by area
                if (self.maxArea != -1 and area > self.maxArea) or (self.minArea != -1 and area < self.minArea):
                    continue

                displayContours.append(contour)

                if(self.checkRectangle):
                    epsilon = 0.1 * cv2.arcLength(contour, True)
                    contour = cv2.approxPolyDP(contour, epsilon, True)
                    if(len(contour) != 4):
                        pass
                elif(self.approximate):
                    epsilon = 0.1 * cv2.arcLength(contour, True)
                    contour = cv2.approxPolyDP(contour, epsilon, True)

                rect = (x, y), (w, h), angle = cv2.minAreaRect(contour)

                if w > h * 1.5:
                    temp = h
                    w = h
                    h = temp

                # TODO: use camera height/angle/fov and block height to convert width and height from pixels to inches

                blocks.append(Block(color['name'], h, w, x, y))
                if(self.box):
                    box = cv2.cv.BoxPoints(rect)
                    box = np.int0(box)
                    contour = box
                filtered_contours.append(contour)
            if display or save:
                cv2.drawContours(displayImage, filtered_contours, -1, color['display'], -1)
                cv2.drawContours(contourImage, displayContours, -1, color['display'], 3)
            colorContours.append(filtered_contours)

        if display or save:
            allColorMasks = np.zeros(hsv.shape, np.uint8)
            for color in colorContours:
                cv2.drawContours(allColorMasks, color, -1, (255, 255, 255), -1)
            allColorMasks = cv2.inRange(allColorMasks, (127, 127, 127), (255, 255, 255))
            displayImage = cv2.bitwise_and(displayImage, displayImage, mask=allColorMasks)

            for block in blocks:
                cv2.circle(displayImage, (int(block.cx), int(block.cy)), 3, (255, 255, 255), 3)
                cv2.putText(displayImage, "L: %d" % (block.length), (int(block.cx), int(block.cy) + 20), cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 255, 255))
                cv2.putText(displayImage, "W: %d" % (block.width), (int(block.cx), int(block.cy) + 40), cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 255, 255))

            both = np.hstack((image, displayImage))
            image2 = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
            both2 = np.hstack((image2, contourImage))
            three = np.vstack((both, both2))
            if display:
                cv2.imshow("BlockDetector", three)

            if save:
                cv2.imwrite(self.saveLocation + "%s-BlockDetector.jpg" % datetime.now(), three)
