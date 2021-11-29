import math
from tool import *

#FEEDER = [(766, 383, 136, 178)]
FEEDER = []

class Box:
    def __init__(self, data, frame):
        self.data = data
        self.frame = frame

    def frameNumber(self):
        return self.frame

    def size(self):
        return self.data

    def diagonal(self):
        (x, y, w, h) = self.data
        return math.hypot(w, h)

class Dive:
    def __init__(self):
        self.points = []
        self.distance = 0
        self.isTouchFeeder = True
        self.absoluteDistance = 0.0
        self.boundary = None

    def add(self, value, feeders):
        if self.boundary == None:
            (x, y, w, h) = value.size()
            self.boundary = [y, y+h, x, x+w]
        self.boundary = calcCurrentBoundary(self.boundary, value.size())
        if len(self.points) > 0:
            self.absoluteDistance += euclidean_distance_4(value.size(), self.points[-1].size())
        self.points.append(value)
        for feeder in feeders:
            if real_distance(value.size(), feeder) < FEEDER_CLOSE:
                self.isTouchFeeder = True

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

    def isTouched(self) -> bool:
        return self.isTouchFeeder
    
    def getAbsDis(self) -> float:
        return self.absoluteDistance

    def getMovingArea(self):
        factor = ((self.boundary[1] - self.boundary[0]) * (self.boundary[3] - self.boundary[2]))
        return factor

def addDive(dives:list, boxData, frameNum, feeders):
    newDive = Dive()
    newDive.add(Box(boxData, frameNum), feeders)
    dives.append(newDive)

def detectDuplicates(i, i2, divesList):
    bigger, smaller = [], []
    if divesList[i].size() > divesList[i2].size():
        bigger, smaller = i, i2
    else:
        bigger, smaller = i2, i
    c, smallerLength = 0, divesList[smaller].size()
    smallerBoxes = [b.size() for b in divesList[smaller].boxes()]
    biggerBoxes = [b.size() for b in divesList[bigger].boxes()]
    for d in smallerBoxes:
        if d in biggerBoxes:
            c += 1
        if c / smallerLength >= DUPLICATE_RATE:
            return [smaller]
    return [smaller, bigger]

def removeDuplicated(dives):
    duplicateIndex = []
    if len(dives) > 1:
        for i, dive1 in enumerate(dives):
            if i not in duplicateIndex:
                for i2, dive2 in enumerate(dives):
                    if i != i2 and i2 not in duplicateIndex:
                        duplicate = detectDuplicates(i, i2, dives)
                        if len(duplicate) == 1:
                            duplicateIndex.append(duplicate[0])
                            if duplicate[0] == i:
                                break
    non_duplicate = [d for i, d in enumerate(dives) if i not in duplicateIndex]
    return non_duplicate

def processDives(dives):
    long = [d for d in dives if d.size() > DIVE_LENGTH_LIMIT]
    non_duplicate = removeDuplicated(long)
    touched = [d for d in non_duplicate if d.isTouched()]
    dis = [d for d in touched if d.getAbsDis() > ABSOLUTE_DISTANCE_LIMIT]
    p = [d for d in dis if d.getMovingArea() > MOVING_AREA_LIMIT]
    return p

def extract(current, active, all, frameNumber, drawFrame, feeders):
    '''
    firstFrame = currentFrame.copy()
    rawPic = currentFrame.copy()
    draw(rawPic, current, i)'''

    if (frameNumber == 1):
        current = mergeBoxes(current)
        for box in current:
            addDive(active, box, frameNumber, feeders)
    else:
        if (len(current) > 0):
            picked = []
            for (i2, dive) in enumerate(active):
                lastBox = dive.lastBox()
                distances = [real_distance(lastBox.size(), b) for b in current]
                minDistance = min(distances)
                if (minDistance < MIN_DISTANCE_OF_CLOSE):
                    minIndex = distances.index(minDistance)
                    picked.append(minIndex)
                    minBox = current[minIndex]
                    merge = mergeBoxes([b for b in current if canMerge(minBox, b)] + [minBox])
                    active[i2].add(Box(merge[0], frameNumber), feeders)

        #add non pick as new dive
        for ele in [box_ for i5, box_ in enumerate(current) if i5 not in picked]:
            addDive(active, ele, frameNumber, feeders)

        #remove inactive
        inactiveIndex = [i3 for i3, dive in enumerate(active) if not dive.isActive(frameNumber)]
        all += [active[ele] for ele in inactiveIndex]
        active[:] = [d for i6, d in enumerate(active) if i6 not in inactiveIndex]

        '''for index, dive in enumerate(active):
            color = randomColor()
            prev = None
            for d in dive.boxes():
                (x, y, w, h) = d.size()
                cv2.rectangle(drawFrame, (x+widthDownLimit, y+heightDownLimit), (x+w+widthDownLimit, y+h+heightDownLimit), 
                            (color[0], color[1], color[2]), 2)
                if (prev != None):
                    (x2, y2, w2, h2) = prev.size()
                    cv2.line(drawFrame, (x2+int(w2/2), y2+int(h2/2)), (x+int(w/2), y+int(h/2)), 
                            (color[0], color[1], color[2]), thickness=3, lineType=8)
                prev = d
        cv2.imwrite("images/coordinates_" + str(frameNumber) + ".jpg", drawFrame)'''