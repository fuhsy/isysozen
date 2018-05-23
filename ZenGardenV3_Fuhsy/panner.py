# Quad panner
# Depends on where (0, 0 is)

# The x, y position should be normalised. 
def panner(method, x, y):
	if method == "quad":
		c1 = (1- x) * (1-y) # (0, 0)
		c2 = x * (1- y)		#  ( 1, 0)
		c3 = x * y          # (1, 1)
		c4 = (1 -x) * y     # (0, 1)
		return [c1,c2,c3,c4]   #
	elif method == "stereo":
		return [x, (1-x), 0, 0]
	else: 
		print "Error: unrecognised panning method: choose quad or stereo"