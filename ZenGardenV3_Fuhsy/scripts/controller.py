import view
import camera
import path_finder_contrast as pfc
import cv2,sys, time
import copy
from PyQt5.QtGui import QImage,QPixmap
import pyqtgraph as pg
import PyQt5.QtCore as QtCore
import pickle
import subprocess
from time import gmtime, strftime
from PIL import Image
from scipy.misc import imsave
import numpy as np
from matplotlib import pyplot as plt
#from matplotlib import stylet
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
from pyo import pa_get_output_devices, pa_get_output_max_channels
import usb
import pyscreenshot as ImageGrab
import time
from random import randint
import sys
import glob
# import Scheduler
import schedule
from apscheduler.scheduler import Scheduler
# PyQt4 version '4.8.6'
# pyo version '4.0.23'


# This class controlls all actions and timersself.
# def start():                      will activate the camera based system with an automatical start and stop integration
# def start_default_image() :       will start the system with a defualt image at ()/images/default/export.jpg)
# def listen_task():                is used for experiment and getting quickly access to an specific defualt images

# def new_callibration:             click at the 4 corners of the zen garden to get the right image garden_update_img
# def load_calibration:             will load the callibration file. if not set, this will use the latest setup
# def serialize:                    dump function for saving dataset

# var path_timer                    Thread is set up for getting controll of moving virtual objects, which controls the audio system
# audio_controller                  Is created just one time and will change if you reset the camera or do another actions
# auto_snapshot                     will update the interaction image if you will change something in the image and lean back for 5 Seconds
#                                   You can also hide the caerma with your hand or an dark objet to stop/play the system

# def follow_garden:                Loop for moving through sand and creating sound.

class Controller():
    def __init__(self, view):
        """Controller Class

        Arguments
        ----------
        view : Class view
            MVC
        Parameters
        ----------
        camera : camera.Camera()
            camera init
        previous_angle : int
            previous detected angle
        feat : np.ndarray
            [pos, radius, theme]
        stone_feat : np.ndarray
            [pos, radius, theme]
        contour_config_v : int
            erode and dilate iter value
        output_device_index : int
            number of output devices
        path_finder : []
            List of sonic anchors in scene
        calibration_pts : []
            Calibrated Points (edges of the sandbox)
        path_finder_max : int
            max number of sonic anchors in scene
        min_move : int
            init value of moving steps in pixels
        stop_flag_init : bool
            init vaule of stop playining music flag
        stop_flag : bool
            opposit of stop playining music flag after init is set
        music_playing_flag : bool
            mixer stop music flag
        stones_act_flag : bool
            Stone wave animation flag
        time_stamp_activation = time.time()
            Time stamp for timing, several usage
        stop_time : time.time()
            Timer for stop fading out and in e.g.
        start_time : time.time()
            Timer for stop fading out and in e.g.
        audio_controller : AudioController()
            AudioController Instance
        cap : np.ndarray
            Image cap frame
        c_saveimg : int
            iterator for naming saved image file
        logs : Logs()
            logs instance for saving params

        """
        import matplotlib
        print "cv2"+cv2.__version__
        print "usb"+usb.__version__
        print "matplotlib"+matplotlib.__version__

        self.view = view
        self.camera = camera.Camera()
        self.view.register(self)
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
        self.c_saveimg = 0
        self.maxVol = 80
        # self.logs = Logs()
        for i in range(0,self.path_finder_max):
            self.path_finder.append(pfc.PathFinder())
            self.path_finder[i].set_current_point(randint(100,250),randint(100,250))
        self.snapshot_trigger = False
        view.setSliderDefault()
        n_out_channel = pa_get_output_max_channels(self.output_device_index+1)
        self.devicelist = pa_get_output_devices()

        self.updateDeviceList()
        self.sched_device = Scheduler()
        self.sched_device.start()
        self.sched_device.add_interval_job(self.updateDeviceList, seconds=20)

        self.theme = audio_theme.AudioTheme('water')
        self.view.register_buttons()
        self.view.show()

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
    def updateDeviceList(self):
        audio_index_count = 0
        self.view.select_audio_output.clear()
        self.view.select_camera.clear()
        for i in range(0,len(self.devicelist[0])):
            self.view.select_audio_output.addItem(self.devicelist[0][i])
            audio_index_count = audio_index_count+1
        self.usbdevices = self.getUsbDevices()
        for i in range(0,len(self.usbdevices)):
            self.view.select_camera.addItem(self.usbdevices.values()[i])

    def getUsbDevices(self):
        import sys
        import usb.core
        # find USB devices
        dev = usb.core.find(find_all=True)
        devices = {}
        for cfg in dev:
          if cfg.port_number < 4:
              devices[cfg.port_number] = cfg.product
        return devices

    def setMaxVolume(self):
        self.maxVol = self.view.maxVolume_slider.value()
        self.view.maxVolume_slider_txt.setText("Max Volume: "+str(self.maxVol)+"%")
        if self.audio_controller != None:
            self.audio_controller.maxVol = self.maxVol
        else:
            print "Audiocontroller not loaded"

    def setDefaultSoundDevice(self):
        """AudioTheme Class

        """
        self.output_device_index = self.view.select_audio_output.currentIndex()
        n_out_channel = pa_get_output_max_channels(self.output_device_index+1)
        if self.audio_controller == None:
            self.audio_controller = actrl.AudioController(n_out_channel,self.output_device_index)
        self.view.button_start.setEnabled(True)
        self.view.button_start_default.setEnabled(False)
        self.view.button_listen_task.setEnabled(True)
        self.view.button_listen_task_2.setEnabled(True)
        self.view.select_audio_output.setEnabled(False)
        self.view.audio_submit.setEnabled(False)
        self.view.setListInfo('Audio Device paired')

    def start(self):
        """start func
        This func is executed after pressing connect camera.
        Camera frame is activated.
        Arguments
        ----------
        str_theme : String
            Theme (Forest,Sea,Fire)
        Parameters
        ----------
        type : Dictionary
            All Soundfiles are saved here

        """
        self.view.save_btn.setEnabled(True)
        try:
            self.view.set_enabled_selection(stop=False,play=False)
            # Camera index -> default to 1 (left macbook pro usb port)
            camera_port = self.usbdevices.keys()[self.view.select_camera.currentIndex()]
            if camera_port == -1:
                camera_port = 0
            self.cap = cv2.VideoCapture(camera_port)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,640)
            self.view.pic.setFixedWidth(940)
            self.snapshot_time_gap = 4
            self.timer = QtCore.QTimer()
            self.show_camera_image = True
            activation_timer = 5
            self.detect_delay_count = 0
            ret, self.camera.frame = self.cap.read()
            self.timer.timeout.connect(self.nextFrameSlot)
            self.timer.start(1./self.camera.fps)
            self.view.setListInfo('Camera Activated')
            self.path_finder[0].radius = 35
            self.path_finder[0].radius_slider = 35
            self.sched_device.shutdown()

            # self.view.set_enabled_selection(play=False,stop=False)
            # self.view.qImage_show(self.camera.frame)
        except Exception, e:
            self.view.set_enabled_selection(new_cal=False,load_cal=False,stop=False,play=False)
            self.view.setListInfo('Camera Activation failed')

        # self.logs.camera_start = {'Camera Start': strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())}
        # self.logs.single_dataset.append(self.logs.camera_start)
        # print 'logged: '+str(self.logs.single_dataset)


    def start_default_image(self):
        """start_default_image func

        Same as start. But instead of loading camera frame, this function
        load a file and use it to start the routine.

        """
        self.view.save_btn.setEnabled(True)
        try:
            self.cap.release()
            self.timer.stop()
        except Exception,e:
            print 'No Camera connected'
        self.view.set_enabled_selection(start=False,cnt_sl=True,audio_out_chn=False,new_cal=False,load_cal=False,start_default=False)
        # self.view.set_enabled_selection(new_cal=False,load_cal=False,stop=True,play=True)
        html_im = ImageGrab.grab(bbox=(1700,180,2640,840)) # X1,Y1,X2,Y2
        html_im = np.asarray(html_im)
        cv2.imwrite('../images/saved_data/'+str(self.view.save_text.text())+'('+str(self.c_saveimg)+').jpg', html_im)
        # imsave('images/saved_data/'+str(self.view.save_text.text())+'('+str(self.c_saveimg)+').jpg',imagetosave)
        html_im = cv2.imread('../images/saved_data/'+str(self.view.save_text.text())+'('+str(self.c_saveimg)+').jpg')
        html_im = cv2.cvtColor(html_im, cv2.COLOR_RGB2BGR)
        html_im = np.asarray(html_im)
        self.view.im_show = html_im
        self.view.im = html_im
        self.c_saveimg += 1
        self.audio_controller.img_height = self.view.im.shape[0]
        self.audio_controller.img_width = self.view.im.shape[1]
        # self.audio_controller.img_width = 640
        # self.audio_controller.img_height = 480
        # self.view.qImage_show(self.view.im_show)
        self.view.qImage_show(html_im)
        self.path_timer = QtCore.QTimer()
        self.stone_feat,self.view.im_show = ds.getFeatures(self.view.im,self.contour_config_v)
        self.audio_controller.init_stone_feat(self.stone_feat)
        #Just for one dot
        self.path_finder[0].radius = 55
        self.path_finder[0].radius_slider = 55
        for i in range(0,len(self.stone_feat)):
            features = {'center': self.stone_feat[i].center, 'radius': self.stone_feat[i].radius, 'theme': self.stone_feat[i].theme }
            # self.logs.image_infos = {'Stone'+str(i): features}
            # self.logs.single_dataset.append(self.logs.image_infos)
            # print 'logged'+str(self.logs.single_dataset)
        # self.logs.camera_start = {'Default Loaded': strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())}
        # self.logs.single_dataset.append(self.logs.camera_start)
        # print 'logged: '+str(self.logs.single_dataset)

    def listen_task(self, index):
        """listen_task func
        Arguments
        ----------
        index : int0
            index 1 or 2

        Needed for experiment.
        A image file was record from second screen, saved as a export+(index).jpg
        and loaded into starting screen.

        """
        self.view.save_btn.setEnabled(True)
        try:
            self.cap.release()
            self.timer.stop()
        except Exception,e:
            print 'No Camera connected'
        self.view.set_enabled_selection(start=False,cnt_sl=True,audio_out_chn=False,new_cal=False,load_cal=False,start_default=False)

        self.c_saveimg += 1
        html_im = cv2.imread('../images/default/export'+str(index)+'.jpg')
        self.view.im_show = html_im
        self.view.im = html_im
        cv2.imwrite('../images/saved_data/'+str(self.view.save_text.text())+'('+str(self.c_saveimg)+').jpg', html_im)
        # self.audio_controller.img_height = self.view.im.shape[0]+60
        # self.audio_controller.img_width = self.view.im.shape[1]+60
        # self.view.qImage_show(self.view.im_show)
        self.view.qImage_show(html_im)
        self.path_timer = QtCore.QTimer()
        self.stone_feat,self.view.im_show = ds.getFeatures(self.view.im,self.contour_config_v)
        self.audio_controller.init_stone_feat(self.stone_feat)
        #Just for one dot
        self.path_finder[0].radius = 55
        self.path_finder[0].radius_slider = 55
        for i in range(0,len(self.stone_feat)):
            features = {'center': self.stone_feat[i].center, 'radius': self.stone_feat[i].radius, 'theme': self.stone_feat[i].theme }
        #     self.logs.image_infos = {'Stone'+str(i): features}
        #     self.logs.single_dataset.append(self.logs.image_infos)
        #     print 'logged'+str(self.logs.single_dataset)
        # self.logs.camera_start = {'Default Loaded': strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())}
        # self.logs.single_dataset.append(self.logs.camera_start)
        # print 'logged: '+str(self.logs.single_dataset)


    def stop_n_play(self):
        if self.path_timer.isActive():
            self.path_timer.stop()
            self.audio_controller.stop_all()
            self.stop_flag = True
        else:
            self.path_timer.start(self.path_finder[0].speed)
            self.audio_controller.restart_all()
            self.stop_flag = False

    def play(self):
        """play func

        This function starts playing a new background sound formation.

        """
        self.audio_controller.fade_out_background()
        # n_out_channel = pa_get_output_max_channels(self.output_device_index+1)
        # self.audio_controller = actrl.AudioController(n_out_channel,self.output_device_index, self.view.im_show.shape[0],self.view.im_show.shape[1])
        if self.stone_feat:
            self.audio_controller.init_stone_feat(self.stone_feat)
            self.audio_controller.playAmbient()
            self.path_timer.timeout.connect(self.follow_garden)
            self.path_timer.start(self.path_finder[0].speed)
            self.view.set_enabled_selection_n(stop=True,cnt_sl=True,reset=True,sl1=True,sl2=True,sl3=True)
            self.view.button_reset.setEnabled(True)
            self.stop_flag_init = False
        else:
            self.view.setListInfo('No Objects detected')

    def reset(self):
        """reset func

        The sound files loaded by the audio controller will be changed to the
        current recognized sound items and themes.
        """
        self.path_timer.stop()
        if self.audio_controller:
            self.audio_controller.s.stop()
        if self.cap:
            self.show_camera_image = True
            self.start()
        else:
            self.view.set_enabled_selection_n(start=True,start_default=True)
        self.stop_flag_init = True
        self.view.button_reset.setEnabled(False)
        # self.logs.camera_end = {'reset ': strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())}
        # self.logs.single_dataset.append(self.logs.camera_end)
        # print self.logs.single_dataset


    def new_calibration(self):
        """new_calibration func

        A new window will be shown, where you can click on four corners of the
        sand plate to warp the image.
        """
        self.timer.stop()
        self.cap.release()
        self.img = self.camera.frame
        print self.img.shape
        cv2.namedWindow('image')
        cv2.imshow('image',self.img)
        cv2.setMouseCallback('image',self.draw_circle)
        self.view.setListInfo('Camera Stopped')

    def draw_circle(self,event,x,y,flags,param):
        """draw_circle func

        This is needed for warping the image and save the clicked corners.
        The results are saved in caldata.npy
        If you start afterwards you can get your old calibration points.
        """
        global mouseX,mouseY

        # cv2.waitKey(0)
        if event == cv2.EVENT_LBUTTONUP:
            cv2.circle(self.img,(x,y),2,(255,255,255),2)
            print x,' , ',y
            mouseX,mouseY = x,y
            temparr = [x,y]
            self.calibration_pts.append(temparr)
            if len(self.calibration_pts) == 4:
                cv2.destroyAllWindows()
                self.calibration_pts = np.asarray(self.calibration_pts)
                self.calibration_pts = self.calibration_pts.astype(int)
                warped = callibration.four_point_transform(self.img,self.calibration_pts)
                np.save('caldata.npy', self.calibration_pts)
                self.calibration_pts = []
                # self.load_calibration()

    def load_calibration(self):
        """load_calibration func

        The saved callibration is loaded here and feature generation is starting.

        """
        # try:
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
        saving_img = copy.copy(self.view.im_show)
        self.audio_controller.img_width = saving_img.shape[1]
        self.audio_controller.img_height = saving_img.shape[0]
        imagetosave = ds.color_stones(saving_img,self.stone_feat)
        imsave('../images/saved_data/'+str(self.view.save_text.text())+'('+str(self.c_saveimg)+').jpg',imagetosave)
        self.path_finder[0].set_current_point(randint(100,250),randint(100,250))
        self.c_saveimg += 1
        for i in range(0,len(self.stone_feat)):
            features = {'center': self.stone_feat[i].center, 'radius': self.stone_feat[i].radius, 'theme': self.stone_feat[i].theme }
            # self.logs.image_infos = {'Stone'+str(i)+' ': features}
            # self.logs.single_dataset.append(self.logs.image_infos)
            # print 'logged'+str(self.logs.single_dataset)
        print self.stone_feat
        # self.logs.camera_end = {'load_callibration ': strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())}
        # self.logs.single_dataset.append(self.logs.camera_end)
        # print self.logs.single_dataset
        if self.stone_feat:
            self.snapshot_trigger = True
            self.show_camera_image = False
            self.view.qImage_show(self.view.im_show)
            self.view.setListInfo('Calibration Loaded')
            self.view.set_enabled_selection(start=False,stop=False,audio_out_chn=False,new_cal=False,load_cal=False,start_default=False,reset=False)


    def nextFrameSlot(self):
        """nextFrameSlot func

        The camera frame recognizes movement in the scene by compare all greyscale
        pixels with the previous frame.
        If there was some changes, the sound is paused.

        """
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
            if np.sum(gray) < 1000000 and (self.start_time - self.stop_time > 3) and self.stop_flag_init == False:
                # self.stop_flag_init = True
                self.stop_time = time.time()
                self.min_move = 0
                self.stop_n_play()
            if self.show_camera_image == True:
                self.view.qImage_show(self.camera.frame)
        else:
            self.__del__()

    def auto_snapshot(self,prev):
        """nextFrameSlot func

        The camera frame recognizes movement in the scene by compare all greyscale
        pixels with the previous frame.
        If there was some changes, the sound is paused.

        """
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
            if self.stone_feat:
                self.play()
            else:
                self.audio_controller.s.stop()
            # self.logs.camera_start = {'auto_snapshot ': strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())}
            # self.logs.single_dataset.append(self.logs.camera_end)
            # print self.logs.single_dataset


    def follow_garden(self):
        """follow_garden func

        This callback function is used to control the sonic anchor.
        Every frame the sonic anchor has to know the previous direction and all
        shadow lines in its view.
        In order of previous moves and current generated directions, the next
        movement is calculated.

        """

        if self.view:
            try:
                img_garden_copy = self.view.im_show.copy()
                color_img = self.view.im_show.copy()
            except:
                self.audio_controller.stop()
            finally:
                color_img = ds.color_stones(color_img,self.stone_feat)
                garden_update_img,color_img = self.path_finder[0].finder(img_garden_copy,color_img)
                for i in range(1,self.view.detector_amount.value()):
                    garden_update_img,color_img = self.path_finder[i].finder(garden_update_img,color_img)
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


    def auto_slider(self):
        """auto_slider func

        Contour, Speed, Radius and angle slider can be automated.

        """
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
        """threshold_slider1 func

        set Radius of sonic anchor.

        """
        for i in range(0,self.view.detector_amount.value()):
            self.path_finder[i].radius  = self.view.slider1.value()
        txt1 = "Radius of Circle " + str(self.path_finder[0].radius)
        self.view.txtslider1.setText(txt1)

    def threshold_slider2(self):
        """threshold_slider2 func

        set Speed of sonic anchor.

        """
        txt1 = "Speed " + str(float(self.view.slider2.value())/100.*float(self.view.fps))
        self.view.txtslider2.setText(txt1)
        self.path_timer.stop()
        for i in range(0,self.view.detector_amount.value()):
            self.path_finder[i].speed = self.linlin(float(self.view.slider2.value()),0,100,1000,10)
        # Change for multiple virtual objects moving
        self.path_timer.start(self.path_finder[0].speed)
        # self.path_timer.setInterval(self.slider2.value())

    def threshold_slider3(self):
        """threshold_slider3 func

        set Detecting Angle of sonic anchor.

        """
        for i in range(0,self.view.detector_amount.value()):
            self.path_finder[i].detecting_angle = self.view.slider3.value()
        txt1 = "Detecting Angle " + str(self.path_finder[0].detecting_angle)
        self.view.txtslider3.setText(txt1)

    def contour_config(self):
        self.contour_config_v = int(self.view.contour_slider.value()/10.)

        try:
            self.stone_feat,self.view.im_show  = ds.getFeatures(self.view.im_show, self.contour_config_v)
            self.view.qImage_show(self.view.im_show)
        except:
            print 'no contour image'

    def save_logs():
        self.logs.right_answers = {"xtilt": game.t_hor,"ytilt": game.t_vert,
                        "xpos": game.pos_x_name, "ypos": game.pos_y_name, "speed": game.speed, "distance": game.distance}

        logs.leveltime_end = time.time()
        total_t = logs.leveltime_end-logs.leveltime_start
        leveltime_total = {"start": logs.leveltime_start, "end": logs.leveltime_end, "total": total_t}
        self.logs.single_dataset = [game.level, logs.right_answers,  logs.temp_listen_p, leveltime_total, logs.checked_data_total]
        self.logs.single_dataset.append(logs.single_dataset)
        print self.logs.single_dataset

    def serialize(self):
        self.logs.dataset = [self.logs.single_dataset]
        print self.logs.dataset
        with open("../saved_pickle/file"+str(self.view.save_text.text())+".pickle", "wb") as pfile:
            pickle.dump(self.logs.dataset, pfile)

    def deserialize(self):
        with open("../saved_pickle/file.pickle", "rb") as pfile:
            data = pickle.load(pfile)
        return data

    def linlin(self,x, smi, sma, dmi, dma):
        """
        Parameters
        -----------
        x : float
            value
        smi : float
            range min within value
        sma : float
            range max within Value
        dmi : float
            range min target value
        dma : float
            range max target value

        linear mapping from one range with value to another

        """
        return (x-smi)/(sma-smi)*(dma-dmi) + dmi
class Logs():
    def __init__(self):
        self.camera_start = {}
        self.image_infos = {}
        self.camera_end = {}
        self.single_dataset = []
        self.dataset = []
