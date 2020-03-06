class Camera():
    def __init__(self):
        """Camera Class

        Parameters
        ----------
        max_smooth, max_smooth_brightness, mean_frame_diff_div : int
        mean_brightness_div, max_brightness, fps : int
        frame : np.ndarray

        usage as name is explaining
        """
        self.max_smooth = 5
        self.max_smooth_brightness = 2
        self.mean_frame_diff_div = 0
        self.mean_brightness_div = 0
        self.max_brightness = 4
        self.frame = None
        self.fps = 1
    def setFPS(self,n):
        self.fps = n
        # self.snap_delay_time = time.time()
