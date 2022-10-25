#!/usr/bin/env python
import RPi.GPIO as GPIO
import time

LedPin = 26    # pin GPIO26
DotTime = 0.25
DashTime = DotTime * 2
PauseBetweenBeeps = 0.25
PauseBetweenLetters = 0.75

GPIO.setmode(GPIO.BCM)       # Numbers GPIOs by standard marking
GPIO.setup(LedPin, GPIO.OUT)   # Set LedPin's mode is output
GPIO.output(LedPin, GPIO.HIGH) # Set LedPin high(+3.3V) to turn off led

# Spell out "Arianna" on an LED using Morse code

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
        print('pause...')
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

a()
r()
i()
a()
n()
n()
a()
