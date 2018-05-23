import OSC

class AudioEngine():
    def __init__(self, *args):
        print "Init Audio Engine"
        self.addr = ('127.0.0.1',9003)
        self.client = OSC.OSCClient()
        self.client.connect(self.addr)

        # panning is required via QuadPanner
    def playOSC(self, path, panning, amp):
        bundle = OSC.OSCBundle()
        bundle.setAddress("playsound")
        bundle.append((path, panning[0], panning[1],
            panning[2], panning[3], amp))
        self.client.send(bundle)


audio = AudioEngine()
audio.playOSC(0, [0.2, 0.3, 0.4, 0.5], 1.)
