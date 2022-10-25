#!/usr/bin/env python
import RPi.GPIO as GPIO
import datetime
import time
import urllib.request

# Additional stuff for LCD
import smbus

ALWAYS_USE_THE_FILE = False

LedPin = 26    # pin GPIO26
BlinkSpeed = 0.5

# https://www.campbellsci.com/blog/easily-parse-data-from-trusted-source
# http://w1.weather.gov/xml/current_obs/
# http://w1.weather.gov/xml/current_obs/KMHT.xml

#LCD pin assignments, constants, etc
I2C_ADDR  = 0x27 # I2C device address
LCD_WIDTH = 16   # Maximum characters per line

# Define some device constants
LCD_CHR = 1 # Mode - Sending data
LCD_CMD = 0 # Mode - Sending command

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
LCD_LINE_3 = 0x94 # LCD RAM address for the 3rd line (ignore)
LCD_LINE_4 = 0xD4 # LCD RAM address for the 4th line (ignore)

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

#Open I2C interface
#bus = smbus.SMBus(0)  # Rev 1 Pi uses 0
bus = smbus.SMBus(1) # Rev 2 Pi uses 1

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
# -------------------------------------

# Positions the cursor so that the next write to the LCD
# appears at a specific row & column, 0-org'd
# Updated for 4-line displays 2/14/20
def lcd_xy(col, row):
        lcd_byte(LCD_CMD_POSITION+col+(64*row)-(0x6c*(row > 1)), LCD_CMD)

# Begins writing a string to the LCD at the current cursor
# position. It doesn't concern itself with whether the cursor
# is visible or not. Go off the screen? Your bad.
def lcd_msg(msg_string):
        for i in range(0, len(msg_string)):
                lcd_byte(ord(msg_string[i]), LCD_CHR)

def webRead(URL):
    # Get a handle to the URL object
    try:
        # If the global is set to force using the canned file
        # we deliberately fail the internet read which will
        # trigger the 'except' clause.
        if ALWAYS_USE_THE_FILE:
            print("Pretending to open http://foo.bar.baz")
            h = urllib.request.urlopen("http://foo.bar.baz")
        else:
            print("Trying to open "+URL)
            h = urllib.request.urlopen(URL)
        print("Opened "+URL)
        response = h.read()
        print(len(response)," chars in the response")
    except:
        print("Houston? We have a problem. Can't open "+URL)
        print("We'll use the canned version")
        h = open("Lab06b_alt.txt","r")
        response = h.read()
        response = response.encode()
        h.close()

    return response

def extractData(bighunk, datatype):
    # The bighunk is what we read from the website. The datatype would be 
    # like "<temp_f>" or "<temp_c>" but without the "<>"
    #
    # Since .find() wants bytes (not string) we'll build a string with the
    # full search text and convert it
    searchfor = "<"+datatype+">"
    # This will tell is where the field STARTED.
    i = bighunk.find(searchfor.encode())
    # To that, add the length of the field so we know where it ended
    i = i + len(searchfor)
    # The field afterwards is the same but with a "/"
    searchfor = "</"+datatype+">"
    # This will tell is where the field STARTED. We can use that as the end of
    # the data we're looking for
    j = bighunk.find(searchfor.encode())
    return website[i:j].decode()  # We'd rather have it as a string!
    
# Get the weather for Manchester, NH
website = webRead("http://www.nhc.noaa.gov/nhc_at3.xml")

"""
reads from National Hurricane Center
if the title has the word "no " in it then light stays off
"""

# website is now a bytes() type
print("Last Updated: ", extractData(website, "pubDate"))
page_title = extractData(website, "title")
page_title_str = str(page_title).lower()
print("Result: ", page_title)

lcd_init()

# if no is not found in website
if (page_title_str.find('no ') == -1):
    print("Description: ", extractData(website, "nhc:headline"))    # show nhc:headline
    lcd_string("Tropical Storm", LCD_LINE_1)
    lcd_string("Seek Shelter", LCD_LINE_2)
    while True:
        GPIO.output(LedPin, GPIO.LOW)  # turn light on
        time.sleep(BlinkSpeed)
        GPIO.output(LedPin, GPIO.HIGH)  # turn light off
        time.sleep(BlinkSpeed)
else:
    GPIO.output(LedPin, GPIO.HIGH)  # turn light off
    lcd_string("No Storm", LCD_LINE_1)
    lcd_string("", LCD_LINE_2)
