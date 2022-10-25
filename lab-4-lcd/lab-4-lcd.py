#!/usr/bin/env python
# -----------------
# Modified 2018-09-30 to use Matt Hawkins' LCD library for I2C available
# from https://bitbucket.org/MattHawkinsUK/rpispy-misc/raw/master/python/lcd_i2c.py
#
import RPi.GPIO as GPIO
import time
import random

# Additional stuff for LCD
import smbus

AButtonPin = 26    # button for Player A
BButtonPin = 16    # button for Player B

ButtonPressed = 0
ButtonUp = 1

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

# Set the buttons' mode as input with the internal pullup 
GPIO.setup(AButtonPin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(BButtonPin, GPIO.IN, pull_up_down = GPIO.PUD_UP)

#Open I2C interface
#bus = smbus.SMBus(0)  # Rev 1 Pi uses 0
bus = smbus.SMBus(1) # Rev 2 Pi uses 1

"""
call once to clear display
"""
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

PuckSpeed = 0.05    # puck speed back and forth between players

# sets puck positions as it moves one space at a time across the display and back
puck_movement = ["| *            |", "|  *           |", "|   *          |", "|    *         |", "|     *        |", "|      *       |", "|       *      |", "|        *     |", "|         *    |", "|          *   |", "|           *  |", "|            * |", "|             *|", "|            * |", "|           *  |", "|          *   |", "|         *    |", "|        *     |", "|       *      |", "|      *       |", "|     *        |", "|    *         |", "|   *          |", "|  *           |", "| *            |", "|*             |"]

winning_score = 5    # adjustable winning score that will end game once reached by highest_score
highest_score = 0    # monitored score that increases until winning_score is met

a_score = 0    # Player A's start score
b_score = 0    # Player B's start score

lcd_init()
lcd_string("|*             |", LCD_LINE_1)    # sets first frame of game
lcd_string(f"  a: {a_score}    b: {b_score}", LCD_LINE_2)    # displays starting scores
time.sleep(PuckSpeed)    # waits until puck begins moving

# while game is in play
while highest_score < winning_score:

  # loop through puck positions making the puck move back and forth
  for position in puck_movement:
    lcd_string(position, LCD_LINE_1)    # sets display as correct 

    # check if button is pressed once the puck reaches the end
    if position == "|*             |" and GPIO.input(AButtonPin) == ButtonUp:    # if Player A doesn't press their button
      b_score = b_score + 1    # add 1 to B score
    elif position == "|             *|" and GPIO.input(BButtonPin) == ButtonUp:    # if Player B doesn't press their button
      a_score  = a_score + 1    # add 1 to A score
    elif position == "|*             |" and GPIO.input(AButtonPin) == ButtonPressed:    # if Player A presses their button
      lcd_string(">*             |", LCD_LINE_1)    # show puck being propelled in other direction
    elif position == "|             *|" and GPIO.input(BButtonPin) == ButtonPressed:    # if Player B presses their button
      lcd_string("|             *<", LCD_LINE_1)    # show puck being propelled in other direction
    lcd_string(f"  a: {a_score}    b: {b_score}", LCD_LINE_2)    # set scores to updated values

    # update highest score by taking highest score out of players A and B
    score_list = [a_score, b_score]
    highest_score = max(score_list)

    time.sleep(PuckSpeed)    # holds puck's position for duration of PuckSpeed

    # end game if winning_score is reached by highest_score
    if highest_score == winning_score:
      break

# display game stats
lcd_string("game over", LCD_LINE_1)    # show this line regardless of who wins

# second line depends on who wins
if highest_score == a_score:
  lcd_string("a wins", LCD_LINE_2)
elif highest_score == b_score:
  lcd_string("b wins", LCD_LINE_2)
else:
  lcd_string("[error]", LCD_LINE_2)
