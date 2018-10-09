import view
import camera
import path_finder_contrast as pfc
from pyo import pa_get_output_devices,pa_get_output_max_channels
import cv2,sys, time
from PyQt4 import QtGui
import copy
from PyQt4.QtGui import QImage,QPixmap
import pyqtgraph as pg
import PyQt4.QtCore as QtCore
# import re
import subprocess
# import os
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import style
from collections import deque
import random
import math
import callibration
import detect_sand
import sounddevice as sd
import soundfile as sf
import audio_theme
import path_finder as pf
import path_finder_contrast as pfc
import detect_sand as ds
import detect_stones as dstones
import audio_controller as actrl
import audio_theme as atheme
from pyo import pa_get_output_devices,pa_get_output_max_channels
import usb
# from thread import start_new_thread
import time
from random import randint
import sys
import glob

class Controller():
    def __init__(self, view):
        self.view = view
        self.camera = camera.Camera()
        self.view.register(self)
        self.view.register_buttons()
        # self.previous_angle = 0
        self.feat = None
        self.stone_feat = None
        self.contour_config_v = 2
        self.output_device_index = 0
        self.path_finder = []
        self.calibration_pts = []
        self.path_finder_max = 5
        self.min_move = 0
        self.stop_flag_init = True
        self.stop_flag = False
        self.music_playing_flag = False
        self.stones_act_flag = False
        self.time_stamp_activation = time.time()
        self.stop_time = time.time()
        self.start_time = time.time()
        self.audio_controller = None
        self.cap = None

        for i in range(0,self.path_finder_max):
            self.path_finder.append(pfc.PathFinder())
            self.path_finder[i].set_current_point(randint(50,300),randint(50,400))
            # print self.path_finder[i].current_point
        self.snapshot_trigger = False
        view.setSliderDefault()
        n_out_channel = pa_get_output_max_channels(self.output_device_index+1)
        self.devicelist = pa_get_output_devices()
        audio_index_count =0
        for i in range(0,len(self.devicelist[0])):
            self.view.select_audio_output.addItem(self.devicelist[0][i])
            audio_index_count = audio_index_count+1
        self.theme = audio_theme.AudioTheme('water')
        self.view.set_theme_box(self.theme)

        #TODO also in main
    def __del__(self):
        try:
            self.path_timer.stop()
        except Exception, e:
            print 'Path Timer blocks'
        try:
            self.timer.stop()
        except Exception, e:
            print 'Flow Timer blocks'
        try:
            self.cap.release()
        except Exception, e:
            print 'Video Cap blocks'
        sys.exit()

        # from collections import namedtuple
        # Color = namedtuple('Color',['hue','saturation','luminosity'])
        # p = Color(170,0.1,0.6)
        # p.saturation

    def setTheme(self):
        theme_index = self.view.select_theme.currentIndex()
        theme_selector = self.theme.type.keys()
        # print theme_selector[theme_index]
        self.theme.setCurrentTheme(str(theme_selector[theme_index]))

    def setDefaultSoundDevice(self):
        self.output_device_index = self.view.select_audio_output.currentIndex()
        print self.devicelist[0][self.output_device_index]

    def start(self):
        self.setDefaultSoundDevice()
        try:
            self.view.set_enabled_selection(stop=False,play=False)
            # Camera index -> default to 1 (left macbook pro usb port)
            self.cap = cv2.VideoCapture(0)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,640)
            self.view.pic.setFixedWidth(940)
            self.snapshot_time_gap = 4
            self.timer = QtCore.QTimer()
            self.show_camera_image = True
            activation_timer = 5
            #Prepare Frame Diffrences and flags

            self.detect_delay_count = 0
            ret, self.camera.frame = self.cap.read()
            # self.timer.timeout.connect(self.view.updateplot)
            # self.timer.start(self._interval)
            self.timer.timeout.connect(self.nextFrameSlot)
            self.timer.start(1./self.camera.fps)
            self.view.setListInfo('Camera Activated')

            # self.view.set_enabled_selection(play=False,stop=False)
            # self.view.qImage_show(self.camera.frame)
        except Exception, e:
            self.view.set_enabled_selection(new_cal=False,load_cal=False,stop=False,play=False)
            self.view.setListInfo('Camera Activation failed')



    def start_default_image(self):
        try:
            self.cap.release()
        except Exception,e:
            print 'No Camera connected'
        self.view.set_enabled_selection(start=False,cnt_sl=True,audio_out_chn=False,theme=False,new_cal=False,load_cal=False,start_default=False)
        # self.view.set_enabled_selection(new_cal=False,load_cal=False,stop=True,play=True)
        self.path_timer = QtCore.QTimer()

        self.stone_feat,self.view.im_show = ds.getFeatures(self.view.im,self.contour_config_v)
        self.view.qImage_show(self.view.im_show)
        # cv2.imshow("coor",self.im)
        # n_out_channel = pa_get_output_max_channels(self.output_device_index+1)
        # self.audio_controller = actrl.AudioController(n_out_channel, self.output_device_index, self.view.im.shape[0],self.view.im.shape[1])
        # self.audio_controller.playAmbient()
        # self.audio_controller.init_stone_feat(self.stone_feat)
        # self.path_timer.timeout.connect(self.follow_garden)
        # self.path_timer.start(1./self.camera.fps)
        # self.view.button_reset.setEnabled(True)
        # self.view.setListInfo('Start Default Image')

    def stop_n_play(self):
        if self.path_timer.isActive():
            self.path_timer.stop()
            self.audio_controller.stop_all()
            self.stop_flag = True
        else:
            # print self.path_finder[0].speed
            self.path_timer.start(self.path_finder[0].speed)
            self.audio_controller.restart_all()
            self.stop_flag = False

    def play(self):
        if self.audio_controller:
            self.audio_controller.fade_out_background()
        n_out_channel = pa_get_output_max_channels(self.output_device_index+1)
        self.audio_controller = actrl.AudioController(n_out_channel,self.output_device_index, self.view.im_show.shape[0],self.view.im_show.shape[1])
        self.audio_controller.init_stone_feat(self.stone_feat)
        self.audio_controller.playAmbient()
        self.path_timer.timeout.connect(self.follow_garden)
        self.path_timer.start(self.path_finder[0].speed)
        self.view.set_enabled_selection_n(stop=True,cnt_sl=True,reset=True,sl1=True,sl2=True,sl3=True)
        self.view.button_reset.setEnabled(True)
        self.stop_flag_init = False

    def reset(self):
        self.path_timer.stop()
        self.audio_controller.shutdown()
        if self.cap:
            self.show_camera_image = True
            self.start()
        else:
            self.view.set_enabled_selection_n(start=False,start_default=True)
        self.stop_flag_init = True
        self.view.button_reset.setEnabled(False)

    def new_calibration(self):
        #self.edgeDetectionApproach()
        self.timer.stop()
        self.cap.release()

        # self.img = self.camera.frame.copy()
        self.img = self.camera.frame
        print self.img.shape
        cv2.namedWindow('image')
        cv2.imshow('image',self.img)
        #cv2.setMouseCallback('canny',img)
        cv2.setMouseCallback('image',self.draw_circle)
        self.view.setListInfo('Camera Stopped')

    def draw_circle(self,event,x,y,flags,param):
        global mouseX,mouseY
        # self.calibration_pts = []
        # cv2.imshow('image',self.img)
        # cv2.waitKey(0)
        if event == cv2.EVENT_LBUTTONUP:
            cv2.circle(self.img,(x,y),2,(255,255,255),2)
            print x,' , ',y
            mouseX,mouseY = x,y
            temparr = [x,y]
            self.calibration_pts.append(temparr)
            #print(len(self.calibration_pts))
            #print(self.calibration_pts)
            if len(self.calibration_pts) == 4:
                cv2.destroyAllWindows()
                self.calibration_pts = np.asarray(self.calibration_pts)
                self.calibration_pts = self.calibration_pts.astype(int)
                warped = callibration.four_point_transform(self.img,self.calibration_pts)
                np.save('caldata.npy', self.calibration_pts)
                # self.load_calibration()

    def load_calibration(self):
        try:
            snap = copy.copy(self.camera.frame)
            self.cal_pts = np.load('caldata.npy')
            print self.cal_pts
            warped = callibration.four_point_transform(snap,self.cal_pts)
            # print warped.shape
            self.camera.frame = warped.copy()
            self.path_timer = QtCore.QTimer()
            # self.camera.frame = cv2.flip(self.camera.frame,0)
            # self.camera.frame = cv2.flip(self.camera.frame,1)
            self.stone_feat,self.view.im_show = ds.getFeatures(warped,self.contour_config_v)
            if self.stone_feat:
                self.snapshot_trigger = True
                self.show_camera_image = False
                self.view.qImage_show(self.view.im_show)
                self.view.setListInfo('Calibration Loaded')
                self.view.set_enabled_selection(start=False,stop=False,audio_out_chn=False,theme=False,new_cal=False,load_cal=False,start_default=False,reset=False)

        except Exception, e:
            self.new_calibration()
            self.view.setListInfo('Calibration Loading failed')

        # finally:
        #     n_out_channel = pa_get_output_max_channels(self.output_device_index+1)
        #     self.audio_controller = actrl.AudioController(n_out_channel, self.theme,self.output_device_index)
        #     self.audio_controller.init_stone_feat(self.stone_feat)
        #     # self.audio_controller.playAmbient()
        #     # self.path_timer.timeout.connect(self.follow_garden)
        #     # self.path_timer.start(1./self.camera.fps)
        #     self.view.button_reset.setEnabled(True)

    def nextFrameSlot(self):
        # try:
        if self.view:
            previous_frame = copy.copy(self.camera.frame)
            _ , self.camera.frame = self.cap.read()
            self.camera.frame = cv2.flip(self.camera.frame,0)
            self.camera.frame = cv2.flip(self.camera.frame,1)
            self.auto_snapshot(previous_frame)
            gray = cv2.cvtColor(self.camera.frame, cv2.COLOR_BGR2GRAY)
            self.start_time = time.time()
            sum_grey = np.sum(gray)
            # print sum_grey
            # # print np.sum(sum_grey)
            # cv2.imshow("img_seaag", gray)
            # cv2.waitKey(0)
            if np.sum(gray) < 1000000 and (self.start_time - self.stop_time > 3) and self.stop_flag_init == False:
                # self.stop_flag_init = True
                self.stop_time = time.time()
                self.min_move = 0
                self.stop_n_play()
            if self.show_camera_image == True:
                self.view.qImage_show(self.camera.frame)
        else:
            self.__del__()


        # except Exception, e:
        #     self.view.setListInfo('Camera Activation failed')
        #     self.timer.stop()
        #     self.cap.release()

    def auto_snapshot(self,prev):
        current_frame_gray = cv2.cvtColor(self.camera.frame, cv2.COLOR_BGR2GRAY)
        previous_frame_gray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)
        mean_diff = 0
        if current_frame_gray.shape == previous_frame_gray.shape:
            frame_diff = cv2.absdiff(current_frame_gray,previous_frame_gray)
            mean_diff = float(np.mean(frame_diff))
        max_mean_diff = 4.5
        if mean_diff > max_mean_diff:
            self.time_stamp_activation = time.time()
            self.snapshot_trigger = False
            self.min_move += 1
        if (time.time() - self.time_stamp_activation) > 5 and self.snapshot_trigger == False and self.min_move > 30 and self.stop_flag == False:
            self.min_move = 0
            self.snapshot_trigger = True
            self.show_camera_image = False
            self.load_calibration()
            self.view.setListInfo("Soundscape activated")
            # self.timer.stop()
            if self.stone_feat:
                self.play()


    def follow_garden(self):
        if self.view:
            try:
                # img_garden_copy = self.camera.frame.copy()
                img_garden_copy = self.view.im_show.copy()
                color_img = self.view.im_show.copy()
            except:
                self.audio_controller.stop()
            finally:
                color_img = ds.color_stones(color_img,self.stone_feat)
                garden_update_img,color_img = self.path_finder[0].finder(img_garden_copy,self.stone_feat,color_img)
                for i in range(1,self.view.detector_amount.value()):
                    garden_update_img,color_img = self.path_finder[i].finder(garden_update_img,self.stone_feat,color_img)
                    in_stone_flag, stone_feat = self.audio_controller.interact(self.path_finder[i].current_point)
                in_stone_flag, stone_feat = self.audio_controller.interact(self.path_finder[0].current_point)
                if in_stone_flag == True or self.stones_act_flag:
                    color_img,stone_act_trigger = self.path_finder[0].stone_interact_view(color_img, stone_feat)
                    self.stones_act_flag = stone_act_trigger
                else:
                    self.path_finder[0].setStart_radius()
            self.view.qImage_show(color_img)
            img_garden_copy = np.asarray(img_garden_copy)
        else:
            self.__del__()
        # qformat= QImage.tents(True)
    # def set_radius(self):
    #     return self.view.set_slider_radius(self.path_finder[0].radius)
    #
    # #TODO
    # def set_speed(self):
    #     return self.view.set_slider_speed()
    # def set_detecting_angle(self):
    #     return self.view.set_slider_angle(self.path_finder[0].detecting_angle)
    def auto_slider(self):
        if self.view.auto_checkbox.isChecked():
            for i in range(0,self.path_finder_max):
                self.path_finder[i].auto_slider = True
            self.view.contour_slider.setEnabled(False)
            self.view.slider1.setEnabled(False)
            self.view.slider2.setEnabled(False)
            self.view.slider3.setEnabled(False)
        else:
            for i in range(0,self.path_finder_max):
                self.path_finder[i].auto_slider = False
            self.view.contour_slider.setEnabled(True)
            self.view.slider1.setEnabled(True)
            self.view.slider2.setEnabled(True)
            self.view.slider3.setEnabled(True)
    def auto_slider_activation(self):
        for i in range(0,self.path_finder_max):
            self.path_finder[i].auto_slider = True
    def threshold_slider1(self):
        for i in range(0,self.view.detector_amount.value()):
            self.path_finder[i].radius  = self.view.slider1.value()
        txt1 = "Radius of Circle " + str(self.path_finder[0].radius)
        self.view.txtslider1.setText(txt1)

    def threshold_slider2(self):
        txt1 = "Speed " + str(float(self.view.slider2.value())/100.*float(self.view.fps))+" fps"
        self.view.txtslider2.setText(txt1)
        # setFPS(self.slider2.value())
        self.path_timer.stop()
        for i in range(0,self.view.detector_amount.value()):
            # self.path_finder[i].mov_step =self.view.slider2.value()
            self.path_finder[i].speed = 1000./(float(self.view.slider2.value()))
            # print self.path_finder[0].speed
        self.path_timer.start()
        # self.path_timer.setInterval(self.slider2.value())

    def threshold_slider3(self):
        for i in range(0,self.view.detector_amount.value()):
            self.path_finder[i].detecting_angle = self.view.slider3.value()
        txt1 = "Detecting Angle " + str(self.path_finder[0].detecting_angle)
        self.view.txtslider3.setText(txt1)

    def contour_config(self):
        self.contour_config_v = int(self.view.contour_slider.value()/10.)
        # print type(self.camera.frame)
        # self.camera.frame = np.array(self.camera.frame, dtype=np.ndarray)
        # self.camera.frame.astype(np.ndarray)
        # print type(self.camera.frame)
        try:
            self.stone_feat,self.view.im_show  = ds.getFeatures(self.camera.frame,self.contour_config_v)
            self.view.qImage_show(self.view.im_show)
        except:
            print 'no contour image'
            # self.feat,self.stone_feat,self.view.im_show = ds.getFeatures(self.view.im,self.contour_config_v)
            # self.view.qImage_show(self.view.im_show)
            # print 'except'
        # self.view.qImage_show(self.view.im_show)
