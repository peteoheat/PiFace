#!/usr/bin/python3
import sys
sys.path.append('/home/pi/PiFace/includes')
import time
from oled_091 import SSD1306
from time import sleep
from os import path, system
import serial
import RPi.GPIO as GPIO
import face_recognition
import pickle
import board
import neopixel_spi
from threading import Thread, Event
import cv2
from picamera2 import Picamera2
import numpy as np

# This dictionary is used to differentiate one, two and three factor cards. For any spare cards I added them to the dictionary with a factor of 99 just to be a record of them
card_factor = {'0D004B5BBAA7': 1, '3900E1BC3753': 1, '3900E24C33A4': 1, '3900DC2807CA': 2, '3900E5EB4770': 2, '3900DC751888': 2, '3900E5E7172C': 3, '3900DC75FB6B': 3, '3900E1BF3453': 3, '3900DC7760F2': 3, '3900DC783AA7': 2, '3900E6685EE9': 1, '3900E4C66C77': 3, '3900E4BAFA9D': 2, '3900E6757FD5': 1, '3900E4BDD2B2': 3, '3900E67049E6': 2, '3900E666873E': 1, '3900E6765FF6': 3, '3900E67817B0': 2, '3900E665A51F': 1, '1D003D3BDDC6': 1, '1D003D1E7C42': 2, '1D0023A7E970': 3, '1D0023ABEC79': 1, '1D0023AD5AC9': 2, '1D0023867DC5': 3, '1D002388A91F': 1, '1D0023884CFA': 2, '1D0026246D72': 3, '1D00237EADED': 1, '1D002D679EC9': 2, '1D002F5A9DF5': 3}

# This dictionary i used to set the access PIN for each card. # is used for spare cards
card_pin = {'0D004B5BBAA7': '1966', '3900E1BC3753': '1966', '3900E24C33A4': '1966', '3900DC2807CA': '1966', '3900E5EB4770': '1966', '3900DC751888': '1966', '3900E5E7172C': '1966', '3900DC75FB6B': '1966', '3900E1BF3453': '1966', '3900DC7760F2': '1966', '3900DC783AA7': '1966', '3900E6685EE9': '1966', '3900E4C66C77': '1966', '3900E4BAFA9D': '1966', '3900E6757FD5': '1966', '3900E4BDD2B2': '1966', '3900E67049E6': '1966', '3900E666873E': '1966', '3900E6765FF6': '1966', '3900E67817B0': '1966', '3900E665A51F': '1966', '1D003D3BDDC6': '1966', '1D003D1E7C42': '1966', '1D0023A7E970': '1966', '1D0023ABEC79': '1966', '1D0023AD5AC9': '1966', '1D0023867DC5': '1966', '1D002388A91F': '1966', '1D0023884CFA': '1966', '1D0026246D72': '1966', '1D00237EADED': '1966', '1D002D679EC9': '1966', '1D002F5A9DF5': 1966}

# This dictionary maps the 3 factor cards only, to a name of the owner
card_name = {'3900E5E7172C': 'Mark', '3900DC75FB6B': 'Dimuthu', '3900E1BF3453': 'Amjad', '3900DC7760F2': 'Lydia', '3900E4C66C77': 'Jawwad', '3900E4BDD2B2': 'Martin', '3900E6765FF6': 'Glen', '1D0023A7E970': 'James', '1D0023867DC5': 'Silvia', '1D0026246D72': 'Unused', '1D002F5A9DF5': 'Unused'}

#Initialize camera
fps=0
fps_pos=(30,60)
fps_font=cv2.FONT_HERSHEY_SIMPLEX
fps_height=1.5
fps_colour=(0,0,255)
fps_weight=3
frame_width=1280
frame_height=720
frame_colour_format="RGB888"
frame_rate=30
small_frame_scale=0.25

# If using a raspberry pi camera on the CSI interface
camera=Picamera2()
camera.preview_configuration.main.size=(frame_width,frame_height)
camera.preview_configuration.main.format=frame_colour_format
camera.preview_configuration.controls.FrameRate=frame_rate
camera.preview_configuration.align()
camera.configure("preview")
camera.start()

#If using a webcam on a USB port. Your camera might be on something other than
#/dev/video0 you can check by running the command 'v4l2-ctl --list-devices
#webCam='/dev/video0'
#camera=cv2.VideoCapture(webcam)
#camera.set(cv2.CAP_PROP_FRAME_WIDTH=frame_width)
#camera.set(cv2.CAP_PROP_FRAME_HEIGHT=frame_height)
#camera.set(cv2.CAP_PROP_FRAME_FPS=frame_rate)


# GPIO PINS
# Beacon is the GPIO pin for the electronic relay to control the 12V flashing beacon
Beacon = 26
# Buzzer is used to control the buzzer on the RFID HAT that beeps when a card is scanned
Buzzer = 17

#Neopixel setup
pixels_num = 56
pixel_ord = neopixel_spi.GRB = 'GRB'
pixel_khz = 3200000
pixel_bits = 3
pixel_brightness = 1
pixel_red = (255, 0, 0)
pixel_green = (0, 255, 0)
pixel_blue = (0, 0, 255)
pixel_off = (0,0,0)

pixels = neopixel_spi.NeoPixel_SPI(
        board.SPI(),
        pixels_num,
        bpp=pixel_bits,
        brightness=pixel_brightness,
        auto_write=False,
        frequency=pixel_khz,
        pixel_order=pixel_ord,
        bit0=0b10000000)

#GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(Buzzer, GPIO.OUT)
GPIO.setup(Beacon, GPIO.OUT)
GPIO.output(Beacon, GPIO.HIGH)

# load the known faces and embeddings along with OpenCV's Haar
# cascade for face detection
encodings_file = "encodings.pickle"
print("[INFO] loading encodings + face detector...")
data = pickle.loads(open(encodings_file, "rb").read())

# load the known faces and embeddings. This file is created using the add_user.py script
#encodings_file = "encodings.pickle"
#system('clear')
#print("[INFO] loading encodings from ", encodings_file, "...")
# Load face encodings
#data = pickle.loads(open(encodings_file, "rb").read())

DIR_PATH = path.abspath(path.dirname(__file__))
DefaultFont = path.join(DIR_PATH, "Fonts/GothamLight.ttf")

draw_red = (0, 0, 255)
draw_green = (0, 255, 0)

# This function reads the 12 character card ID from the RFID HAT reader
def read_rfid():
    ser = serial.Serial("/dev/ttyS0")  # Open named port
    ser.baudrate = 9600  # Set baud rate to 9600
    data = ser.read(12)  # Read 12 characters from serial port to data
    if (data != " "):
        #GPIO.output(Buzzer, GPIO.HIGH)
        sleep(.2)
        #GPIO.output(Buzzer, GPIO.LOW)
        ser.close()  # Close port
        data = data.decode("utf-8")
        return data

def attract_mode(time_seconds, attractmode_stop):
    while not attractmode_stop.is_set():
        time_between_pixels = time_seconds / pixels_num
        for colour in (pixel_red, pixel_green, pixel_blue):
            for i in range(-1, (pixels_num - 1)):
                if not attractmode_stop.is_set():
                    pixels[i + 1] = colour
                    pixels[i - 10] = pixel_off
                    pixels.show()
                    sleep(time_between_pixels)
    pixels.fill(pixel_off)
    pixels.show()

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
    access_image = "ffplay -loglevel quiet -hide_banner -noborder -nostats -autoexit Images/granted.mp4"
    oled.PrintText("Access granted!", FontSize=14)
    pixels.fill(pixel_green)
    pixels.show()
    oled.ShowImage()
    system(access_image)
    pixels.fill(pixel_off)
    pixels.show()
    oled.NoDisplay()

# This function is called when access is denied. It plays a movie of an access denied message and updates the OLED display
def deny_access():
    access_image = "ffplay -loglevel quiet -hide_banner -noborder -nostats -autoexit Images/denied.mp4"
    oled.PrintText("Access denied!", FontSize=14)
    oled.ShowImage()
    GPIO.output(Beacon, GPIO.LOW)
    pixels.fill(pixel_red)
    pixels.show()
    system(access_image)
    GPIO.output(Beacon, GPIO.HIGH)
    pixels.fill(pixel_off)
    pixels.show()
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
    # loop over frames from the video file stream
    print("[INFO] I need to see if you are the person authorised to use this card")
    print("[INFO] Look at the camera and press the <SPACE BAR> when you are ready for me to take your photo.")
    global fps
    global small_frame_scale
    while True:
        # Initialize some variables for each new frame.
        # This ensures that if an authorised person leaves the frame and someone else enters, that access is denied.
        tStart=time.time()
        face_locations = []
        face_encodings = []
        names = []
        currentname = []
        process_this_frame = True
        name = "Unauthorised"
        textname = "Unauthorised"
        drawcolour = draw_red
        # Grab a frame from the camera
        frame = camera.capture_array()
        # Scale the frame down using small_frame_scale to aid recognition performance
        small_frame = cv2.resize(frame, (0, 0), fx=small_frame_scale, fy=small_frame_scale)
        # Detect the face boxes in the small_frame
        face_locations = face_recognition.face_locations(small_frame, model="hog")
        # compute the facial embeddings for each face bounding box
        face_encodings = face_recognition.face_encodings(small_frame, face_locations)
        # loop over the facial embeddings
        for encoding in face_encodings:
            # attempt to match each face in the input image to our known
            # encodings
            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(data["encodings"], face_encoding, tolerance=0.50)

                name = "Unauthorised"
                textname = "Unauthorised"
                drawcolour = draw_red

                # Use the known face with the smallest distance to the new face
                face_distances = face_recognition.face_distance(data["encodings"], face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = data["names"][best_match_index]
                    textname = card_name.get(name)
                    drawcolour = draw_green
                # Scale the box back up to the full size frame for displaying
                top *= int(1/small_frame_scale)
                right *= int(1/small_frame_scale)
                bottom *= int(1/small_frame_scale)
                left *= int(1/small_frame_scale)
                # draw the predicted face name on the image - color is in BGR
                cv2.rectangle(frame, (left, top), (right, bottom), drawcolour, 2)
                y = top - 15 if top - 15 > 15 else top + 15
                cv2.putText(frame, textname, (left, y), cv2.FONT_HERSHEY_SIMPLEX, .8, drawcolour, 2)

        # display the image to our screen
        winname = "Facial Recognition in progress"
        cv2.namedWindow(winname)
        cv2.moveWindow(winname, 40,30)
        cv2.putText(frame, str(int(fps))+'fps',fps_pos,fps_font,fps_height,fps_colour,fps_weight)
        cv2.imshow(winname, frame)
        key = cv2.waitKey(1) & 0xFF

        # quit when 'q' key is pressed
        #if key == ord("q"):
        if key == 32:
            # do a bit of cleanup
            cv2.destroyAllWindows()
            break
        tEnd=time.time()
        loopTime=tEnd-tStart
        fps=.9*fps + .1*(1/loopTime)

    print("[INFO] In the camera I saw the owner of access card : ", textname)
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
        attractmode_stop = Event()
        attractmode = Thread(target = attract_mode, args=(1, attractmode_stop))
        attractmode.start()
        print("[INFO] Ready to scan RFID token")
        card_id = read_rfid()
        attractmode_stop.set()
        # Blue keyfob used to end the program
        if card_id == "020047D742D0": 
            clean_exit()
        else:
            print(f"[INFO] Detected RFID token: {card_id}")
            display_token(card_id)
            this_card_factor = card_factor.get(card_id)
            this_card_pin = card_pin.get(card_id)
            this_card_name = card_name.get(card_id)
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
            oled.PrintText("Scan your card", FontSize=14)
            oled.ShowImage()
camera.stop()
cv2.destroyAllWindows()
