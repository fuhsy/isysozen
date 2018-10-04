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
import pylab
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

class View(QtGui.QWidget):
    def __del__(self):
        # self.cap.release()
        super(QtGui.QWidget, self).deleteLater()

    def __init__(self, *args):
        self.app = QtGui.QApplication(sys.argv)
        super(QtGui.QWidget, self).__init__()
        # self.theme = audio_theme.AudioTheme('water')
        self.fps = 50
        # print pa_get_output_max_channels(4)
        #Lowest snapshot threshold for starting detection

        self.brightness_value_min = 1.2
        self.brightness_value_max = 1.45
        self.smooth_mean_dif = []
        self.brightness = 0
        self.brightness_plt = []
        self.sampleinterval = 0.1
        self.brightness_v = 0
        self.timewindow=10
        self.size = (800,600)
        self.layout = QtGui.QGridLayout()
        self.w = QtGui.QWidget()
        self.w.setMinimumHeight(480)
        self.pic = QtGui.QLabel()

        self.video_frame = QtGui.QLabel()
        self.select_audio_output = QtGui.QComboBox()
        self.detector_amount = QtGui.QSpinBox()
        self.min_detectors = 1
        self.max_detectors = 5
        self.detector_amount.setMinimum(self.min_detectors)
        self.detector_amount.setMaximum(self.max_detectors)
        self.detector_amount.setAlignment(QtCore.Qt.AlignRight)
        # audio_index_count =0
        # self.devicelist = pa_get_output_devices()
        # for i in range(0,len(self.devicelist[0])):
        #     self.select_audio_output.addItem(self.devicelist[0][i])
            # audio_index_count = audio_index_count+1
        self.select_theme = QtGui.QComboBox()


        #self.pic.setPixmap(QtGui.QPixmap('sand_lines.png').scaled(600, 400, QtCore.Qt.KeepAspectRatio))
        self.button_start = QtGui.QPushButton('Camera Connect')
        # self.button_start_default = QtGui.QPushButton('Start Default Image')
        self.button_load_cal = QtGui.QPushButton('Load Calibration')
        self.button_stop = QtGui.QPushButton('Pause/Play')
        self.button_play = QtGui.QPushButton('Start')
        self.button_reset = QtGui.QPushButton('Reset Scene')
        self.button_new_cal = QtGui.QPushButton('New Calibration')
        self.auto_checkbox = QtGui.QCheckBox('Auto Slider')
        self.slider1 = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.slider2 = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.slider3 = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.contour_slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.txtslider1 = QtGui.QLabel('Radius of Circle')
        self.txtslider2 = QtGui.QLabel('Speed '+str(self.fps)+' fps')
        self.txtslider3 = QtGui.QLabel('Detecting Angle')
        self.contour_slider_txt = QtGui.QLabel('Contour Detection')
        self.detector_amount_txt = QtGui.QLabel('                                             Amount of Detectors')
        self.plt = pg.PlotWidget(title='Lightning Conditions')
        self.plt.setFixedWidth(300)
        self.plt.setRange(yRange=[0.9,1.8])
        self.plt.resize(*self.size)
        self.plt.showGrid(x=True,y=True)
        self.plt.setLabel('left', 'Brightness')

        self.slider1.setFixedWidth(300)
        self.slider1.setRange(5,45)
        self.slider2.setFixedWidth(300)
        self.slider2.setRange(1,100)
        self.slider3.setFixedWidth(300)
        self.slider3.setRange(2,120)
        self.contour_slider.setFixedWidth(300)
        self.contour_slider.setRange(0,40)
        self.txtslider1.setFixedWidth(300)
        self.txtslider2.setFixedWidth(300)
        self.txtslider3.setFixedWidth(300)
        self.contour_slider_txt.setFixedWidth(300)
        self.detector_amount_txt.setFixedWidth(300)

        # self.button_start_default.setFixedWidth(300)
        self.button_stop.setFixedWidth(300)
        self.button_play.setFixedWidth(300)
        self.button_reset.setFixedWidth(300)
        self.select_audio_output.setFixedWidth(300)
        self.detector_amount.setFixedWidth(150)
        self.select_theme.setFixedWidth(300)
        self.button_start.setFixedWidth(300)
        self.button_load_cal.setFixedWidth(300)
        self.button_new_cal.setFixedWidth(300)
        self.listw = QtGui.QListWidget()
        self.listw.setFixedWidth(300)
        #self.plot = pg.PlotWidget()
        self.w.setLayout(self.layout)
        self.layout.setMargin(10)
        self.widget_pos = 0
        self.layout.addWidget(self.button_start, self.widget_pos, 0)
        self.widget_pos+=1
        self.layout.addWidget(self.select_audio_output,self.widget_pos,0)
        self.widget_pos+=1
        self.layout.addWidget(self.select_theme,self.widget_pos,0)
        self.widget_pos+=1
        self.layout.addWidget(self.detector_amount_txt,self.widget_pos,0)
        # self.widget_pos+=1
        self.layout.addWidget(self.detector_amount,self.widget_pos,0)
        self.widget_pos+=1
        self.layout.addWidget(self.button_new_cal, self.widget_pos, 0)
        self.widget_pos+=1
        self.layout.addWidget(self.button_load_cal, self.widget_pos, 0)
        # self.widget_pos+=1
        # self.layout.addWidget(self.button_start_default,self.widget_pos,0)
        self.widget_pos+=1
        self.layout.addWidget(self.button_stop,self.widget_pos,0)
        self.widget_pos+=1
        self.layout.addWidget(self.button_play,self.widget_pos,0)
        self.widget_pos+=1
        self.layout.addWidget(self.button_reset,self.widget_pos,0)
        self.widget_pos+=1
        self.layout.addWidget(self.auto_checkbox,self.widget_pos,0)
        self.widget_pos+=1
        self.layout.addWidget(self.contour_slider_txt,self.widget_pos,0)
        self.widget_pos+=1
        self.layout.addWidget(self.contour_slider,self.widget_pos,0)
        self.widget_pos+=1
        self.layout.addWidget(self.txtslider1,self.widget_pos,0)
        self.widget_pos+=1
        self.layout.addWidget(self.slider1,self.widget_pos,0)
        self.widget_pos+=1
        self.layout.addWidget(self.txtslider2,self.widget_pos,0)
        self.widget_pos+=1
        self.layout.addWidget(self.slider2,self.widget_pos,0)
        self.widget_pos+=1
        self.layout.addWidget(self.txtslider3,self.widget_pos,0)
        self.widget_pos+=1
        self.layout.addWidget(self.slider3,self.widget_pos,0)
        self.widget_pos+=1
        # self.layout.addWidget(self.plt,self.widget_pos,0)
        # self.widget_pos+=1
        self.layout.addWidget(self.listw, self.widget_pos, 0)
        self.widget_pos+=1

        self.connect(self, QtCore.SIGNAL('triggered()'), self.closeEvent)
        self.layout.addWidget(self.pic, 0, 1, self.widget_pos, 1)
        self.layout.addWidget(self.video_frame, 0, 1, self.widget_pos, 1)

        # self.select_audio_output.setEnabled(False)
        # self.view.im_show

        # self._interval = int(self.sampleinterval*1000)
        # self._bufsize = int(self.timewindow/self.sampleinterval)
        # self.databuffer = collections.deque([0.0]*self._bufsize, self._bufsize)
        # self.databuffer_threshold_min = collections.deque([0.0]*self._bufsize, self._bufsize)
        # self.databuffer_threshold_max = collections.deque([0.0]*self._bufsize, self._bufsize)
        # self.x_brightness = np.linspace(-self.timewindow, 0.0, self._bufsize)
        # self.y_brightness = np.zeros(self._bufsize, dtype=np.float)
        # self.y_brightness_threshold_v_min = np.zeros(self._bufsize, dtype=np.float)
        # self.y_brightness_threshold_v_max = np.zeros(self._bufsize, dtype=np.float)
        # for item in self.y_brightness_threshold_v_min:
        #     item = self.brightness_value_min
        # for item in self.y_brightness_threshold_v_max:
        #     item = self.brightness_value_max

        # self.plt.setLabel('bottom', 'time')
        # self.curve = self.plt.plot(self.x_brightness, self.y_brightness, pen=(255,0,0))
        # self.brightness_threshold_plot_min = self.plt.plot(self.x_brightness,self.y_brightness_threshold_v_min,"x", pen=(0,255,0))
        # self.brightness_threshold_plot_max = self.plt.plot(self.x_brightness,self.y_brightness_threshold_v_max,"x", pen=(0,255,0))
        #TEST
        self.im = cv2.imread('images/test2.png')
        self.im_show = None
        self.im_standard = cv2.imread('images/test2.png')

        # n_out_channel = pa_get_output_max_channels(self.output_device_index+1)
        # n_out_channel = 4
        # self.audio_controller = actrl.AudioController(n_out_channel, self.theme , self.output_device_index)
        self.button_load_cal.setEnabled(False)
        self.button_new_cal.setEnabled(False)
        # self.button_start_default.setEnabled(False)
        self.button_stop.setEnabled(False)
        self.button_play.setEnabled(False)
        self.button_reset.setEnabled(False)
        self.detector_amount.setEnabled(False)
        self.contour_slider.setEnabled(False)
        self.audio_controller = None
        self.select_audio_output.setEnabled(False)
        self.select_theme.setEnabled(False)
        self.slider1.setEnabled(False)
        self.slider2.setEnabled(False)
        self.slider3.setEnabled(False)
        self.button_reset.setEnabled(False)
        self.controller = None
        self.w.show()

    def register(self, controller):
        self.controller = controller

    def register_buttons(self):
        self.button_start.clicked.connect(lambda: self.controller.start())
        self.button_stop.clicked.connect(lambda: self.controller.stop_n_play())
        self.button_play.clicked.connect(lambda: self.controller.play())
        self.button_reset.clicked.connect(lambda: self.controller.reset())
        self.select_audio_output.currentIndexChanged.connect(lambda: self.controller.setDefaultSoundDevice())
        self.select_theme.currentIndexChanged.connect(lambda: self.controller.setTheme())
        self.button_load_cal.clicked.connect(lambda: self.controller.load_calibration())
        self.button_new_cal.clicked.connect(lambda: self.controller.new_calibration())
        # self.button_start_default.clicked.connect(lambda: self.controller.start_default_image())
        self.slider1.sliderReleased.connect(lambda: self.controller.threshold_slider1())
        self.slider2.sliderReleased.connect(lambda: self.controller.threshold_slider2())
        self.slider3.sliderReleased.connect(lambda: self.controller.threshold_slider3())
        self.auto_checkbox.clicked.connect(lambda: self.controller.auto_slider())
        self.contour_slider.sliderReleased.connect(lambda: self.controller.contour_config())


    def setSliderDefault(self,radius=25,speed=(1./50.),angle=60):
        self.slider1.setValue(radius)
        #Speed Slider Default Value to max
        self.slider2.setValue(50)
        self.slider3.setValue(angle)
        self.contour_slider.setValue(20)


    # def getBrightness(self):
    #     return self.brightness_v
    #
    # def updateplot(self):
    #     self.databuffer.append( self.getBrightness())
    #     self.databuffer_threshold_min.append(1.1)
    #     self.databuffer_threshold_max.append(1.4)
    #     self.y_brightness[:] = self.databuffer
    #     self.y_brightness_threshold_v_min[:] = self.databuffer_threshold_min
    #     self.y_brightness_threshold_v_max[:] = self.databuffer_threshold_max
    #     self.brightness_threshold_plot_min.setData(self.x_brightness, self.y_brightness_threshold_v_min)
    #     self.brightness_threshold_plot_max.setData(self.x_brightness, self.y_brightness_threshold_v_max)
    #     self.curve.setData(self.x_brightness, self.y_brightness)
    #     self.app.processEvents()

    def setFPS(self, fps):
        self.fps = fps

    # def new_calibration(self):
    #     #self.edgeDetectionApproach()
    #     itemlist= QtGui.QListWidgetItem('Camera Stopped')
    #     self.img = self.frame.copy()
    #     cv2.namedWindow('image')
    #     cv2.imshow('image',self.img)
    #     #cv2.setMouseCallback('canny',img)
    #     cv2.setMouseCallback('image',self.draw_circle)
    #     self.listw.addItem(itemlist)
    #     self.cap.release()
    #     self.timer.stop()

    def setListInfo(self,message):
        itemlist= QtGui.QListWidgetItem(message)
        self.listw.addItem(itemlist)

    def qImage_show(self,frame_input):
        qformat= QImage.Format_Indexed8
        if len(frame_input.shape) == 3:
            if frame_input.shape[2] == 4:
                qformat=QImage.Format_RGBA8888
            else:
                qformat=QImage.Format_RGB888

        temp_img = QtGui.QImage(frame_input, frame_input.shape[1], frame_input.shape[0], frame_input.strides[0], qformat)
        temp_img = temp_img.rgbSwapped()
        self.video_frame.setPixmap(QtGui.QPixmap.fromImage(temp_img))
        self.video_frame.setScaledContents(True)

    # def draw_circle(self,event,x,y,flags,param):
    #     global mouseX,mouseY
    #     # cv2.imshow('image',self.img)
    #     # cv2.waitKey(0)
    #     if event == cv2.EVENT_LBUTTONUP:
    #         cv2.circle(self.img,(x,y),4,(255,255,255),2)
    #         print (x,' , ',y)
    #         mouseX,mouseY = x,y
    #         temparr = [x,y]
    #         self.calibration_pts.append(temparr)
    #         #print(len(self.calibration_pts))
    #         #print(self.calibration_pts)
    #         if len(self.calibration_pts) == 4:
    #             cv2.destroyAllWindows()
    #             self.calibration_pts = np.asarray(self.calibration_pts)
    #             self.calibration_pts = self.calibration_pts.astype(int)
    #             warped = callibration.four_point_transform(self.img,self.calibration_pts)
    #             np.save('caldata.npy', self.calibration_pts)
    #             self.load_calibration()

    def set_theme_box(self,theme):
        for k,v in theme.type.items():
            self.select_theme.addItem(k)

    def Cancel(self):
        print('closed')
        #self.close()
        #self.cap.release()
        #super(QtGui.QWidget, self).deleteLater()
    def closeEvent(self, event):
        print ("Closing")
        self.deleteLater()

    def deleteLater(self):
        print('closed')
        self.cap.release()
        super(QtGui.QWidget, self).deleteLater()

    def set_enabled_selection(self,start=True,det_am=True,audio_out_chn=True,cnt_sl=True,theme=True,new_cal=True,load_cal=True,start_default=True,stop=True,play=True,reset=True,sl1=True,sl2=True,sl3=True):
        self.button_start.setEnabled(start)
        self.select_audio_output.setEnabled(audio_out_chn)
        self.select_theme.setEnabled(theme)
        self.contour_slider.setEnabled(cnt_sl)
        self.detector_amount.setEnabled(det_am)
        self.button_new_cal.setEnabled(new_cal)
        self.button_load_cal.setEnabled(load_cal)
        # self.button_start_default.setEnabled(start_default)
        self.button_stop.setEnabled(stop)
        self.button_play.setEnabled(play)
        self.button_reset.setEnabled(reset)
        self.slider1.setEnabled(sl1)
        self.slider2.setEnabled(sl2)
        self.slider3.setEnabled(sl3)
    def set_enabled_selection_n(self,start=False,det_am=False,audio_out_chn=False,cnt_sl=False,theme=False,new_cal=False,load_cal=False,start_default=False,stop=False,play=False,reset=False,sl1=False,sl2=False,sl3=False):
        self.button_start.setEnabled(start)
        self.select_audio_output.setEnabled(audio_out_chn)
        self.select_theme.setEnabled(theme)
        self.contour_slider.setEnabled(cnt_sl)
        self.detector_amount.setEnabled(det_am)
        self.button_new_cal.setEnabled(new_cal)
        self.button_load_cal.setEnabled(load_cal)
        # self.button_start_default.setEnabled(start_default)
        self.button_stop.setEnabled(stop)
        self.button_play.setEnabled(play)
        self.button_reset.setEnabled(reset)
        self.slider1.setEnabled(sl1)
        self.slider2.setEnabled(sl2)
        self.slider3.setEnabled(sl3)
