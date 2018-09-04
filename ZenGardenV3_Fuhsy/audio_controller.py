
from pyo import *
from threading import Timer
import panner as p
from math import sqrt
import copy
from time import sleep
from random import randint

class AudioController():
    def __init__(self,n_out_channel, theme, output_device_index=0,width=640, height=420):
        print"init Audio Controller"
        print"Server started with",n_out_channel,"Ouput Channels"
        self.SNDS_PATH = 'soundfiles/'
        self.s = Server(nchnls=n_out_channel,ichnls=0, duplex=0)
        self.inStone = False
        self.s.setOutputDevice(output_device_index+1) #wrong indices by pyo, so +1

        self.s.boot()
        print 'Number of Output Channels',self.s.getNchnls()
        # self.s.verbosity = 15
        self.s.start()
        self.theme = theme
        self.n_out_channel = n_out_channel
        self.mixer = []
        self.n_sound = 2
        self.offset_hit_stone = 5 #in Seconds
        self.radius_thresh = 5
        self.panning_main = [0.5,0.5,0.5,0.5]
        for i in range(0,self.n_sound):
            self.mixer.append(Mixer(outs=n_out_channel))
        self.init_sfplayers()
        # add a mixer for each soundfile in a thome e.g. ("forest")
        self.mixer[0].addInput(0,self.s_background_theme)
        # self.mixer[1].addInput(0,self.hit_stone[randint(0,2)])
        self.mixer[1].addInput(0,self.hit_stone)
        p = pa_get_output_devices()
        self.panning = None
        # Just Test Image
        # real image should have 600x400
        self.img_width = float(width)
        self.img_height = float(height)
        self.stone_feat = None

        self.n_out_channel = 4
    def setAmplitude(self,mixkey,panning):
        for i in range(0,self.n_out_channel):
            self.mixer[mixkey].setAmp(0,i,panning[i])
    def stop_all(self):
        for i in range(0,len(self.mixer)):
            for j in range(0,self.n_out_channel):
                self.mixer[i].setAmp(0,j,0)
            # self.setAmplitude(i,0

    def restart_all(self):
        for j in range(0,self.n_out_channel):
            self.mixer[0].setAmp(0,j,self.panning_main[j])
    #         self.mixer[i].play()
    #         self.mixer[i].out()
    #cur_position is norm starting top left (0,1)
    # sound_active_key which sound should be played
    def playAmbient(self):
        self.mixer[0].out()
        for j in range(0,self.n_out_channel):
            self.mixer[0].setAmp(0,j,self.panning_main[j])
        # self.mixer[0].setAmp(0,3,self.panning[1])

    def interact(self,cur_position):
        float_x = float(cur_position[0])
        float_y = float(cur_position[1])
        pos_x = float(float_x/self.img_width)
        pos_y = float(float_y/self.img_height)

        #can be replaced by "quad_square" , "quad_circle" or "stereo"

        #Main Ambient Music for index 0
        # self.setAmplitude(0,self.panning)
        # print self.mixer[1].isOutputting(all=False)
        # print stone_feat
        for i in range(0,len(self.stone_feat)):
            if (self.distance(cur_position,self.stone_feat[i].center) < self.stone_feat[i].radius+self.radius_thresh and self.inStone == False):
                self.inStone = True
                self.panning = p.panner("quad_square",pos_x,pos_y)
                # self.hit_stone = SfPlayer(self.SNDS_PATH+self.theme.getSoundFile(1),interp=3)
                self.mixer[1].delInput(0)
                self.hit_stone = SfPlayer(self.SNDS_PATH+self.theme.getSoundFile(randint(1,5)),interp=3)
                # print 'cur_posx',float_x,' cur_posy: ', float_y
                # print self.panning,' posx:',pos_x ,' posy: ',pos_y
                self.mixer[1].addInput(0,self.hit_stone)
                self.mixer[1].out()
                # print self.panning
                self.setAmplitude(1,self.panning)
                # self.setAmplitude(0,self.panning)
                # print 'Black Stone Detected'
                t = Timer(self.offset_hit_stone, self.hit_delay)
                t.start()
                break

    def init_sfplayers(self):
        self.s_background_theme = SfPlayer(self.SNDS_PATH+self.theme.getSoundFile(0),loop= True)
        self.hit_stone = SfPlayer(self.SNDS_PATH+self.theme.getSoundFile(randint(1,5)),interp=3)


    def hit_delay(self):
        self.inStone = False;
        # print "delay passed"
    def init_stone_feat(self,stone_feat):
        self.stone_feat = stone_feat
    def shutdown(self):
        self.s.stop()
        self.s.shutdown()

    def distance(self,p1,p2):
        distance = sqrt( ((p1[0]-p2[0])**2)+((p1[1]-p2[1])**2) )
        return distance
