#!/usr/bin/python3
import sys
sys.path.append('/home/pi/PiFace/includes')
from oled_091 import SSD1306
from time import sleep
import picamera
from os import path, system
import serial
import RPi.GPIO as GPIO
import face_recognition
import pickle
from io import BytesIO

# This dictionary is used to differentiate one, two and three factor cards. For any spare cards I added them to the dictionary with a factor of 99 just to be a record of them
card_factor = {'0D004B5BBAA7': 1, '3900E1BC3753': 1, '3900E24C33A4': 1, '3900DC2807CA': 2, '3900E5EB4770': 2, '3900DC751888': 2, '3900E5E7172C': 3, '3900DC75FB6B': 3, '3900E1BF3453': 3, '3900DC7760F2': 3, '3900DC783AA7': 2, '3900E6685EE9': 1, '3900E4C66C77': 3, '3900E4BAFA9D': 2, '3900E6757FD5': 1, '3900E4BDD2B2': 3, '3900E67049E6': 2, '3900E666873E': 1, '3900E6765FF6': 3, '3900E67817B0': 2, '3900E665A51F': 1}

# This dictionary i used to set the access PIN for each card. # is used for spare cards
card_pin = {'0D004B5BBAA7': '1966', '3900E1BC3753': '1966', '3900E24C33A4': '1966', '3900DC2807CA': '1966', '3900E5EB4770': '1966', '3900DC751888': '1966', '3900E5E7172C': '1966', '3900DC75FB6B': '1966', '3900E1BF3453': '1966', '3900DC7760F2': '1966', '3900DC783AA7': '1966', '3900E6685EE9': '1966', '3900E4C66C77': '1966', '3900E4BAFA9D': '1966', '3900E6757FD5': '1966', '3900E4BDD2B2': '1966', '3900E67049E6': '1966', '3900E666873E': '1966', '3900E6765FF6': '1966', '3900E67817B0': '1966', '3900E665A51F': '1966'}

# GPIO PINS
# Beacon is the GPIO bin for the electronic relay to control the 12V flashing beacon
Beacon = 26
# Buzzer is used to control the buzzer on the RFID HAT that beeps when a card is scanned
Buzzer = 17

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(Buzzer, GPIO.OUT)
GPIO.setup(Beacon, GPIO.OUT)
GPIO.output(Beacon, GPIO.HIGH)

# load the known faces and embeddings
encodings_file = "encodings.pickle"
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

# This function reads the 12 character card ID from the RFID HAT reader
def read_rfid():
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

# This function displays a message on the RFID HAT OLED display before a card is scanned
def info_print():
    # oled.Whiteoled()
    oled.NoDisplay()
    oled.DirImage(path.join(DIR_PATH, "Images/SB.png"))
    oled.DrawRect()
    oled.ShowImage()
    sleep(1)
    oled.PrintText("Place your TAG", FontSize=14)
    oled.ShowImage()

# This function displays the card ID on the RFID HAT OLED when a card is scanned
def display_token(card_id):
    oled.NoDisplay()
    oled.PrintText("ID : " + (card_id), cords=(4, 8), FontSize=11)
    oled.DrawRect()
    oled.ShowImage()

# This functions cleans up the RFID OLED display and turns off the beacon on exit
def clean_exit():
    oled.NoDisplay()
    GPIO.output(Beacon, GPIO.HIGH)
    exit()

# This function is called when access is granted. It plays a movie of the bank vault opening and updates the OLED display
def grant_access():
    access_image = "ffplay -loglevel quiet -hide_banner -noborder -nostats -autoexit Images/granted.avi"
    oled.PrintText("Access granted!", FontSize=14)
    oled.ShowImage()
    system(access_image)
    oled.NoDisplay()

# This function is called when access is denied. It plays a movie of an access denied message and updates the OLED display
def deny_access():
    access_image = "ffplay -loglevel quiet -hide_banner -noborder -nostats -autoexit Images/denied.mp4"
    oled.PrintText("Access denied!", FontSize=14)
    oled.ShowImage()
    GPIO.output(Beacon, GPIO.LOW)
    system(access_image)
    GPIO.output(Beacon, GPIO.HIGH)
    oled.NoDisplay()

# This function is called for the first authentication factor "something you have". If the card is recognised, access is granted
def factor_1(this_card_pin):
    print ('[INFO] I recognise this access card......Factor 1 PASSED!')
    return True

# This function is called for the second authentication factor "something you know". If the card is recognised, you are asked to enter a PIN which is matched to the card.
# If you get the correct PIN then access is granted
def factor_2(this_card_pin):
    entered_code = input('[INFO] Enter 4 digit access code: ')
    if entered_code == this_card_pin:
        print("[INFO] access code accepted......Factor 2 PASSED!")
        return True
    else:
        print("[INFO] access code incorrect......Factor 2 FAILED!")
        return False

# This function is called for the third authentication factor "something you are". A frame is grabbed from the camera and compared to the known faces from encodings.pickle.
# If the face is matched to the card that was scanned, then access is granted.
def factor_3(this_card_pin):
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

    print("[INFO] In the camera I saw the owner of access card : ", name)
    if name == card_id:
        print("[INFO] The ID card and the person I saw in the camera match.....Factor 3 PASSED!")
        return True
    else:
        print("[INFO] The ID card and the person I saw in the camera DO NOT match.....Factor 3 FAILED!")
        return False

oled = SSD1306()

if __name__ == "__main__":
    info_print()
    while True:
        print("[INFO] Ready to scan RFID token")
        card_id = read_rfid()
        # Blue keyfob used to end the program
        if card_id == "020047D742D0": 
            clean_exit()
        else:
            print(f"[INFO] Detected RFID token: {card_id}")
            display_token(card_id)
            this_card_factor = card_factor.get(card_id)
            this_card_pin = card_pin.get(card_id)
            current_factor = 1
            while current_factor <= this_card_factor:
                factor_function = "factor_" + str(current_factor)
                if not globals()[factor_function](this_card_pin):
                    deny_access()
                    break
                elif current_factor == this_card_factor:
                    grant_access()
                current_factor += 1
            sleep(2)
            system('clear')
            oled.NoDisplay()
            oled.PrintText("Place your TAG", FontSize=14)
            oled.ShowImage()
