#!/usr/bin/python3
import cv2
import face_recognition
import time
import pickle
import numpy as np
import os
from picamera2 import Picamera2
from PIL import Image, ImageDraw


#These values are common whether using PiCamera or Webcam
frame_width=640
frame_height=480

# If using a raspberry pi camera on the CSI interface
# Start of picamera specific config. Comment out if using a webcam or other camera.
#camera = Picamera2()
#video_config = camera.create_video_configuration(main={"size": (frame_width, frame_height), "format": "RGB888"})
#camera.configure(video_config)
#camera.start()
#End of pi camera specific setup.

#If using a webcam on a USB port uncomment this section
camera=cv2.VideoCapture('/dev/video0')
camera.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)

#Initialize a few variables
#Number of training images to capture. More images = better training but longer to do.
training_images=50
#These are used for writing frames per second and images captured onto the frame
fps=0
fps_pos=(30,60)
img_count_pos=(30,30)
fps_font=cv2.FONT_HERSHEY_SIMPLEX
fps_height=0.5
fps_colour=(0,255,0)
fps_weight=1
# This are used for the location of the faces
top=0
bottom=0
right=0
left=0
#This is used to store all of the face encodings before writing to pickle file
faces_data=[]
i=0

name=input("Enter Your Name: ")

while True:
    #Loop will stop once we have 50 training images captured
    if len(faces_data)<training_images:
        #Initialzing a counter to generate the frames per second (fps)
        tStart=time.time()
        #camera.read if using USB webcam
        (success, frame)=camera.read()
        #camera.capture_array() if using Picamera
        #frame = camera.capture_array()
        # detect the (x, y, w, h)-coordinates of the bounding boxes
        # corresponding to each face in the input image
        face_boxes = face_recognition.face_locations(frame, model="hog")
        encodings = face_recognition.face_encodings(frame, face_boxes)
        face_landmarks_list = face_recognition.face_landmarks(frame, face_locations=face_boxes)

        #If there are any faces in the captured frame then loop through them and add encodings into faces_data
        for (top, right, bottom, left), face_encoding in zip(face_boxes, encodings):
            i=i+1
            for encoding in encodings:
                faces_data.append(encoding)
            #Draw a rectangle onto the image where the face is.
            cv2.rectangle(frame, (left, top), (right, bottom), (0,255,0), 2)
            
        #Draw the face landmarks onto the image
        pil_image = Image.fromarray(frame)
        d = ImageDraw.Draw(pil_image)
        for face_landmarks in face_landmarks_list:
            # Let's trace out each facial feature in the image with a line!
            for facial_feature in face_landmarks.keys():
                d.line(face_landmarks[facial_feature], width=2)
        #Convert PIL array back to image.
        frame = np.array(pil_image)    
        
        #Display the frame to the screen.
        cv2.putText(frame, 'Training image '+str(len(faces_data))+'/'+str(int(training_images))+' captured',img_count_pos,fps_font,fps_height,fps_colour,fps_weight)
        cv2.putText(frame, str(int(fps))+'fps',fps_pos,fps_font,fps_height,fps_colour,fps_weight)
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF
        # quit when 'q' key is pressed
        #if key == ord("q"):
        if key%256 == 27: # ESC pressed
            break
        tEnd=time.time()
        loopTime=tEnd-tStart
        fps=.9*fps + .1*(1/loopTime)
    else:
        #Once we have 50 training encodings for this face.
        #Comment out camera.stop if using webcam
        #camera.stop()
        cv2.destroyAllWindows()
        for encoding in faces_data:
            print(f"Encoding is {encoding}")
        break
