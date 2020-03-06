import glob
import cv2

"""
Rechange images. for experiments.

"""
# files = glob.glob("/Users/fuhsy/Desktop/sozen/Data_0912/images/saved_data/*.jpg")
#
# for file in files:
#     print file
files = glob.glob("/Users/fuhsy/Desktop/sozen/Data_0912/images/Step3 (interactive Z)/*.jpg")
c = 0
for file in files:
    img = cv2.imread(file)
    c +=1
    # if im is not None:
    #     img = cv2.cvtColor(im, cv2.COLOR_RGB2BGR)

    for i in range(1,3):
        cv2.line(img, (img.shape[1]/3*i, 0), (img.shape[1]/3*i, img.shape[0]), (0, 0, 255), 2, 1)
        cv2.line(img, (0, img.shape[0]/3*i), (img.shape[1], img.shape[0]/3*i), (0, 0, 255), 2, 1)
    cv2.imwrite('/Users/fuhsy/Desktop/sozen/Data_0912/images/saved_data_prepared_web/'+str(c)+".jpg", img)
    # cv2.imshow('lame',img)
    # cv2.waitKey(0)
