from blockdetector import BlockDetector
import cv2

COLORS_2012 = [{'name': 'red', 'lowerRange': (0, 100, 0), 'upperRange': (5, 255, 255), 'lowerRange2': (165, 100, 0), 'upperRange2': (180, 255, 255), 'display': (0, 0, 255)},
               {'name': 'orange', 'lowerRange': (5, 100, 0), 'upperRange': (15, 255, 255), 'display': (0, 127, 255)},
               {'name': 'blue', 'lowerRange': (105, 100, 0), 'upperRange': (135, 255, 255), 'display': (255, 0, 0)},
               {'name': 'green', 'lowerRange': (45, 100, 0), 'upperRange': (75, 255, 255), 'display': (0, 255, 0)},
               {'name': 'yellow', 'lowerRange': (15, 125, 0), 'upperRange': (45, 255, 255), 'display': (0, 255, 255)}]

COLORS_2015 = [{'name': 'red', 'lowerRange': (0, 100, 0), 'upperRange': (15, 255, 255), 'lowerRange2': (165, 100, 0), 'upperRange2': (180, 255, 255), 'display': (0, 0, 255)},
               {'name': 'blue', 'lowerRange': (105, 100, 0), 'upperRange': (135, 255, 255), 'display': (255, 0, 0)},
               {'name': 'green', 'lowerRange': (40, 100, 0), 'upperRange': (75, 255, 255), 'display': (0, 255, 0)},
               {'name': 'yellow', 'lowerRange': (15, 100, 0), 'upperRange': (40, 255, 255), 'display': (0, 255, 255)}]

bd = BlockDetector(minArea=600, box=True, colorOptions=COLORS_2012)
#bd.startVideoStream()

while True:
    blocks = bd.calculate(image="0.jpeg", display=True)
    cv2.waitKey(1)
