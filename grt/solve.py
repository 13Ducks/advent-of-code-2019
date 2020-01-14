import cv2
import numpy as np
import socket

HOST = ''
PORT = 30000        # Port to listen on (non-privileged ports are > 1023)

vision_tape_area = 110.85
bounding_box = (40, 17)
bounding_box_area = bounding_box[0] * bounding_box[1]
coverage_area = vision_tape_area / bounding_box_area
bounding_aspect = bounding_box[0] / bounding_box[1]

max_diff_allow = 85
min_area = 8000

kHorizontalFOVDeg = 62.8
kVerticalFOVDeg = 37.9

kTargetHeightIn = 8*12 + 2.25 #middle of hex height
kCameraHeightIn = 6
kCameraPitchDeg = 40

lower_green = np.array([0,0,250])
upper_green = np.array([200,10,255])

# def nothing(x): pass
# cv2.namedWindow("Output", cv2.WINDOW_NORMAL)
# cv2.createTrackbar('H_min','Output',0,255,nothing)
# cv2.createTrackbar('H_max','Output',200,255,nothing)
# cv2.createTrackbar('S_min','Output',0,255,nothing)
# cv2.createTrackbar('S_max','Output',10,255,nothing)
# cv2.createTrackbar('V_min','Output',250,255,nothing)
# cv2.createTrackbar('V_max','Output',255,255,nothing)
# cv2.createTrackbar('Angle','Output',kCameraPitchDeg,50,nothing)

cap = cv2.VideoCapture("grt/bigtest.mov")

if not cap.isOpened(): 
    print("Error opening stream")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
        while(cap.isOpened()):
            distance = 0
            azimuth = 0

            ret, frame = cap.read()
            if not ret: continue

            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # def onmouse(k, x, y, s, p):
            #     if k == 1:
            #         print(hsv[y, x])

            # cv2.setMouseCallback("Output",onmouse);

            # lower_green = np.array([cv2.getTrackbarPos('H_min','Output'),cv2.getTrackbarPos('S_min','Output'),cv2.getTrackbarPos('V_min','Output')])
            # upper_green = np.array([cv2.getTrackbarPos('H_max','Output'),cv2.getTrackbarPos('S_max','Output'),cv2.getTrackbarPos('V_max','Output')])

            mask = cv2.inRange(hsv, lower_green, upper_green)
            res = cv2.bitwise_and(frame, frame, mask=mask)

            imgray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
            blur = cv2.blur(imgray, (5, 5))
            ret, thresh = cv2.threshold(blur, 127, 255, 0)
            if not ret: continue

            contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            best_contour = (0, 0, 0, 0)

            for cnt in contours:
                rect = cv2.minAreaRect(cnt)
                box = np.int0(cv2.boxPoints(rect))
                area = cv2.contourArea(box)
                
                if area > min_area:
                    diff_coverage = 100 - 100*abs(cv2.contourArea(cnt)/area - coverage_area)
                    width = max(rect[1])
                    height = min(rect[1])
                    diff_aspect = 100 - 100*abs(width/height - bounding_aspect)
                    diff_avg = (diff_aspect + diff_coverage)/2
                    
                    if diff_avg > max_diff_allow:
                        best_contour = ([box], rect, area)
            
            if best_contour[0] != 0: 
                center, dim, angle = best_contour[1]
                
                if dim[0] < dim[1]:
                    dim = list(reversed(dim))
                    angle += 90

                x = int(center[0] + 0.5 * dim[1] * np.sin(np.radians(angle)))
                y = int(center[1] - 0.5 * dim[1] * np.cos(np.radians(angle)))
                
                x_scale = 2 * (x / frame.shape[1]) - 1
                y_scale = -(2 * (y / frame.shape[0]) - 1);
                
                # cv2.drawContours(res, best_contour[0], 0, (0, 0, 255), 2)
                # cv2.drawMarker(res, tuple(map(int,(x,y))), (0,255,0), thickness=2)
                # cv2.putText(res,"x: " + str(round(x_scale,4)), (int(x),int(y)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255))
                # cv2.putText(res,"y: " + str(round(y_scale,4)), (int(x),int(y)+25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255))
            
                azimuth = x_scale * kHorizontalFOVDeg / 2.0
                distance = (kTargetHeightIn - kCameraHeightIn) / np.tan(np.radians(y_scale * (kVerticalFOVDeg / 2.0) + kCameraPitchDeg))
                # print(rangeY, azimuth, rangeY*np.cos(np.radians(kCameraPitchDeg)), rangeY*np.sin(np.radians(kCameraPitchDeg)))

            # cv2.imshow('Output', res)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            conn.send(bytes(str((distance,azimuth))+"\n","UTF-8"))
    
vid.release()
cv2.destroyAllWindows()
