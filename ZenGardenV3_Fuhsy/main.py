
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
import detect_sand as ds


import usb

class QtCapture(QtGui.QWidget):
    def __init__(self, *args):
        self.app = QtGui.QApplication(sys.argv)
        super(QtGui.QWidget, self).__init__()
        theme = audio_theme.AudioTheme('water')
        self.fps = 50
        #Lowest snapshot threshold for starting detection
        self.snap_thres = 2.6
        self.brightness_value_min = 1.2
        self.brightness_value_max = 1.45
        self.smooth_mean_dif = []
        self.brightness = 0
        self.brightness_plt = []
        self.sampleinterval = 0.1
        self.brightness_v = 0
        self.timewindow=10
        self.size = (600,350)
        self.layout = QtGui.QGridLayout()
        self.w = QtGui.QWidget()
        self.w.setMinimumHeight(480)
        self.capture = None
        self.frame = None
        self.pic = QtGui.QLabel()
        self.video_frame = QtGui.QLabel()
        self.select_audio_output = QtGui.QComboBox()
        self.audio_device_list = sd.query_devices()
        audio_index_count =0
        for key in self.audio_device_list:
            self.select_audio_output.addItem('%s (Output Channels=%s)' %(self.audio_device_list[audio_index_count]['name'],self.audio_device_list[audio_index_count]['max_output_channels']))
            audio_index_count = audio_index_count+1

        #self.pic.setPixmap(QtGui.QPixmap('sand_lines.png').scaled(600, 400, QtCore.Qt.KeepAspectRatio))
        self.button_start = QtGui.QPushButton('Camera Connect')
        self.button_detection = QtGui.QPushButton('Start Detection')
        self.button_load_cal = QtGui.QPushButton('Load Calibration')
        self.slider1 = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.slider2 = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.slider3 = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.slider4 = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.slider5 = QtGui.QSlider(QtCore.Qt.Horizontal)

        self.txtslider1 = QtGui.QLabel('Radius of Circle')
        self.txtslider2 = QtGui.QLabel('Speed')
        self.txtslider3 = QtGui.QLabel('Appeal')
        self.txtslider4 = QtGui.QLabel('-empty-')
        self.txtslider5 = QtGui.QLabel('-empty-')
        self.slider1.setFixedWidth(300)
        self.slider2.setFixedWidth(300)
        self.slider3.setFixedWidth(300)
        self.slider4.setFixedWidth(300)
        self.slider5.setFixedWidth(300)
        self.txtslider1.setFixedWidth(300)
        self.txtslider2.setFixedWidth(300)
        self.txtslider3.setFixedWidth(300)
        self.txtslider4.setFixedWidth(300)
        self.txtslider5.setFixedWidth(300)

        self.button_detection.setFixedWidth(300)
        self.select_audio_output.setFixedWidth(300)
        self.button_start.setFixedWidth(300)
        self.button_load_cal.setFixedWidth(300)
        self.button_end = QtGui.QPushButton('New Calibration')
        self.button_end.setFixedWidth(300)
        self.button_start.clicked.connect(lambda: self.start())
        self.select_audio_output.currentIndexChanged.connect(lambda: self.setDefaultSoundDevice())
        self.button_load_cal.clicked.connect(lambda: self.load_calibration())
        self.button_end.clicked.connect(lambda: self.new_calibration())
        self.button_detection.clicked.connect(lambda: self.start_detection(self.frame))
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
        self.layout.addWidget(self.button_end, 2, 0)
        self.layout.addWidget(self.button_load_cal, 3, 0)
        self.layout.addWidget(self.button_detection,4,0)
        self.layout.addWidget(self.txtslider1,5,0)
        self.layout.addWidget(self.slider1,6,0)
        self.layout.addWidget(self.txtslider2,7,0)
        self.layout.addWidget(self.slider2,8,0)
        self.layout.addWidget(self.txtslider3,9,0)
        self.layout.addWidget(self.slider3,10,0)
        self.layout.addWidget(self.txtslider4,11,0)
        self.layout.addWidget(self.slider4,12,0)
        self.layout.addWidget(self.txtslider5,13,0)
        self.layout.addWidget(self.slider5,14,0)
        self.layout.addWidget(self.listw, 16, 0)
        # self.layout.setAlignment(self.txtslider1, QtCore.Qt.AlignCenter)
        # self.layout.setAlignment(self.txtslider2, QtCore.Qt.AlignCenter)
        # self.layout.setAlignment(self.txtslider3, QtCore.Qt.AlignCenter)
        # self.layout.setAlignment(self.txtslider4, QtCore.Qt.AlignCenter)
        # self.layout.setAlignment(self.txtslider5, QtCore.Qt.AlignCenter)
        self.connect(self, QtCore.SIGNAL('triggered()'), self.closeEvent)
        self.layout.addWidget(self.pic, 0, 1, 16, 1)
        self.layout.addWidget(self.video_frame, 0, 1, 16, 1)
        self.button_load_cal.setEnabled(False)
        self.button_end.setEnabled(False)
        self.button_detection.setEnabled(False)
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
        self.layout.addWidget(self.plt,15,0)
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
        self.im = cv2.imread('test1.png')
        self.im_standard = cv2.imread('test1.png')

        self.current_point = [100,300]
        self.previous_angle = 0
        self.feat = None
        self.path_finder = pf.PathFinder()
        self.w.show()

    def setDefaultSoundDevice(self):
        device_index = self.select_audio_output.currentIndex()
        sd.default.device = self.audio_device_list[device_index]['name']
        print sd.default.device



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
        self.button_load_cal.setEnabled(True)
        self.button_end.setEnabled(True)
        try:
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
        self.img = self.frame

        cv2.namedWindow('image')
        cv2.imshow('image',self.img)
        #cv2.setMouseCallback('canny',img)
        cv2.setMouseCallback('image',self.draw_circle)
        self.listw.addItem(itemlist)
        self.cap.release()
        self.timer.stop()


    def load_calibration(self):
        self.button_load_cal.setEnabled(False)
        self.button_end.setEnabled(False)
        self.button_detection.setEnabled(True)
        try:
            itemlist= QtGui.QListWidgetItem('Calibration loaded')
            self.listw.addItem(itemlist)
            self.cap.release()
            self.timer.stop()
            self.cal_pts = np.load('caldata.npy')
            warped = callibration.four_point_transform(self.frame,self.cal_pts)
            self.frame = warped
            qformat= QImage.Format_Indexed8

            if len(self.frame.shape) == 3:
                if self.frame.shape[2] == 4:
                    qformat=QImage.Format_RGBA8888
                else:
                    qformat=QImage.Format_RGB888

            img = QtGui.QImage(self.frame, self.frame.shape[1], self.frame.shape[0], self.frame.strides[0], qformat)
            img=img.rgbSwapped()
            self.video_frame.setPixmap(QtGui.QPixmap.fromImage(img))
            self.video_frame.setScaledContents(True)
            self.timer.stop()
            self.path_timer = QtCore.QTimer()
            self.path_timer.timeout.connect(self.follow_garden)
            self.path_timer.start(10000./self.fps)
            self.feat,self.im = ds.getFeatures(self.im_standard)

        except Exception, e:
            self.path_timer = QtCore.QTimer()
            self.feat,self.im = ds.getFeatures(self.im)
            self.path_timer.timeout.connect(self.follow_garden)
            self.path_timer.start(10000./self.fps)
            itemlist= QtGui.QListWidgetItem('Calibration loading failed')
            self.listw.addItem(itemlist)

    def follow_garden(self):
        img_garden_copy = self.im.copy()
        self.current_point,self.previous_angle,garden_update_img = self.path_finder.finder(self.feat,self.current_point,img_garden_copy,self.previous_angle)
        cv2.imshow('result',garden_update_img)
        #Press ESC for exit
        if cv2.waitKey(100) == 27:
            cv2.destroyAllWindows()
            self.path_timer.stop()
            sys.exit()
        # self.frame = self.im
        # qformat= QImage.Format_Indexed8
        #
        # if len(self.frame.shape) == 3:
        #     if self.frame.shape[2] == 4:
        #         qformat=QImage.Format_RGBA8888
        #     else:
        #         qformat=QImage.Format_RGB888
        #
        # img = QtGui.QImage(self.frame, self.frame.shape[1], self.frame.shape[0], self.frame.strides[0], qformat)
        # img=img.rgbSwapped()
        # self.video_frame.setPixmap(QtGui.QPixmap.fromImage(img))
        # self.video_frame.setScaledContents(True)

    def threshold_slider1(self):
        txt1 = "Radius of Circle (" + str(self.slider1.value())+"%)"
        self.txtslider1.setText(txt1)
    def threshold_slider2(self):
        txt1 = "Speed (" + str(self.slider2.value())+"%)"
        self.txtslider2.setText(txt1)
    def threshold_slider3(self):
        txt1 = "Appeal (" + str(self.slider3.value())+"%)"
        self.txtslider3.setText(txt1)
    def threshold_slider4(self):
        txt1 = "-empy- (" + str(self.slider4.value())+"%)"
        self.txtslider4.setText(txt1)
    def threshold_slider5(self):
        txt1 = "-empy- (" + str(self.slider5.value())+"%)"
        self.txtslider5.setText(txt1)



    def start_detection(self, frame):
        self.button_load_cal.setEnabled(False)
        self.button_end.setEnabled(False)
        rawimage = frame
        height, width, shape = frame.shape
        # print width, height

        features = detect_sand.getFeatures(self.frame)


        rawim = cv2.cvtColor(rawimage, cv2.COLOR_RGB2GRAY)
        ret,thresh1 = cv2.threshold(rawim,40,255,cv2.THRESH_BINARY)
        kernel = np.ones((5,5),np.uint8)
        im = cv2.erode(thresh1,kernel,iterations = 3)
        im = cv2.dilate(im,kernel,iterations = 3)
        # Set up the detector with default parameters.
        _, contours, hierarchy = cv2.findContours(im, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contour_list = []
        for contour in contours:
            area = cv2.contourArea(contour)

            if area > 100 and area < 100000:
                M = cv2.moments(contour)
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                cv2.circle(rawimage, (cX, cY), 7, (0, 255, 0), -1)
                contour_list.append(contour)

                # print 'blob is in col %i, raw %i' % (math.ceil(float(cX)/float(width/3)),math.ceil((float(cY)/float(height/3))))
        # cv2.imshow('blobgrey', im)
        # cv2.imshow('blob',rawimage)
        # cv2.waitKey(0)
        lineThickness = 2
        cv2.line(rawimage, ((width/3), 0), ((width/3), (height)), (255,255,0), lineThickness)
        cv2.line(rawimage, ((width/3)*2, 0), ((width/3)*2, (height)), (255,255,0), lineThickness)
        cv2.line(rawimage, (0, (height/3)), (width, (height/3)), (255,255,0), lineThickness)
        cv2.line(rawimage, (0, (height/3)*2), (width, (height/3)*2), (255,255,0), lineThickness)
        cv2.drawContours(rawimage, contour_list,  -1, (0,255,0), 2)
        self.frame = rawimage

        try:
            itemlist= QtGui.QListWidgetItem('Stone Detection')
            self.listw.addItem(itemlist)
            qformat= QImage.Format_Indexed8

            if len(self.frame.shape) == 3:
                if self.frame.shape[2] == 4:
                    qformat=QImage.Format_RGBA8888
                else:
                    qformat=QImage.Format_RGB888

            img = QtGui.QImage(self.frame, self.frame.shape[1], self.frame.shape[0], self.frame.strides[0], qformat)
            img=img.rgbSwapped()
            self.video_frame.setPixmap(QtGui.QPixmap.fromImage(img))
            self.video_frame.setScaledContents(True)
        except Exception, e:
            itemlist= QtGui.QListWidgetItem('Stone Detection failed')
            self.listw.addItem(itemlist)


    def draw_circle(self,event,x,y,flags,param):
        global mouseX,mouseY
        cv2.imshow('image',self.img)
        if event == cv2.EVENT_LBUTTONUP:
            cv2.circle(self.img,(x,y),2,(255,255,255),-1)
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
