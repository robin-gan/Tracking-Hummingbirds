import cv2
import numpy as np
import tracemalloc
import sys
from frame import *

tracemalloc.start()

VIDEO_PATH = 'video/train/test1.mp4'
BOX_BORDER_COLOR = (111, 0, 51)

cap = cv2.VideoCapture(VIDEO_PATH)

frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height =int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fourcc = cv2.VideoWriter_fourcc('X','V','I','D')
fps = cap.get(cv2.CAP_PROP_FPS)

out = cv2.VideoWriter('video/result/output.mp4', fourcc, 
                        fps, (frame_width,frame_height))

ret, frame1 = cap.read()
ret, frame2 = cap.read()

firstFrame = frame1

heightUpLimit = 650
heightDownLimit = 250
widthUpLimit = 1700
widthDownLimit = 475

s1 = (frame1[heightDownLimit:heightUpLimit, 
        widthDownLimit:widthUpLimit]).copy()
s2 = (frame2[heightDownLimit:heightUpLimit, 
            widthDownLimit:widthUpLimit]).copy()

frames = []
frameNum = 1

while cap.isOpened():
    currentFrame = Frame(frameNumber=frameNum)

    diff = cv2.absdiff(s1, s2)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
    dilated = cv2.dilate(thresh, None, iterations=3)
    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    raw = []
    for contour in contours:
        (x, y, w, h) = cv2.boundingRect(contour)
        if cv2.contourArea(contour) > 100:
            raw.append((x, y, w, h))
            #cv2.rectangle(frame1, (x+widthDownLimit, y+heightDownLimit), 
                        #(x+w+widthDownLimit, y+h+heightDownLimit), (0,255,0), 2)
            
    #merged = mergeBoxes(raw)
    merged = raw
    currentFrame.setBoxes(merged)
    for b in merged:
        (x, y, w, h) = b
        cv2.rectangle(frame1, (x+widthDownLimit, y+heightDownLimit), 
                        (x+w+widthDownLimit, y+h+heightDownLimit), BOX_BORDER_COLOR, 2)
         #cv2.drawContours(frame1, contours, -1, BOX_BORDER_COLOR, 2)
    frameNum += 1
    frames.append(currentFrame)
    out.write(frame1)

    try:
        cv2.imshow("feed", frame1)
    except:
        break 

    frame1 = frame2
    s1 = s2

    ret, frame2 = cap.read()
    if frame2 is not None:
        s2 = (frame2[heightDownLimit:heightUpLimit, widthDownLimit:widthUpLimit]).copy()
    
    if cv2.waitKey(40) == 27:
        break

current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage is {current / 10**6}MB; Peak was {peak / 10**6}MB")
tracemalloc.stop()

#draw the coordinates
for frame in frames:
    for box in frame.getBoxes():
        (x, y, w, h) = box
        cv2.rectangle(firstFrame, (x+widthDownLimit, y+heightDownLimit), 
                    (x+w+widthDownLimit, y+h+heightDownLimit), BOX_BORDER_COLOR, 2)

cv2.imwrite("coordinates.jpg",firstFrame)
cv2.destroyAllWindows()
cap.release()
out.release()