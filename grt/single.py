import cv2
import numpy as np
import socket

HOST = ''
PORT = 30000        # Port to listen on (non-privileged ports are > 1023)

vision_tape_area = 110.85
bounding_box = (40, 17)
bounding_box_area = bounding_box[0] * bounding_box[1]
coverage_area = vision_tape_area / bounding_box_area

hex_ratio = 39.261 / 19.360

max_diff_allow = 80
min_area = 100
min_coverage = 90
min_hex_ratio = 90

kHorizontalFOVDeg = 62.8
kVerticalFOVDeg = 37.9

kTargetHeightIn = 8*12 + 2.25  # middle of hex height
kCameraHeightIn = 6
kCameraPitchDeg = 40

def nothing(x): pass

cv2.namedWindow("Output", cv2.WINDOW_AUTOSIZE)
cv2.namedWindow("hsv", cv2.WINDOW_NORMAL)
cv2.createTrackbar('H_min', 'Output', 65, 255, nothing)
cv2.createTrackbar('H_max', 'Output', 80, 255, nothing)
cv2.createTrackbar('S_min', 'Output', 80, 255, nothing)
cv2.createTrackbar('S_max', 'Output', 255, 255, nothing)
cv2.createTrackbar('V_min', 'Output', 75, 255, nothing)
cv2.createTrackbar('V_max', 'Output', 255, 255, nothing)
cv2.createTrackbar('Angle', 'Output', kCameraPitchDeg, 50, nothing)

# cap = cv2.VideoCapture(0)

# if not cap.isOpened():
#     print("Error opening stream")


def get_box(frame):
    distance = 0
    azimuth = 0

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    cv2.imshow('hsv', hsv)

    lower_green = np.array([cv2.getTrackbarPos('H_min', 'Output'), cv2.getTrackbarPos(
        'S_min', 'Output'), cv2.getTrackbarPos('V_min', 'Output')])
    upper_green = np.array([cv2.getTrackbarPos('H_max', 'Output'), cv2.getTrackbarPos(
        'S_max', 'Output'), cv2.getTrackbarPos('V_max', 'Output')])

    mask = cv2.inRange(hsv, lower_green, upper_green)
    res = cv2.bitwise_and(frame, frame, mask=mask)

    imgray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(imgray, 64, 255, 0)

    contours, hierarchy = cv2.findContours(
        thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[-2:]
    best_hull = 0
    print("b4 cont")

    for cnt in contours:
        area = cv2.contourArea(cnt)

        if area < min_area:
            continue

        print("got past area")

        rect = cv2.minAreaRect(cnt)
        box = np.int0(cv2.boxPoints(rect))
        rect_area = cv2.contourArea(box)

        diff_coverage = 100 - 100 * abs(area/rect_area - coverage_area)
        
        if diff_coverage < min_coverage:
            continue

        print("got past coverage")

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
        print(dist_top, dist_bot)

        if diff_hex_ratio < min_hex_ratio:
            continue

        print("got past hex ratio")

        best_hull = hull

    if best_hull != 0:        
        for p in best_hull:
            cv2.drawMarker(res, tuple(p), (0, 128, 255), thickness=2)
            cv2.putText(res, "x: " + str(p[0]), (p[0], p[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255))
            cv2.putText(res, "y: " + str(p[1]), (p[0], p[1]+12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255))
    
        pts1 = np.array(best_hull, np.float32)
        x,y = [(pts1[0][0] + pts1[3][0])/2, (pts1[0][1] + pts1[3][1])/2]

        pts2 = np.array([[0, 0], [100, 170], [300, 170], [400, 0]], np.float32)

        matrix = cv2.getPerspectiveTransform(pts1, pts2)
        warp = cv2.warpPerspective(frame, matrix, (400, 170))
        cv2.imshow("Perspective transformation", warp)

        # https://stackoverflow.com/questions/15022630/how-to-calculate-the-angle-from-rotation-matrix
        theta_z = np.arctan2(matrix[1][0], matrix[0][0])
        print(np.degrees(theta_z))
       
        x_scale = 2 * (x / frame.shape[1]) - 1
        y_scale = -(2 * (y / frame.shape[0]) - 1)

        cv2.drawMarker(res, tuple(map(int, [x,y])), (0, 255, 0), thickness=2)

        azimuth = x_scale * kHorizontalFOVDeg / 2.0
        distance = (kTargetHeightIn - kCameraHeightIn) / np.tan(
            np.radians(y_scale * (kVerticalFOVDeg / 2.0) + kCameraPitchDeg))

        rel_x = distance * np.cos(theta_z)
        rel_y = distance * np.sin(theta_z)

        print(rel_x, rel_y)
        print(distance, azimuth)

    cv2.imshow('Output', res)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        return
    # print("after wait")
    # return (distance, azimuth)


im = cv2.imread("grt/BlueGoal-060in-Center.jpg")
cap = cv2.VideoCapture(1)
if not cap.isOpened(): 
    print("Error opening stream")
while True:
    #print(get_box(im))
    _, frame = cap.read()
    get_box(frame)