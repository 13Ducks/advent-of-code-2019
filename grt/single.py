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

max_diff_allow = 80
min_area = 1000

kHorizontalFOVDeg = 62.8
kVerticalFOVDeg = 37.9

kTargetHeightIn = 8*12 + 2.25  # middle of hex height
kCameraHeightIn = 6
kCameraPitchDeg = 40

coverage_weight = 100
aspect_weight = 50


def nothing(x): pass


cv2.namedWindow("Output", cv2.WINDOW_AUTOSIZE)
cv2.namedWindow("hsv", cv2.WINDOW_NORMAL)
cv2.createTrackbar('H_min', 'Output', 65, 255, nothing)
cv2.createTrackbar('H_max', 'Output', 80, 255, nothing)
cv2.createTrackbar('S_min', 'Output', 80, 255, nothing)
cv2.createTrackbar('S_max', 'Output', 255, 255, nothing)
cv2.createTrackbar('V_min', 'Output', 130, 255, nothing)
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
    best_contour = (0, 0, 0, 0)
    print("b4 cont")

    for cnt in contours:
        rect = cv2.minAreaRect(cnt)
        box = np.int0(cv2.boxPoints(rect))
        area = cv2.contourArea(box)

        # cv2.drawContours(res, [box], 0,(0,0,255),2)
        # print(area)

        if area > min_area:
            print("got past area")

            diff_coverage = 100 - coverage_weight * abs(cv2.contourArea(cnt)/area - coverage_area)
            width = max(rect[1])
            height = min(rect[1])
            diff_aspect = 100 - aspect_weight * abs(width/height - bounding_aspect)
            diff_avg = (diff_aspect + diff_coverage)/2

            #print(diff_coverage, diff_aspect, width, height)

            if diff_avg > max_diff_allow:
                best_contour = ([box], rect, area, cnt)

    if best_contour[0] != 0:
        hull = list(map(lambda x: x[0], cv2.convexHull(best_contour[3]).tolist()))
        while len(hull) > 4:
            min_dist = [10000,0]
            for i,p in enumerate(hull):
                x0, y0 = p
                x1, y1 = hull[i-1]
                x2, y2 = hull[(i+1)%len(hull)]
                d = abs((y2-y1)*x0 - (x2-x1)*y0 + x2*y1 - y2*x1) / np.sqrt((y2-y1)**2 + (x2-x1)**2)
                if min_dist[0] > d:
                    min_dist = [d,p]

            hull.remove(min_dist[1])
        
        for p in hull:
            cv2.drawMarker(res, tuple(p), (0, 128, 255), thickness=2)
            cv2.putText(res, "x: " + str(p[0]), (p[0], p[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255))
            cv2.putText(res, "y: " + str(p[1]), (p[0], p[1]+12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255))
        
        hull = sorted(hull, key=lambda x: x[1])
        top = hull[:2]
        bot = hull[-2:]
        top_slope = (top[0][1]-top[1][1]) / (top[0][0]- top[1][0])
        bot_slope = (bot[0][1]-bot[1][1]) / (bot[0][0]- bot[1][0])
        print(top_slope - bot_slope)
            

        center, dim, angle = best_contour[1]

        if dim[0] < dim[1]:
            dim = list(reversed(dim))
            angle += 90

        x = int(center[0] + 0.5 * dim[1] *
                np.sin(np.radians(angle)))
        y = int(center[1] - 0.5 * dim[1] *
                np.cos(np.radians(angle)))

        x_scale = 2 * (x / frame.shape[1]) - 1
        y_scale = -(2 * (y / frame.shape[0]) - 1)

        # cv2.drawContours(res, best_contour[0], 0, (0, 0, 255), 2)
        # cv2.drawMarker(res, tuple(map(int, (x, y))), (0, 255, 0), thickness=2)
        # cv2.putText(res, "x: " + str(round(x_scale, 4)),
        #             (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255))
        # cv2.putText(res, "y: " + str(round(y_scale, 4)), (int(x),
        #                                                   int(y)+25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255))

        azimuth = x_scale * kHorizontalFOVDeg / 2.0
        distance = (kTargetHeightIn - kCameraHeightIn) / np.tan(
            np.radians(y_scale * (kVerticalFOVDeg / 2.0) + kCameraPitchDeg))

    cv2.imshow('Output', res)
    if cv2.waitKey(0) & 0xFF == ord('q'):
        return (distance, azimuth)
    # print("after wait")
    # return (distance, azimuth)


im = cv2.imread("grt/BlueGoal-Far-ProtectedZone.jpg")
while True:
    print(get_box(im))