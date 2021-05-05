import cv2 as cv
import numpy as np
import math as m
from numpy.core.fromnumeric import sort

from numpy.core.numeric import Infinity

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
    # print("in cluster: " + str(pointers))
    # for pointer in pointers.copy():
    #     for line in lines:
    #         if(abs(line[0] - pointer[0]) > angleTreshold or abs(line[1] - pointer[1]) > lengthTreshold or line[2] != pointer[2]):
    #             print(abs(line[0] - pointer[0]) > angleTreshold)
    #             print("angle: " + str(line[0]) + " pointer: " + str(pointer[0]))
    #             print("angletresh: " + str(abs(line[0] - pointer[0])) + ">" + str(angleTreshold))
    #             print(abs(line[1] - pointer[1]) > lengthTreshold)
    #             print(line[2] != pointer[2])
    #             pointers.add(line)
    for line in lines:
        addToSetWithThreshold(pointers, line, angleTreshold)
    return pointers


    

def angleFromHorizontal(vector):
    y = vector[1] - vector[3]
    x = vector[0] - vector[2]
    if(x is not 0.0):
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
    print("dist1: " + str(distP1) + ", dist2: " + str(distP2))
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
    return hour

def sortHelp(line):
    return line[1]

def time(pointers):
    ret = sorted(pointers, key=sortHelp)
    print(ret)
    return (round(hour(ret[0][0], ret[0][2])), round(minutes(ret[1][0], ret[1][2])))

img = cv.imread('../Mennyi_az_ido/faliora11.jpg', cv.IMREAD_GRAYSCALE)
cdst = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
print(img.shape)

img = cv.medianBlur(img, 7)
cv.imshow('ora', img)
black = np.zeros(cdst.shape)

segment = cv.inRange(cdst, (0, 0, 0), (255, 255, 110))

# blur = cv.medianBlur(img, 11)
canny = cv.Canny(img, 50, 200)
# cv. imshow('canny', canny)

# lines = cv.HoughLines(segment, 1, np.pi/180, 100, None, 0, 0)
# print('detektalt egyenesek szama: ', len(lines))

# sizemax = m.sqrt(canny.shape[0] ** 2 + canny.shape[1] ** 2)
# for i in range(len(lines)):
#     rho = lines[i][0][0]
#     theta = lines[i][0][1]
#     a = m.cos(theta)
#     b = m.sin(theta)
#     x0 = a*rhofali
#     y0 = b*rho
#     pt1 = (int(x0 + sizemax * (-b)), int(y0 + sizemax * a))
#     pt2 = (int(x0 - sizemax * (-b)), int(y0 - sizemax * a)) 
#     cv.line(cdst, pt1, pt2, (0, 0, 255), 3, cv.LINE_AA)


linesP = cv.HoughLinesP(segment, 1, np.pi/90, 50, None, 220, 10) 
print(len(linesP))
with open('linesP.txt', 'w') as f:
    f.write(str(linesP))

minutesCalculated = []
lengths = []
angles = []
lines = []
for i in range(0, len(linesP)):
        l = linesP[i][0]
        print(l)
        angle = angleFromHorizontal(l)
        quarter = whichQuarter(black, l)
        minute = minutes(angle, quarter)
        length = vectorLength(l)
        minutesCalculated.append(minute)
        lengths.append(length)
        angles.append(angle)
        lines.append((angle, length, quarter))
        print('angle: ' + str(round(angle, 3)))
        print('quarter: ' + str(quarter))
        print('minute: '+ str(minute))
        
        cv.line(black, (l[0], l[1]), (l[2], l[3]), (0, 255, 0), 3, cv.LINE_AA)

print("unique minutes: " + str(filter(minutesCalculated)))
print("unique lengths: " + str(filter(lengths, 2)))
print("unique angles :" + str(filter(angles, 0)))
print("lines: " + str(lines))
pointers = cluster(lines, 3)
print("number of pointers: " + str(len(pointers)))
print("pointers: " + str(pointers))
print("################ TIME ################")
timeOnClock = time(pointers)
print(str(timeOnClock[0])+":" + str(timeOnClock[1]))
#l = linesP[3][0]
# cv.line(black, (l[0], l[1]), (l[2], l[3]), (255, 0, 0), 3, cv.LINE_AA)

# print('first quarter angle: ' + str(angleFromHorizontal([150, 150, 140, 160])))
# print('second quarter angle:' + str(angleFromHorizontal([150, 150, 160, 160])))
# print('third quarter angle:' + str(angleFromHorizontal([150, 150, 160, 140])))
# print('fourth quarter angle:' + str(angleFromHorizontal([150, 150, 140, 140])))


cv.imshow('segment', canny)
cv.imshow('hough', cdst)
cv.imshow('black', black)
cv.waitKey()
cv.destroyAllWindows()