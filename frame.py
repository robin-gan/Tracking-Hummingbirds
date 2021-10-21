import math
import random

MERGE_DISTANCE = 15
MERGE_AREA = 100 #to be determined later
MIN_DISTANCE_OF_CLOSE = 50 #change to factor of the box itself's width and height
INACTIVE_LIMIT = 5

class Box:
    def __init__(self, data, frame):
        self.data = data
        self.frame = frame
    def frameNumber(self):
        return self.frame
    def size(self):
        return self.data

class Dive:
    def __init__(self):
        self.points = []
        self.distance = 0
    def add(self, value):
        self.points.append(value)
    def size(self):
        return len(self.points)
    def lastBox(self) -> Box:
        return self.points[-1]
    def isActive(self, currentFrame) -> bool:
        if (currentFrame - self.lastBox().frameNumber() > INACTIVE_LIMIT):
            return False
        return True
    def boxes(self) -> list:
        return self.points

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

#only used in real_distance
def euclidean_distance(box1, box2):
    (x, y) = box1
    (x2, y2) = box2
    return math.hypot(x2 - x, y2 - y)

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

def isSame(box1, box2):
    (x, y, w, h) = box1
    (x2, y2, w2, h2) = box2
    factor = euclidean_distance((x ,y), (x2, y2)) + abs(w2-w) + abs(h2-h)
    #print(factor)
    return factor < 100

def removeSameBox(frame1: list, frame2: list):
    if (len(frame1) > 0):
        removeIndex = []
        for box in frame2:
            removeIndex += [i for i, box2 in enumerate(frame1) if (isSame(box2, box))]
        frame1 = [ele for i, ele in enumerate(frame1) if i not in removeIndex]

def addDive(dives:list, boxData, frameNum):
    newDive = Dive()
    newDive.add(Box(boxData, frameNum))
    dives.append(newDive)

def extract(frames):
    active = []
    all = []
    for i in range(len(frames) - 1):
        current = frames[i]
        next = frames[i+1]
        removeSameBox(current, next)
        frames[i] = current

        if (i == 0):
            current = mergeBoxes(current)
            for box in current:
                addDive(active, box, i)
        else:
            if (len(current) > 0):
                picked = set([])
                for (i2, dive) in enumerate(active):
                    distances = [real_distance(dive.lastBox().size(), b) for b in current]
                    minDistance = min(distances)
                    if (minDistance < MIN_DISTANCE_OF_CLOSE):
                        minIndex = distances.index(minDistance)
                        picked.add(minIndex)
                        minBox = current[minIndex]
                        mergedSurrounding = mergeBoxes([b for b in current if canMerge(minBox, b)] + [minBox])
                        active[i2].add(Box(mergedSurrounding[0], i))

            #add non pick as new dive
            for ele in [box_ for i5, box_ in enumerate(current) if i5 not in picked]:
                addDive(active, ele, i)

            #remove inactive
            inactiveIndex = [i3 for i3, dive in enumerate(active) if not dive.isActive(i)]
            for index in inactiveIndex:
                all.append(active[index])

            active = [d for i6, d in enumerate(active) if i6 not in inactiveIndex]

    for dive in active:
        all.append(dive)

    return all