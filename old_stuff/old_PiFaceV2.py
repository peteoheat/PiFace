#!/usr/bin/python3
import sys
sys.path.append('/home/pi/PiFace/includes')
from oled_091 import SSD1306
import time
from time import sleep
import picamera
from os import path, system
import serial
import RPi.GPIO as GPIO
import face_recognition
import pickle
from io import BytesIO
from keypad import keypad

one_factor = ['0D004B5BBAA7', '3900E1BC3753', '3900E24C33A4']
two_factor = ['3900DC2807CA', '3900E5EB4770', '3900DC751888']
three_factor = ['3900E5E7172C', '3900DC75FB6B', '3900E1BF3453']
spare_cards = ['3900DC7760F2', '3900DC783AA7']

# Dictionary to differentiate one, two and three factor cards. Factor 99 is for a spare card
card_factor = {'0D004B5BBAA7':1, '3900E1BC3753':1, '3900E24C33A4':1,'3900DC2807CA':2, '3900E5EB4770':2, '3900DC751888':2, '3900E5E7172C':3, '3900DC75FB6B':3, '3900E1BF3453':3, '3900DC7760F2':99, '3900DC783AA7':99}

# Dictionary to set the access PIN for each card. # is used for spare cards
card_pin = {'0D004B5BBAA7':7, '3900E1BC3753':3, '3900E24C33A4':4,'3900DC2807CA':'A', '3900E5EB4770':0, '3900DC751888':8, '3900E5E7172C':'C', '3900DC75FB6B':'B', '3900E1BF3453':3, '3900DC7760F2':'#', '3900DC783AA7':'#'}

access_code = [1, 9, 6, 6]

# GPIO PINS
Beacon = 26
Buzzer = 17

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(Buzzer, GPIO.OUT)
GPIO.setup(Beacon, GPIO.OUT)
GPIO.output(Beacon, GPIO.HIGH)

# Initialize 'current_name' to trigger only when a new person is identified.
current_name = "unknown"
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
            GPIO.output(Buzzer, GPIO.HIGH)
            sleep(.2)
            GPIO.output(Buzzer, GPIO.LOW)
        ser.close()  # Close port
        data = data.decode("utf-8")
        return data


def info_print():
    # oled.Whiteoled()
    oled.NoDisplay()
    oled.DirImage(path.join(DIR_PATH, "Images/SB.png"))
    oled.DrawRect()
    oled.ShowImage()
    sleep(1)
    oled.PrintText("Place your TAG", FontSize=14)
    oled.ShowImage()

def display_token(id):
    oled.NoDisplay()
    oled.PrintText("ID : " + (id), cords=(4, 8), FontSize=11)
    oled.DrawRect()
    oled.ShowImage()

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

def control_beacon(switch_beacon):
    if switch_beacon == "ON":
        GPIO.output(Beacon, GPIO.LOW)
    elif switch_beacon == "OFF":
        GPIO.output(Beacon, GPIO.HIGH)
    else:
        print("[ERROR] Unknown beacon control value")

def clean_exit():
    oled.NoDisplay()
    control_beacon("OFF")
    exit()

def grant_access():
    access_image = "ffplay -loglevel quiet -hide_banner -noborder -nostats -autoexit Images/granted.avi"
    oled.PrintText("Access granted!", FontSize=14)
    oled.ShowImage()
    system(access_image)

def deny_access():
    access_image = "ffplay -loglevel quiet -hide_banner -noborder -nostats -autoexit Images/denied.mp4"
    oled.PrintText("Access denied!", FontSize=14)
    control_beacon("ON")
    system(access_image)
    control_beacon("OFF")

def factor_one():
    print("[INFO] Single Factor Authentication card detected:.....ACCESS GRANTED")
    access_image = "ffplay -loglevel quiet -hide_banner -noborder -nostats -autoexit Images/granted.avi"
    oled.PrintText("Access granted!", FontSize=14)
    oled.ShowImage()
    system(access_image)

def factor_two():
    print("[INFO] Dual Factor Authentication card detected:.....ENTER CODE")
    keypad_result = get_access_code()
    if keypad_result is True:
     access_image = "ffplay -loglevel quiet -hide_banner -noborder -nostats -autoexit Images/granted.avi"
     oled.PrintText("Access granted!", FontSize=14)
     oled.ShowImage()
     system(access_image)
    else:
     access_image = "ffplay -loglevel quiet -hide_banner -noborder -nostats -autoexit Images/denied.mp4"
     oled.PrintText("Access denied!", FontSize=14)
     control_beacon("ON")
     system(access_image)
     control_beacon("OFF")

def factor_three():
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
            if current_name != name:
                current_name = name

        print("[INFO] In the camera I saw the owner of access card : ", name)
        if name == id:
            print("[INFO] The ID card and the person I saw in the camera match.....ACCESS GRANTED")
            access_image = "ffplay -loglevel quiet -hide_banner -noborder -nostats -autoexit Images/granted.avi"
            oled.PrintText("Access granted!", FontSize=14)
            oled.ShowImage()
            system(access_image)
        else:
            print("[INFO] The ID card and the person I saw in the camera DO NOT match.....ACCESS DENIED")
            access_image = "ffplay -loglevel quiet -hide_banner -noborder -nostats -autoexit Images/denied.mp4"
            oled.PrintText("Access denied!", FontSize=14)
            oled.ShowImage()
            control_beacon("ON")
            system(access_image)
            control_beacon("OFF")
    else:
        access_image = "ffplay -loglevel quiet -hide_banner -noborder -nostats -autoexit Images/denied.mp4"
        oled.PrintText("Access denied!", FontSize=14)
        oled.ShowImage()
        control_beacon("ON")
        system(access_image)
        control_beacon("OFF")

oled = SSD1306()
RFID = read_rfid()
kp = keypad(columnCount=4)

if __name__ == "__main__":
    info_print()
    while True:
        print("[INFO] Ready to scan RFID token")
        id = RFID.read_rfid()
        if id == "020047D742D0": clean_exit()
        print("[INFO] Detected RFID token: ", id)
        display_token(id)
        factor = card_factor.get(id)
        pin = card_pin.get(id)
        print(f"[INFO] This card is {factor} factor and the PIN is {pin}")
        if id in one_factor:
            print("[INFO] Single Factor Authentication card detected:.....ACCESS GRANTED")
            access_image = "ffplay -loglevel quiet -hide_banner -noborder -nostats -autoexit Images/granted.avi"
            oled.PrintText("Access granted!", FontSize=14)
            oled.ShowImage()
            system(access_image)
        elif id in two_factor:
            print("[INFO] Dual Factor Authentication card detected:.....ENTER CODE")
            keypad_result = get_access_code()
            if keypad_result is True:
                access_image = "ffplay -loglevel quiet -hide_banner -noborder -nostats -autoexit Images/granted.avi"
                oled.PrintText("Access granted!", FontSize=14)
                oled.ShowImage()
                system(access_image)
            else:
                access_image = "ffplay -loglevel quiet -hide_banner -noborder -nostats -autoexit Images/denied.mp4"
                oled.PrintText("Access denied!", FontSize=14)
                control_beacon("ON")
                system(access_image)
                control_beacon("OFF")
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
                    access_image = "ffplay -loglevel quiet -hide_banner -noborder -nostats -autoexit Images/granted.avi"
                    oled.PrintText("Access granted!", FontSize=14)
                    oled.ShowImage()
                    system(access_image)
                else:
                    print("[INFO] The ID card and the person I saw in the camera DO NOT match.....ACCESS DENIED")
                    access_image = "ffplay -loglevel quiet -hide_banner -noborder -nostats -autoexit Images/denied.mp4"
                    oled.PrintText("Access denied!", FontSize=14)
                    oled.ShowImage()
                    control_beacon("ON")
                    system(access_image)
                    control_beacon("OFF")
            else:
                access_image = "ffplay -loglevel quiet -hide_banner -noborder -nostats -autoexit Images/denied.mp4"
                oled.PrintText("Access denied!", FontSize=14)
                oled.ShowImage()
                control_beacon("ON")
                system(access_image)
                control_beacon("OFF")
        sleep(2)
        oled.PrintText("Place your TAG", FontSize=14)
        oled.ShowImage()
oled.NoDisplay()
