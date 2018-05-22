import numpy as np
from skimage import io, measure, morphology, restoration, filters
from skimage import img_as_float
import cv2
# import matplotlib.pyplot as plt
from collections import deque
import math
from imutils import perspective
from imutils import build_montages
from math import atan2,degrees


class LineFeatures():

    def __init__(self,l_midp,l_len,l_dir,l_cur,p1,p2):
        self.line_mid_point = l_midp
        self.line_len = l_len
        self.line_direction = l_dir
        self.line_curvyness = l_cur
        self.line_p1 = p1
        self.line_p2 = p2
    #float line_len
    #float normalized 0,1 (1=max curvyness) line_curvyness
    # direction of the sand Degree 0,180 line_direction
    #IntxInt line_mid_point


def getFeatures(img):

    features = []
    # img = cv2.imread('test2.png')
    font = cv2.FONT_HERSHEY_DUPLEX
    # gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    clahe = cv2.createCLAHE(clipLimit=1., tileGridSize=(8,8))
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    l2 = clahe.apply(l)
    lab = cv2.merge((l2,a,b))
    img2 = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)  # convert from LAB to BGR
    # cv2.imshow('Increased contrast', img2)

    hsv = cv2.cvtColor(img2,cv2.COLOR_RGB2HSV)
    h, s, v = cv2.split(hsv)
    # ret,thresh = cv2.threshold(gray,155,255,cv2.THRESH_BINARY)
    im = cv2.adaptiveThreshold(v, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 251, 2)
    kernel = np.ones((3,3),np.uint8)

    im = cv2.erode(im,kernel,iterations = 4)
    im = cv2.dilate(im,kernel,iterations = 4)
    im = cv2.erode(im,kernel,iterations = 5)

    #Find contours at a constant value of 0.8
    # contours1 = measure.find_contours(im, 0.8)
    image, contours, hierarchy = cv2.findContours(im,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    im = cv2.cvtColor(im, cv2.COLOR_GRAY2RGB)

    count = 0


    for cnt in contours:
        if cv2.contourArea(cnt) > 50 and cv2.contourArea(cnt) < 30000:
            p1 = Point(0,0)
            p2 = Point(0,0)
            # cv2.drawContours(im, contours, count, (0,0,255), 2)
            hull = cv2.convexHull(cnt)
            x,y,w,h = cv2.boundingRect(cnt)
            # cv2.rectangle(im,(x,y),(x+w,y+h),(0,255,0),2)
            rect = cv2.minAreaRect(cnt)
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            cv2.drawContours(im,[box],0,(0,0,255),2)
            a,b,c,d = box
            rect = perspective.order_points(box)
            box_side1 = distance(rect[0],rect[1])
            box_side2 = distance(rect[0],rect[3])
            if box_side1 < box_side2:

                p1.x = (rect[0][0] + rect[1][0])/2
                p1.y = (rect[0][1] + rect[1][1])/2
                p2.x = (rect[2][0] + rect[3][0])/2
                p2.y = (rect[2][1] + rect[3][1])/2
                line_len = box_side1
                #1 for max curvyness and ... 0 for straight line
                line_curvyness = 1/(box_side2/box_side1)
                # cv2.line(im, (midpoint1), (midpoint2), (0, 255, 0), thickness=3, lineType=8)
            else:
                p1.x = (rect[0][0] + rect[3][0])/2
                p1.y = (rect[0][1] + rect[3][1])/2
                p2.x = (rect[2][0] + rect[1][0])/2
                p2.y = (rect[2][1] + rect[1][1])/2
                line_len = box_side2
                line_curvyness = 1/(box_side1/box_side2)

            p1.x = np.int0(p1.x)
            p1.y = np.int0(p1.y)
            p2.x  = np.int0(p2.x)
            p2.y = np.int0(p2.y)

            boxArea = box_side1 * box_side2
            area_proportion = 1
            if boxArea > (area_proportion*cv2.contourArea(cnt)):
                if boxArea < 50000:
                    line_angle = GetAngleOfLineBetweenTwoPoints(p1,p2)
                    line_mid_point = GetMidPoint(p1,p2)
                    line_features = LineFeatures(line_mid_point,line_len,line_angle,line_curvyness,p1,p2)
                    # print 'p1: %f%f P2: %f%f' %(p1.x,p1.y,p2.x,p2.y)
                    # print line_angle
                    # line_features.__init__(line_mid_point,line_len,line_angle,line_curvyness)
                    features.append(line_features)
                    im = cv2.line(im, (p1.x,p1.y), (p2.x,p2.y), (0,255,0),4)
                    # cv2.putText(im,str(cv2.contourArea(cnt)),(p1.x+5,p1.y+5), font, 0.8,(0,0,255),2,cv2.LINE_AA)
            count += 1
    # get mix image real and filtered
    # stencil = np.zeros(im.shape).astype(im.dtype)
    # color = [255, 255, 255]
    # cv2.fillPoly(stencil, contours, color)
    # result = cv2.bitwise_and(img2, stencil)
    return features,im

def distance(p1,p2):
    distance = math.sqrt( ((p1[0]-p2[0])**2)+((p1[1]-p2[1])**2) )
    return distance

def GetAngleOfLineBetweenTwoPoints(p1, p2):
        xDiff = p2.x - p1.x
        yDiff = p2.y - p1.y
        # print degrees(atan2(yDiff, xDiff))
        return degrees(atan2(yDiff, xDiff))



def GetMidPoint(p1,p2):
    midx = (p1.x+p2.x)/2
    midy = (p1.y+p2.y)/2
    mid_point = Point(midx,midy)

    return mid_point

class Point():
    def __init__(self,x=None,y=None):
        self.x = x or 0
        self.y = y or 0
# cv2.imwrite("result.jpg", result)
# images = []
# images.append(im)
# images.append(img)
# montages = build_montages(images, (800, 600), (2, 1))
# for montage in montages:
# 	cv2.imshow("Montage", montage)
#
#
#
# cv2.waitKey(0)
# cv2.destroyAllWindows()
