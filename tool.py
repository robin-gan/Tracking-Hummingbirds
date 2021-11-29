import random
import cv2
import math

MERGE_DISTANCE = 15
FEEDER_CLOSE = 100
MERGE_AREA = 100 #to be determined later
MIN_DISTANCE_OF_CLOSE = 50 #change to factor of the box itself's width and height
INACTIVE_LIMIT = 1
BOX_BORDER_COLOR = (111, 0, 51)
DIVE_LENGTH_LIMIT = 3
DUPLICATE_RATE = 2/3
ABSOLUTE_DISTANCE_LIMIT = 100
MOVING_AREA_LIMIT = 10000
BIG_WIDTH_LIMIT = 100

heightUpLimit = 1080
heightDownLimit = 0
widthUpLimit = 1920
widthDownLimit = 0

def convert(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
      
    return "%d:%02d:%02d" % (hour, minutes, seconds)

def randomColor():
    r = random.randint(0,255)
    g = random.randint(0,255)
    b = random.randint(0,255)
    return [r,g,b]

def mergeBoxes(boxesIn:list):
    boxes = boxesIn.copy()
    i = 0

    for curr in boxes:
        if (i + 1 < len(boxes)):
            j = i + 1

            for compare in boxes[i+1:]:
                if (canMerge(curr, compare)):
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
    boxesIn = boxes
    return boxes

def canMerge(box1, box2):
    (x1, y1, w1, h1) = box1
    (x2, y2, w2, h2) = box2
    return real_distance(box1, box2) < MERGE_DISTANCE and min(w2*h2, w1*h1) < MERGE_AREA

def calcCurrentBoundary(current, add):
    (x, y, w, h) = add
    top = y
    bottom = y + h
    left = x
    right = x + w
    if current[0] > top:
        current[0] = top
    if current[1] < bottom:
        current[1] = bottom
    if current[2] > left:
        current[2] = left
    if current[3] < right:
        current[3] = right
    return current

#only used in real_distance
def euclidean_distance(box1, box2):
    (x, y) = box1
    (x2, y2) = box2
    return math.hypot(x2 - x, y2 - y)

def euclidean_distance_4(box1, box2):
    return euclidean_distance((box1[0], box1[1]), (box2[0], box2[1]))

def real_distance(box1, box2):
    (x1, y1, w1, h1) = box1
    (x2, y2, w2, h2) = box2
    x1b, x2b, y1b, y2b = x1+w1, x2+w2, y1+h1, y2+h2
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

#deprecated
def isSame(box1, box2):
    (x, y, w, h) = box1
    (x2, y2, w2, h2) = box2
    factor = euclidean_distance((x ,y), (x2, y2)) + abs(w2-w) + abs(h2-h)
    return factor < 100

#deprecated
def removeSameBox(frame1: list, frame2: list):
    originalFrame = frame1.copy()
    if (len(originalFrame) > 0):
        removeIndex = []
        for box in frame2:
            removeIndex += [i3 for i3, box2 in enumerate(originalFrame) if (isSame(box2, box))]
        return [ele for i2, ele in enumerate(originalFrame) if i2 not in removeIndex]
    return originalFrame

def draw(pic, boxes, i):
    for b in boxes:
        (x, y, w, h) = b
        cv2.rectangle(pic, (x+widthDownLimit, y+heightDownLimit), 
                        (x+w+widthDownLimit, y+h+heightDownLimit), BOX_BORDER_COLOR, 2)
    cv2.imwrite("images/coordinates_" + str(i) + "_raw.jpg", pic)

#draw the coordinates - old method
'''for i, frame in enumerate(frames):
    for box in frame:
        (x, y, w, h) = box
        cv2.rectangle(firstFrame, (x+widthDownLimit, y+heightDownLimit), 
                    (x+w+widthDownLimit, y+h+heightDownLimit), BOX_BORDER_COLOR, 2)
    #cv2.imwrite("images/coordinates_" + str(i) + ".jpg", firstFrame)'''