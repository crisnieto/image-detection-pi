import RPi.GPIO as GPIO  # Import Raspberry Pi GPIO library
import time
import requests
import os
from picamera import PiCamera
from playsound import playsound


camera = PiCamera()

GPIO.setwarnings(False)  # Ignore warning for now
GPIO.setmode(GPIO.BOARD)  # Use physical pin numbering
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


image_path = '/home/pi/selfie.png'

while(True):
    if GPIO.input(10) == GPIO.HIGH:
        print("Button was pushed!")
        time.sleep(1)
        camera.capture(image_path)
        camera.close()
        image_filename = os.path.basename(image_path)
        print(image_filename)
        multipart_form_data = {
            'upload': (image_filename, open(image_path, 'rb')),
        }
        response = requests.post('http://ec2-18-218-255-55.us-east-2.compute.amazonaws.com:8080/api/v1/upload',
                                 files=multipart_form_data)
        print(response.status_code)
        print(response.json())
        os.remove(image_path)
        s3file = response.json()['file'] + '.mp3'
        s3path = "http://ec2-18-218-255-55.us-east-2.compute.amazonaws.com:8080/api/v1/download/" + s3file
        print("Searching for: " + s3file)
        r = requests.get(
            s3path, allow_redirects=True)
        open('/home/pi/translate.mp3', 'wb').write(r.content)
        bashCommand = "mplayer -noconsolecontrols translate.mp3"
        import subprocess
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        os.remove("translate.mp3")
