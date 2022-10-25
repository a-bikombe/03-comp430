#!/usr/bin/env python
import RPi.GPIO as GPIO
import time

LedPin = 26    # GPIO pin 26
ButtonPin = 21
StartButtonPin = 16    # button for starting reading of pattern

ButtonDown = 0
ButtonUp = 1
PatternReading = False

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)       # Numbers GPIOs by standard marking
GPIO.setup(LedPin, GPIO.OUT)   # Set LedPin's mode is output
GPIO.output(LedPin, GPIO.HIGH) # Set LedPin high(+3.3V) to turn off led
# Set ButtonPin's mode as input with the internal pullup 
GPIO.setup(ButtonPin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
# Set StartButtonPin's mode as input with the internal pullup 
GPIO.setup(StartButtonPin, GPIO.IN, pull_up_down = GPIO.PUD_UP)

print("Press the gray button to start.")

while (ButtonUp == GPIO.input(StartButtonPin)):    # while button is up
    pass
time.sleep(0.2)    # debounce switch
while (ButtonDown == GPIO.input(StartButtonPin)):    # while button is down
    pass
time.sleep(0.2)    # debounce switch


# presses start button
PatternReading = True
timelist = []
start_time = 0
stop_time = 0

print("Press the yellow button 10 times to record your pattern.")
    
while (PatternReading == True):

    for count in range(0, 10):
        item = count + 1
        
        while (ButtonUp == GPIO.input(ButtonPin)):    # wait for pattern button to be pressed
            pass
        time.sleep(0.2)    # debounce switch

        GPIO.output(LedPin, GPIO.LOW)    # led on
        start_time = time.time()    # gets time led was turned on
        print("Pattern Item #", item, ". Pressing down...")
        
        while (ButtonDown == GPIO.input(ButtonPin)):    # presses pattern button
            pass
        time.sleep(0.2)    # debounce switch

        GPIO.output(LedPin, GPIO.HIGH)    # led off
        stop_time = time.time()    # gets time led was turned off
        
        led_duration = stop_time - start_time    # gets led-on duration led was on
        
        timelist.append(led_duration)    # adds duration of led-on to timelist
        print("You pressed down for ", led_duration, " seconds.")

    PatternReading = False
    
print("Goodbye. Your pattern is ", timelist, ". Your light will begin to blink now.")

for count in range(len(timelist)):  # loops through timelist of durations
    GPIO.output(LedPin, GPIO.LOW)    # led on
    time.sleep(timelist[count])  # led is held in on position for the duration in the timelist
    GPIO.output(LedPin, GPIO.HIGH)    # led off
    time.sleep(0.3)    # pause for 0.3 seconds between each blink