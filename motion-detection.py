import cv2
import numpy as np

'''
TODO:
1. merge box if they are close
2. select area
'''
videoPath = 'video/train/test.mp4'

cap = cv2.VideoCapture(videoPath)
frame_width = int( cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height =int( cap.get( cv2.CAP_PROP_FRAME_HEIGHT))
fourcc = cv2.VideoWriter_fourcc('X','V','I','D')
fps = cap.get(cv2.CAP_PROP_FPS)
out = cv2.VideoWriter('video/result/out.mp4', fourcc, fps, (frame_width,frame_height))

ret, frame1 = cap.read()
ret, frame2 = cap.read()

s1 = frame1[250: 650, 475: 1700]
s2 = frame2[250: 650, 475: 1700]

while cap.isOpened():
    diff = cv2.absdiff(s1, s2)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
    dilated = cv2.dilate(thresh, None, iterations=3)
    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        (x, y, w, h) = cv2.boundingRect(contour)

        if cv2.contourArea(contour) < 110:
            continue
        cv2.rectangle(frame1, (x+475, y+250), (x+w+475, y+h+250), (0, 255, 0), 2)
        #cv2.putText(frame1, "Status: {}".format('Movement'), (10, 20), cv2.FONT_HERSHEY_SIMPLEX,
                    #1, (0, 0, 255), 3)
    #cv2.drawContours(frame1, contours, -1, (0, 255, 0), 2)

    image = cv2.resize(frame1, (frame_width,frame_height))
    out.write(image)
    cv2.imshow("feed", frame1)
    cv2.imshow("select", s1)

    frame1 = frame2
    s1 = s2
    ret, frame2 = cap.read()
    s2 = frame2[250: 650, 475: 1700]

    if cv2.waitKey(40) == 27:
        break

def mergeBox(boxes):
    pass

cv2.destroyAllWindows()
cap.release()
out.release()