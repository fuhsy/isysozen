import cv2
import numpy as np

class StoneFeatures():
    def __init__(self,center,radius):
        self.center = center
        self.radius = radius


def blob_detection(img):
    params = cv2.SimpleBlobDetector_Params()
    # cv2.imgshow("Blob_detection_inside",img)
    # cv2.waitKey(0)
    # Change thresholds
    params.minThreshold = 10;
    params.maxThreshold = 200;

    # Filter by Area.
    params.filterByArea = True
    params.minArea = 50
    params.maxArea = 5000

    # Filter by Circularity
    # params.filterByCircularity = False
    # params.minCircularity = 0.01
    #
    # # Filter by Convexity
    # params.filterByConvexity = False
    # params.minConvexity = 0.5
    #
    # # Filter by Inertia
    # params.filterByInertia = False
    # params.minInertiaRatio = 0.01
    ver = (cv2.__version__).split('.')
    if int(ver[0]) < 3 :
        detector = cv2.SimpleBlobDetector(params)
    else :
        detector = cv2.SimpleBlobDetector_create(params)
    # Detect blobs.
    keypoints = detector.detect(255-img)
    # coordinates = getCoordinates(keypoints)
    # for i in range(len(coordinates)):
    #     cv2.circle(img,(coordinates[i,0],coordinates[i,1]),int(keypoints[i].size),(255,0,255),1)
    #     print "Keypoint %i P1:%i, P2:%i"%(i,coordinates[i,0],coordinates[i,1])
    return keypoints

def getCoordinates(keypoints):
	amount = len(keypoints)
	# Find out the coordinate
	coordinates = np.ndarray(shape=(amount,2), dtype=int)
	for i in range(amount):
		# normalised the coordinate.
		coordinates[i, 0] = keypoints[i].pt[0]
		coordinates[i, 1] = keypoints[i].pt[1]
	return coordinates

def findSize(keypoints):
	amount = len(keypoints)
	sizes = np.zeros(amount)
	for i in range (amount):
		sizes[i] = keypoints[i].size
	return sizes


# img = cv2.imread('blob.png',0)
def blob_detection2(img):
    # img = cv2.medianBlur(img,5)
    cimg = cv2.cvtColor(img,cv2.COLOR_GRAY2BGR)

    circles = cv2.HoughCircles(img,cv2.HOUGH_GRADIENT,1,10,
                                param1=50,param2=20,minRadius=20,maxRadius=200)

    circles = np.uint16(np.around(circles))
    for i in circles[0,:]:
        # draw the outer circle
        cv2.circle(cimg,(i[0],i[1]),i[2],(0,255,0),2)
        # draw the center of the circle
        cv2.circle(cimg,(i[0],i[1]),2,(0,0,255),3)

    cv2.imshow('detected circles',cimg)
    cv2.waitKey(0)
    # cv2.destroyAllWindows()
    return cimg
def blob_detection3(img):
    image, contours, hierarchy = cv2.findContours(img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    stone_features = []
    for cnt in contours:
        # hull = cv2.convexHull(cnt)
        # x,y,w,h = cv2.boundingRect(cnt)
        # # cv2.rectangle(im,(x,y),(x+w,y+h),(0,255,0),2)
        # rect = cv2.minAreaRect(cnt)
        # box = cv2.boxPoints(rect)
        # box = np.int0(box)
        # cv2.drawContours(img,[box],0,(0,0,255),2)

        (x,y),radius = cv2.minEnclosingCircle(cnt)
        center = (int(x),int(y))
        radius = int(radius)
        stone_object = StoneFeatures(center,radius)
        stone_features.append(stone_object)

    return stone_features
# img = cv2.imread('blob.png',0)
# print type(img)
# blob_detection2(img)
