import cv2
import cvzone
import math
import random
import time
import numpy as np
from score import getScore
from cvzone.ClassificationModule import Classifier
from cvzone.HandTrackingModule import HandDetector

# WEBCAM INITIALIZATION
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800) # -- WIDTH 
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 800) # -- HEIGHT

# INITIALIZE HAND DETECTOR AND VARIABLES
detector = HandDetector(maxHands=1)
classifier = Classifier("model/keras_model.h5", "model/labels.txt")
offset = 20
imgSize = 300

# CLASS NAMES
labels = ["rock", "paper", "scissors"]

# GLOBAL VARIABLES
start_time = 0.0
userChoice = ""
aiChoice = ""
userScore = 0
aiScore = 0

while True:
    success, img = cap.read()
    hands, img = detector.findHands(img, draw=False)

    # CHECK IF HANDS IS PRESENT AND IF THE USER AND AI DID NOT CHOOSE YET, THEN CROP HANDS
    if (hands) and (len(userChoice) == 0) and (len(aiChoice) == 0):
        current_time = time.time() # -- GRAB THE CURRENT TIME

        if start_time == 0.0:
            start_time = time.time()

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

            # CLASSIFY IMAGE
            prediction, index = classifier.getPrediction(imgBack, draw=False)

        else: # -- IF WIDTH IS GREATER THAN THE HEIGHT
            k = imgSize/w
            hCal = math.ceil(k * h)

            # OVERLAY AREAS OF THE BACKGROUND IMAGE WITH THE CROPPED IMAGE OF THE HANDS
            imgResize = cv2.resize(imgCrop, (imgSize, hCal))
            imgResizeShape = imgResize.shape # -- VALUES: 0:HEIGHT, 1:WIDTH, 3:CHANNELS
            hGap = math.ceil((imgSize - hCal)/2) # -- CALCULATE GAP TO CENTER IMAGE
            imgBack[hGap:hCal + hGap, :] = imgResize

            # CLASSIFY IMAGE
            prediction, index = classifier.getPrediction(imgBack, draw=False)

        # USER CHOICE GRAPHICS
        user_choice_graphics = cv2.imread(f"graphics/user_{labels[index]}.png", cv2.IMREAD_UNCHANGED)
        user_choice_graphics = cv2.resize(user_choice_graphics, (100, 122))
        cvzone.overlayPNG(img, user_choice_graphics, (30, 330))

        # CHECK IF 5 SECONDS HAS PASSED
        if (current_time - start_time > 5.0):
            userChoice = labels[index] # -- SET LAST SIGN AS THE USER CHOICE

    # IF USER HAS CHOSEN
    if len(userChoice) != 0:
        # USER CHOICE GRAPHICS
        user_choice_graphics = cv2.imread(f"graphics/user_{userChoice}.png", cv2.IMREAD_UNCHANGED)
        user_choice_graphics = cv2.resize(user_choice_graphics, (100, 122))
        cvzone.overlayPNG(img, user_choice_graphics, (30, 330))

        # AFTER USER HAS CHOSEN, CHECK IF AI HAS CHOSEN, IF NOT THEN CHOOSE A RANDOM SIGN
        if len(aiChoice) == 0:
            aiChoice = random.choice(labels)
            score = getScore(userChoice, aiChoice) # GET THE WINNER

            if score == 1: # -- USER WON
                userScore += 1
            elif score == -1: # -- AI WON
                aiScore += 1
        
        # AI CHOICE GRAPHICS
        ai_choice_graphics = cv2.imread(f"graphics/ai_{aiChoice}.png", cv2.IMREAD_UNCHANGED)
        ai_choice_graphics = cv2.resize(ai_choice_graphics, (100, 122))
        cvzone.overlayPNG(img, ai_choice_graphics, (510, 330))

        # CLEAR ALL CHOICES AND START AGAIN AFTER SPACEBAR IS PRESSED | OTHER KEYBIND
        key = cv2.waitKey(1) & 0xFF
        if key == 32: # -- 'SPACEBAR' KEY
            userChoice = ""
            aiChoice = ""
            start_time = 0.0
        elif key == 27: # -- 'ESC' KEY
            break
        elif cv2.getWindowProperty("Rock Paper Scissors Game", cv2.WND_PROP_VISIBLE) < 1: # -- CLOSE BUTTON 
            break

    else:
        # INFO GRAPHICS
        info_graphics = cv2.imread(f"graphics/info.png", cv2.IMREAD_UNCHANGED)
        info_graphics = cv2.resize(info_graphics, (150, 34))
        info_graphics_x = (img.shape[1] - 150) / 2 # -- CENTER GRAPHICS TO SCREEN (HORIZONTALLY)
        cvzone.overlayPNG(img, info_graphics, (math.floor(info_graphics_x), 20))

        # BLANK USER CHOICE GRAPHICS
        blank_user_choice_graphics = cv2.imread(f"graphics/choice_blank.png", cv2.IMREAD_UNCHANGED)
        blank_user_choice_graphics = cv2.resize(blank_user_choice_graphics, (100, 122))
        cvzone.overlayPNG(img, blank_user_choice_graphics, (30, 330))

        # BLANK AI CHOICE GRAPHICS
        blank_ai_choice_graphics = cv2.imread(f"graphics/choice_blank.png", cv2.IMREAD_UNCHANGED)
        blank_ai_choice_graphics = cv2.resize(blank_ai_choice_graphics, (100, 122))
        cvzone.overlayPNG(img, blank_ai_choice_graphics, (510, 330))
    
    # STATIC GRAPHICS SECTION

    # USER SCORE GRAPHICS
    user_score_graphics = cv2.imread(f"graphics/user_score.png", cv2.IMREAD_UNCHANGED)
    user_score_graphics = cv2.resize(user_score_graphics, (150, 20))
    cvzone.overlayPNG(img, user_score_graphics, (10, 10))

    # USER SCORE
    cv2.putText(img, text=str(userScore), org=(60,65), fontFace=1,
                fontScale=2, color=(255,255,255), thickness=2)

    # AI SCORE GRAPHICS
    ai_score_graphics = cv2.imread(f"graphics/ai_score.png", cv2.IMREAD_UNCHANGED)
    ai_score_graphics = cv2.resize(ai_score_graphics, (121, 20))
    cvzone.overlayPNG(img, ai_score_graphics, (505, 10))

    # AI SCORE
    cv2.putText(img, text=str(aiScore), org=(560,65), fontFace=1,
                fontScale=2, color=(255,255,255), thickness=2)

    cv2.imshow("Rock Paper Scissors Game", img)
    cv2.waitKey(1)

    # KEYBIND
    k = cv2.waitKey(1) & 0xFF
    if k == 27: # -- 'ESC' KEY
        break
    elif cv2.getWindowProperty("Rock Paper Scissors Game", cv2.WND_PROP_VISIBLE) < 1: # -- CLOSE BUTTON 
        break

cv2.destroyAllWindows()