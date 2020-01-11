import cv2
import numpy as np
import time

vid = cv2.VideoCapture("grt/bigtest.mov")

vision_tape_area = 110.85
bounding_box = (40, 17)
bounding_box_area = bounding_box[0] * bounding_box[1]
coverage_area = vision_tape_area / bounding_box_area
coverage_weight = 100
bounding_aspect = bounding_box[0] / bounding_box[1]
aspect_weight = 50

max_diff_allow = 80

kHorizontalFOVDeg = 61
kTargetHeightIn = 8*12 + 2.25 #middle of hex height
kCameraHeightIn = 15
kCameraPitchDeg = 50
kVerticalFOVDeg = 0

while(True):
    begin = time.time()
    ret, frame = vid.read()
    #frame = cv2.flip(frame, 0)
    kVerticalFOVDeg = frame.shape[0]/frame.shape[1]*kHorizontalFOVDeg
    #print(frame.shape)

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # lower_green = np.array([0,0,240])
    # upper_green = np.array([20,20,255])
    lower_green = np.array([30,0,250])
    upper_green = np.array([100,10,255])
    mask = cv2.inRange(hsv, lower_green, upper_green)
    res = cv2.bitwise_and(frame, frame, mask=mask)
    
    def onmouse(k, x, y, s, p):
        global hsv
        if k == 1:
            print(hsv[y, x])

    cv2.namedWindow("hsv", cv2.WINDOW_NORMAL)
    cv2.setMouseCallback("hsv", onmouse)
    cv2.imshow("hsv", hsv)

    cv2.namedWindow("Output", cv2.WINDOW_NORMAL)
    cv2.setMouseCallback("Output",onmouse);

    imgray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(imgray, 127, 255, 0)
    contours, hierarchy = cv2.findContours(
        thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    max_contour = (0, 0, 0, 0)

    for cnt in contours:
        # area_cnt = cv2.contourArea(cnt)
        # if max_contour[3] < area_cnt:
        #     rect = cv2.minAreaRect(cnt)
        #     box = cv2.boxPoints(rect)
        #     box = np.int0(box)
        #     area_box = cv2.contourArea(box)
        #     max_contour = ([box], rect, area_box, area_cnt)

        box = cv2.boundingRect(cnt)
        area = box[2]*box[3]
        if area > 10000:
            #print(area)
            diff_coverage = 100 - coverage_weight*abs(cv2.contourArea(cnt)/area - coverage_area)
            diff_aspect = 100 - aspect_weight*abs(box[2]/box[3] - bounding_aspect)
            diff_sum = (diff_aspect + diff_coverage)/2
            if diff_sum > 80:
                #print(diff_coverage, diff_aspect)
                max_contour = (box, area, cv2.contourArea(cnt), cnt)
            
    if max_contour[0] != 0:        
        x,y,w,h = max_contour[0]

        diff_coverage = 100 - coverage_weight*abs(max_contour[2]/max_contour[1] - coverage_area)
        diff_aspect = 100 - aspect_weight*abs(w/h - bounding_aspect)
        diff_sum = (diff_aspect + diff_coverage)/2
        #print(diff_sum)

        frame_reso = (frame.shape[1]/2, frame.shape[0]/2)
        # print(x,(x-frame_reso[0])/frame_reso[0])
        # print(y,-(y-frame_reso[1])/frame_reso[1])
        # print(x+w,(x+w-frame_reso[0])/frame_reso[0])
        # print(y+h,-(y+h-frame_reso[1])/frame_reso[1])

        #if diff_sum > max_diff_allow:
            # cv2.drawContours(res, max_contour[0], 0, (0, 0, 255), 2)
            # cv2.circle(res, (int(max_contour[1][0][0] + 0.5 * max_contour[1][1][1] * np.sin(np.radians(max_contour[1][2]))), int(
            #     max_contour[1][0][1] - 0.5 * max_contour[1][1][1]  * np.cos(np.radians(max_contour[1][2])))), 20, (254, 0, 0), 20)
        cv2.rectangle(res,(x,y),(x+w,y+h),(0,255,0),2)
        # print((bounding_box[0]/12)*frame.shape[1]/(2*w*np.tan(np.radians(40))))

        x_scaled = x+w/2
        x_scaled = 2 * (x_scaled / frame.shape[1]) - 1;
        y_scaled = -(2 * (y / frame.shape[0]) - 1);
        cv2.putText(res,"x: " + str(round(x_scaled,4)), (int(x+w/2),y), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,255))
        cv2.putText(res,"y: " + str(round(y_scaled,4)), (int(x+w/2),int(y-50)), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,255))
        # cv2.putText(res,"x: " + str(round((x+w-frame_reso[0])/frame_reso[0],4)), (x+w,y+h), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,255))
        # cv2.putText(res,"y: " + str(-round((y+h-frame_reso[1])/frame_reso[1],4)), (x+w,y+h-50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,255))

        cv2.imshow('Output', res)
        
        # #print(time.time() - begin)
        kVerticalFOVDeg = frame.shape[0]/frame.shape[1]*kHorizontalFOVDeg
        azimuth = (x_scaled * kHorizontalFOVDeg / 2.0) % 360
        range = (kTargetHeightIn - kCameraHeightIn) / np.tan(np.radians(y_scaled * kVerticalFOVDeg / 2.0 + kCameraPitchDeg))
        print(range, azimuth)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
vid.release()
cv2.destroyAllWindows()
