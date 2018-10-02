
from pyo import *
from threading import Timer
import panner as p
from math import sqrt
import copy
from time import sleep
from random import randint
import glob
import random
import path_finder_contrast as path_finder

class AudioController():
    def __init__(self,n_out_channel, output_device_index=0,width=640, height=420):
        print"init Audio Controller"
        print"Server started with",n_out_channel,"Ouput Channels"
        self.n_out_channel = n_out_channel
        self.SNDS_PATH = 'soundfiles/'
        self.s = Server(nchnls=n_out_channel,ichnls=0, duplex=0)
        self.inStone = False
        self.s.setOutputDevice(output_device_index+1) #wrong indices by pyo, so +1
        self.soundfiles_forest = glob.glob("soundfiles/forest/*.wav")
        self.soundfiles_sea = glob.glob("soundfiles/sea/*.wav")
        self.soundfiles_fire = glob.glob("soundfiles/fire/*.wav")
        self.sf_background_forest = glob.glob("soundfiles/forest/forest2.wav")
        self.sf_background_sea = glob.glob("soundfiles/sea/seaA1.wav")
        self.s.boot()
        print 'Number of Output Channels',self.s.getNchnls()
        # self.s.verbosity = 15
        self.s.start()
        # self.theme = None
        self.n_out_channel = n_out_channel
        self.mixer = []
        self.background_mixer = []
        self.n_sound = 5
        self.offset_hit_stone = 5 #in Seconds
        self.radius_thresh = 5
        self.panning_main = [0.5,0.5,0.5,0.5]
        # for i in range(0,self.n_sound):
        self.mixer.append(Mixer(outs=n_out_channel))
        for i in range(0,self.n_sound):
            self.background_mixer.append(Mixer(outs=n_out_channel))
        # self.init_sfplayers()
        # add a mixer for each soundfile in a thome e.g. ("forest")

        # self.mixer[1].addInput(0,self.hit_stone[randint(0,2)])
        self.hit_stone = SfPlayer(random.choice(self.soundfiles_forest))
        self.mixer[0].addInput(0,self.hit_stone)
        p = pa_get_output_devices()
        self.panning = None
        # Just Test Image
        # real image should have 600x400
        self.img_width = float(width)
        self.img_height = float(height)
        self.stone_feat = None

        self.n_out_channel = 4
        self.stone_feature = None

    def __del__(self):
        self.shutdown()
    # def __del__(self):
    #     self.s.close()
    #TODO
    def setAmplitude_background(self,mixkey,panning):
        for i in range(0,self.n_out_channel):
            self.background_mixer[mixkey].setAmp(0,i,panning[i])
    def setAmplitude(self,mixkey,panning):
        for i in range(0,self.n_out_channel):
            self.mixer[mixkey].setAmp(0,i,panning[i])
    #TODO
    def stop_all(self):
        for i in range(0,len(self.background_mixer)):
            for j in range(0,self.n_out_channel):
                self.background_mixer[i].setAmp(0,j,0)
            # self.setAmplitude(i,0
    #TODO
    def restart_all(self):
        for i in range(0,len(self.stone_feat)):
            for j in range(0,self.n_out_channel):
                self.background_mixer[i].setAmp(0,j,self.panning_main[j])
    #         self.mixer[i].play()
    #         self.mixer[i].out()
    #cur_position is norm starting top left (0,1)
    # sound_active_key which sound should be played
    #TODO
    def playAmbient(self):
        for i in range(0,len(self.background_mixer)):
            self.background_mixer[i].out()
            for j in range(0,self.n_out_channel):
                self.background_mixer[i].setAmp(0,j,self.panning_main[j])
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
                self.stone_feature = self.stone_feat[i]
                self.panning = p.panner("quad_square",pos_x,pos_y)
                # self.hit_stone = SfPlayer(self.SNDS_PATH+self.stone_feat[i].getSoundFile(1),interp=3)
                self.mixer[0].delInput(0)
                if self.stone_feat[i].theme == 'GREEN':
                    self.hit_stone = SfPlayer(random.choice(self.soundfiles_forest))
                elif self.stone_feat[i].theme == 'BLUE':
                    self.hit_stone = SfPlayer(random.choice(self.soundfiles_sea))
                elif self.stone_feat[i].theme == 'RED':
                    self.hit_stone = SfPlayer(random.choice(self.soundfiles_forest))
                else:
                    self.hit_stone = SfPlayer(random.choice(self.soundfiles_forest))
                # print 'cur_posx',float_x,' cur_posy: ', float_y
                # print self.panning,' posx:',pos_x ,' posy: ',pos_y
                self.mixer[0].addInput(0,self.hit_stone)
                self.mixer[0].out()
                # print self.panning
                for i in range(0,len(self.stone_feat)):
                    self.setAmplitude_background(i,self.panning)
                self.setAmplitude(0,self.panning)
                # print 'Black Stone Detected'
                t = Timer(self.offset_hit_stone, self.hit_delay)
                t.start()
                break
        return self.inStone, self.stone_feature

    def fadeout(self):
        for i in range (100):
            self.panning = self.panning - 0.01
            self.mixer[1].setAmplitude(1,self.panning)


    # def init_sfplayers(self):


    def set_sf_theme(color):
        if color == 'RED':
            return self.soundfiles_forest
        elif color == 'GREEN':
            return self.soundfiles_forest
        elif color == 'BLUE':
            return self.soundfiles_sea
        else:
            return self.soundfiles_forest
    def hit_delay(self):
        self.inStone = False;
        # print "delay passed"
    def init_stone_feat(self,stone_feat):
        self.stone_feat = stone_feat
        self.stone_feature = self.stone_feat[0]
        # self.theme = self.stone_feat.theme
        self.mixer.append(Mixer(outs=self.n_out_channel))
        for i in range(0,len(self.stone_feat)):
            self.background_mixer.append(Mixer(outs=self.n_out_channel))
        self.hit_stone = SfPlayer(random.choice(self.soundfiles_forest))
        self.mixer[0].addInput(0,self.hit_stone)

        for i in range(0,len(stone_feat)):
            if self.stone_feat[i].theme == 'RED':
                self.s_background_theme = SfPlayer(self.sf_background_forest,loop= True)
                self.hit_stone = SfPlayer(random.choice(self.soundfiles_forest),interp=3)
            elif self.stone_feat[i].theme == 'GREEN':
                self.s_background_theme = SfPlayer(random.choice(self.sf_background_forest),loop= True)
                self.hit_stone = SfPlayer(random.choice(self.soundfiles_forest),interp=3)
            elif self.stone_feat[i].theme == 'BLUE':
                self.s_background_theme = SfPlayer(random.choice(self.sf_background_sea),loop= True)
                self.hit_stone = SfPlayer(random.choice(self.soundfiles_forest),interp=3)
            else:
                self.s_background_theme = SfPlayer(random.choice(self.sf_background_sea),loop= True)
                self.hit_stone = SfPlayer(random.choice(self.soundfiles_forest),interp=3)
            self.background_mixer[i].addInput(0,self.s_background_theme)

    def shutdown(self):
        self.s.stop()
        self.s.shutdown()

    def distance(self,p1,p2):
        distance = sqrt( ((p1[0]-p2[0])**2)+((p1[1]-p2[1])**2) )
        return distance
