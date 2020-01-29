import cv2
import numpy as np
import socket

HOST = ''
PORT = 30000        # Port to listen on (non-privileged ports are > 1023)

vision_tape_area = 110.85
bounding_box = (40, 17)
bounding_box_area = bounding_box[0] * bounding_box[1]
coverage_area = vision_tape_area / bounding_box_area
# bounding_aspect = bounding_box[0] / bounding_box[1]

hex_ratio = 39.261 / 19.360

max_diff_allow = 80
min_area = 100
min_coverage = 90
# min_aspect = 65
min_hex_ratio = 90

kHorizontalFOVDeg = 62.8
kVerticalFOVDeg = 37.9

kTargetHeightIn = 8*12 + 2.25  # middle of hex height
kCameraHeightIn = 15
kCameraPitchDeg = 30

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
                    pitch = 0

                    _, frame = cap.read()

                    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

                    mask = cv2.inRange(hsv, lower_green, upper_green)
                    res = cv2.bitwise_and(frame, frame, mask=mask)

                    imgray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
                    # NOTE: median blur
                    blur = cv2.medianBlur(imgray,7)
                    ret, thresh = cv2.threshold(blur, 64, 255, 0)

                    contours, hierarchy = cv2.findContours(
                        thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[-2:]

                    best_hull = 0
                    best_diff = 0

                    for cnt in contours:
                        area = cv2.contourArea(cnt)

                        if area < min_area:
                            continue

                        rect = cv2.minAreaRect(cnt)
                        box = np.int0(cv2.boxPoints(rect))
                        rect_area = cv2.contourArea(box)

                        diff_coverage = 100 - 100 * abs(area/rect_area - coverage_area)

                        # width = max(rect[1])
                        # height = min(rect[1])
                        # diff_aspect = 100 - 100*abs(width/height - bounding_aspect)
                        
                        if diff_coverage < min_coverage:
                            continue

                        hull = list(map(lambda x: x[0], cv2.convexHull(cnt).tolist()))

                        while len(hull) > 4:
                            min_dist = [10000,0]
                            for i,p in enumerate(hull):
                                x0, y0 = p
                                x1, y1 = hull[i-1]
                                x2, y2 = hull[(i+1)%len(hull)]
                                d = abs((y2-y1)*x0 - (x2-x1)*y0 + x2*y1 - y2*x1) / np.hypot((y2-y1),(x2-x1))
                                if min_dist[0] > d:
                                    min_dist = [d,p]
                            hull.remove(min_dist[1])

                        hull = sorted(hull, key=lambda x: x[0])
                        top = (hull[0],hull[3])
                        bot = (hull[1],hull[2])
                        dist_top = np.hypot(top[0][0]-top[1][0], top[0][1]-top[1][1])
                        dist_bot = np.hypot(bot[0][0]-bot[1][0], bot[0][1]-bot[1][1])
                        diff_hex_ratio = 100 - 100*(hex_ratio - dist_top/dist_bot)

                        if diff_hex_ratio < min_hex_ratio:
                            continue
                        
                        total_diff = (diff_hex_ratio + diff_coverage) / 2
                        if total_diff > best_diff:
                            best_hull = hull
                            best_diff = total_diff

                    if best_hull != 0:        
                        
                        pts1 = np.array(best_hull, np.float32)
                        x,y = [(pts1[0][0] + pts1[3][0])/2, (pts1[0][1] + pts1[3][1])/2]
                        pts2 = np.array([[0, 0], [100, 170], [300, 170], [400, 0]], np.float32)

                        matrix = cv2.getPerspectiveTransform(pts1, pts2)
                        pitch = np.arcsin(matrix[1][0])
                    
                        x_scale = 2 * (x / frame.shape[1]) - 1
                        y_scale = -(2 * (y / frame.shape[0]) - 1)

                        azimuth = x_scale * kHorizontalFOVDeg / 2.0
                        distance = (kTargetHeightIn - kCameraHeightIn) / np.tan(
                            np.radians(y_scale * (kVerticalFOVDeg / 2.0) + kCameraPitchDeg))

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

                    conn.send(bytes(str((distance,azimuth,pitch))+"\n","UTF-8"))
    except (BrokenPipeError, ConnectionResetError, ConnectionRefusedError) as e:
        print("connection lost... retrying")
    
vid.release()
cv2.destroyAllWindows()
