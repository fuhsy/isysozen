
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

class QtCapture(QtGui.QWidget):
    def __init__(self, *args):
        self.app = QtGui.QApplication(sys.argv)
        super(QtGui.QWidget, self).__init__()
        self.theme = audio_theme.AudioTheme('water')
        self.fps = 50
        # print pa_get_output_max_channels(4)
        #Lowest snapshot threshold for starting detection
        self.output_device_index = 0
        self.snap_thres = 2.6
        self.brightness_value_min = 1.2
        self.brightness_value_max = 1.45
        self.smooth_mean_dif = []
        self.brightness = 0
        self.brightness_plt = []
        self.sampleinterval = 0.1
        self.brightness_v = 0
        self.timewindow=10
        self.size = (600,400)
        self.layout = QtGui.QGridLayout()
        self.w = QtGui.QWidget()
        self.w.setMinimumHeight(480)
        self.capture = None
        self.frame = None
        self.pic = QtGui.QLabel()
        self.video_frame = QtGui.QLabel()
        self.select_audio_output = QtGui.QComboBox()
        audio_index_count =0
        self.devicelist = pa_get_output_devices()
        for i in range(0,len(self.devicelist[0])):
            self.select_audio_output.addItem(self.devicelist[0][i])
            audio_index_count = audio_index_count+1
        self.select_theme = QtGui.QComboBox()
        for k,v in self.theme.type.items():
            self.select_theme.addItem(k)

        #self.pic.setPixmap(QtGui.QPixmap('sand_lines.png').scaled(600, 400, QtCore.Qt.KeepAspectRatio))
        self.button_start = QtGui.QPushButton('Camera Connect')
        self.button_start_default = QtGui.QPushButton('Start Default Image')
        self.button_load_cal = QtGui.QPushButton('Load Calibration')
        self.slider1 = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.slider2 = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.slider3 = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.slider4 = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.slider5 = QtGui.QSlider(QtCore.Qt.Horizontal)

        self.txtslider1 = QtGui.QLabel('Radius of Circle')
        self.txtslider2 = QtGui.QLabel('Speed '+str(self.fps)+' fps')
        self.txtslider3 = QtGui.QLabel('Detecting Angle')
        self.txtslider4 = QtGui.QLabel('-empty-')
        self.txtslider5 = QtGui.QLabel('-empty-')
        self.slider1.setFixedWidth(300)
        self.slider1.setRange(2,100)
        self.slider2.setFixedWidth(300)
        self.slider2.setRange(2,100)
        self.slider3.setFixedWidth(300)
        self.slider4.setFixedWidth(300)
        self.slider5.setFixedWidth(300)
        self.txtslider1.setFixedWidth(300)
        self.txtslider2.setFixedWidth(300)
        self.txtslider3.setFixedWidth(300)
        self.txtslider4.setFixedWidth(300)
        self.txtslider5.setFixedWidth(300)

        self.button_start_default.setFixedWidth(300)
        self.select_audio_output.setFixedWidth(300)
        self.select_theme.setFixedWidth(300)
        self.button_start.setFixedWidth(300)
        self.button_load_cal.setFixedWidth(300)
        self.button_end = QtGui.QPushButton('New Calibration')
        self.button_end.setFixedWidth(300)
        self.button_start.clicked.connect(lambda: self.start())
        self.select_audio_output.currentIndexChanged.connect(lambda: self.setDefaultSoundDevice())
        self.select_theme.currentIndexChanged.connect(lambda: self.setTheme())
        self.button_load_cal.clicked.connect(lambda: self.load_calibration())
        self.button_end.clicked.connect(lambda: self.new_calibration())
        self.button_start_default.clicked.connect(lambda: self.start_default_image())
        self.slider1.sliderReleased.connect(lambda: self.threshold_slider1())
        self.slider2.sliderReleased.connect(lambda: self.threshold_slider2())
        self.slider3.sliderReleased.connect(lambda: self.threshold_slider3())
        self.slider4.sliderReleased.connect(lambda: self.threshold_slider4())
        self.slider5.sliderReleased.connect(lambda: self.threshold_slider5())
        self.listw = QtGui.QListWidget()
        self.listw.setFixedWidth(300)
        #self.plot = pg.PlotWidget()

        self.w.setLayout(self.layout)
        self.layout.setMargin(10)



        self.layout.addWidget(self.button_start, 0, 0)
        self.layout.addWidget(self.select_audio_output,1,0)
        self.layout.addWidget(self.select_theme,2,0)
        self.layout.addWidget(self.button_end, 3, 0)
        self.layout.addWidget(self.button_load_cal, 4, 0)
        self.layout.addWidget(self.button_start_default,5,0)
        self.layout.addWidget(self.txtslider1,6,0)
        self.layout.addWidget(self.slider1,7,0)
        self.layout.addWidget(self.txtslider2,8,0)
        self.layout.addWidget(self.slider2,9,0)
        self.layout.addWidget(self.txtslider3,10,0)
        self.layout.addWidget(self.slider3,11,0)
        self.layout.addWidget(self.txtslider4,12,0)
        self.layout.addWidget(self.slider4,13,0)
        self.layout.addWidget(self.txtslider5,14,0)
        self.layout.addWidget(self.slider5,15,0)
        self.layout.addWidget(self.listw, 17, 0)
        # self.layout.setAlignment(self.txtslider1, QtCore.Qt.AlignCenter)
        # self.layout.setAlignment(self.txtslider2, QtCore.Qt.AlignCenter)
        # self.layout.setAlignment(self.txtslider3, QtCore.Qt.AlignCenter)
        # self.layout.setAlignment(self.txtslider4, QtCore.Qt.AlignCenter)
        # self.layout.setAlignment(self.txtslider5, QtCore.Qt.AlignCenter)
        self.connect(self, QtCore.SIGNAL('triggered()'), self.closeEvent)
        self.layout.addWidget(self.pic, 0, 1, 18, 1)
        self.layout.addWidget(self.video_frame, 0, 1, 18, 1)
        self.button_load_cal.setEnabled(False)
        self.button_end.setEnabled(False)
        self.button_start_default.setEnabled(False)
        # self.select_audio_output.setEnabled(False)
        self.calibration_pts = []


        self._interval = int(self.sampleinterval*1000)
        self._bufsize = int(self.timewindow/self.sampleinterval)
        self.databuffer = collections.deque([0.0]*self._bufsize, self._bufsize)
        self.databuffer_threshold_min = collections.deque([0.0]*self._bufsize, self._bufsize)
        self.databuffer_threshold_max = collections.deque([0.0]*self._bufsize, self._bufsize)
        self.x_brightness = np.linspace(-self.timewindow, 0.0, self._bufsize)
        self.y_brightness = np.zeros(self._bufsize, dtype=np.float)
        self.y_brightness_threshold_v_min = np.zeros(self._bufsize, dtype=np.float)
        self.y_brightness_threshold_v_max = np.zeros(self._bufsize, dtype=np.float)
        for item in self.y_brightness_threshold_v_min:
            item = self.brightness_value_min
        for item in self.y_brightness_threshold_v_max:
            item = self.brightness_value_max

        self.plt = pg.PlotWidget(title='Lightning Condictions')
        self.layout.addWidget(self.plt,16,0)
        self.plt.setFixedWidth(300)
        self.plt.setRange(yRange=[0.9,1.8])

        self.plt.resize(*self.size)
        self.plt.showGrid(x=True,y=True)
        self.plt.setLabel('left', 'Brightness')

        # self.plt.setLabel('bottom', 'time')
        self.curve = self.plt.plot(self.x_brightness, self.y_brightness, pen=(255,0,0))
        self.brightness_threshold_plot_min = self.plt.plot(self.x_brightness,self.y_brightness_threshold_v_min,"x", pen=(0,255,0))
        self.brightness_threshold_plot_max = self.plt.plot(self.x_brightness,self.y_brightness_threshold_v_max,"x", pen=(0,255,0))


        #TEST
        self.im = cv2.imread('images/test2.png')
        self.im_standard = cv2.imread('images/test2.png')

        self.current_point = [100,200]
        self.previous_angle = 0
        self.feat = None
        self.stone_feat = None
        self.path_finder = pfc.PathFinder()

        #Radius Slider Default Value
        self.slider1.setValue(self.path_finder.radius)
        #Speed Slider Default Value to max
        self.slider2.setValue(100)
        self.slider3.setValue(self.path_finder.detecting_angle)

        n_out_channel = pa_get_output_max_channels(self.output_device_index+1)
        self.audio_controller = actrl.AudioController(n_out_channel, self.theme , self.output_device_index)

        self.select_audio_output.setEnabled(False)
        self.select_theme.setEnabled(False)
        self.slider1.setEnabled(False)
        self.slider2.setEnabled(False)
        self.slider3.setEnabled(False)
        self.slider4.setEnabled(False)
        self.slider5.setEnabled(False)
        self.w.show()

    def setDefaultSoundDevice(self):
        self.output_device_index = self.select_audio_output.currentIndex()

        print self.devicelist[0][self.output_device_index]

    def setTheme(self):
        theme_index = self.select_theme.currentIndex()
        theme_selector = self.theme.type.keys()
        # print theme_selector[theme_index]
        self.theme.setCurrentTheme(str(theme_selector[theme_index]))


    def getBrightness(self):

        return self.brightness_v

    def updateplot(self):
        self.databuffer.append( self.getBrightness())
        self.databuffer_threshold_min.append(1.1)
        self.databuffer_threshold_max.append(1.4)
        self.y_brightness[:] = self.databuffer
        self.y_brightness_threshold_v_min[:] = self.databuffer_threshold_min
        self.y_brightness_threshold_v_max[:] = self.databuffer_threshold_max
        self.brightness_threshold_plot_min.setData(self.x_brightness, self.y_brightness_threshold_v_min)
        self.brightness_threshold_plot_max.setData(self.x_brightness, self.y_brightness_threshold_v_max)
        self.curve.setData(self.x_brightness, self.y_brightness)
        self.app.processEvents()


    def setFPS(self, fps):
        self.fps = fps

    def nextFrameSlot(self):
        try:
            previous_frame = self.current_frame
            #maximum Elements the smooth function look at
            max_smooth = 5
            max_smooth_brightness = 2
            mean_frame_diff_div = 0
            mean_brightness_div = 0
            max_brightness = 4

            ret, self.frame = self.cap.read()
            #img = cv2.imread(frame, cv2.IMREAD_COLOR)
            self.current_frame = self.frame
            self.snap_delay_time = time.time()
            #Brightness of the Image -> Influence the snap_thresh
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
                        # print 'Start Detection'
                        # print mean_diff
                        # print (self.snap_thres*self.brightness_v)


            #cv2.imshow('frame diff ',frame_diff)
            qformat= QImage.Format_Indexed8
            if len(self.frame.shape) == 3:
                if self.frame.shape[2] == 4:
                    qformat=QImage.Format_RGBA8888
                else:
                    qformat=QImage.Format_RGB888
            img = QtGui.QImage(self.frame, self.frame.shape[1], self.frame.shape[0], self.frame.strides[0], qformat)
            img = img.rgbSwapped()
            self.video_frame.setPixmap(QtGui.QPixmap.fromImage(img))

            self.video_frame.setScaledContents(True)
        except Exception, e:
            itemlist = QtGui.QListWidgetItem('Camera Activation failed')
            self.listw.addItem(itemlist)
            self.timer.stop()


    def start(self):
        self.setDefaultSoundDevice()
        try:
            self.button_load_cal.setEnabled(True)
            self.button_end.setEnabled(True)
            self.button_start_default.setEnabled(True)
            self.select_audio_output.setEnabled(True)
            self.select_theme.setEnabled(True)
            self.slider1.setEnabled(True)
            self.slider2.setEnabled(True)
            self.slider3.setEnabled(True)
            self.slider4.setEnabled(False)
            self.slider5.setEnabled(False)
            self.cap = cv2.VideoCapture(1)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,640)
            itemlist = QtGui.QListWidgetItem('Camera Activated')
            self.listw.addItem(itemlist)
            self.snapshot_time_gap = 4
            self.start_time = time.time()
            self.timer = QtCore.QTimer()
            #Prepare Frame Diffrences and flags
            self.snapshot_flag = False
            self.detect_delay_count = 0
            ret, self.current_frame = self.cap.read()
            self.timer.timeout.connect(self.updateplot)
            # self.timer.start(self._interval)
            self.timer.timeout.connect(self.nextFrameSlot)
            self.timer.start(1./self.fps)
        except Exception, e:
            itemlist = QtGui.QListWidgetItem('Camera Activation failed')
            self.listw.addItem(itemlist)


    def new_calibration(self):
        #self.edgeDetectionApproach()
        itemlist= QtGui.QListWidgetItem('Camera Stopped')
        self.img = self.frame.copy()
        cv2.namedWindow('image')
        cv2.imshow('image',self.img)
        #cv2.setMouseCallback('canny',img)
        cv2.setMouseCallback('image',self.draw_circle)
        self.listw.addItem(itemlist)
        self.cap.release()
        self.timer.stop()


    def load_calibration(self):
        self.button_start.setEnabled(False)
        self.button_load_cal.setEnabled(False)
        self.button_end.setEnabled(False)
        self.button_start_default.setEnabled(False)
        self.select_audio_output.setEnabled(False)
        self.select_theme.setEnabled(False)
        self.slider1.setEnabled(True)
        self.slider2.setEnabled(True)
        self.slider3.setEnabled(True)
        self.frame = cv2.flip(self.frame,0)
        self.frame = cv2.flip(self.frame,1)
        try:
            self.cap.release()
            self.timer.stop()
            self.cal_pts = np.load('caldata.npy')

            warped = callibration.four_point_transform(self.frame,self.cal_pts)
            print 'inside0'
            self.frame = warped
            print 'inside1'
            qformat= QImage.Format_Indexed8

            if len(self.frame.shape) == 3:
                if self.frame.shape[2] == 4:
                    qformat=QImage.Format_RGBA8888
                else:
                    qformat=QImage.Format_RGB888

            img = QtGui.QImage(self.frame, self.frame.shape[1], self.frame.shape[0], self.frame.strides[0], qformat)
            img=img.rgbSwapped()
            print 'inside2'
            self.video_frame.setPixmap(QtGui.QPixmap.fromImage(img))
            self.video_frame.setScaledContents(True)
            self.timer.stop()
            self.path_timer = QtCore.QTimer()
            self.feat,self.stone_feat,self.frame = ds.getFeatures(self.frame)
            self.path_timer.timeout.connect(self.follow_garden)
            self.path_timer.start(1./self.fps)
            itemlist= QtGui.QListWidgetItem('Calibration loaded')
            self.listw.addItem(itemlist)
            # cv2.imshow("features",self.frame)
            # cv2.waitKey(0)

        except Exception, e:
            self.path_timer = QtCore.QTimer()
            self.feat,self.stone_feat,self.im = ds.getFeatures(self.im)
            # cv2.imshow("coor",self.im)
            self.path_timer.timeout.connect(self.follow_garden)
            self.path_timer.start(1./self.fps)
            itemlist= QtGui.QListWidgetItem('Calibration loading failed')
            self.listw.addItem(itemlist)
        finally:
            n_out_channel = pa_get_output_max_channels(self.output_device_index+1)
            self.audio_controller = actrl.AudioController(n_out_channel, self.theme,self.output_device_index)

    def follow_garden(self):
        try:
            img_garden_copy = self.frame.copy()

        except:
            img_garden_copy = self.im.copy()
        finally:

            garden_update_img,self.current_point,self.previous_angle = self.path_finder.finder(img_garden_copy,self.current_point,self.previous_angle)

            self.audio_controller.interact(self.current_point,self.stone_feat)


        qformat= QImage.Format_Indexed8
        # img_garden_copy = np.asarray(img_garden_copy)
        if len(garden_update_img.shape) == 3:
            if garden_update_img.shape[2] == 4:
                qformat=QImage.Format_RGBA8888
            else:
                qformat=QImage.Format_RGB888

        img = QtGui.QImage(garden_update_img, garden_update_img.shape[1], garden_update_img.shape[0], garden_update_img.strides[0], qformat)
        img=img.rgbSwapped()
        self.video_frame.setPixmap(QtGui.QPixmap.fromImage(img))
        self.video_frame.setScaledContents(True)

    def start_default_image(self):
        self.button_load_cal.setEnabled(False)
        self.button_end.setEnabled(False)
        self.button_start_default.setEnabled(False)
        self.path_timer = QtCore.QTimer()
        self.feat,self.stone_feat,self.im = ds.getFeatures(self.im)
        # cv2.imshow("coor",self.im)
        self.path_timer.timeout.connect(self.follow_garden)
        self.path_timer.start(1./self.fps)
        itemlist= QtGui.QListWidgetItem('Calibration loading failed')
        self.listw.addItem(itemlist)
        # qformat= QImage.tents(True)

    def threshold_slider1(self):
        self.path_finder.radius  = self.slider1.value()
        txt1 = "Radius of Circle " + str(self.path_finder.radius)
        self.txtslider1.setText(txt1)
    def threshold_slider2(self):
        txt1 = "Speed " + str(float(self.slider2.value())/100.*float(self.fps))+" fps"
        self.txtslider2.setText(txt1)
        # setFPS(self.slider2.value())
        self.path_timer.stop()
        self.path_timer.start(1./(float(self.slider2.value())/100.*float(self.fps)))
        # self.path_timer.setInterval(self.slider2.value())
    def threshold_slider3(self):
        self.path_finder.detecting_angle = self.slider3.value()
        txt1 = "Detecting Angle " + str(self.path_finder.detecting_angle)
        self.txtslider3.setText(txt1)

    def threshold_slider4(self):
        txt1 = "-empy- (" + str(self.slider4.value())+"%)"
        self.txtslider4.setText(txt1)
    def threshold_slider5(self):
        txt1 = "-empy- (" + str(self.slider5.value())+"%)"
        self.txtslider5.setText(txt1)


    def draw_circle(self,event,x,y,flags,param):
        global mouseX,mouseY
        # cv2.imshow('image',self.img)
        # cv2.waitKey(0)
        if event == cv2.EVENT_LBUTTONUP:
            cv2.circle(self.img,(x,y),4,(255,255,255),2)
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


    def Cancel(self):
        print('closed')
        #self.close()
        #self.cap.release()
        #super(QtGui.QWidget, self).deleteLater()


    def closeEvent(self, event):
        print "Closing"
        self.deleteLater()

    def deleteLater(self):
        print('closed')
        self.cap.release()
        super(QtGui.QWidget, self).deleteLater()




def main():
    #calibration_pts = getCalibrationCoordinates(cameraChoice)

    sozen = QtCapture()
    sys.exit(sozen.app.exec_())

    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
