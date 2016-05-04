from blockdetector import BlockDetector
import cv2

bd = BlockDetector(minArea=800, box=True)
#bd.startVideoStream()

while True:
    blocks = bd.calculate(image="0.jpeg", display=True)
    cv2.waitKey(1)
