
from pyo import *
from time import sleep
from random import randint
import glob
import random
import cv2
import view as v

def main():
    view = v.View()

    s = Server(nchnls=4,ichnls=0, duplex=0)
    s.setOutputDevice(2)
    s.boot()
    s.start()
    mixer = Mixer(outs=4)

    soundfile = SfPlayer('soundfiles/callibration/sine440G1.wav', loop=True)
    mixer.addInput(0, soundfile)
    # setAmp(mixkey, output_channel, volume)
    mixer.setAmp(0,0,1)
    mixer.out()
    print 'success'
    view.app.exec_()

if __name__ == '__main__':
    main()
