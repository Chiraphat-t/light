import cv2
import mediapipe as mp
import time
from pyfirmata import Arduino, SERVO, util

time.sleep(2.0)

mp_draw = mp.solutions.drawing_utils  # Use drawing_utils to draw straight connect landmark points
mp_hand = mp.solutions.hands  # Use hands function to detect hand landmarks

tipIds = [4, 8, 12, 16, 20]  # MediaPipe positions of fingertips

def check_user_input(input):
    try:
        val = int(input)  # Convert it to an integer
        bv = True
    except ValueError:
        try:
            val = float(input)  # Convert it to a float
            bv = True
        except ValueError:
            bv = False
    return bv

#### SERVO function control ####
def rotateservo(pin, angle):  # Create function to control servo motor
    board.digital[pin].write(angle)
    time.sleep(0.015)

def servo(total, pin):  # Create condition to control servo based on finger count
    if (total)==0:
            rotateservo(pin,0)
    elif (total)==1:
            rotateservo(pin,18)
    elif (total)==2:
            rotateservo(pin,36)
    elif (total)==3:
            rotateservo(pin,54)
    elif (total)==4:
            rotateservo(pin,72)
    elif (total)==5:
            rotateservo(pin,90)
    elif (total)==6:
            rotateservo(pin,108)
    elif (total)==7:
            rotateservo(pin,126)
    elif (total)==8:
            rotateservo(pin,144)
    elif (total)==9:
            rotateservo(pin,162)
    elif (total)==10:
            rotateservo(pin,180)

########################################

cport = input('Enter the camera port: ')
while not check_user_input(cport):
    print('Please enter a number not a string')
    cport = input('Enter the camera port: ')

comport = input('Enter the arduino board COM port: ')
while not check_user_input(comport):
    print('Please enter a number not a string')
    comport = input('Enter the arduino board COM port: ')

board = Arduino('COM' + comport)
pin = 9
board.digital[pin].mode = SERVO  # Set pin mode for servo

video = cv2.VideoCapture(0)  # Open camera at index position 0

with mp_hand.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
    while True:
        ret, image = video.read()  # Read frame from camera
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert color BGR to RGB
        image.flags.writeable = False  # To improve nothing drawn in image
        results = hands.process(image)  # Process the image
        image.flags.writeable = True   # Can draw on the image
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)  # Convert color RGB to BGR
        lmList = []

        if results.multi_hand_landmarks:  # Check if hands are detected
            total_fingers = 0
            for hand_landmark in results.multi_hand_landmarks:  # Loop through all hands detected
                for id, lm in enumerate(hand_landmark.landmark):
                    h, w, c = image.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lmList.append([id, cx, cy])  # Add landmark positions
                mp_draw.draw_landmarks(image, hand_landmark, mp_hand.HAND_CONNECTIONS)  # Draw hand skeleton

            fingers = []
            if len(lmList) != 0:
                for hand in range(len(results.multi_hand_landmarks)):  # Iterate through each detected hand
                    lmList = []
                    hand_landmark = results.multi_hand_landmarks[hand]
                    for id, lm in enumerate(hand_landmark.landmark):
                        h, w, c = image.shape
                        cx, cy = int(lm.x * w), int(lm.y * h)
                        lmList.append([id, cx, cy])
                    # Counting fingers
                    hand_fingers = 0
                    if lmList[9][1] < lmList[5][1]:
                        if lmList[tipIds[0]][1] > lmList[tipIds[0] - 1][1]:  # Check thumb
                            hand_fingers += 1
                    else:
                        if lmList[tipIds[0]][1] < lmList[tipIds[0] - 1][1]:
                            hand_fingers += 1
                    for id in range(1, 5):
                        if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:  # Check other fingers
                            hand_fingers += 1
                    total_fingers += hand_fingers  # Add up fingers from both hands

            servo(total_fingers, pin)  # Control servo based on total fingers

            # Display finger count
            if results.multi_hand_landmarks:
                cv2.rectangle(image, (20, 300), (270, 425), (0, 255, 0), cv2.FILLED)
                cv2.putText(image, str(total_fingers), (40, 375), cv2.FONT_HERSHEY_SIMPLEX,
                            2, (255, 0, 0), 5)
                cv2.putText(image, "Servo", (100, 375), cv2.FONT_HERSHEY_SIMPLEX,
                            2, (255, 0, 0), 5)

        cv2.imshow("Frame", image)  # Show the processed frame
        k = cv2.waitKey(1)
        if k == ord('q'):  # Press "q" to exit the program
            break

video.release()
cv2.destroyAllWindows()