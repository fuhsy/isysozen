import sounddevice as sd
import soundfile as sf

class AudioTheme():


    def __init__(self,str_theme):
        self.type = {
        		'Sea' : {
                		0 : 'seaA1.wav',
                		1 : 'wave1.wav',
                		2 : 'wave2.wav',
                		3 : 'seagull1.wav',
                		4 : 'seagull2.wav',
                		5 : 'wave1.wav'
                	},
        		'Forest' : {
                		0 : 'forest2.wav',
                		1 : 'bird1.wav',
                		2 : 'bird2.wav',
                		3 : 'bird6.wav',
                		4 : 'bird7.wav',
                		5 : 'frog1.wav',
                	}
        	}
        self.current_theme =  str_theme
        # print self.type[self.current_theme][0]
        # print self.current_theme

    def setCurrentTheme(self,str_theme):
        self.current_theme = str_theme

    def getSoundFile(self,index):
        return self.type[self.current_theme][index]
