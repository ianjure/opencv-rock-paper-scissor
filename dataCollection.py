import cv2
import math
import time
import numpy as np
from cvzone.HandTrackingModule import HandDetector

# WEBCAM INITIALIZATION
cap = cv2.VideoCapture(0)

# INITIALIZE HAND DETECTOR AND VARIABLES
detector = HandDetector(maxHands=1)
offset = 20
imgSize = 300

# SAVE IMAGES TO DATA PATH
path_rock = "data/rock"
path_paper = "data/paper"
path_scissors = "data/scissors"
counter = 0


while True:
    success, img = cap.read()
    hands, img = detector.findHands(img)

    # CROP HANDS
    if hands:
        hand = hands[0] # -- GET THE HAND IF IT IS PRESENT IN THE SCREEN
        x, y, w, h = hand['bbox'] # -- GET BOUNDING BOX

        # SET A FIX SIZE FOR ALL IMAGES BEFORE CROPPING
        imgBack = np.ones(shape=(imgSize, imgSize, 3), dtype=np.uint8)*255 # -- CREATING A WHITE BACKGROUND
        imgCrop = img[y - offset:y + h + offset, x - offset:x + w + offset]
        
        # STRETCH THE IMAGE TO FIT THE BACKGROUND
        aspectRatio = h/w

        if aspectRatio > 1: # -- IF HEIGHT IS GREATER THAN THE WIDTH
            k = imgSize/h
            wCal = math.ceil(k * w)

            # OVERLAY AREAS OF THE BACKGROUND IMAGE WITH THE CROPPED IMAGE OF THE HANDS
            imgResize = cv2.resize(imgCrop, (wCal, imgSize))
            imgResizeShape = imgResize.shape # -- VALUES: 0:HEIGHT, 1:WIDTH, 3:CHANNELS
            wGap = math.ceil((imgSize - wCal)/2) # -- CALCULATE GAP TO CENTER IMAGE
            imgBack[:, wGap:wCal + wGap] = imgResize

        else: # -- IF WIDTH IS GREATER THAN THE HEIGHT
            k = imgSize/w
            hCal = math.ceil(k * h)

            # OVERLAY AREAS OF THE BACKGROUND IMAGE WITH THE CROPPED IMAGE OF THE HANDS
            imgResize = cv2.resize(imgCrop, (imgSize, hCal))
            imgResizeShape = imgResize.shape # -- VALUES: 0:HEIGHT, 1:WIDTH, 3:CHANNELS
            hGap = math.ceil((imgSize - hCal)/2) # -- CALCULATE GAP TO CENTER IMAGE
            imgBack[hGap:hCal + hGap, :] = imgResize
        
        cv2.imshow("Hands", imgBack)


    cv2.imshow("Window", img)

    # SAVE IMAGE KEYBIND
    key = cv2.waitKey(1)
    if key == ord("s"):
        counter += 1
        cv2.imwrite(f"{path_rock}/Image_{time.time()}.jpg", imgBack) # -- CHANGE DIRECTORY OF DATA PATH

        # CLOSE WINDOW AFTER 300 IMAGES ARE SAVED
        if counter == 250:
            cv2.destroyAllWindows()

    # KEYBIND
    k = cv2.waitKey(1) & 0xFF
    if k == 27: # -- 'ESC' KEY
        break
    elif cv2.getWindowProperty("Window", cv2.WND_PROP_VISIBLE) < 1: # -- CLOSE BUTTON 
        break

cv2.destroyAllWindows()
