import cv2 as cv
import numpy as np
import math as m

def angleFromHorizontal(vector):
    y = vector[1] - vector[3]
    x = vector[0] - vector[2]
    return m.degrees(m.atan(y/x))

def whichQuarter(img, vector):
    x = vector[0]
    y = vector[1]
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


img = cv.imread('../Mennyi_az_ido/faliora.jpg', cv.IMREAD_GRAYSCALE)
cdst = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
print(img.shape)

cv.imshow('ora', img)
black = np.zeros(cdst.shape)

segment = cv.inRange(cdst, (0, 0, 0), (255, 255, 110))

# blur = cv.medianBlur(img, 11)
canny = cv.Canny(img, 50, 200)
# cv. imshow('canny', canny)

lines = cv.HoughLines(segment, 1, np.pi/180, 100, None, 0, 0)
print('detektalt egyenesek szama: ', len(lines))

sizemax = m.sqrt(canny.shape[0] ** 2 + canny.shape[1] ** 2)
for i in range(len(lines)):
    rho = lines[i][0][0]
    theta = lines[i][0][1]
    a = m.cos(theta)
    b = m.sin(theta)
    x0 = a*rho
    y0 = b*rho
    pt1 = (int(x0 + sizemax * (-b)), int(y0 + sizemax * a))
    pt2 = (int(x0 - sizemax * (-b)), int(y0 - sizemax * a)) 
    cv.line(cdst, pt1, pt2, (0, 0, 255), 3, cv.LINE_AA)


linesP = cv.HoughLinesP(canny, 1, np.pi/180, 50, None, 60, 10)
print(len(linesP))
with open('linesP.txt', 'w') as f:
    f.write(str(linesP))
for i in range(0, len(linesP)):
        l = linesP[i][0]
        print(l)
        print('angle: ', angleFromHorizontal(l))
        print('quarter: ', whichQuarter(black, l))
        cv.line(black, (l[0], l[1]), (l[2], l[3]), (0, 255, 0), 3, cv.LINE_AA)

l = linesP[3][0]
cv.line(black, (l[0], l[1]), (l[2], l[3]), (255, 0, 0), 3, cv.LINE_AA)

cv.imshow('segment', canny)
cv.imshow('hough', cdst)
cv.imshow('black', black)
cv.waitKey()
cv.destroyAllWindows()