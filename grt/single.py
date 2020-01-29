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

hex_dim = (39.261, 19.360)
hex_ratio = hex_dim[0] / hex_dim[1]
hex_area = 3/2 * np.sqrt(3) * (hex_dim[0]/2)**2 / 2
solidity_expect = vision_tape_area / hex_area

max_diff_allow = 80
min_area = 50
min_coverage = 90
min_solidity = 90
# min_aspect = 65
min_hex_ratio = 70

kHorizontalFOVDeg = 62.8
kVerticalFOVDeg = 37.9

kTargetHeightIn = 8*12 + 2.25  # middle of hex height
kCameraHeightIn = 15
kCameraPitchDeg = 30

cameraMatrix = np.array([[678.154, 0,          318.135],
                         [0,          678.17, 228.374],
                         [0,          0,          1]])

dist_coeffs =np.array([0.154576, -1.19143, 0, 0, 2.06105, 0, 0, 0])

obj_points = []

obj_points.append([-19.631, 0, 0])
obj_points.append([-9.816, -17, 0])
obj_points.append([9.816, -17, 0])
obj_points.append([19.631, 0, 0])

obj_points = np.array(obj_points, np.float32)

def nothing(x): pass

cv2.namedWindow("Output", cv2.WINDOW_AUTOSIZE)

cv2.createTrackbar('H_min', 'Output', 65, 255, nothing)
cv2.createTrackbar('H_max', 'Output', 100, 255, nothing)
cv2.createTrackbar('S_min', 'Output', 80, 255, nothing)
cv2.createTrackbar('S_max', 'Output', 255, 255, nothing)
cv2.createTrackbar('V_min', 'Output', 75, 255, nothing)
cv2.createTrackbar('V_max', 'Output', 255, 255, nothing)

# cap = cv2.VideoCapture(0)

# if not cap.isOpened():
#     print("Error opening stream")

def valid_hex_contour(cnt):
    area = cv2.contourArea(cnt)

    print(area)
    if area < min_area:
        return (0,0)

    # print("past area")

    rect = cv2.minAreaRect(cnt)
    box = np.int0(cv2.boxPoints(rect))
    rect_area = cv2.contourArea(box)

    diff_coverage = 100 - 100 * abs(area/rect_area - coverage_area)

    # width = max(rect[1])
    # height = min(rect[1])
    # diff_aspect = 100 - 100*abs(width/height - bounding_aspect)

    if diff_coverage < min_coverage:
        return (0,0)

    print("past cov")

    hull = list(map(lambda x: x[0], cv2.convexHull(cnt).tolist()))
    while len(hull) > 4:
        min_dist = [10000, 0]
        for i, p in enumerate(hull):
            x0, y0 = p
            x1, y1 = hull[i-1]
            x2, y2 = hull[(i+1) % len(hull)]
            d =abs((y2-y1)*x0 - (x2-x1)*y0 + x2*y1 - y2*x1) / np.hypot((y2-y1), (x2-x1))
            if min_dist[0] > d:
                min_dist = [d, p]
        hull.remove(min_dist[1])

    hull = sorted(hull, key=lambda x: x[0])
    top = (hull[0], hull[3])
    bot = (hull[1], hull[2])
    dist_top = np.hypot(top[0][0]-top[1][0], top[0][1]-top[1][1])
    dist_bot = np.hypot(bot[0][0]-bot[1][0], bot[0][1]-bot[1][1])
    diff_hex_ratio = 100 - 100*(hex_ratio - dist_top/dist_bot)

    if diff_hex_ratio < min_hex_ratio:
        return (0,0)

    total_diff = (diff_hex_ratio + diff_coverage) / 2
    return (total_diff, hull)

def get_box(frame):
    distance = 0
    azimuth = 0
    pitch = 0

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_green =np.array([cv2.getTrackbarPos("H_min", "Output"), cv2.getTrackbarPos(
        "S_min", "Output"), cv2.getTrackbarPos("V_min", "Output")])
    upper_green =np.array([cv2.getTrackbarPos("H_max", "Output"), cv2.getTrackbarPos(
        "S_max", "Output"), cv2.getTrackbarPos("V_max", "Output")])

    mask = cv2.inRange(hsv, lower_green, upper_green)
    res = cv2.bitwise_and(frame, frame, mask=mask)

    imgray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
    # NOTE: median blur
    blur = cv2.medianBlur(imgray, 7)
    ret, thresh = cv2.threshold(blur, 64, 255, 0)

    contours, hierarchy =cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2:]

    best_hull = 0
    best_diff = 0

    for cnt in contours:
        total_diff, hull = valid_hex_contour(cnt)
        if total_diff > best_diff:
            best_hull = hull
            best_diff = total_diff
            # leftmost = tuple(cnt[cnt[:,:,0].argmin()][0])
            # rightmost = tuple(cnt[cnt[:,:,0].argmax()][0])
            # bottommost = tuple(cnt[cnt[:,:,1].argmax()][0])
            # cv2.drawMarker(res, bottommost, (0, 128, 255), thickness=3)
            # cv2.drawMarker(res, leftmost, (0, 128, 255), thickness=3)
            # cv2.drawMarker(res, rightmost, (0, 128, 255), thickness=3)
            area = cv2.contourArea(cnt)
            hull = cv2.convexHull(cnt)
            hull_area = cv2.contourArea(hull)
            solidity = float(area)/hull_area
            #print(100 - 100 * abs(solidity - solidity_expect))

    if best_hull != 0:
        pts1 = np.array(best_hull, np.float32)
        pts1 = np.array(list([x,frame.shape[0]-y] for x,y in best_hull), np.float32)
        #test = []
        for p in pts1:
            cv2.drawMarker(res, tuple(p), (0, 255, 0), thickness=3)
            # y_scale = -(2 * (p[1] / frame.shape[0]) - 1)
            # distance = (kTargetHeightIn - kCameraHeightIn) / np.tan(
            #     np.radians(y_scale * (kVerticalFOVDeg / 2.0) + kCameraPitchDeg))
            # #print(distance, p)
            # test.append(distance)

        # d1,d2 = test[0], test[3]
        # print(d1,d2)
        # test_ans = np.degrees(np.arccos((40**2-d1**2-d2**2)/(-2*d1*d2)))
        # print(test_ans)

        # print(pts1, obj_points)

        retval, revec, tvec, inliers = cv2.solvePnPRansac(obj_points, pts1, cameraMatrix, dist_coeffs)
        print(tvec[0][0], tvec[1][0], tvec[2][0])
        print(np.degrees(revec[0][0]), np.degrees(revec[1][0]), np.degrees(revec[2][0]))

        x, y = [(pts1[0][0] + pts1[3][0])/2, (pts1[0][1] + pts1[3][1])/2]
        pts2 = np.array([[0, 0], [100, 170], [300, 170], [400, 0]], np.float32)

        matrix = cv2.getPerspectiveTransform(pts1, pts2)
        yaw = np.arctan2(matrix[2][0],matrix[0][0]);
        pitch = np.arcsin(matrix[1][0])
        roll = np.arctan2(matrix[1][2],matrix[1][1]);

        x_scale = 2 * (x / frame.shape[1]) - 1
        y_scale = -(2 * (y / frame.shape[0]) - 1)

        azimuth = x_scale * kHorizontalFOVDeg / 2.0
        distance =(kTargetHeightIn - kCameraHeightIn) / np.tan(
            np.radians(y_scale * (kVerticalFOVDeg / 2.0) + kCameraPitchDeg))

        #print(pts1)

    cv2.imshow('Output', res)
    cv2.imshow("blur", blur)
    print(np.degrees(yaw), np.degrees(pitch), np.degrees(roll))
    if cv2.waitKey(1) & 0xFF == ord('q'):
        return
    # print("after wait")
    # return (distance, azimuth)

im = cv2.imread("grt/BlueGoal-228in-ProtectedZone.jpg")
# cap = cv2.VideoCapture("grt/bigtest.mov")
# if not cap.isOpened():
# print("Error opening stream")
while True:
    print(get_box(im))
    # _, frame = cap.read()
    # get_box(frame)