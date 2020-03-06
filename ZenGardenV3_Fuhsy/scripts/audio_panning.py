import numpy as np
import scipy.io.wavfile as wavfile

print scipy.io.wavfile.__version__
def ampradio_to_angle(x):
    # converts ratio of amplitude of left and right channel to degree in radians """
    if x == 1:
        return 0
    else:
        return 2 * np.arctan((-1 * np.sqrt(2) * np.sqrt(x*x + 1) + x + 1) / (x - 1))
#Just for 180 Deggree (two Channels)
def rad_to_unit(x):
    # scales -45° to 45° in radiants between -1 and 1 """
    return np.degrees(x)/45

sr, left_channel, = wavfile.read("leftfile.wav")
sr, right_channel = wavfile.read("rightfile.wav")
idx = right_channel != 0
if len(right_channel[idx]) == 0:
    ratio = 1e9 # some big number
else:
    ratio = np.average(left_channel[idx] / right_channel[idx])

print(rad_to_unit(ampradio_to_angle(ratio)))
