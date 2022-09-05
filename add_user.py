#!/usr/bin/python3
import cv2
import sys
import os
from os import path
sys.path.append('/home/pi/PiFace/includes')
from oled_091 import SSD1306
from time import sleep
import serial
import RPi.GPIO as GPIO
from picamera import PiCamera
from picamera.array import PiRGBArray

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(17,GPIO.OUT)

cam = PiCamera()
cam.resolution = (512, 304)
cam.framerate = 10
rawCapture = PiRGBArray(cam, size=(512, 304))
DIR_PATH = path.abspath(path.dirname(__file__))
DefaultFont = path.join(DIR_PATH, "Fonts/GothamLight.ttf")

class read_rfid:
    def read_rfid (self):
        ser = serial.Serial ("/dev/ttyS0")    #Open named port
        ser.baudrate = 9600                   #Set baud rate to 9600
        data = ser.read(12)                   #Read 12 characters from serial port to data
        if(data != " "):
            GPIO.output(17,GPIO.HIGH)
            sleep(.1)
            GPIO.output(17,GPIO.LOW)
        ser.close ()                          #Close port
        data=data.decode("utf-8")
        return data

def info_print():
    # display.WhiteDisplay()
    display.DirImage(path.join(DIR_PATH, "Images/SB.png"))
    display.DrawRect()
    display.ShowImage()
    sleep(1)
    display.PrintText("Place your TAG", FontSize=14)
    display.ShowImage()

display = SSD1306()
SB = read_rfid()

info_print()
print ("[INFO] Ready to scan RFID token")
id=SB.read_rfid()
print ("[INFO] Detected RFID token: ", id)
display.PrintText("ID : " +(id), cords=(4, 8), FontSize=11)
display.DrawRect()
display.ShowImage()
image_dir = "dataset/"+ id
# If folder doesn't exist, then create it.
if not os.path.isdir(image_dir):
    os.makedirs(image_dir)
    print("[INFO] Created folder : ", image_dir)

else:
    print("[INFO] Folder " + image_dir + " already exists.")


img_counter = 0
while True:
    for frame in cam.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        image = frame.array
        cv2.imshow("Press Space to take a photo", image)
        rawCapture.truncate(0)
    
        k = cv2.waitKey(1)
        rawCapture.truncate(0)
        if k%256 == 27: # ESC pressed
            break
        elif k%256 == 32:
            # SPACE pressed
            img_name = "dataset/"+ id +"/image_{}.jpg".format(img_counter)
            cv2.imwrite(img_name, image)
            print("[INFO] {} written!".format(img_name))
            img_counter += 1
            
    if k%256 == 27:
     print("Escape hit, closing...")
     break

display.NoDisplay()
cv2.destroyAllWindows()
