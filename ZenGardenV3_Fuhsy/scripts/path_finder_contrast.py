# import detect_sand as ds
import cv2
import numpy as np
import math
from math import atan2,degrees
import copy
import time
# import statistics

class PathFinder():

    def __init__(self):
        self.auto_contrl = True
        self.radius = 35
        self.radius_slider = 35
        self.detecting_angle = 25
        self.detecting_angle_slider = 35
        self.px_thresh = 60
        self.average_direction  = 0
        self.mov_step = 10
        self.col_px = []
        self.img_mid_point = Point(442/2,393/2)
        self.current_point = [150,150]
        self.previous_angle = 0
        self.speed = 200
        self.start_radius = 20
        self.start_radius_2 = 20
        self.start_radius_3 = 20
        self.img_width = 0
        self.img_height = 0
        self.wall_detected = 'default'
        self.time_wall = time.time()
        """Pathfinder class

        Attributes
        ----------
        func finder
        func cart2pol
        func pol2cart
        func reflect
        func check_angle
        func stone_interact_view
        func setStart_radius
        func path_direction
        func GetAngleOfLineBetweenTwoPoints
        func set_current_point
        func distance
        Parameters
        ----------
        auto_contrl : bool
            autocontrol trigger for gestures
        radius = 35 : int
            Radius of Sonic Anchor
        radius_slider = 35 : int
            Max Value of Radius, if no sandline is detected
        detecting_angle = 25 : int
            Detecting angle of sonic Anchor. Searching radius
        detecting_angle_slider = 35 : int
            Max Value of detecting angle, if no sandline is detected
        px_thresh = 60 : int
            Treshold for shadow pixel (sand)
        average_direction  = 0 : int
            Average of all Direction, where a shadow pixel is recognized
            init with zero
        mov_step = 10 : int
            Moves 10 Pixel into direction of detecting angle
        col_px = [] : array
            Pixel Value of Pixel in Searching area
        img_mid_point = Point(442/2,393/2) : np.ndarray
            init mid point of image
        current_point = [150,150] : np.ndarray
            init current point of sonic anchor
        previous_angle = 0 : int
            Previous detected moving direction in degree
        speed = 200 : int
            Moving Speed
        start_radius = 20 : int
            Start radius of Waves by hitting sound item
        start_radius_2 = 20 : int
            Start radius of Waves by hitting sound item
        start_radius_3 = 20 : int
            Start radius of Waves by hitting sound item
        img_width = 0 : int
            Saved width of image, init 0
        img_height = 0 : int
            Saved height of image, init 0
        wall_detected = 'default' : String (Left,Right,Top,Bottom)
            Detection direction
        time_wall = time.time() : double
            Time after hitting wall

        """

    # This func is called every Frame and realizes the movement through the sand lines
    def finder(self, img, color_im):
        """finder func

        Arguments
        ----------
        img : np.ndarray
            Current Image frame
        color_im : np.ndarray
            Image to paint on

        Parameters
        ----------
        temp_iter_angle : int
            temporal angle of detection
        current_point_t : np.ndarray
            Current point of sonic anchor
        path_pointer : np.ndarray
            Next Moving point
        path_len_x : int
        path_len_y : int
            Moving Step in Pixels

        Returns
        -------
        img : np.array
            Current Image frame
        color_im : np.array
            Image to paint on
        """
        self.average_direction  = 0
        current_point_tuple = (self.current_point[0],self.current_point[1])
        current_point_t = Point(self.current_point[0],self.current_point[1])

        median_list = []
        self.img_width = img.shape[1]
        self.img_height = img.shape[0]
        # Check if Movment-Dot is in image-area
        if self.current_point[0]+self.radius < self.img_width and self.current_point[0] - self.radius > 0 and self.current_point[1]+self.radius < self.img_height and self.current_point[1]-self.radius > 0:
            # range can be changed to set focus on diffrent radius.
            # max range devides the radius in several path_finder_contrast
            for i in range(1,2):
                for j in range(1, self.detecting_angle):
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
                if self.auto_contrl == True and self.radius >= self.radius_slider and self.detecting_angle >= 50:
                    self.radius -= 5
                    self.detecting_angle -= 5
            else:
                self.average_direction = self.detecting_angle/2
                if self.auto_contrl == True:
                    self.radius += 5
                    if self.detecting_angle <= 180:
                        self.detecting_angle += 5
            self.previous_angle = self.check_angle(self.average_direction)

        else:
            self.previous_angle = self.reflect(current_point_t,self.previous_angle)
            if self.auto_contrl == True and self.radius >= self.radius_slider and time.time()-self.time_wall < 2:
                self.radius -= 5
            # if self.previous_angle >= 180:
            #     self.previous_angle = (self.previous_angle-180)
            # else:
            #     self.previous_angle = (self.previous_angle+180)
        dir_path_x_norm,dir_path_y_norm = self.path_direction(self.previous_angle)
        self.current_point[0] += np.int0(self.radius*dir_path_x_norm/(self.radius/self.mov_step))
        self.current_point[1] += np.int0(self.radius*dir_path_y_norm/(self.radius/self.mov_step))
        path_len_x = int(self.current_point[0]+(self.radius*dir_path_x_norm))
        path_len_y = int(self.current_point[1]+(self.radius*dir_path_y_norm))
        path_pointer = (path_len_x, path_len_y)
        color_im = cv2.arrowedLine(color_im, current_point_tuple, path_pointer, (0,200,0),2)
        color_im = cv2.circle(color_im, current_point_tuple, self.radius+12, (0,0,255), 2)
        return img, color_im

    def cart2pol(x, y):
        """cart2pol func

        Arguments
        ----------
        x : int
            Len x from origin
        y : int
            Len y from origin

        Returns
        ----------
        rho : float
            rho angle Polar Coordinates
        phi : float
            phi angle Polar Coordinates
        """
        rho = np.sqrt(x**2 + y**2)
        phi = np.arctan2(y, x)
        return(rho, phi)

    def pol2cart(rho, phi):
        """pol2cart func

        Arguments
        ----------
        rho : float
            rho angle Polar Coordinates
        phi : float
            phi angle Polar Coordinates

        Returns
        ----------
        x : int
            Len x from origin
        y : int
            Len y from origin
        """
        x = rho * np.cos(phi)
        y = rho * np.sin(phi)
        return(x, y)

    def reflect(self,p,pre_a):
        """reflect func

        Arguments
        ----------
        p : Class Point(x,y)
            Current point
        pre_a : Class Point(x,y)
            Previous detected Point

        Parameters
        ----------
        edge : int
            Distance from Wall

        Returns
        -------
        prev_angle : int
            reflected angle
        """
        prev_angle = pre_a
        edge = 45
        if p.x <= edge and pre_a < 180 and (self.wall_detected != 'left' or time.time() - self.time_wall > 2):
            self.time_wall = time.time()
            prev_angle = 180-pre_a
            self.wall_detected = 'left'
        elif p.x > self.img_width-edge and pre_a < 180 and (self.wall_detected != 'right' or time.time() - self.time_wall > 2):
            prev_angle = 180-pre_a
            self.wall_detected = 'right'
            self.time_wall = time.time()
        elif p.x <= edge and pre_a >= 180 and (self.wall_detected != 'left' or time.time() - self.time_wall > 2):
            pre_a2 = 270-pre_a
            prev_angle = 270+pre_a2
            self.wall_detected = 'left'
            self.time_wall = time.time()
        elif p.x > self.img_width-edge and pre_a >= 180 and (self.wall_detected != 'right' or time.time() - self.time_wall > 2):
            pre_a2 = 270-pre_a
            prev_angle = 270+pre_a2
            self.wall_detected = 'right'
            self.time_wall = time.time()
        # elif p.y <= edge and pre_a < 180 and (self.wall_detected != 'top' or time.time() - self.time_wall > 2):
        #     prev_angle = 360-pre_a
        #     self.wall_detected = 'top'
        #     self.time_wall = time.time()
        elif p.y > self.img_height-edge and pre_a < 180 and (self.wall_detected != 'bottom' or time.time() - self.time_wall > 2):
            prev_angle = 360-pre_a
            self.wall_detected = 'bottom'
            self.time_wall = time.time()
        elif p.y <= 0 and pre_a >= 180 and (self.wall_detected != 'top' or time.time() - self.time_wall > 2):
            prev_angle = 360-pre_a
            self.wall_detected = 'top'
            self.time_wall = time.time()
        # elif p.y > self.img_height and pre_a >= 180 and (self.wall_detected != 'bottom' or time.time() - self.time_wall > 2):
        #     prev_angle = 360-pre_a
        #     self.wall_detected = 'bottom'
        #     self.time_wall = time.time()
        return prev_angle

    def check_angle(self,j):
        """check_angle func

        Arguments
        ----------
        j : int
            Iter Value of each ray to find shadow pixels

        Parameters
        ----------
        iter_angle : int
            degree value for kart. coordinate system

        Returns
        -------
        iter_angle : int
            degree value for kart. coordinate system
        """
        iter_angle = (self.previous_angle-(self.detecting_angle/2))+j
        if iter_angle > 360:
            iter_angle = iter_angle - 360
        if iter_angle < 0:
            iter_angle = 360 + iter_angle
            # iter_angle = (-1*self.detecting_angle-(self.detecting_angle/2))+j
        return iter_angle

    def stone_interact_view(self,img,feat):
        """stone_interact_view func

        Arguments
        ----------
        img : np.ndarray
            current frame
        feat : np.ndarray
            All informations of sonic items(place, theme)

        Parameters
        ----------
        stone_trigger : bool
            wave animation of sonic item activator

        Returns
        -------
        img : np.ndarray
            painted outcoming image (waves animated)
        stone_trigger : bool
            wave animation of sonic item activator
        """
        if self.start_radius <= feat.radius:
            cv2.circle(img,(feat.center),(self.start_radius),(200,200,200),2)
            self.start_radius += 2
        if self.start_radius > 50 and self.start_radius_2 < feat.radius:
            cv2.circle(img,(feat.center),(self.start_radius_2),(200,200,200),2)
            self.start_radius_2 += 2
        if self.start_radius_2 > 50 and self.start_radius_3 < feat.radius:
            cv2.circle(img,(feat.center),(self.start_radius_3),(200,200,200),2)
            self.start_radius_3 += 2
        if self.start_radius_3 >= feat.radius:
            self.start_radius = 20
            self.start_radius_2 = 20
            self.start_radius_3 = 20
            stone_trigger = True
        else:
            stone_trigger = False
        return img,stone_trigger

    def setStart_radius(self):
        """setStart_radius func
            Simple default setter
        """
        self.start_radius = 20
        self.start_radius_2 = 20
        self.start_radius_3 = 20

    def path_direction(self,angle):
        """stone_interact_view func

        Arguments
        ----------
        angle : int
            current moving direction

        Returns
        -------
        cos : float
            transform angle in cos
        sin : float
            transform angle in sin
        """
        cos =  math.cos(math.radians(angle))
        sin = math.sin(math.radians(angle))
        return cos,sin

    def GetAngleOfLineBetweenTwoPoints(self,p1, p2):
        """GetAngleOfLineBetweenTwoPoints func

        Arguments
        ----------
        p1 : Class Point(x,y)
        p2 : Class Point(x,y)

        Returns
        -------
         degree : float
            degree (0,360)
        """
        xDiff = p2.x - p1.x
        yDiff = p2.y - p1.y
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
