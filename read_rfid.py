#!/usr/bin/python3
import sys
import os
from os import path
sys.path.append('/home/pi/PiFace/includes')
from oled_091 import SSD1306
from time import sleep
import serial
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(17,GPIO.OUT)

DefaultFont = "./Fonts/GothamLight.ttf"

def read_rfid ():
    ser = serial.Serial ("/dev/ttyS0")                           #Open named port 
    ser.baudrate = 9600                                            #Set baud rate to 9600
    data = ser.read(12)                                            #Read 12 characters from serial port to data
    if(data != " "):
     GPIO.output(17,GPIO.HIGH)
     sleep(.1)
     GPIO.output(17,GPIO.LOW)
     ser.close ()                                                   #Close port
     data=data.decode("utf-8")
    return data

def info_print():
    display.PrintText("Place your TAG", FontSize=14)
    display.ShowImage()

display = SSD1306()
cardlist=[]
while True:
    try:
        info_print()
        id = read_rfid()
        display.PrintText("ID : " +(id), cords=(4, 8), FontSize=11)
        cardlist.append(id)
        display.DrawRect()
        display.ShowImage()
        display.NoDisplay()
    except KeyboardInterrupt:
        print (cardlist)
        exit()
