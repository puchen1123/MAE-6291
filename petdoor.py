import RPi.GPIO as GPIO
import time
import smtplib
from email.message import EmailMessage
import ssl
from time import asctime

#GPIO setup
GPIO.setmode(GPIO.BOARD)

PIR = 11       
GREEN_LED = 12
RED_LED = 13
COUNT = 0
LED_on = False
GREEN_offtime = 0
RED_offtime = 0
RED_on = False

GPIO.setup(PIR, GPIO.IN)
GPIO.setup(GREEN_LED, GPIO.OUT)
GPIO.setup(RED_LED, GPIO.OUT)
GPIO.output(GREEN_LED, GPIO.LOW)
GPIO.output(RED_LED, GPIO.LOW)

#email setup
email_sender = "puchen1123@gmail.com"
email_password = "hfsu kggg kgkd yody"
email_receiver = ["puchen.wang@gwmail.gwu.edu"]

def send_email(trigger_count):
    """ Sends an email notification when pet door is triggered """
    try:
        current_timestamp = str(asctime())
        msg = EmailMessage()
        msg['From'] = email_sender
        msg['To'] = email_receiver
        msg['Subject'] = "Pet Door Activity Alert"

        header = f"Pet door activity detcted on {current_timestamp}\n"
        text = f"""
        Dear User, \n
        The pet door has been triggered {trigger_count} times.
        """

        msg.set_content(header + text)
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.sendmail(email_sender, email_receiver, msg.as_string())

    except Exception as e:
        print(f"Failed to send email: {e}")

try:
    print("Initializing system...Please wait 30 seconds...")
    time.sleep(30)
    print("System is now active. Press Ctrl+C to stop")
    last_state = False

    while True:
        current_state = GPIO.input(PIR)
        current_time = time.time()

        if current_state and not last_state and not (LED_on or RED_on):  # Avoid duplicate triggers
            COUNT += 1
            GPIO.output(GREEN_LED, GPIO.HIGH)
            LED_on = True
            GREEN_offtime = current_time + 5
            print(f"[{time.strftime('%H:%M:%S')}] Trigger event #{COUNT}")
            send_email(COUNT)

        if LED_on and current_time >= GREEN_offtime:
            RED_on = True
            LED_on = False
            GPIO.output(GREEN_LED, GPIO.LOW)
            GPIO.output(RED_LED, GPIO.HIGH)
            RED_offtime = current_time + 5

        if RED_on and current_time >= RED_offtime:
            RED_on = False
            GPIO.output(RED_LED, GPIO.LOW)
            
        last_state = current_state
        time.sleep(0.1)  

except KeyboardInterrupt:
    print(f"\nMonitoring stopped. Total triggers: {COUNT}")
    GPIO.cleanup()

