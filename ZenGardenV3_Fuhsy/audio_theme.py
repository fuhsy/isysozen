import sounddevice as sd
import soundfile as sf

class AudioTheme():


    def __init__(self,str_theme):
        self.type = {
        		'normal' : {
                		0 : 'normal0.wav',
                		1 : 'normal1.wav',
                		2 : 'normal2.wav',
                		3 : 'normal3.wav',
                		4 : 'normal4.wav',
                		5 : 'normal5.wav'
                	},
        		'water' : {
                		0 : 'ambient.wav',
                		1 : 'water_test.wav',
                		2 : 'water_test.wav',
                		3 : 'water_test.wav',
                		4 : 'water_test.wav',
                		5 : 'water_test.wav'
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
        self.current_theme =  str_theme
        # print self.type[self.current_theme][0]
        # print self.current_theme

    def setCurrentTheme(self,str_theme):
        self.current_theme = str_theme

    def getSoundFile(self,index):
        return self.type[self.current_theme][index]
