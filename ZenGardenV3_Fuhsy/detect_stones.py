import cv2
import numpy as np
import copy

class StoneFeatures():
    def __init__(self,center,radius,theme):
        self.center = center
        self.radius = radius
        self.theme = theme




def blob_detection(img,img_col,hsv):
    color_img = copy.copy(img_col)

    # HSV-space
    lower_blue = np.array([0,100,50])
    upper_blue = np.array([40,255,150])
    lower_green = np.array([40,100,20])
    upper_green = np.array([90,255,150])
    lower_red = np.array([115,70,100])
    upper_red = np.array([180,255,255])
    # for (lower,upper) in boundaries:
    # lower_blue = np.array(lower_blue, dtype = "uint8")
    # upper_blue = np.array(upper_blue, dtype = "uint8")
    mask_b = cv2.inRange(hsv, lower_blue, upper_blue)
    mask_g = cv2.inRange(hsv, lower_green, upper_green)
    mask_r = cv2.inRange(hsv, lower_red, upper_red)
    output_b = cv2.bitwise_and(color_img, color_img, mask = mask_b)
    output_g = cv2.bitwise_and(color_img, color_img, mask = mask_g)
    output_r = cv2.bitwise_and(color_img, color_img, mask = mask_r)
    img_seg = output_b+output_g+output_r
    # cv2.imshow("img_seg", img_seg)
    # cv2.waitKey(0)
    # h,s,img = cv2.split(img)
    # print 'blob detection'
    # kernel = np.ones((3,3),np.uint8)
    # # img = cv2.dilate(img,kernel,iterations = 30)
    # # img = cv2.erode(img,kernel,iterations = 50)
    # # img = cv2.dilate(img,kernel,iterations = 20)
    # params = cv2.SimpleBlobDetector_Params()
    # # cv2.imgshow("Blob_detection_inside",img)
    # # cv2.waitKey(0)
    # # Change thresholds
    # # params.minThreshold = 10;
    # # params.maxThreshold = 400;
    #
    # # Filter by Area.
    # params.filterByArea = True
    # params.minArea = 1000
    # params.maxArea = 100000
    #
    # # Filter by Circularity
    # params.filterByCircularity = True
    # params.minCircularity = 0.4
    #
    # # Filter by Convexity
    # params.filterByConvexity = False
    # params.minConvexity = 0.05
    #
    # # Filter by Inertia
    # params.filterByInertia = False
    # params.minInertiaRatio = 0.01
    # ver = (cv2.__version__).split('.')
    # if int(ver[0]) < 3 :
    #     detector = cv2.SimpleBlobDetector(params)
    # else :
    #     detector = cv2.SimpleBlobDetector_create(params)
    # # Detect blobs.
    # keypoints = detector.detect(255-img)
    # coordinates = getCoordinates(keypoints)
    stone_features = []
    pixelc = []
    r=0
    b=0
    g=0
    img_seg_gray = cv2.cvtColor(img_seg, cv2.COLOR_BGR2GRAY)
    kernel = np.ones((3,3),np.uint8)
    img_seg_gray = cv2.dilate(img_seg_gray, kernel, iterations = 2)
    img_seg_gray = cv2.erode(img_seg_gray, kernel, iterations = 2)
    img_seg_gray = cv2.dilate(img_seg_gray, kernel, iterations = 2)

    image_COL, contours_COL, _ = cv2.findContours(img_seg_gray,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    # cv2.imshow("img_seg", image_COL)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    for cnt in contours_COL:
            if cv2.contourArea(cnt) > 3000 and cv2.contourArea(cnt) < 200000:
                hull = cv2.convexHull(cnt)
                x,y,w,h = cv2.boundingRect(cnt)
                # cv2.rectangle(im,(x,y),(x+w,y+h),(0,255,0),2)
                rect = cv2.minAreaRect(cnt)
                box = cv2.boxPoints(rect)
                box = np.int0(box)
                cv2.drawContours(img_seg,[box],0,(255,255,255),2)
                (x,y),radius = cv2.minEnclosingCircle(cnt)
                center = (int(x),int(y))
                radius = int(radius)
                print "radius: %i center %i %i" %(radius,center[0],center[1])
                left = center[0]-(radius/2)
                right = center[0]+(radius/2)
                top = center[1]-(radius/2)
                down = center[1]+(radius/2)
                max_right, max_down = image_COL.shape
                if left<0:
                    left=0
                if right>max_right:
                    right=max_right
                if top<0:
                    right=0
                if down<max_down:
                    down = max_down
                    # pixelc = img_seg[center[1]-(radius/2):center[0]+(radius/2),center[1]-(radius/2):center[0]+(radius/2)]
                pixelc = img_seg[top:down,left:right]
                b = pixelc[:,:,0]
                g = pixelc[:,:,1]
                r = pixelc[:,:,2]
                r = sum_ret(r)
                g = sum_ret(g)
                b = sum_ret(b)
                print "r:%i,g:%i,b:%i" %(r,g,b)
                if r > b and r > g:
                    print "RED"
                    stone_object = StoneFeatures(center,radius,'RED')
                elif b > r and b > g:
                    print "BLUE"
                    stone_object = StoneFeatures(center,radius,'BLUE')
                elif g > r and g > b:
                    print "GREEN"
                    stone_object = StoneFeatures(center,radius,'GREEN')
                else:
                    print "NOTHING"
                    stone_object = StoneFeatures(center,radius,'NOTHING')

                stone_features.append(stone_object)

    return stone_features

def sum_ret(input):
    return sum([sum(x) for x in input])

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
start_radius = 20
