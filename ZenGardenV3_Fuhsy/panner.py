# Quad panner
# Depends on where (0, 0 is)

import numpy as np
from math import pi as pi

def cart2pol(x, y):
    rho = np.sqrt(x**2 + y**2)
    phi = np.arctan2(y, x)
    return(rho, phi)


# The x, y position should be normalised.
def panner(method, x, y):
	if method == "quad_square":
		c1 = (1- x) * (1-y) # (0, 0)
		c2 = x * (1- y)		#  ( 1, 0)
		c3 = (1 -x) * y          # (1, 1)
		c4 = x * y     # (0, 1)
		return [c1,c2,c3,c4]   #
	elif method == "quad_circle":
		# But this method doesn't deal with the amplitude right.
		rho, phi = cart2pol(x - 0.5,y - 0.5)
		phi_norm = phi/pi /2
		c = np.zeros(4)
		offset = [0.625, 0.375, 0.875, 0.125] # FL, FR, BL, BR
		# print phi_norm
		for i in range(4):
			c[i] = np.sin((offset[i] + phi_norm)  * 2 *  pi)
			# c[i] = np.sin((0.+ offset[i]) * 2 * pi )
			if c[i] < 0:
				c[i] = 0
		print c

	elif method == "stereo":
		return [(1-x), x, 0, 0]
	else:
		print "Error: unrecognised panning method: choose quad or stereo"


# panner("quad_rad", 0.0 , 0.5)
