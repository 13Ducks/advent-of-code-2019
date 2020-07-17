import numpy as np
import cv2

camera = np.array([[1.00941325e+03, 0.00000000e+00, 7.91825831e+02],
 [0.00000000e+00, 9.77571111e+02, 3.64266358e+02],
 [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
dist = np.array([-0.15291752,  0.11312259,  0.0044382,   0.03888565, -0.04706539])

cap = cv2.VideoCapture(0)
while (cap.isOpened()):
    _, frame = cap.read()
    cv2.imshow("frame", frame)

    undistort = cv2.undistort(frame, camera, dist)

    cv2.imshow("undist", undistort)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
