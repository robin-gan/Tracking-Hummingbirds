import cv2
import tracemalloc
from frame import *
import timeit
from tool import convert

start = timeit.default_timer()
tracemalloc.start()

VIDEO_PATH = 'video/train/test1.mp4'

cap = cv2.VideoCapture(VIDEO_PATH)

length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height =int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fourcc = cv2.VideoWriter_fourcc('X','V','I','D')
fps = cap.get(cv2.CAP_PROP_FPS)

#out = cv2.VideoWriter('video/result/output' + VIDEO_PATH[16] + '.mp4', fourcc, 
#                        fps, (frame_width,frame_height))

ret, curr = cap.read()
ret, next = cap.read()
firstFrame = curr.copy()

'''s1 = (curr[heightDownLimit:heightUpLimit, 
        widthDownLimit:widthUpLimit]).copy()
s2 = (next[heightDownLimit:heightUpLimit, 
            widthDownLimit:widthUpLimit]).copy()'''

frameNum = 1
active = []
all = []

while next is not None and frameNum <= length:
    diff = cv2.absdiff(curr, next)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
    dilated = cv2.dilate(thresh, None, iterations=3)
    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    currentBoxes = []
    for contour in contours:
        (x, y, w, h) = cv2.boundingRect(contour)
        if cv2.contourArea(contour) > 100:
            currentBoxes.append((x, y, w, h))
            #cv2.rectangle(curr, (x+widthDownLimit, y+heightDownLimit), 
                        #(x+w+widthDownLimit, y+h+heightDownLimit), (0,255,0), 2)
            
    extract(currentBoxes, active, all, frameNum)
    frameNum += 1

    '''for b in currentBoxes:
        (x, y, w, h) = b
        cv2.rectangle(curr, (x+widthDownLimit, y+heightDownLimit), 
                        (x+w+widthDownLimit, y+h+heightDownLimit), BOX_BORDER_COLOR, 2)
         #cv2.drawContours(curr, contours, -1, BOX_BORDER_COLOR, 2)
    print(convert(frameNum / fps))
    print(frameNum, length)
    print("----------")'''
    #out.write(curr)
    '''try:
        cv2.imshow("feed", curr)
    except:
        break'''

    curr = next
    #s1 = s2

    ret, next = cap.read()
    #if next is not None:
        #s2 = (next[heightDownLimit:heightUpLimit, widthDownLimit:widthUpLimit]).copy()
    
    #if cv2.waitKey(40) == 27:
        #break

cv2.destroyAllWindows()
cap.release()
#out.release()

currentMemory, peak = tracemalloc.get_traced_memory()
print(f"Video: Current memory usage is {currentMemory / 10**6}MB; Peak was {peak / 10**6}MB")
tracemalloc.stop()
stop = timeit.default_timer()
print('Time video: ', stop - start)

#----post process-----
start = timeit.default_timer()
tracemalloc.start()

all += active
print(len(all))
divesRaw = processDives(all)
lens = [len(d.boxes()) for d in divesRaw]
dives2 = [divesRaw[lens.index(max(lens))]]

originalFrame = firstFrame.copy()
for i, dives in enumerate([divesRaw, dives2]):
    for index, dive in enumerate(dives):
        color = randomColor()
        prev = None
        for d in dive.boxes():
            (x, y, w, h) = d.size()
            cv2.rectangle(firstFrame, (x+widthDownLimit, y+heightDownLimit), 
                        (x+w+widthDownLimit, y+h+heightDownLimit), 
                        (color[0], color[1], color[2]), 2)
            if (prev != None):
                (x2, y2, w2, h2) = prev.size()
                cv2.line(firstFrame, (x2+int(w2/2), y2+int(h2/2)), (x+int(w/2), y+int(h/2)), 
                        (color[0], color[1], color[2]), thickness=3, lineType=8)
            prev = d

    #cv2.imwrite("images/coordinates_" + str(index) + ".jpg", firstFrame)
    cv2.imwrite("coordinates" + VIDEO_PATH[16]+ "_" + str(i) + ".jpg",firstFrame)
    firstFrame = originalFrame

print("-------")
currentMemory, peak = tracemalloc.get_traced_memory()
print(f"Post: Current memory usage is {currentMemory / 10**6}MB; Peak was {peak / 10**6}MB")
tracemalloc.stop()
stop = timeit.default_timer()
print('Time post: ', stop - start)