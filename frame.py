import cv2
from skimage.metrics import mean_squared_error
from skimage.metrics import structural_similarity as ssim
import math

class Frame:
    def __init__(self, frameNumber):
        self.number = frameNumber
        self.boxes = []
    def add(self, boxData):
        self.boxes.append(boxData)
    def getBoxes(self):
        return self.boxes

def mergeBoxes(boxes):
    boxes = list(boxes)
    i = 0
    for curr in boxes:
        if(i + 1 < len(boxes)):
            j = i + 1
            for compare in boxes[i+1:]:
                if(isClosed(curr, compare)):
                    (x, y, w, h) = curr
                    (x2, y2, w2, h2) = compare
                    print("remove")
                    boxes.pop(j)
                    pt1 = (min(x, x2), min(y, y2))
                    pt2 = (max(x+w, x2+w2), max(y+h, y2+h2))
                    boxes[i] = (pt1[0], pt1[1], (pt2[0]-pt1[0]), (pt2[1]-pt1[1]))
                    curr = boxes[i]
                else:
                    j += 1
        i += 1
    return boxes

def isClosed(box1, box2):
    (x, y, w, h) = box1
    (x2, y2, w2, h2) = box2
    return math.hypot(x2 - x, y2 - y) <= 50 #<-closeness limit

def processBoxes(boxes):
    #compare previous remove dpulicate
    #remove static frame
    pass

