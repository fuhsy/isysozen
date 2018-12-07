from pyo import *
from time import sleep
s = Server().boot()
s.start()
SNDS_PATH = 'soundfiles/'
a = SfPlayer(SNDS_PATH+"/stone_hit.wav", loop=False, mul=.2)
b = SfPlayer(SNDS_PATH+"/stone_hit.wav", loop=False, mul=.2)
mm = Mixer(outs=2, chnls=1, time=.025).out()

for i in range (4):
	print i
	a = SfPlayer(SNDS_PATH+"/stone_hit.wav", loop=False, mul=.2)
	b = SfPlayer(SNDS_PATH+"/stone_hit.wav", loop=False, mul=.2)
	temp = i % 2
	if (temp== 0):
		print "even"
		mm.addInput(temp, a)
	else:
		print "odd"

		mm.addInput(temp, b)
	mm.setAmp(temp,0,.9)
	mm.setAmp(temp,1,.9)

	sleep(2.5)
	mm.delInput(temp)
