import numpy as np
from skimage import io, measure, morphology, restoration, filters
from skimage import img_as_float
import cv2
import matplotlib.pyplot as plt
from collections import deque
import math
from math import atan2,degrees
from imutils import perspective
from imutils import build_montages
import path_finder as pf
import detect_sand as ds
import pylibfreenect2

im = cv2.imread('test1.png')
# print math.degrees(math.acos(5,5))
print math.cos(360)
# font = cv2.FONT_HERSHEY_DUPLEX
# # gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
#
# clahe = cv2.createCLAHE(clipLimit=1., tileGridSize=(8,8))
# lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
# l, a, b = cv2.split(lab)
# l2 = clahe.apply(l)
# lab = cv2.merge((l2,a,b))
# img2 = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)  # convert from LAB to BGR
# # cv2.imshow('Increased contrast', img2)
#
#
# hsv = cv2.cvtColor(img2,cv2.COLOR_RGB2HSV)
# h, s, v = cv2.split(hsv)
# # ret,thresh = cv2.threshold(gray,155,255,cv2.THRESH_BINARY)
# im = cv2.adaptiveThreshold(v, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 201, 2)
# kernel = np.ones((3,3),np.uint8)
#
# im = cv2.erode(im,kernel,iterations = 4)
# im = cv2.dilate(im,kernel,iterations = 4)
# im = cv2.erode(im,kernel,iterations = 5)
#
#
#
# # Construct some test data
#
# def distance(p1,p2):
#     distance = math.sqrt( ((p1[0]-p2[0])**2)+((p1[1]-p2[1])**2) )
#     return distance
#
# #Find contours at a constant value of 0.8
# contours1 = measure.find_contours(im, 0.8)
# image, contours, hierarchy = cv2.findContours(im,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
# im = cv2.cvtColor(im, cv2.COLOR_GRAY2RGB)
#
# count = 0
#
# for cnt in contours:
#     if cv2.contourArea(cnt) > 50 and cv2.contourArea(cnt) < 30000:
#         # cv2.drawContours(im, contours, count, (0,0,255), 2)
#         # hull = cv2.convexHull(cnt)
#         x,y,w,h = cv2.boundingRect(cnt)
#         # cv2.rectangle(im,(x,y),(x+w,y+h),(0,255,0),2)
#         rect = cv2.mxinAreaRect(cnt)
#         box = cv2.boxPoints(rect)
#         box = np.int0(box)
#         cv2.drawContours(im,[box],0,(0,0,255),2)
#         a,b,c,d = box
#         rect = perspective.order_points(box)
#         if distance(rect[0],rect[1]) < distance(rect[0],rect[3]):
#
#             mid1x = (rect[0][0] + rect[1][0])/2
#             mid1y = (rect[0][1] + rect[1][1])/2
#             mid2x = (rect[2][0] + rect[3][0])/2
#             mid2y = (rect[2][1] + rect[3][1])/2
#
#             # cv2.line(im, (midpoint1), (midpoint2), (0, 255, 0), thickness=3, lineType=8)
#         else:
#             mid1x = (rect[0][0] + rect[3][0])/2
#             mid1y = (rect[0][1] + rect[3][1])/2
#             mid2x = (rect[2][0] + rect[1][0])/2
#             mid2y = (rect[2][1] + rect[1][1])/2
#
#         mid1x = np.int0(mid1x)
#         mid1y = np.int0(mid1y)
#         mid2x = np.int0(mid2x)
#         mid2y = np.int0(mid2y)
#         boxArea = distance(rect[0],rect[1]) * distance(rect[0],rect[3])
#         area_proportion = 1
#         if boxArea > (area_proportion*cv2.contourArea(cnt)):
#             im = cv2.line(im, (mid1x,mid1y), (mid2x,mid2y), (0,255,0),4)
#             cv2.putText(im,str(cv2.contourArea(cnt)),(mid1x+5,mid1y+5), font, 0.8,(0,0,255),2,cv2.LINE_AA)
#         # rows,cols = im.shape[:2]
#         # [vx,vy,x,y] = cv2.fitLine(cnt, cv2.DIST_L2,0,0.01,0.01)
#         # lefty = int((-x*vy/vx) + y)
#         # righty = int(((cols-x)*vy/vx)+y)
#         # cv2.line(im,(cols-1,righty),(0,lefty),(0,255,0),2)
#     count += 1

# get mix image real and filtered
# stencil = np.zeros(im.shape).astype(im.dtype)
# color = [255, 255, 255]
# cv2.fillPoly(stencil, contours, color)
# result = cv2.bitwise_and(img2, stencil)
# cv2.imwrite("result.jpg", result)

# feat,im = ds.getFeatures(im)
# # for f in feat:
# #     print f.line_p1.x
# # a,b,im = pf.find_next_line_flow(feat,[1,1],im)
# current_point,im = pf.path_finder(feat,[100,100],im)
# images = []
# images.append(im)
# # images.append(img)
# montages = build_montages(images, (800, 600), (2, 1))
# for montage in montages:
# 	cv2.imshow("Montage", montage)
#
# cv2.waitKey(0)
# cv2.destroyAllWindows()
