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

frame_count = 5

lower_green = np.array([0,2,75])
upper_green = np.array([255,50,255])

cv2.namedWindow("output", cv2.WINDOW_AUTOSIZE)
def nothing(x): pass
cv2.createTrackbar("H_min", "output", 0, 255, nothing)
cv2.createTrackbar("S_min", "output", 0, 255, nothing)
cv2.createTrackbar("V_min", "output", 250, 255, nothing)
cv2.createTrackbar("H_max", "output", 100, 255, nothing)
cv2.createTrackbar("S_max", "output", 100, 255, nothing)
cv2.createTrackbar("V_max", "output", 255, 255, nothing)

cap = cv2.VideoCapture(1)

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
                    distance = []
                    azimuth = []
                    pitch = []

                    for i in range(frame_count):
                        _, frame = cap.read()

                        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

                        lower_green = np.array([cv2.getTrackbarPos('H_min', "output"), cv2.getTrackbarPos('S_min', "output"), cv2.getTrackbarPos('V_min', "output")])
                        upper_green = np.array([cv2.getTrackbarPos('H_max', "output"), cv2.getTrackbarPos('S_max', "output"), cv2.getTrackbarPos('V_max', "output")])
                        mask = cv2.inRange(hsv, lower_green, upper_green)
                        res = cv2.bitwise_and(frame, frame, mask=mask)

                        imgray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
                        blur = cv2.medianBlur(imgray, 5)
                        ret, thresh = cv2.threshold(blur, 64, 255, 0)

                        contours, hierarchy = cv2.findContours(
                            thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[-2:]

                        best_hull = 0
                        best_diff = 0

                        for cnt in contours:
                            area = cv2.contourArea(cnt)
                            #print(area)

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
                            for p in pts1:
                                cv2.drawMarker(res, tuple(p), (0,255,0), thickness=5)
                            x,y = [(pts1[0][0] + pts1[3][0])/2, (pts1[0][1] + pts1[3][1])/2]

                            pts2 = np.array([[0, 0], [100, 170], [300, 170], [400, 0]], np.float32)

                            matrix = cv2.getPerspectiveTransform(pts1, pts2)

                            yaw_curr = np.arctan2(matrix[2][0],matrix[0][0])
                            pitch_curr = np.arcsin(matrix[1][0])
                            roll_curr = np.arctan2(matrix[1][2],matrix[1][1])
                            # yaw_curr = np.arctan2(matrix[2][0],matrix[2][2])
                            # pitch_curr = np.arcsin(matrix[2][1])
                            # roll_curr = np.arctan2(matrix[0][1],matrix[1][1])
                            print(np.degrees(yaw_curr), np.degrees(pitch_curr), np.degrees(roll_curr))
                            
                        
                            x_scale = 2 * (x / frame.shape[1]) - 1
                            y_scale = -(2 * (y / frame.shape[0]) - 1)

                            azimuth_curr = x_scale * kHorizontalFOVDeg / 2.0
                            distance_curr = (kTargetHeightIn - kCameraHeightIn) / np.tan(
                                np.radians(y_scale * (kVerticalFOVDeg / 2.0) + kCameraPitchDeg))

                            azimuth.append(azimuth_curr)
                            distance.append(distance_curr)
                            pitch.append(pitch_curr)

                        cv2.imshow("output", res)

                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break
                    
                    distance_med = np.median(distance)
                    azimuth_med = np.median(azimuth)
                    pitch_med = np.median(pitch)
                    print(frame.shape)
                    conn.send(bytes(str((distance_med,azimuth_med,np.degrees(pitch_med)))+"\n","UTF-8"))
    except (BrokenPipeError, ConnectionResetError, ConnectionRefusedError) as e:
        print("connection lost... retrying")
    
vid.release()
cv2.destroyAllWindows()
