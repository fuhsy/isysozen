import cv2,sys, time
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel,QGroupBox, QLineEdit, QComboBox, QMessageBox,\
    QSlider, QProgressBar, QGridLayout, QSpinBox, QListWidget, QMainWindow, QCheckBox, QListWidgetItem
from PyQt5.QtGui import QImage,QPixmap
import pyqtgraph as pg
import PyQt5.QtCore as QtCore
import re
import subprocess
import os
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image, ImageStat
from matplotlib import style
from collections import deque
import pylab
import thread
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

# Gui elements

class View(QMainWindow):
    # def __del__(self):
        # self.cap.release()
        # super(QWidget, self).deleteLater()

    def __init__(self, *args):
        self.app = QApplication(sys.argv)
        super(QMainWindow, self).__init__()
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
        self.timewindow = 10
        self.size = (1920,1080)
        self.layout = QGridLayout()
        # self.w = QWidget()
        self.pic = QLabel()
        self.video_frame = QLabel()
        self.select_audio_output =  QComboBox()
        self.audio_submit = QPushButton('Submit')
        self.detector_amount =  QSpinBox()
        self.min_detectors = 1
        self.max_detectors = 5
        self.detector_amount.setMinimum(self.min_detectors)
        self.detector_amount.setMaximum(self.max_detectors)
        self.detector_amount.setAlignment(QtCore.Qt.AlignRight)
        self.button_start = QPushButton('Camera Connect')
        self.button_start_default = QPushButton('Start Computer GUI')
        self.button_listen_task = QPushButton('Listening Task')
        self.button_listen_task_2 = QPushButton('Listening Task 2')
        self.button_load_cal = QPushButton('Load Calibration')
        self.button_stop = QPushButton('Pause/Play')
        self.save_btn = QPushButton('Save Dataset')
        self.save_text = QLineEdit('User ID')
        self.button_play = QPushButton('Start')
        self.button_reset = QPushButton('Reset Scene')
        self.button_new_cal = QPushButton('New Calibration')
        self.auto_checkbox = QCheckBox('Auto Slider')
        self.slider1 = QSlider(QtCore.Qt.Horizontal)
        self.slider2 = QSlider(QtCore.Qt.Horizontal)
        self.slider3 = QSlider(QtCore.Qt.Horizontal)
        self.contour_slider = QSlider(QtCore.Qt.Horizontal)
        self.txtslider1 = QLabel('Radius of Circle')
        self.txtslider2 = QLabel('Speed '+str(self.fps)+' fps')
        self.txtslider3 = QLabel('Detecting Angle')
        self.contour_slider_txt = QLabel('Contour Detection')
        self.detector_amount_txt = QLabel('                                             Amount of Detectors')

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
        self.save_btn.setFixedWidth(300)
        self.save_text.setFixedWidth(300)
        self.button_start_default.setFixedWidth(300)
        self.button_stop.setFixedWidth(300)
        self.button_play.setFixedWidth(300)
        self.button_reset.setFixedWidth(300)
        self.button_listen_task.setFixedWidth(300)
        self.button_listen_task_2.setFixedWidth(300)
        self.select_audio_output.setFixedWidth(300)
        self.audio_submit.setFixedWidth(300)
        self.detector_amount.setFixedWidth(150)
        # self.select_theme.setFixedWidth(300)
        self.button_start.setFixedWidth(300)
        self.button_load_cal.setFixedWidth(300)
        self.button_new_cal.setFixedWidth(300)
        self.listw = QListWidget()
        self.listw.setFixedWidth(300)
        #self.plot = pg.PlotWidget()
        self.setLayout(self.layout)
        self.layout.setMargin(10)
        self.widget_pos = 0
        self.layout.addWidget(self.button_start, self.widget_pos, 0)
        self.widget_pos+=1
        self.layout.addWidget(self.button_start_default,self.widget_pos,0)
        self.widget_pos+=1
        self.layout.addWidget(self.button_listen_task,self.widget_pos,0)
        self.widget_pos+=1
        self.layout.addWidget(self.button_listen_task_2,self.widget_pos,0)
        self.widget_pos+=1
        self.layout.addWidget(self.select_audio_output,self.widget_pos,0)
        self.widget_pos+=1
        self.layout.addWidget(self.audio_submit,self.widget_pos,0)
        self.widget_pos+=1
        # self.layout.addWidget(self.select_theme,self.widget_pos,0)
        # self.widget_pos+=1
        self.layout.addWidget(self.detector_amount_txt,self.widget_pos,0)
        self.layout.addWidget(self.detector_amount,self.widget_pos,0)
        self.widget_pos+=1
        self.layout.addWidget(self.button_new_cal, self.widget_pos, 0)
        self.widget_pos+=1
        self.layout.addWidget(self.button_load_cal, self.widget_pos, 0)
        self.widget_pos+=1
        self.layout.addWidget(self.button_stop,self.widget_pos,0)
        self.widget_pos+=1
        self.layout.addWidget(self.button_play,self.widget_pos,0)
        self.widget_pos+=1
        self.layout.addWidget(self.button_reset,self.widget_pos,0)
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
        self.layout.addWidget(self.save_btn, self.widget_pos, 0)
        self.widget_pos+=1
        self.layout.addWidget(self.save_text, self.widget_pos, 0)
        self.widget_pos+=1
        self.layout.addWidget(self.listw, self.widget_pos, 0)
        self.widget_pos+=1
        # self.connect(self, QtCore.SIGNAL('triggered()'), self.closeEvent)
        self.layout.addWidget(self.pic, 0, 1, self.widget_pos, 1)
        self.layout.addWidget(self.video_frame, 0, 1, self.widget_pos, 1)
        self.im = cv2.imread("../images/default/export.jpg")
        self.im_show = None
        self.button_start.setEnabled(False)
        self.button_start_default.setEnabled(False)
        self.button_load_cal.setEnabled(False)
        self.button_new_cal.setEnabled(False)
        self.button_listen_task.setEnabled(False)
        self.button_listen_task_2.setEnabled(False)
        # self.button_start_default.setEnabled(False)
        self.button_stop.setEnabled(False)
        self.button_play.setEnabled(False)
        self.button_reset.setEnabled(False)
        self.detector_amount.setEnabled(False)
        self.contour_slider.setEnabled(False)
        self.audio_controller = None
        self.select_audio_output.setEnabled(False)
        self.save_btn.setEnabled(False)
        # self.select_theme.setEnabled(False)
        self.slider1.setEnabled(False)
        self.slider2.setEnabled(False)
        self.slider3.setEnabled(False)
        self.button_reset.setEnabled(False)
        self.controller = None
        self.setCentralWidget(QWidget(self))
        self.centralWidget().setLayout(self.layout)
        self.show()
    #     start_new_thread(self.run,())
    #
    # def run(self):
    #     while 1:
    #         self.app.processEvents()
    #         time.sleep(0.1)
    def register(self, controller):
        self.controller = controller

    def register_buttons(self):
        self.button_start.clicked.connect(lambda: self.controller.start())
        # self.connect(self.button_start, QtCore.SIGNAL("clicked()"), self.controller.start)
        # self.connect(self.ui.PB_button1, QtCore.SIGNAL("clicked()"),
        #              self.funct_button1)
        self.button_stop.clicked.connect(lambda: self.controller.stop_n_play())
        self.button_play.clicked.connect(lambda: self.controller.play())
        self.button_reset.clicked.connect(lambda: self.controller.reset())
        self.save_btn.clicked.connect(lambda: self.controller.serialize())
        # self.select_audio_output.currentIndexChanged.connect(lambda: self.controller.setDefaultSoundDevice())
        self.audio_submit.clicked.connect(lambda: self.controller.setDefaultSoundDevice())
        self.button_listen_task.clicked.connect(lambda: self.controller.listen_task(1))
        self.button_listen_task_2.clicked.connect(lambda: self.controller.listen_task(2))
        # self.select_theme.currentIndexChanged.connect(lambda: self.controller.setTheme())
        self.button_load_cal.clicked.connect(lambda: self.controller.load_calibration())
        self.button_new_cal.clicked.connect(lambda: self.controller.new_calibration())
        self.button_start_default.clicked.connect(lambda: self.controller.start_default_image())
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
        self.select_audio_output.setEnabled(True)



    def setFPS(self, fps):
        self.fps = fps


    def setListInfo(self,message):
        itemlist= QListWidgetItem(message)
        self.listw.addItem(itemlist)

    def qImage_show(self,frame_input):
        qformat= QImage.Format_Indexed8
        if len(frame_input.shape) == 3:
            if frame_input.shape[2] == 4:
                qformat=QImage.Format_RGBA8888
            else:
                qformat=QImage.Format_RGB888

        temp_img = QImage(frame_input, frame_input.shape[1], frame_input.shape[0], frame_input.strides[0], qformat)
        temp_img = temp_img.rgbSwapped()
        self.video_frame.setPixmap(QPixmap.fromImage(temp_img))
        self.video_frame.setScaledContents(True)


    def Cancel(self):
        print('closed')

    def closeEvent(self, event):
        print ("Closing")
        self.deleteLater()

    def deleteLater(self):
        print('closed')
        # self.cap.release()
        super(QWidget, self).deleteLater()

    def set_enabled_selection(self,start=True,det_am=True,audio_out_chn=True,cnt_sl=True,new_cal=True,load_cal=True,start_default=True,stop=True,play=True,reset=True,sl1=True,sl2=True,sl3=True):
        self.button_start.setEnabled(start)
        self.select_audio_output.setEnabled(audio_out_chn)
        self.contour_slider.setEnabled(cnt_sl)
        self.detector_amount.setEnabled(det_am)
        self.button_new_cal.setEnabled(new_cal)
        self.button_load_cal.setEnabled(load_cal)
        self.button_start_default.setEnabled(start_default)
        self.button_stop.setEnabled(stop)
        self.button_play.setEnabled(play)
        self.button_reset.setEnabled(reset)
        self.slider1.setEnabled(sl1)
        self.slider2.setEnabled(sl2)
        self.slider3.setEnabled(sl3)

        
    def set_enabled_selection_n(self,start=False,det_am=False,audio_out_chn=False,cnt_sl=False,new_cal=False,load_cal=False,start_default=False,stop=False,play=False,reset=False,sl1=False,sl2=False,sl3=False):
        self.button_start.setEnabled(start)
        self.select_audio_output.setEnabled(audio_out_chn)
        self.contour_slider.setEnabled(cnt_sl)
        self.detector_amount.setEnabled(det_am)
        self.button_new_cal.setEnabled(new_cal)
        self.button_load_cal.setEnabled(load_cal)
        self.button_start_default.setEnabled(start_default)
        self.button_stop.setEnabled(stop)
        self.button_play.setEnabled(play)
        self.button_reset.setEnabled(reset)
        self.slider1.setEnabled(sl1)
        self.slider2.setEnabled(sl2)
        self.slider3.setEnabled(sl3)
