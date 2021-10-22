import math
from tool import *

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

def addDive(dives:list, boxData, frameNum):
    newDive = Dive()
    newDive.add(Box(boxData, frameNum))
    dives.append(newDive)

def processDives(dives):
    p = [d for d in dives if d.size() > 3]
    return p

def extract(frames:list, currentFrame):
    active = []
    all = []
    for i in range(len(frames)):
        current = frames[i]

        '''
        firstFrame = currentFrame.copy()
        rawPic = currentFrame.copy()
        draw(rawPic, current, i)'''

        if (i == 0):
            current = mergeBoxes(current)
            for box in current:
                addDive(active, box, i)
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
                        active[i2].add(Box(merge[0], i))

            #add non pick as new dive
            for ele in [box_ for i5, box_ in enumerate(current) if i5 not in picked]:
                addDive(active, ele, i)

            #remove inactive
            inactiveIndex = [i3 for i3, dive in enumerate(active) if not dive.isActive(i)]
            all += [active[ele] for ele in inactiveIndex]
            active = [d for i6, d in enumerate(active) if i6 not in inactiveIndex]

            '''for index, dive in enumerate(active):
                color = randomColor()
                prev = None
                for d in dive.boxes():
                    (x, y, w, h) = d.size()
                    cv2.rectangle(firstFrame, (x+widthDownLimit, y+heightDownLimit), (x+w+widthDownLimit, y+h+heightDownLimit), 
                                (color[0], color[1], color[2]), 2)
                    if (prev != None):
                        (x2, y2, w2, h2) = prev.size()
                        cv2.line(firstFrame, (x2+int(w2/2), y2+int(h2/2)), (x+int(w/2), y+int(h/2)), 
                                (color[0], color[1], color[2]), thickness=3, lineType=8)
                    prev = d
            cv2.imwrite("images/coordinates_" + str(i) + ".jpg", firstFrame)'''
            
    all += active
    return processDives(all)