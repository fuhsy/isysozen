
from pyo import *
from threading import Timer
import panner as p
from math import sqrt
import copy
from time import sleep
from random import randint

s = Server(nchnls=2,ichnls=0, duplex=0)
# s.setOutputDevice(output_device_index+1) #wrong indices by pyo, so +1
s.boot()
s.start()
sound = SfPlayer("ambient.wav",loop= True,interp=3)
mixer = Mixer(outs=2)
mixer.addInput(0,sound)
mixer.out()
