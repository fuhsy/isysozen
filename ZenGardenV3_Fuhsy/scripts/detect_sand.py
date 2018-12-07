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
import detect_stones as dstones

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


def getFeatures(img,contour_value):

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
    blob_im = im.copy()
    # cv2.imshow("inside_detect_sand",im)
    # cv2.waitKey(0)
    im = cv2.erode(im,kernel,iterations = contour_value)
    im = cv2.dilate(im,kernel,iterations = contour_value)
    im = cv2.erode(im,kernel,iterations = contour_value)

    blob_im = cv2.erode(blob_im,kernel,iterations = 15)
    blob_im = cv2.dilate(blob_im,kernel,iterations = 15)
    hsv2rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
    # hsvim = cv2.merge((h,s,blob_im))
    stone_features = dstones.blob_detection(blob_im,img,hsv)

    color_im = cv2.cvtColor(im,cv2.COLOR_GRAY2RGB)
    noisy_area = 5
    for feat in stone_features:
        cv2.circle(color_im,(feat.center),(feat.radius+noisy_area),(0,0,0),-1)

    
    return stone_features,color_im
def color_stones(color_im,stone_features):
    noisy_area = 5
    font = cv2.FONT_HERSHEY_SIMPLEX
    for feat in stone_features:
        cv2.circle(color_im,(feat.center),(feat.radius+noisy_area),(0,0,0),-1)
        if feat.theme == 'RED':
            cv2.circle(color_im,(feat.center),(feat.radius),(41,41,150),-1)
            cv2.putText(color_im,'FIRE',(feat.center[0]-20,feat.center[1]), font, 0.5,(255,255,255),1,cv2.LINE_AA)
        elif feat.theme == 'BLUE':
            cv2.circle(color_im,(feat.center),(feat.radius),(150,41,20),-1)
            cv2.putText(color_im,'SEA',(feat.center[0]-20,feat.center[1]), font, 0.5,(255,255,255),1,cv2.LINE_AA)
        elif feat.theme == 'GREEN':
            cv2.circle(color_im,(feat.center),(feat.radius),(41,100,41),-1)
            cv2.putText(color_im,'FOREST',(feat.center[0]-30,feat.center[1]), font, 0.5,(255,255,255),1,cv2.LINE_AA)
    return color_im
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
