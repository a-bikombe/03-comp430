#!/usr/bin/env python
import RPi.GPIO as GPIO
import time

# on an "on" press of the button, spell out my first name using morse code. on an "off" press, spell out last name

ButtonPin = 21
LedPin = 26

DotTime = 0.15
DashTime = DotTime * 2
PauseBetweenBeeps = 0.15
PauseBetweenLetters = 0.4

LED_was_on = False

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)       # Numbers GPIOs by standard marking
GPIO.setup(LedPin, GPIO.OUT)
GPIO.output(LedPin, GPIO.HIGH)
# Set ButtonPin's mode as input with the internal pullup 
GPIO.setup(ButtonPin, GPIO.IN, pull_up_down = GPIO.PUD_UP)

def beepPause():
        GPIO.output(LedPin, GPIO.HIGH) # pause between beeps
        time.sleep(PauseBetweenBeeps)

def dot():
        GPIO.output(LedPin, GPIO.LOW)  # dot
        time.sleep(DotTime)
        beepPause()

def dash():
        GPIO.output(LedPin, GPIO.LOW)  # dash
        time.sleep(DashTime)
        beepPause()

def letterPause():
        GPIO.output(LedPin, GPIO.HIGH) # pause between letters
        time.sleep(PauseBetweenLetters)

def a(): 
        # A
        print('A')
        dot()
        dash()
        letterPause()

def r(): 
        # R
        print('R')
        dot()
        dash()
        dot()
        letterPause()

def i():
        # I
        print('I')
        dot()
        dot()
        letterPause()


def n():
        # N
        print('N')
        dash()
        dot()
        letterPause()

def b():
        # B
        print('B')
        dash()
        dot()
        dot()
        dot()
        letterPause()

def k():
        # K
        print('K')
        dash()
        dot()
        dash()
        letterPause()

def o():
        # O
        print('O')
        dash()
        dash()
        dash()
        letterPause()

def m():
        # M
        print('M')
        dash()
        dash()
        letterPause()

def e():
        # E
        print('E')
        dot()
        letterPause()



while True:
        if (GPIO.input(ButtonPin) == 0):        # button down
                if (LED_was_on == False):       # led was off
                        a()
                        r()
                        i()
                        a()
                        n()
                        n()
                        a()
                        GPIO.output(LedPin, GPIO.LOW)  # led on
                        print('led on')
                        LED_was_on = True       # turned led on
                else:       # led was on
                        b()
                        i()
                        k()
                        o()
                        m()
                        b()
                        e()
                        GPIO.output(LedPin, GPIO.HIGH)  # led off
                        print('led off')
                        LED_was_on = False      # turned led off
                time.sleep(0.2) # delays execution to avoid switch bouncing
                while (GPIO.input(ButtonPin) == 0):     # hold toggle while the button is pressed down
                        pass
                
