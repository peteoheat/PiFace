import sys
import sys
sys.path.append('/home/pi/PiFace/includes')
sys.path.append('/home/pi/PiFace/config')
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from oled_091 import SSD1306
from datetime import datetime
from subprocess import check_output
import logging
import time
from time import sleep
import getopt
import picamera
import os
from os import path
import boto3
from botocore.exceptions import ClientError
import json
import serial
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(17,GPIO.OUT)

# AWS S3 properties
bucket_name = 'piface-images'
host = "a2i1eobk06mt4j-ats.iot.eu-west-2.amazonaws.com"
rootCAPath = "/home/pi/PiFace/config/root-CA.crt"
certificatePath = "/home/pi/PiFace/config/PiFace.cert.pem"
privateKeyPath = "/home/pi/PiFace/config/PiFace.private.key"

# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

# Init AWSIoTMQTTClient
myAWSIoTMQTTClient = None

myAWSIoTMQTTClient = AWSIoTMQTTClient("basicPubSub")
myAWSIoTMQTTClient.configureEndpoint(host, 8883)
myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

# photo properties
image_path = "/home/pi/Pictures/PiFace-camera-images/"
image_width = 1280
image_height = 1024
file_extension = '.jpg'

# camera setup
camera = picamera.PiCamera()
camera.resolution = (image_width, image_height)
camera.awb_mode = 'auto'


DIR_PATH = path.abspath(path.dirname(__file__))
DefaultFont = path.join(DIR_PATH, "Fonts/GothamLight.ttf")

class read_rfid:
    def read_rfid (self):
        ser = serial.Serial ("/dev/ttyS0")                           #Open named port 
        ser.baudrate = 9600                                            #Set baud rate to 9600
        data = ser.read(12)                                            #Read 12 characters from serial port to data
        if(data != " "):
            GPIO.output(17,GPIO.HIGH)
            sleep(.2)
            GPIO.output(17,GPIO.LOW)
        ser.close ()                                                   #Close port
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

def uploadToS3(id):
    file_name = image_path + id + file_extension
    s3 = boto3.client('s3')
    f = open(file_name, "rb")
    s3.upload_fileobj(f, bucket_name, id + file_extension)
    print ("Uploaded ", file_name, "to", bucket_name)

def ExistsS3(id):
    file_name = id + file_extension
    s3 = boto3.client('s3')
    try:
        response = s3.head_object(Bucket=bucket_name, Key=file_name)
        print ("File found in S3 : ", response['ContentLength'])
        return True
    except ClientError as e:
        if e.response['ResponseMetadata']['HTTPStatusCode'] == 404:
            print ("File not found in S3 :", file_name)
        return False


def TakePhoto(id):
    file_path = image_path + id + file_extension
    camera.capture(file_path)
    print ("Captured photo to: ", file_path)

# Custom MQTT message callback
def photoVerificationCallback(client, userdata, message):
    print("Received a new message: ")
    data = json.loads(message.payload)
    try:
        similarity = data[1][0]['Similarity']
        print("Received similarity: " + str(similarity))
        if(similarity >= 90):
            print("Access allowed, opening doors.")
            print("Thank you!")
    except:
        pass
    print("Finished processing event.")

# Connect and subscribe to AWS IoT
myAWSIoTMQTTClient.connect()
myAWSIoTMQTTClient.subscribe("rekognition/result", 1, photoVerificationCallback)
time.sleep(2)


display = SSD1306()
SB = read_rfid()

if __name__ == "__main__":
    info_print()
    while True:
        id=SB.read_rfid()
        print ("Detected RFID token: ", id)
        display.PrintText("ID : " +(id), cords=(4, 8), FontSize=11)
        display.DrawRect()
        display.ShowImage()
        TakePhoto(id)
        if ExistsS3(id):
            print ("Photo for this RFID already in S3 so skipping upload")
        else:
            print ("Photo for this RFID not in S3 so uploading")
            uploadToS3(id)
        sleep(2)
        display.PrintText("Place your TAG", FontSize=14)
        display.ShowImage()
        
        
