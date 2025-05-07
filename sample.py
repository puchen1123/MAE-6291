import time
import os
from datetime import datetime
from picamera2.picamera2 import Picamera2, Preview
import cv2


sample_dir = "/home/pi/object_samples"
if not os.path.exists(sample_dir):
    os.makedirs(sample_dir)


picam2 = Picamera2()


picam2.start_preview(Preview.QT)
picam2.start()

print("CD")
time.sleep(8)


num_samples = 5
interval = 5                                                                                                                                     

for i in range(num_samples):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(sample_dir, f"sample_{timestamp}_{i+1}.jpg")


    frame = picam2.capture_array()
    cv2.imwrite(filename, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
    print(f"saved as: {filename}")
    time.sleep(interval)


picam2.stop_preview()
picam2.stop()

print("end")
