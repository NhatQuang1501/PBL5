from gpiozero import Button, LED
from signal import pause
import subprocess
from time import sleep
import threading

BUTTON_PIN = 26
LED_PIN = 17
PRESS_DURATION = 3

def run_test_script():
    subprocess.run(['/home/pi/Desktop/PBL5/myenv/bin/python', '/home/pi/Desktop/PBL5/thuAm_btn.py'])

def turn_on_led_after_delay():
    sleep(PRESS_DURATION)
    led.on()
    sleep(7)
    led.off()
    sleep(3)
    #Blink
    for i in range(10):
        led.on()
        sleep(0.3)
        led.off()
        sleep(0.3)
    

def button_pressed():
    print("Button pressed!")
    led.off()  
    led.on()
    sleep(1)
    led.off()  

    test_script_thread = threading.Thread(target=run_test_script)
    test_script_thread.start()

    led_thread = threading.Thread(target=turn_on_led_after_delay)
    led_thread.start()

button = Button(BUTTON_PIN, pull_up=True)
button.when_pressed = button_pressed

led = LED(LED_PIN)
led.off() 

print("Ready")
pause()
