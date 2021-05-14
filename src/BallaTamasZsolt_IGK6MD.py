import cv2 as cv
import numpy as np
import math as m
import sys

def filter(array, precision=0):
    ret = set()
    for i in range(len(array)):
        ret.add(round(array[i], precision))
    return ret

def addToSetWithThreshold(pSet, pValue, angleTreshold):
    vList = [entry for entry in pSet if abs(pValue[0] - entry[0]) < angleTreshold and pValue[2] == entry[2]]
    if len(vList) == 0:
        pSet.add(pValue)

def cluster(lines, angleTreshold):
    pointers = set()
    pointers.add(lines[0])
    for line in lines:
        addToSetWithThreshold(pointers, line, angleTreshold)
    return pointers

def angleFromHorizontal(vector):
    y = vector[1] - vector[3]
    x = vector[0] - vector[2]
    if(x != 0.0):
        return m.degrees(m.atan(y*1.0/x))
    return 0.0

def distanceFromMiddle(img, point):
    middleX = img.shape[1]/2
    middleY = img.shape[0]/2
    return m.sqrt((middleX-point[0])**2 + (middleY-point[1])**2)

def vectorLength(vector):
    return m.sqrt((vector[0]-vector[2])**2 + (vector[1]-vector[3])**2)

def whichQuarter(img, vector):
    distP1 = distanceFromMiddle(img, (vector[0], vector[1]))
    distP2 = distanceFromMiddle(img, (vector[2], vector[3]))
    # print("dist1: " + str(distP1) + ", dist2: " + str(distP2))
    if(distP1 > distP2):
        x = vector[0]
        y = vector[1]
    else:
        x = vector[2]
        y = vector[3]
    
    h = img.shape[0]
    w = img.shape[1]
    if(y <= h/2 and x < w/2):
        return 4
    elif(y < h/2 and x >= w/2):
        return 1
    elif(y >= h/2 and x >= w/2):
        return 2
    elif(y > h/2 and x < w/2):
        return 3

def minutes(angle, quarter):
    if(quarter is 1):
        minute = abs(abs(angle)/6-15)
    elif(quarter is 2):
        minute = angle/6+15
    elif(quarter is 3):
        minute = abs(abs(angle)/6-15)+30
    elif(quarter is 4):
        minute = angle/6+45
    if minute == 60:
        minute = 0
    return minute

def hour(angle, quarter):
    if(quarter is 1):
        hour = abs(abs(angle)/30-3)
    elif(quarter is 2):
        hour = angle/30+3
    elif(quarter is 3):
        hour = abs(abs(angle)/30-3)+6
    elif(quarter is 4):
        hour = angle/30+9
    if hour == 0:
        hour = 12
    return hour

def sortHelp(line):
    return line[1]

def time(pointers):
    ret = sorted(pointers, key=sortHelp)
    # print(ret)
    return (round(hour(ret[0][0], ret[0][2])), round(minutes(ret[1][0], ret[1][2])))

def reinit():
    global img, cdst, black, segment, canny
    
    cdst = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
    # print(img.shape)
    img = cv.medianBlur(img, 7)
    #cv.imshow('ora', img)
    black = np.zeros(cdst.shape)
    segment = cv.inRange(cdst, (0, 0, 0), (255, 255, 110))
    #blur = cv.medianBlur(img, 11)
    canny = cv.Canny(img, 50, 200)
    # cv. imshow('canny', canny)
    cv.imshow('image', img)

def recalculateLines():
    global minLineLength, black
    minutesCalculated = []
    lengths = []
    angles = []
    lines = []

    linesP = cv.HoughLinesP(segment, 1, np.pi/90, 50, None, minLineLength, 10) 
    # print(len(linesP))
    # with open('linesP.txt', 'w') as f:
    #     f.write(str(linesP))

    if linesP is not None:
        for i in range(0, len(linesP)):
                l = linesP[i][0]
                # print(l)
                angle = angleFromHorizontal(l)
                quarter = whichQuarter(black, l)
                minute = minutes(angle, quarter)
                length = vectorLength(l)
                minutesCalculated.append(minute)
                lengths.append(length)
                angles.append(angle)
                lines.append((angle, length, quarter))
                
                cv.line(black, (l[0], l[1]), (l[2], l[3]), (0, 255, 0), 3, cv.LINE_AA)

    pointers = []
    if len(lines) != 0:
        pointers = cluster(lines, 3)

    if(len(pointers) > 3 or len(pointers) < 2):
        print("Can't tell the time!")
    else:
        timeOnClock = time(pointers)
        print(str(timeOnClock[0])+":" + str(timeOnClock[1]))

def setMinLineLength(trackPos):
    global minLineLength, black, cdst
    minLineLength = trackPos
    black = np.ndarray(cdst.shape)
    #cv.imshow('black', black)
    recalculateLines()

def changePicture(pic):
    global img
    img = cv.imread('../Mennyi_az_ido/' + pic, cv.IMREAD_GRAYSCALE)
    reinit()

def test():
    global minLineLength
    print('faliora.jpg:')
    changePicture('faliora.jpg')
    setMinLineLength(50)
    print('faliora5.jpg')
    changePicture('faliora5.jpg')
    setMinLineLength(100)
    print('faliora7.jpg')
    changePicture('faliora7.jpg')
    setMinLineLength(50)
    print('faliora9.png')
    changePicture('faliora9.png')
    setMinLineLength(50)
    print('faliora11.jpg')
    changePicture('faliora11.jpg')
    setMinLineLength(220)
    print('sp_noise.jpg')
    changePicture('sp_noise.jpg')
    setMinLineLength(200)
    


try:
    if sys.argv[1] == 'test':
        test()
except:
    img = cv.imread('../Mennyi_az_ido/faliora11.jpg', cv.IMREAD_GRAYSCALE)
    minLineLength = 220
    reinit()
    cv.namedWindow('GUI')
    cv.createTrackbar('min. line length', 'GUI', 1, 300, setMinLineLength)
    recalculateLines() 

    while True:
        key = cv.waitKey()
        if key & 0xFF == ord('q') or key == 27:
            break
        if key & 0xFF == ord('1'):
            changePicture('faliora.jpg')
        if key & 0xFF == ord('2'):
            changePicture('faliora5.jpg')
        if key & 0xFF == ord('3'):
            changePicture('faliora9.png')
        if key & 0xFF == ord('4'): 
            changePicture('faliora7.jpg')
        if key & 0xFF == ord('5'): 
            changePicture('faliora11.jpg')
        if key & 0xFF == ord('6'):
            changePicture('sp_noise.jpg')

cv.destroyAllWindows()