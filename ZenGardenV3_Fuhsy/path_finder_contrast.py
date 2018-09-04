# import detect_sand as ds
import cv2
import numpy as np
import math
from math import atan2,degrees
# import statistics

class PathFinder():
    def __init__(self):
        self.auto_slider = False
        self.radius = 20
        self.radius_slider = 20
        self.radius_temp = self.radius_slider
        self.detecting_angle = 60
        self.detecting_angle_slider = 60
        self.px_thresh = 100
        self.average_direction  = 0
        self.mov_step = 3
        self.col_px = []
        self.img_mid_point = Point(442/2,393/2)
        self.current_point = [100,200]
        self.previous_angle = 0
        self.speed = 20

    # This func is called every Frame and realizes the movement through the sand lines
    def finder(self,img,stone_features):

        self.average_direction  = 0

        current_point_tuple = (self.current_point[0],self.current_point[1])
        current_point_t = Point(self.current_point[0],self.current_point[1])
        # stone_distance_thresh = 200
        # stone_gravity_angle = 0
        # for stone in stone_features:
        #     stone_pos = (stone[0],stone[1])
        #     stone_distance = distance(current_point_tuple,stone_pos)
        #     if stone_distance < stone_distance_thresh:
        #         stone_point_t = Point(stone[0],stone[1])
        #         stone_gravity_angle = GetAngleOfLineBetweenTwoPoints(current_point_t,stone_point_t)

        median_list = []
        width = img.shape[1]
        height = img.shape[0]
        # Check if Movment-Dot is in image-area
        if self.current_point[0]+self.radius < width and self.current_point[0]-self.radius > 0 and self.current_point[1]+self.radius < height and self.current_point[1]-self.radius > 0:
            # range can be changed to set focus on diffrent radius.
            # max range devides the radius in several path_finder_contrast
            for i in range(1,2):
                for j in range(1, self.detecting_angle+1):
                    # checking if pixel in target angle - angle iterate
                    temp_iter_angle = self.check_angle(j)
                    px_x_norm,px_y_norm = self.path_direction(temp_iter_angle)
                    self.col_px = [np.int0(self.current_point[0]+((self.radius/i)*px_x_norm)),np.int0(self.current_point[1]+((self.radius/i)*px_y_norm))]
                    px_value = img[self.col_px[1],self.col_px[0]]
                    # do not detect stone with specific color
                    px_value_sum = px_value[0]+px_value[1]+px_value[2]
                    if px_value_sum > self.px_thresh:
                        median_list.append(j)
            if median_list:

                self.average_direction = np.median(median_list)

                if self.auto_slider:
                    self.radius = self.radius_slider
                    self.radius_temp = self.radius_slider
                    self.detecting_angle = self.detecting_angle_slider

            else:
                self.average_direction = self.detecting_angle/2
                if self.auto_slider:
                    self.radius_temp = self.radius_temp+0.2
                    self.radius = int(self.radius_temp)
                    self.detecting_angle = self.detecting_angle+1
            div_angle = self.check_angle(self.average_direction)

            self.previous_angle = div_angle
        else:
            self.previous_angle = self.GetAngleOfLineBetweenTwoPoints(current_point_t,self.img_mid_point)
            # if self.previous_angle >= 180:
            #     self.previous_angle = (self.previous_angle-180)
            # else:
            #     self.previous_angle = (self.previous_angle+180)
        dir_path_x_norm,dir_path_y_norm = self.path_direction(self.previous_angle)
        self.current_point[0] = np.int0(self.current_point[0]+(self.radius*dir_path_x_norm/(self.radius/self.mov_step)))
        self.current_point[1] = np.int0(self.current_point[1]+(self.radius*dir_path_y_norm/(self.radius/self.mov_step)))
        path_len_x = np.int0(self.current_point[0]+(self.radius*dir_path_x_norm))
        path_len_y = np.int0(self.current_point[1]+(self.radius*dir_path_y_norm))
        img = cv2.line(img, current_point_tuple, (path_len_x,path_len_y), (0,200,0),3)
        img = cv2.circle(img, current_point_tuple, self.radius+2, (0,0,255), 2)
        return img

    def check_angle(self,j):
        iter_angle = (self.previous_angle-(self.detecting_angle/2))+j
        if iter_angle > 360:
            iter_angle = iter_angle - 360
        if iter_angle < 0:
            iter_angle = 360 + iter_angle
            # iter_angle = (-1*self.detecting_angle-(self.detecting_angle/2))+j
        return iter_angle

    def path_direction(self,angle):
        cos =  math.cos(math.radians(angle))
        sin = math.sin(math.radians(angle))
        x = cos
        y = sin
        # print 'sin %f, 1-cos%f'%(sin,(1-cos))
        return x,y

    def GetAngleOfLineBetweenTwoPoints(self,p1, p2):
            xDiff = p2.x - p1.x
            yDiff = p2.y - p1.y
            # print degrees(atan2(yDiff, xDiff))
            return degrees(atan2(yDiff, xDiff))
    def set_current_point(self,x,y):
        self.current_point = [x,y]
    def distance(p1,p2):
        distance = math.sqrt( ((p1[0]-p2[0])**2)+((p1[1]-p2[1])**2) )
        return distance
class Point():
    def __init__(self,x=None,y=None):
        self.x = x or 0
        self.y = y or 0

    # def getMedian(self,list):

    # print math.cos(math.radians(90))
