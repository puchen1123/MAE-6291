import cv2
import os
import time
import numpy as np
import datetime
import RPi.GPIO as GPIO
from picamera2.picamera2 import Picamera2, Preview


sample_root = "/home/pi/object_samples"
match_threshold = 13
match_quality_threshold = 47
camera_resolution = (800,600)


today = datetime.datetime.now().weekday()  
enable_extra_folder = (today == 2)  # Wed


GPIO.setmode(GPIO.BOARD)

PIR = 11
GREEN_LED = 12
RED_LED = 13

GPIO.setup(PIR, GPIO.IN)
GPIO.setup(GREEN_LED, GPIO.OUT)
GPIO.setup(RED_LED, GPIO.OUT)
GPIO.output(GREEN_LED, GPIO.LOW)
GPIO.output(RED_LED, GPIO.LOW)


orb = cv2.ORB_create(nfeatures=1000)
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)


sample_features = []
for root, dirs, files in os.walk(sample_root):
    folder_name = os.path.relpath(root, sample_root)
    if folder_name == "Speaker" and not enable_extra_folder:
        continue
    for fname in files:
        if fname.lower().endswith(".jpg"):
            path = os.path.join(root, fname)
            rel_path = os.path.relpath(path, sample_root)
            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            kp, des = orb.detectAndCompute(img, None)
            if des is not None:
                sample_features.append((kp, des, rel_path))



picam2 = Picamera2()
config = picam2.create_still_configuration(main={"size": camera_resolution, "format": "RGB888"})
picam2.configure(config)
picam2.start()
time.sleep(2)


print("waiting PIR sensor...")

try:
    while True:
        if GPIO.input(PIR):
            print("start detective")
            frame = picam2.capture_array()
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            kp2, des2 = orb.detectAndCompute(gray, None)

            detected_items = []

            if des2 is not None:
                for kp1, des1, rel_path in sample_features:
                    matches = bf.match(des1, des2)
                    if len(matches) > match_threshold:
                        avg_dist = np.mean([m.distance for m in matches])
                        if avg_dist < match_quality_threshold:
                            detected_items.append(rel_path)

            if detected_items:
                print("You forget：")
                for item in detected_items:
                    print("  -", item)
                GPIO.output(RED_LED, GPIO.HIGH)
                GPIO.output(GREEN_LED, GPIO.LOW)
            else:
                print("You got everything you need!")
                GPIO.output(GREEN_LED, GPIO.HIGH)
                GPIO.output(RED_LED, GPIO.LOW)
                
            cv2.imshow("now", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            time.sleep(2)
        else:
            time.sleep(0.1)
            
        

        

except KeyboardInterrupt:
    print("end")

finally:
    picam2.stop()
    cv2.destroyAllWindows()
    GPIO.cleanup()
    print("end")

  