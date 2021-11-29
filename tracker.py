import cv2
import tracemalloc
from frame import *
import timeit
from tool import convert
import os

#paths = ['video/birds/Finca/13-Mayo/Green/GP011049.LRV']
paths = ['video/train/test1.mp4']

for path in paths:
    print(path)
    start = timeit.default_timer()
    tracemalloc.start()
    cap = cv2.VideoCapture(path)

    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height =int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    downSize = (int(frame_width/2), int(frame_height/2))
    fourcc = cv2.VideoWriter_fourcc('X','V','I','D')
    fps = cap.get(cv2.CAP_PROP_FPS)

    #out = cv2.VideoWriter('video/result/output' + path[16] + '.mp4', fourcc, 
    #                        fps, (frame_width,frame_height))

    ret, curr = cap.read()
    ret, next = cap.read()
    if frame_width >= BIG_WIDTH_LIMIT:
        curr = cv2.resize(curr, downSize, fx=0, fy=0, interpolation = cv2.INTER_CUBIC)
    firstFrame = curr.copy()

    '''s1 = (curr[heightDownLimit:heightUpLimit, 
            widthDownLimit:widthUpLimit]).copy()
    s2 = (next[heightDownLimit:heightUpLimit, 
                widthDownLimit:widthUpLimit]).copy()'''

    frameNum = 1
    active = []
    all = []

    while next is not None and frameNum <= length:
        print(frameNum, length)
        if frame_width >= BIG_WIDTH_LIMIT:
            curr = cv2.resize(curr, downSize, fx=0, fy=0, interpolation = cv2.INTER_CUBIC)
            next = cv2.resize(next, downSize, fx=0, fy=0, interpolation = cv2.INTER_CUBIC)

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
            
        extract(currentBoxes, active, all, frameNum, firstFrame.copy(), FEEDER)
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

        #cv2.imwrite("images/test+" + str(frameNum) + ".jpg", curr)
        curr = next
        ret, next = cap.read()
        
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
    divesRaw = processDives(all)
    originalFrame = firstFrame.copy()

    output_path = "output/" + path
    l = output_path.split('/')
    pa = '/'.join(l[:len(l)-1])
    if not os.path.exists(pa):
        os.makedirs(pa)
    
    with open(output_path + '.txt', 'w') as f:
        for index, dive in enumerate(divesRaw):
            color = randomColor()
            prev = None
            f.write('Dive' + str(index+1) + "\n")

            for d in dive.boxes():
                (x, y, w, h) = d.size()
                f.write(str(x) + ',' + str(y) + ',' + str(d.frameNumber()/fps) + "\n")
                '''cv2.rectangle(firstFrame, (x+widthDownLimit, y+heightDownLimit), 
                            (x+w+widthDownLimit, y+h+heightDownLimit), 
                            (color[0], color[1], color[2]), 2)'''
                cv2.circle(firstFrame, (x+int(w/2), y+int(h/2)), 7, (color[0], color[1], color[2]), -1)
                if (prev != None):
                    (x2, y2, w2, h2) = prev.size()
                    cv2.line(firstFrame, (x2+int(w2/2), y2+int(h2/2)), (x+int(w/2), y+int(h/2)), 
                            (color[0], color[1], color[2]), thickness=3, lineType=8)
                prev = d
            f.write('\n')
            cv2.imwrite("images/coordinates" + path[16] + '_' + str(index) +".jpg", firstFrame)
            firstFrame = originalFrame.copy()

    print("-------")
    currentMemory, peak = tracemalloc.get_traced_memory()
    print(f"Post: Current memory usage is {currentMemory / 10**6}MB; Peak was {peak / 10**6}MB")
    tracemalloc.stop()
    stop = timeit.default_timer()
    print('Time post: ', stop - start)