import detect_sand as ds
import cv2
import numpy as np
import math
from math import atan2,degrees

class PathFinder():
    def __init__(self,lineFeatures=None,start_point=None):
        self.line_data = lineFeatures
        self.start_point = start_point


    def finder(self,lineFeatures,current_point,img,previous_angle):
        radius = 100
        angles_in_radius = 0
        angles_in_radius_n = 0
        len_multiplicator = 0
        current_point_tuple = (current_point[0],current_point[1])
        im = img
        im = cv2.circle(im, current_point_tuple, radius, (255,0,255), 5)

        for feature in lineFeatures:
            mid_point = [(feature.line_p1.x+feature.line_p2.x)/2,(feature.line_p1.y+feature.line_p2.y)/2]

            if ds.distance([feature.line_p1.x,feature.line_p1.y],current_point) < radius or ds.distance([feature.line_p2.x,feature.line_p2.y],current_point) < radius or ds.distance(mid_point,current_point) < radius:

                im = cv2.line(im, (feature.line_p1.x,feature.line_p1.y), (feature.line_p2.x,feature.line_p2.y), (255,0,0),4)
                im = cv2.line(im, (feature.line_p1.x,feature.line_p1.y), (current_point[0],current_point[1]), (255,0,0),4)
                cv2.putText(im,str(self.GetAngleOfLineBetweenTwoPoints(feature.line_p1,current_point)),(feature.line_p1.x+5,feature.line_p1.y+5), cv2.FONT_HERSHEY_DUPLEX, 0.8,(0,0,255),2,cv2.LINE_AA)
                print self.angle_in_range(previous_angle,feature.line_direction)
                if self.angle_in_range(previous_angle,feature.line_direction) > 1:
                    temp_line_angle = np.sign(feature.line_direction)-feature.line_direction
                else:
                    temp_line_angle = feature.line_direction

                angles_in_radius = (temp_line_angle)+angles_in_radius
                angles_in_radius_n = angles_in_radius_n+1

            else:
                im = cv2.line(im, (feature.line_p1.x,feature.line_p1.y), (feature.line_p2.x,feature.line_p2.y), (0,255,0),4)
        # print 'Amount of Features: %i' %(angles_in_radius_n)
        if angles_in_radius != 0:

            div_angle = ((angles_in_radius/(angles_in_radius_n)) + previous_angle)/2

            previous_angle = div_angle
        else:
            div_angle = previous_angle
            #Default to center of image

        dir_path_x_norm,dir_path_y_norm = self.path_direction(div_angle)

        current_point[0] = np.int0(current_point[0]+(radius*dir_path_x_norm/(radius/5)))
        current_point[1] = np.int0(current_point[1]+(radius*dir_path_y_norm/(radius/5)))
        path_len_x = np.int0(current_point[0]+(radius*dir_path_x_norm))
        path_len_y = np.int0(current_point[1]+(radius*dir_path_y_norm))


        im = cv2.line(im, current_point_tuple, (path_len_x,path_len_y), (255,255,255),4)

        return current_point,previous_angle,im

    def path_direction(self,angle):
        cos =  math.cos(math.radians(angle))
        sin = math.sin(math.radians(angle))
        x = cos
        y = sin
        # print 'sin %f, 1-cos%f'%(sin,(1-cos))
        return x,y

    def GetAngleOfLineBetweenTwoPoints(self,p1, p2):
            xDiff = p2[0]-p1.x
            yDiff = p2[1]-p1.y
            degree =  degrees(atan2(yDiff, xDiff))
            # degree = np.sign(degree)*(180-degree)
            # print 'Degree between %f' %(degree)
            return degree
    # def len_weight(self,len):
    #     w = math.ceil(len/100)
    #     return w
    def angle_in_range(self, previous_a, detected_b):
        a = math.cos(previous_a*math.pi/180)
        b = math.cos(detected_b*math.pi/180)
        range = abs(a-b)

        return range
