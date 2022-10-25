#!/usr/bin/env python
# -----------------
# Modified 2018-09-30 to use Matt Hawkins' LCD library for I2C available
# from https://bitbucket.org/MattHawkinsUK/rpispy-misc/raw/master/python/lcd_i2c.py
#
import RPi.GPIO as GPIO
import time

# Additional stuff for LCD
import smbus

LedPin = 26    # our LED is on GPIO17

# Ultrasonic sensor pin assignments
SR04_trigger_pin = 20  # GPIO20
SR04_echo_pin = 21  # GPIO21

#LCD pin assignments, constants, etc
I2C_ADDR  = 0x27 # I2C device address
LCD_WIDTH = 16   # Maximum characters per line

# Define some device constants
LCD_CHR = 1 # Mode - Sending data
LCD_CMD = 0 # Mode - Sending command

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
LCD_LINE_3 = 0x94 # LCD RAM address for the 3rd line
LCD_LINE_4 = 0xD4 # LCD RAM address for the 4th line

LCD_BACKLIGHT  = 0x08  # On
#LCD_BACKLIGHT = 0x00  # Off

ENABLE = 0b00000100 # Enable it

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

# LCD commands
LCD_CMD_4BIT_MODE = 0x28   # 4 bit mode, 2 lines, 5x8 font
LCD_CMD_CLEAR = 0x01
LCD_CMD_HOME = 0x02   # goes to position 0 in line 0
LCD_CMD_POSITION = 0x80  # Add this to DDRAM address

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)       # Numbers GPIOs by standard marking
GPIO.setup(LedPin, GPIO.OUT)   # Set LedPin's mode is output
GPIO.output(LedPin, GPIO.HIGH) # Set LedPin high(+3.3V) to turn off led

# Set up the SR04 pins
setup_trig = GPIO.setup(SR04_trigger_pin, GPIO.OUT)
setup_echo = GPIO.setup(SR04_echo_pin, GPIO.IN)
GPIO.output(SR04_trigger_pin, GPIO.LOW)

#Open I2C interface
#bus = smbus.SMBus(0)  # Rev 1 Pi uses 0
bus = smbus.SMBus(1) # Rev 2 Pi uses 1

def distance(metric):
        try:
                # set Trigger to HIGH
                GPIO.output(SR04_trigger_pin, GPIO.HIGH)

                # set Trigger after 0.01ms to LOW
                time.sleep(0.00001)
                GPIO.output(SR04_trigger_pin, GPIO.LOW)
                
                startTime = time.time()
                stopTime = time.time()

                # Get the returnb pulse start time
                while 0 == GPIO.input(SR04_echo_pin):
                        startTime = time.time()
                
                # Get the pulse length
                while 1 == GPIO.input(SR04_echo_pin):
                        stopTime = time.time()
                
                elapsedTime = stopTime - startTime
                # The speed of sound is 33120 cm/S or 13039.37 inch/sec.
                # Divide by 2 since this is a round trip
                if (1 == metric):
                        d = (elapsedTime * 33120.0) / 2   # metric
                else:
                        d = (elapsedTime * 13039.37) / 2   # english
                
                return d
        except:
                print("Sensor Connection Error")

def lcd_init():
        # Initialise display
        lcd_byte(0x33,LCD_CMD) # 110011 Initialise
        lcd_byte(0x32,LCD_CMD) # 110010 Initialise
        lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
        lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off 
        lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
        lcd_byte(0x01,LCD_CMD) # 000001 Clear display
        time.sleep(E_DELAY)

def lcd_byte(bits, mode):
        # Send byte to data pins
        # bits = the data
        # mode = 1 for data
        #        0 for command

        bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
        bits_low = mode | ((bits<<4) & 0xF0) | LCD_BACKLIGHT

        # High bits
        bus.write_byte(I2C_ADDR, bits_high)
        lcd_toggle_enable(bits_high)

        # Low bits
        bus.write_byte(I2C_ADDR, bits_low)
        lcd_toggle_enable(bits_low)

def lcd_toggle_enable(bits):
        # Toggle enable
        time.sleep(E_DELAY)
        bus.write_byte(I2C_ADDR, (bits | ENABLE))
        time.sleep(E_PULSE)
        bus.write_byte(I2C_ADDR,(bits & ~ENABLE))
        time.sleep(E_DELAY)

def lcd_string(message,line):
        # Send string to display

        message = message.ljust(LCD_WIDTH," ")

        lcd_byte(line, LCD_CMD)

        for i in range(LCD_WIDTH):
                lcd_byte(ord(message[i]),LCD_CHR)

# functions not in the original library
#--------------------------------------
# Positions the cursor so that the next write to the LCD
# appears at a specific row & column, 0-org'd
# Updated for 4-line displays 2/14/20
def lcd_xy(col, row):
        lcd_byte(LCD_CMD_POSITION+col+(64*row)-(108*(row > 1)), LCD_CMD)

# Begins writing a string to the LCD at the current cursor
# position. It doesn't concern itself with whether the cursor
# is visible or not. Go off the screen? Your bad.
def lcd_msg(msg_string):
        for i in range(0, len(msg_string)):
                lcd_byte(ord(msg_string[i]), LCD_CHR)

# initialize display and previous values
lcd_init()
previous_distance = 10
previous_time = time.time() - 1

nextDist = time.time() - 1   # force an immediate update
while True:
        if time.time() > nextDist:
                current_distance = int(100 * distance(False)) / 100
                distance_traveled = current_distance - previous_distance        # calculate distance traveled
                current_time = time.time()
                velocity = distance_traveled / (current_time - previous_time)   # calculate velocity
                safe_distance = abs(velocity) * 2       # calculate safe distance
                # if the car is farther away from an object than the safe distance
                if current_distance > safe_distance:
                        lcd_string("Driving...", LCD_LINE_1)
                        GPIO.output(LedPin, GPIO.HIGH)    # keep brake off
                else:
                        lcd_string("Car Stopped", LCD_LINE_1)
                        GPIO.output(LedPin, GPIO.LOW)    # turn on brake
                        time.sleep(1)
                message = str(current_distance) + " in."
                # formatting for distance
                if current_distance < 100:
                        message = " " + message
                if current_distance < 10:
                        message = " " + message
                message = message + "            "
                message = message[0:12]

                # print distance from object
                lcd_xy(0, 1)
                lcd_msg(message)
                nextDist = time.time() + 0.1  # 10 times per second

                # set current distance and time as previous for later subtraction
                previous_distance = current_distance
                previous_time = current_time
