import cv2
import cvzone
import math
import random
import time
import numpy as np
import win32.lib.win32con as win32con
from win32 import win32gui
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
compChoice = ""
userScore = 0
compScore = 0
message = ""

while True:
    success, img = cap.read()
    hands, img = detector.findHands(img, draw=False)

    # CHECK IF HANDS IS PRESENT AND IF THE USER AND COMPUTER DID NOT CHOOSE YET, THEN CROP HANDS
    if (hands) and (len(userChoice) == 0) and (len(compChoice) == 0):
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
    
    # RESET START TIME IF HANDS IS NOT PRESENT ON THE SCREEN
    else:
        start_time = 0.0

    # IF USER HAS CHOSEN
    if len(userChoice) != 0:
        # USER CHOICE GRAPHICS
        user_choice_graphics = cv2.imread(f"graphics/user_{userChoice}.png", cv2.IMREAD_UNCHANGED)
        user_choice_graphics = cv2.resize(user_choice_graphics, (100, 122))
        cvzone.overlayPNG(img, user_choice_graphics, (30, 330))

        # AFTER USER HAS CHOSEN, CHECK IF COMPUTER HAS CHOSEN, IF NOT THEN CHOOSE A RANDOM SIGN
        if len(compChoice) == 0:
            compChoice = random.choice(labels)
            score = getScore(userChoice, compChoice) # GET THE WINNER

            if score == 1: # -- USER WON
                userScore += 1
                message = "user"
            elif score == -1: # -- COMPUTER WON
                compScore += 1
                message = "computer"
            else:
                message = "tie"

        # SHOW MESSAGE GRAPHICS BASED ON WHO WON THE ROUND
        if message == "computer":
            # COMPUTER WIN GRAPHICS
            comp_win_graphics = cv2.imread(f"graphics/comp_win.png", cv2.IMREAD_UNCHANGED)
            comp_win_graphics = cv2.resize(comp_win_graphics, (174, 15))
            comp_win_graphics_x = (img.shape[1] - 174) / 2 # -- CENTER GRAPHICS TO SCREEN (HORIZONTALLY)
            cvzone.overlayPNG(img, comp_win_graphics, (math.floor(comp_win_graphics_x), 15))
        elif message == "user":
            # USER WIN GRAPHICS
            user_win_graphics = cv2.imread(f"graphics/user_win.png", cv2.IMREAD_UNCHANGED)
            user_win_graphics = cv2.resize(user_win_graphics, (91, 15))
            user_win_graphics_x = (img.shape[1] - 91) / 2 # -- CENTER GRAPHICS TO SCREEN (HORIZONTALLY)
            cvzone.overlayPNG(img, user_win_graphics, (math.floor(user_win_graphics_x), 15))
        else:
            # GAME TIE GRAPHICS
            tie_graphics = cv2.imread(f"graphics/tie.png", cv2.IMREAD_UNCHANGED)
            tie_graphics = cv2.resize(tie_graphics, (92, 15))
            tie_graphics_x = (img.shape[1] - 92) / 2 # -- CENTER GRAPHICS TO SCREEN (HORIZONTALLY)
            cvzone.overlayPNG(img, tie_graphics, (math.floor(tie_graphics_x), 15))

        # COMPUTER CHOICE GRAPHICS
        comp_choice_graphics = cv2.imread(f"graphics/comp_{compChoice}.png", cv2.IMREAD_UNCHANGED)
        comp_choice_graphics = cv2.resize(comp_choice_graphics, (100, 122))
        cvzone.overlayPNG(img, comp_choice_graphics, (510, 330))

        # PRESS SPACEBAR GRAPHICS
        spacebar_graphics = cv2.imread(f"graphics/spacebar.png", cv2.IMREAD_UNCHANGED)
        spacebar_graphics = cv2.resize(spacebar_graphics, (150, 70))
        spacebar_graphics_x = (img.shape[1] - 150) / 2 # -- CENTER GRAPHICS TO SCREEN (HORIZONTALLY)
        spacebar_graphics_y = (img.shape[0] - 70) / 2 # -- CENTER GRAPHICS TO SCREEN (VERTICALLY)
        cvzone.overlayPNG(img, spacebar_graphics, (math.floor(spacebar_graphics_x), math.floor(spacebar_graphics_y)))

        # CLEAR ALL CHOICES AND START AGAIN AFTER SPACEBAR IS PRESSED | OTHER KEYBIND
        key = cv2.waitKey(1) & 0xFF
        if key == 32: # -- 'SPACEBAR' KEY
            userChoice = ""
            compChoice = ""
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

        # BLANK COMPUTER CHOICE GRAPHICS
        blank_comp_choice_graphics = cv2.imread(f"graphics/choice_blank.png", cv2.IMREAD_UNCHANGED)
        blank_comp_choice_graphics = cv2.resize(blank_comp_choice_graphics, (100, 122))
        cvzone.overlayPNG(img, blank_comp_choice_graphics, (510, 330))
    
    # STATIC GRAPHICS SECTION

    # USER SCORE GRAPHICS
    user_score_graphics = cv2.imread(f"graphics/user_score.png", cv2.IMREAD_UNCHANGED)
    user_score_graphics = cv2.resize(user_score_graphics, (150, 20))
    cvzone.overlayPNG(img, user_score_graphics, (10, 10))

    # USER SCORE
    cv2.putText(img, text=str(userScore), org=(70,65), fontFace=1,
                fontScale=2, color=(255,255,255), thickness=2)

    # COMPUTER SCORE GRAPHICS
    comp_score_graphics = cv2.imread(f"graphics/comp_score.png", cv2.IMREAD_UNCHANGED)
    comp_score_graphics = cv2.resize(comp_score_graphics, (153, 20))
    cvzone.overlayPNG(img, comp_score_graphics, (480, 10))

    # COMPUTER SCORE
    cv2.putText(img, text=str(compScore), org=(550,65), fontFace=1,
                fontScale=2, color=(255,255,255), thickness=2)

    cv2.imshow("Rock Paper Scissors Game", img)
    cv2.waitKey(1)

    # ICON
    hwnd = win32gui.FindWindow(None, "Rock Paper Scissors Game")
    icon_path = "graphics/icon.ico" # -- FILE SHOULD BE .ICO
    win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_BIG,
                        win32gui.LoadImage(None, icon_path, win32con.IMAGE_ICON,
                        0, 0, win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE))

    # KEYBIND
    k = cv2.waitKey(1) & 0xFF
    if k == 27: # -- 'ESC' KEY
        break
    elif cv2.getWindowProperty("Rock Paper Scissors Game", cv2.WND_PROP_VISIBLE) < 1: # -- CLOSE BUTTON 
        break

cv2.destroyAllWindows()
