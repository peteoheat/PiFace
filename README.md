# PiFace
PiFace is a Raspberry Pi facial recognition multi-factor authentication security system built for a STEM education event that I have presented at for the London Science Museum STEM skills fair. It has also been used for several other STEM engagement events.

# Introductory Video
The project is best explained through a demonstration, and that can be found here https://youtu.be/reMThsNkrDE

# Hardware used in this project
1. Raspberry Pi4 4GB https://thepihut.com/products/raspberry-pi-4-model-b?variant=20064052740158
2. Waveshare relay HAT for Raspberry Pi https://thepihut.com/products/raspberry-pi-relay-board
3. SB components RFID HAT https://thepihut.com/products/rfid-hat-for-raspberry-pi
4. AZ-Delivery extra RFID cards (as many as you require) https://www.amazon.co.uk/gp/product/B01MR2CLM7/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1
5. Hawkeye 12V rotating LED beacon https://www.amazon.co.uk/gp/product/B08DXSNYHL/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1
6. Raspberry Pi HQ Camera module https://thepihut.com/products/raspberry-pi-high-quality-camera-module
7. Raspberry Pi Camera lens (the 6mm one) https://thepihut.com/products/raspberry-pi-high-quality-camera-lens

# Software used.
This  iteration of PiFace uses Dlib, the face-recognition project from Adam Geitgey and OpenCV In addition to this, you will need 
1. An image to display as the desktop background that in my video looks like the bank vault in it's closed state.
2. A video to be played for the 'Access Denied'
3. A video to be played for the 'Access Granted'.
All of the videos in my project were licensed from Pond5 specifically for my project. I therefore, cannot distribute them with the code for the project.
I licensed 3 different videos and then edited them together to get the desired results. I also had to add the siren sound to the 'access denied' video using a video editor.

# Installation
Setup a fresh SD card with Raspbian bullseye desktop 64bit. These instructions do not detail how to do that, I assume you know already.

# Update the raspberry pi
sudo apt update
sudo apt upgrade -y

#Enable I2C and SPI
sudo raspi-config
'Interface Options'-> 'SPI' -> 'Yes'
'Interface Options' -> I2C -> 'Yes'
exit
reboot

# Install HAT dependencies
## Waveshare Relay HAT
sudo pip install RPi.GPIO

## SB Components RFID HAT
For Pinouts look here https://github.com/sbcshop/SB-RFID-HAT
sudo raspi-config and enable SPI and I2C
sudo pip install smbus2
sudo apt-get install i2c-tools

To verify the list of connected device on I2C interface, you can run below commond :
sudo i2cdetect -y 1

# Download this project
cd /home/pi
git clone https://github.com/peteoheat/PiFace

# install RFID required libraries and examples
git clone https://github.com/sbcshop/SB-RFID-HAT.git
cd SB-RFID-HAT
You can test the RFID reader with either of the following
Without Oled display, output on terminal/shell
python rfid.py
or
To show detected tag id on Oled as well as on terminal/shell
python rfid_with_oled.py
Now copy the required files from SB-RFID-HAT into the PiFace home directory
mkdir /home/pi/PiFace/includes
Copy the RFID OLED display driver into the /home/pi/PiFace/includes directory
cp oled_091.py /home/pi/PiFace/includes
cp oled_091.py /home/pi/PiFace/
Copy the screen fonts for the RFID OLED display into a new /home/Pi/PiFace/Fonts directory
find Fonts -print | cpio -pdumv /home/pi/PiFace
The SB-RFID-HAT directory can now be removed unless you want to keep the example files around.

#PiFace uses dlib, OpenCV, Image Utils and face-recognition. Here's how to install those
This section of configuration changes should all be changed back to the original settings once dlib and OpenCV are compiled
## dlib
A good source of instructions is https://pyimagesearch.com/2017/05/01/install-dlib-raspberry-pi/
But here are mine:
# We need to increase the swap size just whilst we get things compiled.
Edit /etc/dphys-swapfile
Change CONF_SWAPSIZE=100 to CONF_SWAPSIZE=2048
sudo /etc/init.d/dphys-swapfile stop
sudo /etc/init.d/dphys-swapfile start
Confirm swap increase
free -m
If you have a Raspberry Pi with a low amount of memory (1GB or 2GB), you can help the dlib compile speed by disabling
PIXEL desktop from starting on boot, and compile from the command line. I have not found this necessary on the 4GB. To do this sudo raspi-config and then
Boot Options => Desktop / CLI => Console Autologin
Advanced Options => Memory Split and change this from 64MB to 16MB so that less memory is assigned to the GPU on boot
Exit rasp-config and reboot.

## Install dlib pre-requisites
sudo apt-get install build-essential cmake
sudo apt-get install libgtk-3-dev
sudo apt-get install libboost-all-dev
sudo pip install numpy
sudo pip install scipy
sudo pip install scikit-image

## Install dlib with python bindings
sudo pip install dlib
On a Raspberry Pi4 with 4GB of memory and Bullseye 64bit OS, the compile took me 27mins. So go and make a coffee or something

## Install OpenCV 4.8. 
This method compiles OpenCV on the pi rather than installing with pip or apt. It means you can ensure you have the
latest version and the most flexible install but be aware that it is by far the slowest. I didn't time exactly, but I think it took about an hour and 10 mins.
I used this method because I wanted version 4.8.0 which has integration with Tensorflow lite models that wasn't available using pip or apt.
PiFace version 1 doesn't use Tensorflow, but I want to have a play with it for possible use in later versions or other projects.

Before doing the install, if not done previously we need to increase the SWAP so that we have at least 6GB of available total memory.
On a 4GB raspberry Pi, we increase SWAP to 2048. You can adjust based on how much physical memory your Pi has.
Also need to change the GPU settings as we did previously, but this time revise it up to at least 128MB and reboot.

wget https://github.com/Qengineering/Install-OpenCV-Raspberry-Pi-64-bits/raw/main/OpenCV-4-8-0.sh
sudo chmod 755 ./OpenCV-4-8-0.sh
./OpenCV-4-8-0.sh

## Test the OpenCV installation
python
>>> import cv2
>>> print( cv2.getBuildInformation() )

That should display a detailed page about your OpenCV installation

## Now we can backout the change we made to /etc/dphys-swapfile
vi /etc/dphys-swapfile and change the line CONF_SWAPSIZE=2048 back to CONF_SWAPSIZE=100
sudo /etc/init.d/dphys-swapfile stop
sudo /etc/init.d/dphys-swapfile start
## Confirm swap decrease with
free -m

## Re-enable the desktop and increase the memory allocated to the GPU. I made the memory more than the default to try to improve frames per second for image processing
sudo raspi-config
Boot Options => Desktop / CLI => Console Autologin 
Advanced Options => Memory Split and change this from 16MB to 256MB.

# Final setup
##Raspberry desktop
So the static screen of the closed bank vault is a bit of a trick. All you are really looking at is the desktop background at this stage. To achieve this I did the following
* Capture a single image from the bank vault video you purchased, then set this as your desktop background.
* Set the taskbar to auto-hide
* Remove the wastebacket icon from the desktop.
You should now have a complete clear desktop showing an image of the bankvault.

##Setting up PiFace
###Add 'authorised' bank staff.

####Capture images for each card/person pair
There are a few steps to this process.
1. Capture images of the authorised person that are associated to their individual access card. We do this using the add_user.py python script. Run it in a terminal window and it will ask you to scan a card.
Scan an unused access card and it will then launch a camera capture window. Have the individual look at the camera and press <SPACE> to capture their image. 
Then repeat this with their face in slightly different orientations somewhere between 30-50 times to make a decent set of training data. Then press <esc> to complete the process for this person.
2. Repeat step (1) with as many authorised people as you need. But remember, the more people you have the slower the recognition will be.
The images will all be stored under PiFace/data/<card number>

####Train the facial recognition model to recognise the authorised faces.
1. Run train_model.py and wait. This process can take a while based on how many images there are. This could be enhanced in the future by making it multi-threaded and by making it only adding any changes rather than processing every image.
train_the model proccesses all of the files under PiFace/dataset/<card number>. It finds faces within the images and creates an encoding of them using the HOG model. All of the encodings are then added to the file encodings.pickle.

You should now be ready to run PiFace.py

