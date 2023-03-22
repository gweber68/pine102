#!/usr/bin/python3
import RPi.GPIO as GPIO
from time import sleep
from evdev import UInput, ecodes as e
import logging
 
# TODO:
# Add an exception for handling Shift + [
# Add a new keymap for when CODE is held. Need to add chars: \ | ` ~ { }
 

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
#logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
 
ui = UInput(name = "Tandy 102 Keyboard", vendor = 0x01, product = 0x01)
 
# Tandy 102 Keyboard pin to GPIO pin map
# 1   :   11,     10  :   23,      
# 2   :   12,     11  :   29,
# 3   :   13,     12  :   31,
# 4   :   15,     13  :   32,
# 5   :   16,     14  :   33,
# 6   :   18,     15  :   35,
# 7   :   19,     16  :   36,
# 8   :   21,     17  :   37,
# 9   :   22,     18  :   0
 
cols = [11,12,13,15,16,18,19,21,22]
rows = [23,29,31,32,33,35,36,37]

keymap = [
    e.KEY_Z,    e.KEY_A,    e.KEY_Q,    e.KEY_O,           e.KEY_1,    e.KEY_9,      e.KEY_SPACE,     e.KEY_F1,    e.KEY_LEFTSHIFT,
    e.KEY_X,    e.KEY_S,    e.KEY_W,    e.KEY_P,           e.KEY_2,    e.KEY_0,      e.KEY_BACKSPACE, e.KEY_F2,    e.KEY_LEFTCTRL,
    e.KEY_C,    e.KEY_D,    e.KEY_E,    e.KEY_LEFTBRACE,   e.KEY_3,    e.KEY_MINUS,  e.KEY_TAB,       e.KEY_F3,    e.KEY_LEFTALT,
    e.KEY_V,    e.KEY_F,    e.KEY_R,    e.KEY_SEMICOLON,   e.KEY_4,    e.KEY_EQUAL,  e.KEY_ESC,       e.KEY_F4,    e.KEY_FN,
    e.KEY_B,    e.KEY_G,    e.KEY_T,    e.KEY_APOSTROPHE,  e.KEY_5,    e.KEY_LEFT,   e.KEY_GRAVE,     e.KEY_F5,    e.KEY_NUMLOCK,
    e.KEY_N,    e.KEY_H,    e.KEY_Y,    e.KEY_COMMA,       e.KEY_6,    e.KEY_RIGHT,  e.KEY_COPY,      e.KEY_F6,    e.KEY_CAPSLOCK,
    e.KEY_M,    e.KEY_J,    e.KEY_U,    e.KEY_DOT,         e.KEY_7,    e.KEY_UP,     e.KEY_CLEAR,     e.KEY_F7,    e.KEY_RESERVED,
    e.KEY_L,    e.KEY_K,    e.KEY_I,    e.KEY_SLASH,       e.KEY_8,    e.KEY_DOWN,   e.KEY_ENTER,     e.KEY_F8,    e.KEY_PAUSE,
]
 
GPIO.setmode(GPIO.BOARD)
 
for row in rows:
    logging.info(f"Setting pin {row} as an output")
    GPIO.setup(row, GPIO.OUT)
 
for col in cols:
    logging.info(f"Setting pin {col} as an input")
    GPIO.setup(col, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
 
pressed = set()
sleep_time = 1/60
polls_since_press = 0
 
while True:
    sleep(sleep_time)
    syn = False
    for i in range(len(rows)):
        logging.debug(f"Setting row {i} high, pin {rows[i]}")
        GPIO.output(rows[i], GPIO.HIGH)
        for j in range(len(cols)):
            keycode = i * (len(rows) + 1) + j
            logging.debug(f"Checking column {j}, pin {cols[j]} which results in key {keymap[keycode]}")
            newval = GPIO.input(cols[j]) == GPIO.HIGH
            if  newval and not keycode in pressed:
                pressed.add(keycode)
                logging.info(f"Pressed {keycode} which results in key {e.KEY[keymap[keycode]]} Column {i} Row {j}")
                ui.write(e.EV_KEY, keymap[keycode], 1)
                syn = True
            elif not newval and keycode in pressed:
                pressed.discard(keycode)
                logging.info(f"Released {keycode} which results in key {e.KEY[keymap[keycode]]}")
                ui.write(e.EV_KEY, keymap[keycode], 0)
                syn = True
        GPIO.output(rows[i], GPIO.LOW)
    if syn:
        ui.syn()
        polls_since_press = 0
        sleep_time = 1/60
    else:
        polls_since_press = polls_since_press + 1
 
    if polls_since_press == 600:
        logging.info(f"Reducing polling rate")
        sleep_time = 1/10
    elif polls_since_press == 1200:
        logging.info(f"Reducing polling rate again")
        sleep_time = 1/5
