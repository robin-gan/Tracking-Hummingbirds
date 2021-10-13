import cv2
import numpy as np
import tracemalloc
import sys

tracemalloc.start()

videoPath = 'video/train/test1.mp4'

cap = cv2.VideoCapture(videoPath)

frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height =int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fourcc = cv2.VideoWriter_fourcc('X','V','I','D')
fps = cap.get(cv2.CAP_PROP_FPS)

out = cv2.VideoWriter('video/result/output.mp4', fourcc, fps, (frame_width,frame_height))

ret, frame1 = cap.read()
ret, frame2 = cap.read()

firstFrame = frame1

heightUpLimit = 650
heightDownLimit = 250
widthUpLimit = 1700
widthDownLimit = 475

s1 = frame1[heightDownLimit: heightUpLimit, widthDownLimit: widthUpLimit]
s2 = frame2[heightDownLimit: heightUpLimit, widthDownLimit: widthUpLimit]

frames = []
frameNum = 1

class Frame:
    def __init__(self, frameNumber):
        self.number = frameNumber
        self.boxes = []
    def add(self, boxData):
        self.boxes.append(boxData)
    def getBoxes(self):
        return self.boxes

def mergeBoxes(boxes):
    for box in boxes:
        (x, y, w, h) = cv2.boundingRect(box)
    #    print((x, y, w, h))
    #print('---------')

while cap.isOpened():
    currentFrame = Frame(frameNumber=frameNum)

    diff = cv2.absdiff(s1, s2)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
    dilated = cv2.dilate(thresh, None, iterations=3)

    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    mergeBoxes(contours)

    for contour in contours:
        (x, y, w, h) = cv2.boundingRect(contour)
        if cv2.contourArea(contour) > 105:
            currentFrame.add((x, y, w, h))
            cv2.rectangle(frame1, (x+widthDownLimit, y+heightDownLimit), (x+w+widthDownLimit, y+h+heightDownLimit), (0, 255, 0), 2)
        #cv2.putText(frame1, "Status: {}".format('Movement'), (10, 20), cv2.FONT_HERSHEY_SIMPLEX,
                    #1, (0, 0, 255), 3)
    #cv2.drawContours(frame1, contours, -1, (0, 255, 0), 2)

    frameNum += 1
    frames.append(currentFrame)
    #image = cv2.resize(frame1, (frame_width,frame_height))
    image = frame1
    out.write(image)

    try:
        cv2.imshow("feed", frame1)
    except:
        break 

    frame1 = frame2
    s1 = s2
    ret, frame2 = cap.read()

    if frame2 is not None:
        s2 = frame2[heightDownLimit: heightUpLimit, widthDownLimit: widthUpLimit]
    
    if cv2.waitKey(40) == 27:
        break

current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage is {current / 10**6}MB; Peak was {peak / 10**6}MB")
tracemalloc.stop()

#draw the coordinates
for frame in frames:
    for box in frame.getBoxes():
        (x, y, w, h) = box
        cv2.rectangle(firstFrame, (x+widthDownLimit, y+heightDownLimit), (x+w+widthDownLimit, y+h+heightDownLimit), (0, 255, 0), 2)

cv2.imwrite("frame.jpg",firstFrame)

cv2.destroyAllWindows()

cap.release()
out.release()