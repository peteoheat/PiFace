import time
import RPi.GPIO as GPIO
from keypad import keypad
 
GPIO.setwarnings(False)
 
if __name__ == '__main__':
    # Initialize
    kp = keypad(columnCount = 4)
 
    # waiting for a keypress
    #digit = None
    #while digit == None:
    #    digit = kp.getKey()
        # Print result
    #print (digit)
    #time.sleep(0.5)
 
    ###### 4 Digit wait ######
    seq = []
    print ('Enter 4 digit access code: ')
    for i in range(4):
        digit = None
        while digit == None:
            digit = kp.getKey()
        seq.append(digit)
        time.sleep(0.4)
        print (digit)
 
    # Check digit code
    if seq == [1, 2, 3, '#']:
        print ("Code accepted")
