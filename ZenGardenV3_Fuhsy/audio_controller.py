
from pyo import *
from threading import Timer
import panner as p
from math import sqrt
import copy

class AudioController():
    def __init__(self,n_out_channel, theme, output_device_index=0):
        print"init Audio Controller"
        print"Server started with",n_out_channel,"Ouput Channels"
        self.SNDS_PATH = 'soundfiles/'
        self.s = Server(nchnls=n_out_channel,ichnls=0, duplex=0)
        self.inStone = False
        self.s.setOutputDevice(output_device_index+1) #wrong indices by pyo, so +1

        self.s.boot()
        print self.s.getNchnls()
        # self.s.verbosity = 15
        self.s.start()
        self.theme = theme
        self.n_out_channel = n_out_channel
        self.mixer = []
        self.n_sound = 4
        self.offset_hit_stone = 5 #in Seconds
        for i in range(0,self.n_sound):
            self.mixer.append(Mixer(outs=n_out_channel))

        # self.name = self.theme.getSoundFile(0)
        self.init_sfplayers()

        # add a mixer for each soundfile in a thome e.g. ("forest")
        self.mixer[0].addInput(0,self.s_background_theme)
        self.mixer[1].addInput(0,self.s_enter_stone)
        self.mixer[2].addInput(0,self.s_leave_stone)
        self.mixer[3].addInput(0,self.hit_edge)

        self.mixer[0].out()
        p = pa_get_output_devices()

        # Just Test Image
        # real image should have 600x400
        self.img_width = float(1270)
        self.img_height = float(972)


    def setAmp(self,mixkey,panning):
        for i in range(self.n_out_channel):
            self.mixer[mixkey].setAmp(0,i,panning[i])

    #cur_position is norm starting top left (0,1)
    # sound_active_key which sound should be played
    def interact(self,cur_position,stone_feat):
        float_x = float(cur_position[0])
        float_y = float(cur_position[1])
        pos_x = float(float_x/self.img_width)
        pos_y = float(float_y/self.img_height)

        #can be replaced by "quad_square" , "quad_circle" or "stereo"
        panning = p.panner("stereo",pos_x,pos_y)
        #Main Ambient Music for index 0
        self.setAmp(0,panning)
        # print self.mixer[1].isOutputting(all=False)
        for stone in stone_feat:
            if (self.distance(cur_position,stone.center) < stone.radius+5 and self.inStone == False):
                self.inStone = True
                self.s_enter_stone = SfPlayer(self.SNDS_PATH+self.theme.getSoundFile(1))
                self.mixer[1].delInput(0)
                self.mixer[1].addInput(0,self.s_enter_stone)
                self.mixer[1].out()
                self.setAmp(1,panning)
                print 'Hit Stone %f',self.mixer[1].time
                t = Timer(self.offset_hit_stone, self.hit_delay)
                t.start()
                break

    def init_sfplayers(self):
        self.s_background_theme = SfPlayer(self.SNDS_PATH+self.theme.getSoundFile(0),loop= True)
        self.s_enter_stone = SfPlayer(self.SNDS_PATH+self.theme.getSoundFile(1))
        self.s_leave_stone = SfPlayer(self.SNDS_PATH+self.theme.getSoundFile(2))
        self.hit_edge = SfPlayer(self.SNDS_PATH+self.theme.getSoundFile(3))
    def hit_delay(self):
        self.inStone = False;
        print "delay passed"


    def distance(self,p1,p2):
        distance = sqrt( ((p1[0]-p2[0])**2)+((p1[1]-p2[1])**2) )
        return distance
