import sounddevice as sd
import soundfile as sf

class AudioTheme():

    theme = {
    		'normal' : {
            		0 : 'normal0.wav',
            		1 : 'normal1.wav',
            		2 : 'normal2.wav',
            		3 : 'normal3.wav',
            		4 : 'normal4.wav',
            		5 : 'normal5.wav'
            	},
    		'water' : {
            		0 : 'water0.wav',
            		1 : 'water1.wav',
            		2 : 'water2.wav',
            		3 : 'water3.wav',
            		4 : 'water4.wav',
            		5 : 'water5.wav'
            	},
    		'forest' : {
            		0 : 'forest0.wav',
            		1 : 'forest1.wav',
            		2 : 'forest2.wav',
            		3 : 'forest3.wav',
            		4 : 'forest4.wav',
            		5 : 'forest5.wav'
            	}
    	}

    def __init__(self,str_theme):
        current_theme = str_theme


    def setCurrentTheme(str_theme):
        current_theme = theme[str_theme]

    def getSoundFile(index):
        return theme[current_theme][index]
