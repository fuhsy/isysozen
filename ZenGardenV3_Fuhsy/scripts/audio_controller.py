
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
    def __init__(self,n_out_channel, output_device_index=0,width=640, height=480):
        """Pathfinder class

        Attributes
        ----------
        func setAmplitude_background
        func setAmplitude
        func stop_all
        func reflect
        func restart_all
        func playAmbient
        func interact
        func fadeout
        func fade_out_background
        func shutdown
        func distance
        Parameters
        ----------
        n_out_channel : int
            Number of ouputchannels
        SNDS_PATH : starting
            Path of sound files
        s : Server from pyo
        inStone : bool
            is sonic anchor placed in sonic item currently?
        soundfiles_forest : glob np.ndarray
            all trigger forest soundfiles
        soundfiles_sea : glob np.ndarray
            all trigger sea soundfiles
        self.soundfiles_fire : glob np.ndarray
            all trigger fire soundfiles
        sf_background_forest : glob np.ndarray
            all background forest soundfiles
        sf_background_sea : glob np.ndarray
            all background sea soundfiles
        sf_background_fire : glob np.ndarray
         all background fire soundfiles
        mixer : array
            mixer param for server pyo trigger sounds
        background_mixer = []
            mixer param for server pyo background sounds
        n_sound : int
            Number of sounds background
        offset_hit_stone : int
            Offset of playing sound after hitting sonic item
        radius_thresh : int
            Thresh for Radius sonic item
        panning_main : np.ndarray, len 4
            Init with half power 0.5 for each channel
        panning : np.ndarray, len 4
            Init with half power 0.5 for each channel
        hit_stone : SfPlayer()
            Soundfile for hit stone
        p : pa_get_output_devices()
            finds all output devices in list
        img_width : float(width)
        img_height : float(height)
        stone_feat : np.ndarray
            [Point, radius, theme]
        n_out_channel : int
            Number of ouput channel audio
        stone_feature : np.ndarray
            [Point, radius, theme]
        one_fire : bool
            at least one fire item
        one_forest : bool
            at least one forest item
        one_sea : bool
            at least one sea item
        """
        print "init Audio Controller"
        print "Server started with",n_out_channel,"Ouput Channels"
        self.n_out_channel = n_out_channel
        self.SNDS_PATH = 'soundfiles/'
        self.s = Server(nchnls=n_out_channel,ichnls=0, duplex=0)
        self.inStone = False
        self.s.setOutputDevice(output_device_index+1) #wrong indices by pyo, so +1
        self.soundfiles_forest = glob.glob("../soundfiles/forest/*.wav")
        self.soundfiles_sea = glob.glob("../soundfiles/sea/*.wav")
        self.soundfiles_fire = glob.glob("../soundfiles/fire/*.wav")
        self.sf_background_forest = glob.glob("../soundfiles/forest/background/Leaf2.wav")
        self.sf_background_sea = glob.glob("../soundfiles/sea/background/Water2.wav")
        self.sf_background_fire = glob.glob("../soundfiles/fire/background/Fire2.wav")
        self.s.boot()
        print 'Number of Output Channels',self.s.getNchnls()
        # self.s.verbosity = 15
        self.s.start()
        # self.theme = None
        self.n_out_channel = n_out_channel
        self.mixer = []
        self.background_mixer = []
        self.n_sound = 5
        self.offset_hit_stone = 2 #in Seconds
        self.radius_thresh = 5
        self.panning_main = [0.5,0.5,0.5,0.5]
        self.panning = [0.5,0.5,0.5,0.5]
        # for i in range(0,self.n_sound):
        # self.mixer.append(Mixer(outs=n_out_channel,time=1))
        # for i in range(0,self.n_sound):
        #     self.background_mixer.append(Mixer(outs=n_out_channel, time=1))
        # self.init_sfplayers()
        # add a mixer for each soundfile in a thome e.g. ("forest")
        # self.mixer[1].addInput(0,self.hit_stone[randint(0,2)])
        # self.hit_stone = SfPlayer(random.choice(self.soundfiles_forest))
        # self.mixer[0].addInput(0,self.hit_stone)
        p = pa_get_output_devices()

        # Just Test Image
        # real image should have 600x400
        self.img_width = float(width)
        self.img_height = float(height)
        self.stone_feat = None
        self.n_out_channel = 4
        self.stone_feature = None
        self.one_fire = True
        self.one_forest = True
        self.one_sea = True
        self.maxVol = 80

    def __del__(self):
        """__del__ func
            Shut down audio Server
        """
        self.shutdown()
        self.s.__del__()

    #TODO
    def setAmplitude_background(self,mixkey,panning,pos,s_center):
        """finder func

        Arguments
        ----------
        mixkey : int
            key for specific mixer
        panning : np.ndarray
            current panning depending on sonic anchor position

        Parameters
        ----------
        dir_mult : int
            Multiplicator for panning

        """
        dir_mult = 200/self.distance(pos,s_center)
        for i in range(0,self.n_out_channel):
            if dir_mult > 1: dir_mult=1
            self.background_mixer[mixkey].setAmp(0,i,panning[i]*dir_mult*self.maxVol)
            # print str(dir_mult)+' '+str(s_center)
    def setAmplitude(self,mixkey,panning):
        """setAmplitude func
            same as function setAmplitude_background, but also for
            trigger sounds
        """
        for i in range(0,self.n_out_channel):
            # with fading in panning
            self.mixer[mixkey].setAmp(0,i,panning[i]*self.maxVol)

    def stop_all(self):
        """stop_all func
            Stops playing all sounds
        """
        for i in range(0,len(self.background_mixer)):
            for j in range(0,self.n_out_channel):
                self.background_mixer[i].setAmp(0,j,0)
            # self.setAmplitude(i,0
    #TODO
    def restart_all(self):
        """restart_all func
            Restart playing all sounds
        """
        for i in range(0,len(self.stone_feat)):
            for j in range(0,self.n_out_channel):
                self.background_mixer[i].setAmp(0,j,self.panning_main[j]*self.maxVol)
    #         self.mixer[i].play()
    #         self.mixer[i].out()
    #cur_position is norm starting top left (0,1)
    # sound_active_key which sound should be played
    #TODO
    def playAmbient(self):
        """playAmbient func
            starts playing all background sounds
        """
        for i in range(0,len(self.background_mixer)):
            self.background_mixer[i].out()
            for j in range(0,self.n_out_channel):
                self.background_mixer[i].setAmp(0,j,self.panning_main[j]*self.maxVol)
        # self.mixer[0].setAmp(0,3,self.panning[1])

    def interact(self,cur_position):
        """interact func

        Arguments
        ----------
        cur_position : Class Point(x,y)
            Current Position of sonic anchor

        Returns
        ----------
        inStone : bool
            is sonic anchor placec in sound item
        stone_feature : np.ndarray
            [Point, radius, theme]

        """
        float_x = float(cur_position[0])
        float_y = float(cur_position[1])
        pos_x = float(float_x/self.img_width)
        pos_y = float(float_y/self.img_height)
        n = 4
        self.panning = p.panner("quad_square",pos_x,pos_y)
        #can be replaced by "quad_square" , "quad_circle" or "stereo"

        #Main Ambient Music for index 0
        for i in range(0,len(self.stone_feat)):
            self.setAmplitude_background(i,self.panning,cur_position,self.stone_feat[i].center)
        for i in range(0,len(self.stone_feat)):
            if (self.distance(cur_position,self.stone_feat[i].center) < self.stone_feat[i].radius+self.radius_thresh and self.inStone == False):
                self.inStone = True
                self.stone_feature = self.stone_feat[i]
                self.panning = p.panner("quad_square",pos_x,pos_y)
                self.mixer[0].delInput(0)
                if self.stone_feat[i].theme == 'GREEN':
                    self.hit_stone = SfPlayer(random.choice(self.soundfiles_forest))
                elif self.stone_feat[i].theme == 'BLUE':
                    self.hit_stone = SfPlayer(random.choice(self.soundfiles_sea))
                elif self.stone_feat[i].theme == 'RED':
                    self.hit_stone = SfPlayer(random.choice(self.soundfiles_fire))
                else:
                    self.hit_stone = SfPlayer(random.choice(self.soundfiles_forest))
                # print 'cur_posx',float_x,' cur_posy: ', float_y
                # print self.panning,' posx:',pos_x ,' posy: ',pos_y
                self.mixer[0].addInput(0,self.hit_stone)
                self.mixer[0].out()
                # print self.panning

                self.setAmplitude(0,self.panning)
                t = Timer(self.offset_hit_stone, self.hit_delay)
                t.start()
                break
        return self.inStone, self.stone_feature

    def fadeout(self):
        """fadeout func
            Fadeout sound
        """
        for i in range (100):
            self.panning = self.panning - 0.01
            self.mixer[1].setAmplitude(1,self.panning)


    # def init_sfplayers(self):


    def set_sf_theme(color):
        """set_sf_theme func
            Theme of background sound setter
        """
        if color == 'RED':
            return self.soundfiles_fire
        elif color == 'GREEN':
            return self.soundfiles_forest
        elif color == 'BLUE':
            return self.soundfiles_sea
        else:
            return self.soundfiles_forest

    def hit_delay(self):
        """hit_delay func
            activate delay by hitting sound item
        """
        self.inStone = False;

        # print "delay passed"
    def init_stone_feat(self,stone_feat):
        """finder func

        Arguments
        ----------
        stone_feat : np.ndarray
            [Point, radius, theme]

        Pyo Server starts first.
        Then init all mixer with Stone Features.
        """
        # self.s.start()
        self.stone_feat = stone_feat
        self.stone_feature = self.stone_feat[0]
        self.background_mixer = []
        # self.theme = self.stone_feat.theme
        self.mixer.append(Mixer(outs=self.n_out_channel, time=2))
        for i in range(0,len(self.stone_feat)):
            self.background_mixer.append(Mixer(outs=self.n_out_channel))
        self.hit_stone = SfPlayer(random.choice(self.soundfiles_forest))
        self.mixer[0].addInput(0,self.hit_stone)

        for i in range(0,len(stone_feat)):
            if self.stone_feat[i].theme == 'RED' and self.one_fire:
                self.s_background_theme = SfPlayer(self.sf_background_fire,loop= True)
                self.hit_stone = SfPlayer(random.choice(self.soundfiles_fire),interp=3)
                self.one_fire = False
            elif self.stone_feat[i].theme == 'GREEN' and self.one_forest:
                self.s_background_theme = SfPlayer(random.choice(self.sf_background_forest),loop= True)
                self.hit_stone = SfPlayer(random.choice(self.soundfiles_forest),interp=3)
                self.one_forest = False
            elif self.stone_feat[i].theme == 'BLUE' and self.one_sea:
                self.s_background_theme = SfPlayer(random.choice(self.sf_background_sea),loop= True)
                self.hit_stone = SfPlayer(random.choice(self.soundfiles_forest),interp=3)
                self.one_sea = False
            else:
                self.s_background_theme = SfPlayer(random.choice(self.sf_background_sea),loop= True)
                self.hit_stone = SfPlayer(random.choice(self.soundfiles_forest),interp=3)
            self.background_mixer[i].addInput(0,self.s_background_theme)
        self.one_fire = True
        self.one_forest = True
        self.one_sea = True
    def fade_out_background(self):
        for mixer in self.background_mixer:
            for i in range(0,self.n_out_channel):
                for item in self.panning: item -= 0.05
                mixer.setAmp(0,i,self.panning[i])
                time.sleep(.01)
    def shutdown(self):
        self.s.stop()
        self.s.shutdown()

    def distance(self,p1,p2):
        distance = sqrt( ((p1[0]-p2[0])**2)+((p1[1]-p2[1])**2) )
        return distance
