#!/usr/bin/python3
import RPi.GPIO as GPIO
from time import sleep
from evdev import UInput, ecodes as e
import logging
 
# ================= Special keyboard handling =================
# [GW]: I tried to create a whole new keymap for when the CODE key is held, but since most of the keys
# require two events to be generated (SHIFT + some other key), there's no way to represent that in a keymap.
#
# Created special logic for each of these:
#       
#       SHIFT BS = "DEL": unpress KEY_LEFTSHIFT, press KEY_DELETE
#       SHIFT [ = "]" : unpress KEY_LEFTSHIFT, press KEY_RIGHTBRACE
#       CODE 1 = "|"  : press KEY_LEFTSHIFT + KEY_BACKSLASH
#       CODE 9 = "{"  : press KEY_LEFTSHIFT + KEY_LEFTBRACE
#       CODE 0 = "}"  : press KEY_LEFTSHIFT + KEY_RIGHTBRACE
#       CODE / = "\"  : press KEY_BACKSLASH (this could have been in a new keymap, but why create a whole keymap for only one key?)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
#logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
 
ui = UInput(name = "TRS-80 Model 100 Keyboard", vendor = 0x01, product = 0x01)
 
# TRS-80 Keyboard pin to GPIO pin map
# 1   :   11,     11  :   0,
# 2   :   12,     12  :   23,
# 3   :   13,     13  :   29,
# 4   :   15,     14  :   31,
# 5   :   16,     15  :   32,
# 6   :   18,     16  :   33,
# 7   :   19,     17  :   35,
# 8   :   21,     18  :   36,
# 9   :   22,     19  :   37,
# 10  :   0,      20  :   0
 
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
    logging.debug(f"Setting pin {row} as an output")
    GPIO.setup(row, GPIO.OUT)
 
for col in cols:
    logging.debug(f"Setting pin {col} as an input")
    GPIO.setup(col, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
 
pressed = set()
sleep_time = 1/60
polls_since_press = 0
 
shifted_key = 0
coded_key = 0 

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

            # Detect a newly pressed key (Is our pressed key not yet in the set of pressed keys?)
            if  newval and not keycode in pressed:
                
                # Add it to the set
                pressed.add(keycode)

                # SHIFT BS - Generate DEL
                if keycode == 15 and 8 in pressed:
                    logging.info(f"Pressed {keycode} but actually press e.KEY_DELETE instead due to SHIFT key")
                    # Release the SHIFT key
                    ui.write(e.EV_KEY, e.KEY_LEFTSHIFT, 0)
                    # Press the DEL key
                    ui.write(e.EV_KEY, e.KEY_DELETE, 1)
                    shifted_key = e.KEY_DELETE

                # SHIFT [ - Generate right brace
                elif keycode == 21 and 8 in pressed:
                    logging.info(f"Pressed {keycode} but actually press e.KEY_RIGHTBRACE instead due to SHIFT key")
                    # Release the SHIFT key
                    ui.write(e.EV_KEY, e.KEY_LEFTSHIFT, 0)
                    # Press the right brace key
                    ui.write(e.EV_KEY, e.KEY_RIGHTBRACE, 1)
                    ui.write(e.EV_KEY, e.KEY_LEFTSHIFT, 1)
                    shifted_key = e.KEY_RIGHTBRACE

                # CODE / - Generate backslash
                elif keycode == 66 and 35 in pressed:
                    logging.info(f"Pressed {keycode} but actually press e.KEY_BACKSLASH instead due to CODE key")
                    ui.write(e.EV_KEY, e.KEY_BACKSLASH, 1)
                    coded_key = e.KEY_BACKSLASH

                # CODE 1 - Generate verticle bar
                elif keycode == 4 and 35 in pressed:
                    logging.info(f"Pressed {keycode} but actually press e.KEY_LEFTSHIFT + e.KEY_BACKSLASH instead due to CODE key")
                    # Send SHIFT \ to get a |
                    ui.write(e.EV_KEY, e.KEY_LEFTSHIFT, 1)
                    ui.write(e.EV_KEY, e.KEY_BACKSLASH, 1)
                    coded_key = e.KEY_BACKSLASH

                # CODE 9 - Generate Left curly brace
                elif keycode == 5 and 35 in pressed:
                    logging.info(f"Pressed {keycode} but actually press e.KEY_LEFTSHIFT + e.KEY_LEFTBRACE instead due to CODE key")
                    # Send SHIFT [ to get a {
                    ui.write(e.EV_KEY, e.KEY_LEFTSHIFT, 1)
                    ui.write(e.EV_KEY, e.KEY_LEFTBRACE, 1)
                    coded_key = e.KEY_LEFTBRACE

                # CODE 0 - Generate Right curly brace
                elif keycode == 14 and 35 in pressed:
                    logging.info(f"Pressed {keycode} but actually press e.KEY_LEFTSHIFT + e.KEY_RIGHTBRACE instead due to CODE key")
                    # Send SHIFT ] to get a }
                    ui.write(e.EV_KEY, e.KEY_LEFTSHIFT, 1)
                    ui.write(e.EV_KEY, e.KEY_RIGHTBRACE, 1)
                    coded_key = e.KEY_RIGHTBRACE

                # Otherwise record the normal pressed key state to the system
                else: 
                    logging.info(f"Pressed {keycode} which results in key {e.KEY[keymap[keycode]]} Column {i} Row {j}")
                    ui.write(e.EV_KEY, keymap[keycode], 1)

                syn = True

            # Detect if the key is released (If there was a state change, was our pressed key in the set of pressed keys?)
            elif not newval and keycode in pressed:
                
                # Record the released key state to the system - process all exceptions
                if keycode == 15 and 8 in pressed:
                    logging.info(f"Released {keycode} but actually release e.KEY_DELETE due to SHIFT key")
                    ui.write(e.EV_KEY, e.KEY_DELETE, 0)
                elif keycode == 21 and 8 in pressed:
                    logging.info(f"Released {keycode} but actually release e.KEY_RIGHTBRACE due to SHIFT key")
                    ui.write(e.EV_KEY, e.KEY_RIGHTBRACE, 0)
                elif keycode == 66 and 35 in pressed:
                    logging.info(f"Released {keycode} but actually release e.KEY_BACKSLASH instead due to CODE key")
                    ui.write(e.EV_KEY, e.KEY_BACKSLASH, 0)
                elif keycode == 4 and 35 in pressed:
                    logging.info(f"Released {keycode} but actually release e.KEY_LEFTSHIFT + e.KEY_BACKSLASH instead due to CODE key")
                    ui.write(e.EV_KEY, e.KEY_BACKSLASH, 0)
                    ui.write(e.EV_KEY, e.KEY_LEFTSHIFT, 0)
                elif keycode == 5 and 35 in pressed:
                    logging.info(f"Released {keycode} but actually release e.KEY_LEFTSHIFT + e.KEY_LEFTBRACE instead due to CODE key")
                    ui.write(e.EV_KEY, e.KEY_LEFTBRACE, 0)
                    ui.write(e.EV_KEY, e.KEY_LEFTSHIFT, 0)
                elif keycode == 14 and 35 in pressed:
                    logging.info(f"Released {keycode} but actually release e.KEY_LEFTSHIFT + e.KEY_RIGHTBRACE instead due to CODE key")
                    ui.write(e.EV_KEY, e.KEY_RIGHTBRACE, 0)
                    ui.write(e.EV_KEY, e.KEY_LEFTSHIFT, 0)
                else: 
                    logging.info(f"Released {keycode} which results in key {e.KEY[keymap[keycode]]}")
                    ui.write(e.EV_KEY, keymap[keycode], 0)

                # If CODE was released while another is still being held down:
                # 1. Release this extra key to prevent continuous key repeat
                # 2. Release the shift key
                if keycode == 35 and len(pressed)>1:
                    logging.info(f"Also releasing {coded_key} and SHIFT")
                    ui.write(e.EV_KEY, coded_key, 0)
                    ui.write(e.EV_KEY, e.KEY_LEFTSHIFT, 0)
                # If SHIFT was released while another is still being held down, release any specially modded key to prevent continuous repeat
                if keycode == 8 and len(pressed)>1:
                    logging.info(f"Also releasing {shifted_key}")
                    ui.write(e.EV_KEY, shifted_key, 0)

                # Remove it from the set
                pressed.discard(keycode)

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
