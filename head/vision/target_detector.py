import numpy as np
import cv2
from ..timer import Timer
from ..units import Time
from ..constants import Constants


class TargetDetector:
    constants = Constants()
    kMinTargetWidth = constants.constants.target_detector.min_target_width
    kMaxTargetWidth = constants.constants.target_detector.max_target_width
    kMinTargetHeight = constants.constants.target_detector.min_target_height
    kMaxTargetHeight = constants.constants.target_detector.max_target_height
    kNearlyHorizontalSlope = 1 / 1.25
    kNearlyVerticalSlope = 1.25
    kMinFullness = constants.constants.target_detector.min_fullness
    kMaxFullness = constants.constants.target_detector.max_fullness
    kSaveLocation = constants.constants.camera.save_location

    class Target:
        def __init__(self):
            self.cx = 0
            self.cy = 0
            self.width = 0
            self.height = 0

    def __init__(self, camera):
        lower_h = self.constants.constants.target_detector.lower_hue
        lower_s = self.constants.constants.target_detector.lower_saturation
        lower_v = self.constants.constants.target_detector.lower_value
        self.lower_range = np.array([lower_h, lower_s, lower_v])

        upper_h = self.constants.constants.target_detector.upper_hue
        upper_s = self.constants.constants.target_detector.upper_saturation
        upper_v = self.constants.constants.target_detector.upper_value
        self.upper_range = np.array([upper_h, upper_s, upper_v])

        self.camera = camera

    def process_image(self, image=None, display=False, save=False):
        if image is None:
            timestamp, image = self.camera.read()
        elif isinstance(image, str):
            image = cv2.imread(image)
            timestamp = Timer.time()

        if save:
            cv2.write("{0:s}/image_{1:f}.jpg".format(self.kSaveLocation, timestamp.to(Time.s)), image)

        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        thresh = cv2.inRange(hsv, self.lower_range, self.upper_range)
        if display or save:
            res = cv2.bitwiseAnd(image, image, thresh)
            if save:
                cv2.write("{0:s}/thresh_{1:f}.jpg".format(self.kSaveLocation, timestamp.to(Time.s)), res)
            if display:
                top_two = np.hstack((image, res))
        contour_input = thresh.copy()
        contours, hierchy = cv2.findContours(contour_input, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_KCOS)
        rejected_targets = []
        targets = []

        for contour in contours:
            convex_contour = cv2.convexHull(contour, False)
            poly = cv2.approxPolyDP(convex_contour, 20, True)
            if len(poly) == 4 and cv2.isContourConvex(poly):
                target = {}
                target['cx'] = 0
                target['cy'] = 0
                min_x = float("inf")
                max_x = -float("inf")
                min_y = float("inf")
                max_y = -float("inf")
                for point in poly:
                    if point.x < min_x:
                        min_x = point.x
                    if point.x > max_x:
                        max_x = point.x
                    if point.y < min_y:
                        min_y = point.y
                    if point.y > max_y:
                        max_y = point.y
                    target['cx'] += point.x
                    target['cy'] += point.y
                target['cx'] /= 4
                target['cy'] /= 4
                target['width'] = max_x - min_x
                target['height'] = max_y - min_y
                target['points'] = poly

                if(target['width'] < self.kMinTargetWidth or
                   target['width'] > self.kMaxTargetWidth or
                   target['height'] < self.kMinTargetHeight or
                   target['height'] > self.kMaxTargetHeight):
                    rejected_targets.append(target)

                num_nearly_horizontal_slope = 0
                num_nearly_vertical_slope = 0
                last_edge_vertical = False
                for i in range(4):
                    dy = target['points'][i].y - target['points'][(i + 1) % 4].y
                    dx = target['points'][i].x - target['points'][(i + 1) % 4].x
                    slope = float("inf")

                    if dx != 0:
                        slope = dy / dx

                    if(abs(slope) <= self.kNearlyHorizontalSlope and
                       (i == 0 or last_edge_vertical)):
                        last_edge_vertical = False
                        num_nearly_horizontal_slope += 1
                    elif(abs(slope) >= self.kNearlyVerticalSlope and
                         (i == 0 or not last_edge_vertical)):
                        last_edge_vertical = True
                        num_nearly_vertical_slope += 1
                    else:
                        break

                if(num_nearly_horizontal_slope != 2 and num_nearly_vertical_slope != 2):
                    rejected_targets.append(target)
                    continue

                original_contour_area = cv2.contourArea(contour)
                poly_area = cv2.contourArea(poly)
                fullness = original_contour_area / poly_area

                if(fullness < self.kMinFullness or fullness > self.kMaxFullness):
                    rejected_targets.append(target)
                    continue
            targets.append(target)
        if save or display:
            image_w_targets = image.copy()
            for target in targets:
                cv2.polylines(image_w_targets, target['points'], True, np.array([0, 112, 255]), 3)
                cv2.circle(image_w_targets, (target['cx'], target['cy']), 5, np.array([0, 112, 255]), 3)
            if save:
                cv2.imwrite("{0:s}/target_{1:f}.jpg".format(self.kSaveLocation, timestamp.to(Time.s)),
                            image_w_targets)
            image_w_targets_plus = image_w_targets.copy()
            for target in rejected_targets:
                cv2.polylines(image_w_targets_plus, target['points'], True, np.array([255, 0, 0]), 3)
            if save:
                cv2.imwrite("{0:s}/target_plus_{1:f}.jpg".format(self.kSaveLocation, timestamp.to(Time.s)),
                            image_w_targets_plus)
            if display:
                bottom_two = np.hstack((image_w_targets, image_w_targets_plus))
                all = np.vstack((top_two, bottom_two))
                cv2.imshow("Target Tracking", all)
        return timestamp, targets
