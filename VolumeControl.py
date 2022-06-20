import cv2
import mediapipe as mp
import time
import numpy
import numpy as np
import HandTrackingModule as htm
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
########################

wCam, hCam = 640, 480

########################
pTime = cTime = 0
cap = cv2.VideoCapture(1)
cap.set(3, wCam)
cap.set(4, hCam)

detector = htm.handDetector(detectionCon=0.8)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
#(-63.5, 0.0, 0.5)
vol = 0
volBar = 300
volPer = 0
while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img,draw=False)
    if len(lmList) != 0:
        x1,y1 = lmList[4][1],lmList[4][2] #thumb
        x2, y2 = lmList[8][1], lmList[8][2] #index finger
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2 #middle of the line btwn fingers
        cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 2)

        length = numpy.hypot(x2-x1, y2-y1)

        # hand range 50 - 300
        # volume range -63.5 - 0

        vol = np.interp(length, [50, 220], [minVol, maxVol])
        volBar = np.interp(length, [50, 220], [300, 150])
        volPer = np.interp(length, [50, 220], [0, 100])
        print(vol)
        volume.SetMasterVolumeLevel(vol, None)
        if length<50:
            cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)

    cv2.rectangle(img,(50, 150), (85, 300), (255, 0, 0), 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 300), (255, 0, 0), cv2.FILLED)
    cv2.putText(img, f' Vol:{int(volPer)}%', (10, 350), cv2.FONT_HERSHEY_PLAIN, 2,
                (255, 0, 0), 2)
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, f' fps:{int(fps)}', (10, 50), cv2.FONT_HERSHEY_PLAIN, 2,
                (255, 0, 255), 2)
    cv2.imshow("image", img)
    cv2.waitKey(1)