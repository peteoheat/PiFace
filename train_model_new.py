#! /usr/bin/python3

# import the necessary packages
from imutils import paths
import face_recognition
#import argparse
import pickle
import cv2
import os
import sys
from os import path
sys.path.append('/home/pi/PiFace/includes')
import serial
import RPi.GPIO as GPIO
from oled_091 import SSD1306

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(17,GPIO.out)

class read_rfid:
    def read_rfid(self):
        ser = serial.Serial ("/dev/tty/S0")
        ser.baudrate = 9600
        data = ser.read(12)
        if(data!= " "):
            GPIO.output(17,GPIO.HIGH)
            sleep(.2)
            GPIO.output(17,GPIO.LOW)
        ser.close()
        data=data.decode("utf-8")
        return data

def info_print():
    #display.WhiteDisplay()
    display.DirImage(path.join(DIR_PATH, "Images/SB.png"))
    display.DrawRect()
    display.ShowImage()
    sleep(1)
    display.PrintText("Place your TAG", Fontsize =14)
    display.ShowImage()

display = SSD1306()

info_print()
print ("[INFO Ready to scan RFID token")
card_id=read_rfid()
print ("[INFO] Detected RFID token: ", card_id)

# our images are located in the dataset folder
print("[INFO] start processing faces for this card ID...")
imagePaths = list(paths.list_images("dataset/", card_id))

# initialize the list of known encodings and known names
knownEncodings = []
knownNames = []

# loop over the image paths
for (i, imagePath) in enumerate(imagePaths):
	# extract the person name from the image path
	print("[INFO] processing image {}/{}".format(i + 1,
		len(imagePaths)))
	name = imagePath.split(os.path.sep)[-2]
	print("[INFO] Processing image of: ", name)

	# load the input image and convert it from RGB (OpenCV ordering)
	# to dlib ordering (RGB)
	image = cv2.imread(imagePath)
	rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

	# detect the (x, y)-coordinates of the bounding boxes
	# corresponding to each face in the input image
	boxes = face_recognition.face_locations(rgb,
		model="hog")

	# compute the facial embedding for the face
	encodings = face_recognition.face_encodings(rgb, boxes)

	# loop over the encodings
	for encoding in encodings:
		# add each encoding + name to our set of known names and
		# encodings
		knownEncodings.append(encoding)
		knownNames.append(name)

# dump the facial encodings + names to disk
print("[INFO] serializing encodings...")
data = {"encodings": knownEncodings, "names": knownNames}
f = open("encodings.pickle", "wb")
f.write(pickle.dumps(data))
f.close()
