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

cap = cv2.VideoCapture(0)

if not cap.isOpened(): 
    print("Error opening stream")

while True:
    try:
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

                    mask = cv2.inRange(hsv, lower_green, upper_green)
                    res = cv2.bitwise_and(frame, frame, mask=mask)

                    imgray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
                    blur = cv2.blur(imgray, (5, 5))
                    ret, thresh = cv2.threshold(blur, 64, 255, 0)
                    if not ret: continue

                    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[-2:]
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
                        
                        azimuth = x_scale * kHorizontalFOVDeg / 2.0
                        distance = (kTargetHeightIn - kCameraHeightIn) / np.tan(np.radians(y_scale * (kVerticalFOVDeg / 2.0) + kCameraPitchDeg))
                        
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

                    conn.send(bytes(str((distance,azimuth))+"\n","UTF-8"))
    except (BrokenPipeError) as e:
        print("connection lost... retrying")
    
vid.release()
cv2.destroyAllWindows()
