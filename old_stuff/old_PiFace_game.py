#!/usr/bin/python3
import sys
sys.path.append('/home/pi/PiFace/includes')
from oled_091 import SSD1306
import time
from time import sleep
import picamera
from os import path,system
import serial
import RPi.GPIO as GPIO
import face_recognition
import pickle
import cv2
from io import BytesIO
from keypad import keypad

one_factor = ['0D004B5BBAA7', '3900DC2807CA']
two_factor = ['3900E5E7172C', '3900E5EB4770', '3900E1BC3753', '3900E1BF3453', '3900E24C33A4', '3900DC751888']
three_factor = ['3900DC75FB6B', '3900DC7760F2', '3900DC783AA7']

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(17, GPIO.OUT)

# Initialize 'currentname' to trigger only when a new person is identified.
currentname = "unknown"
# Determine faces from encodings.pickle file model created from train_model.py
encodings_file = "encodings.pickle"

# load the known faces and embeddings along with OpenCV's Haar
# cascade for face detection
system('clear')
print("[INFO] loading encodings from ", encodings_file, "...")
# Load face encodings
data = pickle.loads(open(encodings_file, "rb").read())

# camera setup
print("[INFO] Warming up camera...")
image_width = 512
image_height = 304
camera = picamera.PiCamera()
camera.awb_mode = 'auto'
camera.resolution = (image_width, image_height)
camera.start_preview()

DIR_PATH = path.abspath(path.dirname(__file__))
DefaultFont = path.join(DIR_PATH, "Fonts/GothamLight.ttf")


class read_rfid:
    def read_rfid(self):
        ser = serial.Serial("/dev/ttyS0")  # Open named port
        ser.baudrate = 9600  # Set baud rate to 9600
        data = ser.read(12)  # Read 12 characters from serial port to data
        if (data != " "):
            GPIO.output(17, GPIO.HIGH)
            sleep(.1)
            GPIO.output(17, GPIO.LOW)
        ser.close()  # Close port
        data = data.decode("utf-8")
        return data


def info_print():
    # oled.Whiteoled()
    oled.DirImage(path.join(DIR_PATH, "Images/SB.png"))
    oled.DrawRect()
    oled.ShowImage()
    sleep(1)
    oled.PrintText("Place your TAG", FontSize=14)
    oled.ShowImage()


def display_token(id):
    oled.PrintText("ID : " + (id), cords=(4, 8), FontSize=11)
    oled.DrawRect()
    oled.ShowImage()


def display_access_results(access_message, access_image):
    # check if the video capture is open
    cap = cv2.VideoCapture(access_image)
    if not cap.isOpened():
        print("[ERROR] Error Opening Video Stream Or File", access_image)
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            cv2.imshow(access_message, frame)
            if cv2.waitKey(1) == ord('q'):
                break
        else:
            break
    cap.release()
    cv2.destroyAllWindows()


def get_access_code():
    seq = []
    print('[INFO] Enter 4 digit access code: ')
    for i in range(4):
        digit = None
        while digit == None:
            digit = kp.getKey()
        seq.append(digit)
        time.sleep(0.4)
        print(digit)

    # Check digit code
    if seq == access_code:
        print("[INFO] access code accepted")
        return True
    else:
        print("[INFO] access code incorrect")
        return False


oled = SSD1306()
SB = read_rfid()
kp = keypad(columnCount=4)
access_code = [1, 9, 6, 6]

if __name__ == "__main__":
    info_print()
    while True:
        print("[INFO] Ready to scan RFID token")
        id = SB.read_rfid()
        if id == "020047D742D0": exit()
        print("[INFO] Detected RFID token: ", id)
        display_token(id)
        if id in one_factor:
            print("[INFO] Single Factor Authentication card detected:.....ACCESS GRANTED")
            access_image = "Images/granted.avi"
            access_message = "ACCESS GRANTED"
            oled.PrintText("Access granted!", FontSize=14)
            oled.ShowImage()
            display_access_results(access_message, access_image)
        elif id in two_factor:
            print("[INFO] Dual Factor Authentication card detected:.....ENTER CODE")
            keypad_result = get_access_code()
            if keypad_result is True:
                access_image = "Images/granted.avi"
                access_message = "ACCESS GRANTED"
                oled.PrintText("Access granted!", FontSize=14)
                oled.ShowImage()
                display_access_results(access_message, access_image)
            else:
                access_image = "Images/denied.avi"
                access_message = "ACCESS DENIED"
                oled.PrintText("Access denied!", FontSize=14)
            display_access_results(access_message, access_image)
        elif id in three_factor:
            print("[INFO] Three Factor Authentication card detected:.....ENTER CODE")
            keypad_result = get_access_code()
            if keypad_result is True:
                stream = BytesIO()
                camera.capture(stream, format="jpeg")
                print("[INFO] Taking your photo to see if I recognise you")
                stream.seek(0)
                image = face_recognition.load_image_file(stream)
                boxes = face_recognition.face_locations(image)
                print("[INFO] Faces detected in image at location: ", boxes)
                encodings = face_recognition.face_encodings(image, boxes)
                names = []
                matches = []
                name = "nobody"
                # loop over the facial embeddings
                for encoding in encodings:
                    # attempt to match each face in the input image to our known
                    # encodings
                    matches = face_recognition.compare_faces(data["encodings"], encoding)
                    name = "Unknown"  # if face is not recognized, then print Unknown

                # check to see if we have found a match
                if True in matches:
                    # find the indexes of all matched faces then initialize a
                    # dictionary to count the total number of times each face
                    # was matched
                    matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                    counts = {}

                    # loop over the matched indexes and maintain a count for
                    # each recognized face face
                    for i in matchedIdxs:
                        name = data["names"][i]
                        counts[name] = counts.get(name, 0) + 1

                    # determine the recognized face with the largest number
                    # of votes (note: in the event of an unlikely tie Python
                    # will select first entry in the dictionary)
                    name = max(counts, key=counts.get)

                    # If someone in your dataset is identified, print their name on the screen
                    if currentname != name:
                        currentname = name

                print("[INFO] In the camera I saw the owner of access card : ", name)
                if name == id:
                    print("[INFO] The ID card and the person I saw in the camera match.....ACCESS GRANTED")
                    access_image = "Images/granted.avi"
                    access_message = "ACCESS GRANTED"
                    oled.PrintText("Access granted!", FontSize=14)
                    oled.ShowImage()
                else:
                    print("[INFO] The ID card and the person I saw in the camera DO NOT match.....ACCESS DENIED")
                    access_image = "Images/denied.avi"
                    access_message = "ACCESS DENIED"
                    oled.PrintText("Access denied!", FontSize=14)
                    oled.ShowImage()
                display_access_results(access_message, access_image)
            else:
                access_image = "Images/denied.avi"
                access_message = "ACCESS DENIED"
                oled.PrintText("Access denied!", FontSize=14)
                oled.ShowImage()
                display_access_results(access_message, access_image)
        sleep(2)
        oled.PrintText("Place your TAG", FontSize=14)
        oled.ShowImage()
oled.NoDisplay()
