
import numpy as np
import cv2
import time
import RPi.GPIO as GPIO
import picamera
import thread
import glob
import os
from picamera.array import PiRGBArray

GPIO.setmode(GPIO.BCM)
GPIO.setup(22, GPIO.IN)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(27, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)
p = GPIO.PWM(18, 3200)

global frame
global activation_flag
global condition

condition = 1
camera = picamera.PiCamera()
camera.resolution = (640, 480)
camera.framerate = 10
rawCapture = PiRGBArray(camera, size = (640, 480))
fourcc = cv2.cv.CV_FOURCC(*'XVID')
out = cv2.VideoWriter('output.avi' , fourcc, 10.0, (640, 480))
feature_params = dict(maxCorners=100,
                      qualityLevel=0.3,
                      minDistance=7,
                      blockSize=20)


def analyze_activation_flag(prev_flag, new_activation_flag):
    weight = 0
    for i in prev_flag:
        if i == 1:
            original_point = new_activation_flag[i]
            first_bottom = new_activation_flag[i+10]
            second_bottom = new_activation_flag[i+20]
            third_bottom = new_activation_flag[i+30]
            if original_point == 1:
                weight = weight + 0.4
            if first_bottom == 1:
                weight = weight + 0.5
            if second_bottom == 1:
                weight = weight + 0.3
            if third_bottom == 1:
                weight = weight + 0.1
    return weight

def vibrate():
    GPIO.output(17, False)

def led():
    GPIO.output(27, False)
    
##def sound():
##    while 1:
##        #print condition
##        if condition: 
##            p.start(95)
##        else:
##            p.stop()
        
def analyze_camera(frame):
    frame = cv2.resize(frame, (640, 480))
    h,w,_ = frame.shape
    frame = frame[h/2:h, 8/w:7*w/8]

    
    ks = 10
    x_each = w / ks
    y_each = h / ks
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    corners = cv2.goodFeaturesToTrack(gray, 25, 0.01, 10)
    try:
        corners = np.int0(corners)
    except TypeError:
        corners = []
    
    
    slot = [[],[],[],[],[],[],[],[],[],[],
            [],[],[],[],[],[],[],[],[],[],
            [],[],[],[],[],[],[],[],[],[],
            [],[],[],[],[],[],[],[],[],[],
            [],[],[],[],[],[],[],[],[],[],
            [],[],[],[],[],[],[],[],[],[],
            [],[],[],[],[],[],[],[],[],[],
            [],[],[],[],[],[],[],[],[],[],
            [],[],[],[],[],[],[],[],[],[],
            [],[],[],[],[],[],[],[],[],[]]


    for point in corners:
        for x in range(0, ks):
            for y in range(0, ks):
                if x_each*x <= point[0][0] <= x_each * (x+1):
                    if y_each*y <= point[0][1] <= y_each * (y+1):
                        slot[x*ks+y].extend([[point[0][0],point[0][1]]])

    for i in range(0, ks*ks):
        length = len(slot[i])
        if length == 0:
            continue
        avg_x = 0
        avg_y = 0
        for j in range(0, length):
            avg_x = avg_x + slot[i][j][0]
            avg_y = avg_y + slot[i][j][1]
        avg_x = int(avg_x / length)
        avg_y = int(avg_y / length)

    activation_flag = [0] * 100
    for x in range(0, ks):
        for y in range(0, ks):
            region_number = x*ks + y
            cnt = len(slot[x*ks+y])
            x1 = x_each*x
            y1 = y_each*y
            if cnt > 2:
                activation_flag[region_number] = 1
    
    cv2.waitKey(1)
    return activation_flag

def record():
    dir = "/home/pi/Desktop/ABCDVideos/" #base video directory
    x = sorted(glob.glob(dir+"*")) # Create list of all files in base directory
    #Create a new folder if none exist.
    if not x:
        newdir = dir + "1"
    #Otherwise increment the last folder name and create a new one
    else:
        num = int(x[-1][-1]) + 1
        newdir = dir + str(num)
    #Create new directory
    os.mkdir(newdir)
    i = 1
    while True:
        #out.write(frame)
        camera.start_recording(newdir + "/" + str(i) + ".h264")
        camera.wait_recording(30)
        camera.stop_recording()
        i += 1

# Thread for Detection
def detection():
    while True:
        activation_flag = [0] * 100
        activation_flag = analyze_camera(frame)
        ir_value = GPIO.input(22)
        global condition
              
        if ir_value:
            #print "Danger"
            vibrate()
            p.start(5)
            #condition = 1
            new_activation_flag = analyze_camera(frame)
            weight = analyze_activation_flag(activation_flag, new_activation_flag)
            if weight > 0.3:
                led() 
        else:
            #new_activation_flag = analyze_camera(frame)
            #print "All Clear"
            GPIO.output(27, True)
            #condition = 0
            p.stop()
            GPIO.output(17, True)
            continue
        
        
started = 0        

#Create Threads
def runThreads():
    print "Start Record"
    thread.start_new_thread(record, ())
    print "Start detection"
    thread.start_new_thread(detection, ())
#   thread.start_new_thread(sound, ())

for capture in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    frame = capture.array
    rawCapture.truncate(0)
    if not started :
        runThreads()
    started = 1


    
GPIO.cleanup()
camera.release()
time.sleep(0.1)
cv2.destroyAllWindows()
out.release()
