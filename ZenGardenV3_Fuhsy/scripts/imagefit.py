
from pyo import *
from time import sleep
from random import randint
import glob
import random
import cv2
import view as v
import pyscreenshot as ImageGrab
import sys
def main():
    # view = v.View()

    html_im = ImageGrab.grab(bbox=(1840,140,2840,840))
    html_im.show()

    # view.app.exec_()

if __name__ == '__main__':
    main()
