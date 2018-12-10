# isysozen

Interactive Zen Garden:

The Zen Garden System interprets image features and generates a soundscape. There are three basic themes which are implemented for an individual Soundscape: Campfire (Red Object), Forest (Green Object), Sea (Blue Object).

1. At first you have to select the audio ouput device
2. You can start the Camera . The Camera is set by default to USB-Port 1 (right port on Macbook)
2.1 Either you can start a default setup. You can change the default image by replacing  the file: (/images/default/export.jpg)
3. After starting the camera you can start to carve the sand and place objects. At least you have to place one object to start. If you are stopping to interact with the system, it will automatically start to play your individual soundscape.
3.1 If you change some objects the system will automatically change the soundscape.
3.2 If you want to Pause the system you can click the pause/play button in the GUI Interface or you can hide the camera with your hand. If you want to continue playing music, you can hide it again.

Soundscape:

A random placed virtual object will follow the detected sand lines in the scene and play sound depending on the position of the virtual object. The Amplitude of a basic theme soundscape, e.g. sea-soundscape will increase, if the virtual object gets closer to it.
If the virtual object will cross an theme object, the audio engine will play an specific sound for that theme.

You can also set up different params for detecting sand lines. You can change:
    1. Radius of virtual object
    2. Detecting Angle 
    3. Speed 
    4. 

Reset:

If you have started playing a soundscape and change the input method, you can press restart and the audio will stop and you can choose your interaction method.
