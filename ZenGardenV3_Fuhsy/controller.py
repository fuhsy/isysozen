import view
import camera
import path_finder_contrast as pfc
from pyo import pa_get_output_devices,pa_get_output_max_channels
import cv2,sys, time
from PyQt4 import QtGui

from PyQt4.QtGui import QImage,QPixmap
import pyqtgraph as pg
import PyQt4.QtCore as QtCore
import re
import subprocess
import os
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image, ImageStat
from matplotlib import style
from collections import deque
# import pylabacsca
import collections
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
from thread import start_new_thread
from random import randint

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
        for i in range(0,self.path_finder_max):
            self.path_finder.append(pfc.PathFinder())
            self.path_finder[i].set_current_point(randint(10,500),randint(10,400))
            # print self.path_finder[i].current_point

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
            self.cap = cv2.VideoCapture(1)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,640)
            self.view.pic.setFixedWidth(940)
            self.snapshot_time_gap = 4
            self.start_time = time.time()
            self.timer = QtCore.QTimer()
            #Prepare Frame Diffrences and flags
            self.snapshot_flag = False
            self.detect_delay_count = 0
            ret, self.camera.frame = self.cap.read()
            self.timer.timeout.connect(self.view.updateplot)
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
        self.view.set_enabled_selection(start=False,cnt_sl=True,audio_out_chn=False,theme=False,new_cal=False,load_cal=False,start_default=False)
        # self.view.set_enabled_selection(new_cal=False,load_cal=False,stop=True,play=True)
        self.path_timer = QtCore.QTimer()
        self.feat,self.stone_feat,self.view.im_show = ds.getFeatures(self.view.im,self.contour_config_v)
        self.view.qImage_show(self.view.im_show)
        # cv2.imshow("coor",self.im)
        # n_out_channel = pa_get_output_max_channels(self.output_device_index+1)
        # self.audio_controller = actrl.AudioController(n_out_channel, self.theme,self.output_device_index)
        # self.audio_controller.playAmbient()
        # self.audio_controller.init_stone_feat(self.stone_feat)
        # self.path_timer.timeout.connect(self.follow_garden)
        # self.path_timer.start(1./self.camera.fps)
        self.view.button_reset.setEnabled(True)
        self.view.setListInfo('Start Default Image')

    def stop_n_play(self):
        if self.path_timer.isActive():
            self.path_timer.stop()
            self.audio_controller.stop_all()
        else:
            self.path_timer.start(self.path_finder[0].speed)
            self.audio_controller.restart_all()

    def play(self):
        n_out_channel = pa_get_output_max_channels(self.output_device_index+1)
        self.audio_controller = actrl.AudioController(n_out_channel, self.theme,self.output_device_index)
        # self.audio_controller.playAmbient()
        self.audio_controller.init_stone_feat(self.stone_feat)
        self.path_timer.timeout.connect(self.follow_garden)
        self.path_timer.start(1./self.camera.fps)
        self.view.set_enabled_selection_n(stop=True,reset=True,sl1=True,sl2=True,sl3=True)


    def reset(self):
        self.path_timer.stop()
        self.start()

    def new_calibration(self):
        #self.edgeDetectionApproach()
        self.timer.stop()
        self.cap.release()

        self.img = self.camera.frame.copy()
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
            cv2.circle(self.img,(x,y),6,(255,255,255),2)
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
                self.load_calibration()

    def load_calibration(self):

        try:
            self.timer.stop()
            self.cap.release()
            self.cal_pts = np.load('caldata.npy')
            print self.cal_pts
            warped = callibration.four_point_transform(self.camera.frame,self.cal_pts)
            self.camera.frame = warped
            self.path_timer = QtCore.QTimer()
            # self.camera.frame = cv2.flip(self.camera.frame,0)
            # self.camera.frame = cv2.flip(self.camera.frame,1)
            self.feat,self.stone_feat,self.view.im_show = ds.getFeatures(warped,self.contour_config_v)
            self.view.qImage_show(self.view.im_show)
            self.view.setListInfo('Calibration Loaded')
            self.view.set_enabled_selection(start=False,stop=False,audio_out_chn=False,theme=False,new_cal=False,load_cal=False,start_default=False)

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
            self.path_finder[i].speed = 1000./(float(self.view.slider2.value()*10))
        self.path_timer.start(self.path_finder[0].speed)
        print self.path_finder[0].speed
        # self.path_timer.setInterval(self.slider2.value())

    def threshold_slider3(self):
        for i in range(0,self.view.detector_amount.value()):
            self.path_finder[i].detecting_angle = self.view.slider3.value()
        txt1 = "Detecting Angle " + str(self.path_finder[0].detecting_angle)
        self.view.txtslider3.setText(txt1)

    def contour_config(self):
        self.contour_config_v = int(self.view.contour_slider.value()/10.)
        try:
            self.feat,self.stone_feat,self.view.im_show  = ds.getFeatures(self.camera.frame,self.contour_config_v)
            self.view.qImage_show(self.view.im_show)
            # print 'try'
        except:
            self.feat,self.stone_feat,self.view.im_show = ds.getFeatures(self.view.im,self.contour_config_v)
            self.view.qImage_show(self.view.im_show)
            # print 'except'
        # self.view.qImage_show(self.view.im_show)

    def nextFrameSlot(self):
        try:
            # previous_frame = self.current_frame
            # #maximum Elements the smooth function look at
            # max_smooth = 5
            # max_smooth_brightness = 2
            # mean_frame_diff_div = 0
            # mean_brightness_div = 0
            # max_brightness = 4
            _ , self.camera.frame = self.cap.read()
            # self.snap_delay_time = time.time()
            self.view.qImage_show(self.camera.frame)

        except Exception, e:
            self.view.setListInfo('Camera Activation failed')
            self.timer.stop()
            self.cap.release()

    def is_frame_moving(self):
        brightness_img = cv2.cvtColor(self.current_frame,cv2.COLOR_BGR2RGB)
        im = Image.fromarray(brightness_img)
        stat = ImageStat.Stat(im)
        if(stat.mean[0]/100 < max_brightness):
            self.brightness = stat.mean[0]/100

        #Smooth the signal -> when the you finish to work in ZenGarden, So you have no zeros between
        self.brightness_plt.append(self.brightness)
        if self.brightness_plt.__len__() == max_smooth_brightness:
            for item in self.brightness_plt:
                mean_brightness_div+=item
            self.brightness_v = mean_brightness_div/max_smooth_brightness
            self.brightness_plt.pop(0)
        if (self.snap_delay_time - self.start_time > 4) & (self.snapshot_flag == False):
            current_frame_gray = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2GRAY)
            previous_frame_gray = cv2.cvtColor(previous_frame, cv2.COLOR_BGR2GRAY)
            frame_diff = cv2.absdiff(current_frame_gray,previous_frame_gray)
            mean_diff = float(np.mean(frame_diff))
            self.smooth_mean_dif.append(mean_diff)
            if self.smooth_mean_dif.__len__() == max_smooth:
                for item in self.smooth_mean_dif:
                    mean_frame_diff_div += item
                mean_frame_diff_div = mean_frame_diff_div/max_smooth
                #print mean_frame_diff_div
                self.smooth_mean_dif.pop(0)
            # if self.brightness_plt.__len__() >= 100:
            #     self.brightness_plt.pop(0)
            print ('Threshold %f , Mean Diff  %f ' % (self.snap_thres, mean_diff))
            if (mean_diff < self.snap_thres):
                self.detect_delay_count += 1
                if(self.detect_delay_count == 4):
                    self.snapshot_flag == True
                    self.load_calibration()
                    itemlist= QtGui.QListWidgetItem('Detection started')
                    self.listw.addItem(itemlist)
                    self.start_time.stop()

    def follow_garden(self):
        try:
            # img_garden_copy = self.camera.frame.copy()
            img_garden_copy = self.view.im_show.copy()
        except:
            self.reset()
        finally:
            garden_update_img = self.path_finder[0].finder(img_garden_copy)
            for i in range(1,self.view.detector_amount.value()):
                garden_update_img = self.path_finder[i].finder(garden_update_img)
                self.audio_controller.interact(self.path_finder[i].current_point)
            self.audio_controller.interact(self.path_finder[0].current_point)

        self.view.qImage_show(garden_update_img)
        img_garden_copy = np.asarray(img_garden_copy)
        # qformat= QImage.tents(True)
    # def set_radius(self):
    #     return self.view.set_slider_radius(self.path_finder[0].radius)
    #
    # #TODO
    # def set_speed(self):
    #     return self.view.set_slider_speed()
    # def set_detecting_angle(self):
    #     return self.view.set_slider_angle(self.path_finder[0].detecting_angle)
