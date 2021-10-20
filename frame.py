import cv2
from skimage.metrics import mean_squared_error
from skimage.metrics import structural_similarity as ssim
import math

MERGE_DISTANCE = 15
MERGE_AREA = 100 #to be determined later

class Frame:
    def __init__(self, frameNumber):
        self.number = frameNumber
        self.boxes = []
    def add(self, boxData):
        self.boxes.append(boxData)
    def getBoxes(self):
        return self.boxes
    def setBoxes(self, newBoxes):
        self.boxes = newBoxes
    def getFrameNum(self):
        return self.number

class Dive:
    def __init__(self):
        self.points = []
        self.distance = 0
    def add(self, value):
        self.points.append(value)
    def size(self):
        return len(self.points)

def mergeBoxes(boxesIn):
    boxes = list(boxesIn)
    i = 0
    for curr in boxes:
        if(i + 1 < len(boxes)):
            j = i + 1
            for compare in boxes[i+1:]:
                if(canMerge(curr, compare)):
                    (x, y, w, h) = curr
                    (x2, y2, w2, h2) = compare
                    boxes.pop(j)
                    pt1 = (min(x, x2), min(y, y2))
                    pt2 = (max(x+w, x2+w2), max(y+h, y2+h2))
                    boxes[i] = (pt1[0], pt1[1], (pt2[0]-pt1[0]), (pt2[1]-pt1[1]))
                    curr = boxes[i]
                else:
                    j += 1
        i += 1
    return boxes

def canMerge(box1, box2):
    (x, y, w, h) = box1
    (x2, y2, w2, h2) = box2
    return real_distance((x, y, x+w, y+h), (x2, y2, x2+w2, y2+h2)) < MERGE_DISTANCE and min(w2*h2, w*h) < MERGE_AREA

def extract(frames):
    result = []
    for i in range(len(frames) - 1):
        current = frames[i]
        next = frames[i + 1]
        for f in current:
            pass

#only used in real_distance
def euclidean_distance(box1, box2):
    (x, y) = box1
    (x2, y2) = box2
    return math.hypot(x2 - x, y2 - y)

def real_distance(box1, box2):
    (x1, y1, x1b, y1b) = box1
    (x2, y2, x2b, y2b) = box2
    left = x2b < x1
    right = x1b < x2
    bottom = y2b < y1
    top = y1b < y2
    if top and left:
        return euclidean_distance((x1, y1b), (x2b, y2))
    elif left and bottom:
        return euclidean_distance((x1, y1), (x2b, y2b))
    elif bottom and right:
        return euclidean_distance((x1b, y1), (x2, y2b))
    elif right and top:
        return euclidean_distance((x1b, y1b), (x2, y2))
    elif left:
        return x1 - x2b
    elif right:
        return x2 - x1b
    elif bottom:
        return y1 - y2b
    elif top:
        return y2 - y1b
    else:             # rectangles intersect
        return 0.