#!/usr/bin/python3
import RPi.GPIO as GPIO
from time import sleep
from evdev import UInput, ecodes as e

# Logging removed for improving keystroke response
import logging
 
# ================= Special keyboard handling [GW] =================
# Support for Num-Lock with the numlock_keymap.  This requires a modified Tandy keyboard that has the Num-Lock
# mechanical locking keyswitch replaced with a momentary-contact keyswitch, like that of most keys on the keyboard.
# This will mean a user can press Num-lock it will simply switch a state, not remain locked down in the ON position.
# numlock_keymap[] contains the modified keyboard layout including the numeric keys for m,j,k,l,u,i and o.
#
# A lot of CODE keys require two events to be generated (shift + some other key), so special logic had to be created
# for those that couldn't be represented in the code_keymap.
#
# Here's the list of SHIFT & CODE keys requiring special handling:
#       
#       SHIFT BS = DEL  : unpress KEY_LEFTSHIFT, press KEY_DELETE
#       SHIFT [ = ]     : unpress KEY_LEFTSHIFT, press KEY_RIGHTBRACE
#       CODE 1 = |      : press KEY_LEFTSHIFT + KEY_BACKSLASH
#       CODE 9 = {      : press KEY_LEFTSHIFT + KEY_LEFTBRACE
#       CODE 0 = }      : press KEY_LEFTSHIFT + KEY_RIGHTBRACE
#
# Regular CODE key map for simple substitutions:
#
#       CODE / = \      : press KEY_BACKSLASH
#       CODE F5 = F9    : press KEY_F9
#       CODE F6 = F10   : press KEY_F10
#       CODE F7 = F11   : press KEY_F11
#       CODE F8 = F12   : press KEY_F12

#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
#logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
#logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logging.basicConfig(level=logging.CRITICAL, format='%(asctime)s - %(levelname)s - %(message)s')
 
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

# NUM LOCK keymap: M=0, J=1, K=2, L=3, U=4, I=5, O=6
numlock_keymap = [
    e.KEY_Z,    e.KEY_A,    e.KEY_Q,    e.KEY_6,           e.KEY_1,    e.KEY_9,      e.KEY_SPACE,     e.KEY_F1,    e.KEY_LEFTSHIFT,
    e.KEY_X,    e.KEY_S,    e.KEY_W,    e.KEY_P,           e.KEY_2,    e.KEY_0,      e.KEY_BACKSPACE, e.KEY_F2,    e.KEY_LEFTCTRL,
    e.KEY_C,    e.KEY_D,    e.KEY_E,    e.KEY_LEFTBRACE,   e.KEY_3,    e.KEY_MINUS,  e.KEY_TAB,       e.KEY_F3,    e.KEY_LEFTALT,
    e.KEY_V,    e.KEY_F,    e.KEY_R,    e.KEY_SEMICOLON,   e.KEY_4,    e.KEY_EQUAL,  e.KEY_ESC,       e.KEY_F4,    e.KEY_FN,
    e.KEY_B,    e.KEY_G,    e.KEY_T,    e.KEY_APOSTROPHE,  e.KEY_5,    e.KEY_LEFT,   e.KEY_GRAVE,     e.KEY_F5,    e.KEY_NUMLOCK,
    e.KEY_N,    e.KEY_H,    e.KEY_Y,    e.KEY_COMMA,       e.KEY_6,    e.KEY_RIGHT,  e.KEY_COPY,      e.KEY_F6,    e.KEY_CAPSLOCK,
    e.KEY_0,    e.KEY_1,    e.KEY_4,    e.KEY_DOT,         e.KEY_7,    e.KEY_UP,     e.KEY_CLEAR,     e.KEY_F7,    e.KEY_RESERVED,
    e.KEY_3,    e.KEY_2,    e.KEY_5,    e.KEY_SLASH,       e.KEY_8,    e.KEY_DOWN,   e.KEY_ENTER,     e.KEY_F8,    e.KEY_PAUSE,
]

# CODE keymap: /=\, F5=F9, F6=F10, F7=F11, F8=F12
code_keymap = [
    e.KEY_Z,    e.KEY_A,    e.KEY_Q,    e.KEY_O,           e.KEY_1,    e.KEY_9,      e.KEY_SPACE,     e.KEY_F1,    e.KEY_LEFTSHIFT,
    e.KEY_X,    e.KEY_S,    e.KEY_W,    e.KEY_P,           e.KEY_2,    e.KEY_0,      e.KEY_BACKSPACE, e.KEY_F2,    e.KEY_LEFTCTRL,
    e.KEY_C,    e.KEY_D,    e.KEY_E,    e.KEY_LEFTBRACE,   e.KEY_3,    e.KEY_MINUS,  e.KEY_TAB,       e.KEY_F3,    e.KEY_LEFTALT,
    e.KEY_V,    e.KEY_F,    e.KEY_R,    e.KEY_SEMICOLON,   e.KEY_4,    e.KEY_EQUAL,  e.KEY_ESC,       e.KEY_F4,    e.KEY_FN,
    e.KEY_B,    e.KEY_G,    e.KEY_T,    e.KEY_APOSTROPHE,  e.KEY_5,    e.KEY_LEFT,   e.KEY_GRAVE,     e.KEY_F9,    e.KEY_NUMLOCK,
    e.KEY_N,    e.KEY_H,    e.KEY_Y,    e.KEY_COMMA,       e.KEY_6,    e.KEY_RIGHT,  e.KEY_COPY,      e.KEY_F10,   e.KEY_CAPSLOCK,
    e.KEY_M,    e.KEY_J,    e.KEY_U,    e.KEY_DOT,         e.KEY_7,    e.KEY_UP,     e.KEY_CLEAR,     e.KEY_F11,   e.KEY_RESERVED,
    e.KEY_L,    e.KEY_K,    e.KEY_I,    e.KEY_BACKSLASH,   e.KEY_8,    e.KEY_DOWN,   e.KEY_ENTER,     e.KEY_F12,   e.KEY_PAUSE,
]

GPIO.setmode(GPIO.BOARD)
 
for row in rows:
    logging.debug(f"Setting pin {row} as an output")
    GPIO.setup(row, GPIO.OUT)
 
for col in cols:
    logging.debug(f"Setting pin {col} as an input")
    GPIO.setup(col, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
 
# Set object to store pressed keys
pressed = set()
# Normal polling rate
sleep_time = 1/60
# Keep track of how many keyboard polls since the last keypress
polls_since_press = 0
# Keep track of the numlock state, default to off
num_lock = 0

# SHIFT/CODE/NUM-LOCK key scan values
SHIFT_KEY = 8
CODE_KEY = 35
NUMLOCK_KEY = 44

# Keep track of keys modified with SHIFT and CODE keys
shifted_key = 0
coded_key = 0 

while True:
    sleep(sleep_time)
    syn = False
    for i in range(len(rows)):
        logging.debug(f"Setting row {i} high, pin {rows[i]}")
        GPIO.output(rows[i], GPIO.HIGH)
        for j in range(len(cols)):
            # Look up the keycode in our map
            keycode = i * (len(rows) + 1) + j
            logging.debug(f"Checking column {j}, pin {cols[j]} which results in key {keymap[keycode]}")
            newval = GPIO.input(cols[j]) == GPIO.HIGH

            # ========================================================================================================================
            # Detect a newly pressed key (Is our pressed key not yet in the set of pressed keys?)
            # ========================================================================================================================
            if  newval and not keycode in pressed:
                
                # Add it to the set
                pressed.add(keycode)

                # ---------------------------------------------------------
                # NUM-LOCK handler
                # ---------------------------------------------------------
                if keycode == NUMLOCK_KEY:
                    if num_lock == 0:
                        num_lock = 1
                        logging.info(f"Pressed {keycode} - Set num_lock = 1")
                    else:
                        num_lock = 0
                        logging.info(f"Pressed {keycode} - Set num_lock = 0")
    
                # ---------------------------------------------------------
                # Handling for SHIFT BS, SHIFT [, and CODE modifiers
                # ---------------------------------------------------------
                # SHIFT BS - Generate DEL
                if keycode == 15 and SHIFT_KEY in pressed:
                    # Release the SHIFT key and send DEL instead
                    logging.info(f"Pressed {keycode} but actually press e.KEY_DELETE instead due to SHIFT key")
                    ui.write(e.EV_KEY, e.KEY_LEFTSHIFT, 0)
                    ui.write(e.EV_KEY, e.KEY_DELETE, 1)
                    shifted_key = e.KEY_DELETE

                # SHIFT [ - Generate right brace
                elif keycode == 21 and SHIFT_KEY in pressed:
                    # Release the SHIFT key and send right brace instead
                    logging.info(f"Pressed {keycode} but actually press e.KEY_RIGHTBRACE instead due to SHIFT key")
                    ui.write(e.EV_KEY, e.KEY_LEFTSHIFT, 0)
                    ui.write(e.EV_KEY, e.KEY_RIGHTBRACE, 1)
                    shifted_key = e.KEY_RIGHTBRACE

                # CODE 1 - Generate verticle bar
                elif keycode == 4 and CODE_KEY in pressed:
                    # Send SHIFT \ to get a |
                    logging.info(f"Pressed {keycode} but actually send e.KEY_LEFTSHIFT + e.KEY_BACKSLASH instead due to CODE key")
                    ui.write(e.EV_KEY, e.KEY_LEFTSHIFT, 1)
                    ui.write(e.EV_KEY, e.KEY_BACKSLASH, 1)
                    coded_key = e.KEY_BACKSLASH

                # CODE 9 - Generate Left curly brace
                elif keycode == 5 and CODE_KEY in pressed:
                    # Send SHIFT [ to get a {
                    logging.info(f"Pressed {keycode} but actually send e.KEY_LEFTSHIFT + e.KEY_LEFTBRACE instead due to CODE key")
                    ui.write(e.EV_KEY, e.KEY_LEFTSHIFT, 1)
                    ui.write(e.EV_KEY, e.KEY_LEFTBRACE, 1)
                    coded_key = e.KEY_LEFTBRACE

                # CODE 0 - Generate Right curly brace
                elif keycode == 14 and CODE_KEY in pressed:
                    # Send SHIFT ] to get a }
                    logging.info(f"Pressed {keycode} but actually send e.KEY_LEFTSHIFT + e.KEY_RIGHTBRACE instead due to CODE key")
                    ui.write(e.EV_KEY, e.KEY_LEFTSHIFT, 1)
                    ui.write(e.EV_KEY, e.KEY_RIGHTBRACE, 1)
                    coded_key = e.KEY_RIGHTBRACE

                # -------------------------------------------------------------------
                # Regular handler using keymap[], numlock_keymap[], and code_keymap[]
                # -------------------------------------------------------------------
                else:
                    # Check for CODE being held down; if so use code_keymap
                    if CODE_KEY in pressed:
                        logging.info(f"Pressed {keycode} which is CODE-key {e.KEY[code_keymap[keycode]]} Column {i} Row {j}")
                        ui.write(e.EV_KEY, code_keymap[keycode], 1)
                        coded_key = code_keymap[keycode]
                    # Check for num-lock being set; if so use numlock_keymap
                    elif num_lock:
                        logging.info(f"Pressed {keycode} which is num-locked key {e.KEY[numlock_keymap[keycode]]} Column {i} Row {j}")
                        ui.write(e.EV_KEY, numlock_keymap[keycode], 1)
                    # Otherwise use regular keymap
                    else:
                        logging.info(f"Pressed {keycode} which is key {e.KEY[keymap[keycode]]} Column {i} Row {j}")
                        ui.write(e.EV_KEY, keymap[keycode], 1)

                syn = True

            # ========================================================================================================================
            # Detect if the key is released (If there was a state change, was our pressed key in the set of pressed keys?)
            # ========================================================================================================================
            elif not newval and keycode in pressed:
                
                # Record the released key state to the system - process all exceptions
                if keycode == 15 and SHIFT_KEY in pressed:
                    logging.info(f"Released {keycode} but actually release e.KEY_DELETE due to SHIFT key")
                    ui.write(e.EV_KEY, e.KEY_DELETE, 0)
                elif keycode == 21 and SHIFT_KEY in pressed:
                    logging.info(f"Released {keycode} but actually release e.KEY_RIGHTBRACE due to SHIFT key")
                    ui.write(e.EV_KEY, e.KEY_RIGHTBRACE, 0)
#                elif keycode == 66 and CODE_KEY in pressed:
#                    logging.info(f"Released {keycode} but actually release e.KEY_BACKSLASH instead due to CODE key")
#                    ui.write(e.EV_KEY, e.KEY_BACKSLASH, 0)
                elif keycode == 4 and CODE_KEY in pressed:
                    logging.info(f"Released {keycode} but actually release e.KEY_LEFTSHIFT + e.KEY_BACKSLASH instead due to CODE key")
                    ui.write(e.EV_KEY, e.KEY_BACKSLASH, 0)
                    ui.write(e.EV_KEY, e.KEY_LEFTSHIFT, 0)
                elif keycode == 5 and CODE_KEY in pressed:
                    logging.info(f"Released {keycode} but actually release e.KEY_LEFTSHIFT + e.KEY_LEFTBRACE instead due to CODE key")
                    ui.write(e.EV_KEY, e.KEY_LEFTBRACE, 0)
                    ui.write(e.EV_KEY, e.KEY_LEFTSHIFT, 0)
                elif keycode == 14 and CODE_KEY in pressed:
                    logging.info(f"Released {keycode} but actually release e.KEY_LEFTSHIFT + e.KEY_RIGHTBRACE instead due to CODE key")
                    ui.write(e.EV_KEY, e.KEY_RIGHTBRACE, 0)
                    ui.write(e.EV_KEY, e.KEY_LEFTSHIFT, 0)

                # -------------------------------------------------------------------
                # Regular handler using keymap[], numlock_keymap[], and code_keymap[]
                # -------------------------------------------------------------------
                else:
                    # Check for CODE key being held down; if so use code_keymap for the release event
                    if CODE_KEY in pressed:
                        logging.info(f"Released {keycode} which is CODE-key key {e.KEY[numlock_keymap[keycode]]}")
                        ui.write(e.EV_KEY, code_keymap[keycode], 0)
                    # Check for num-lock being set; if so use numlock_keymap for the release event
                    elif num_lock:
                        logging.info(f"Released {keycode} which is num-locked key {e.KEY[numlock_keymap[keycode]]}")
                        ui.write(e.EV_KEY, numlock_keymap[keycode], 0)
                    # Otherwise use regular keymap for the release event
                    else:
                        logging.info(f"Released {keycode} which is {e.KEY[keymap[keycode]]}")
                        ui.write(e.EV_KEY, keymap[keycode], 0)

                # If CODE was released while another is still being held down:
                # 1. Release this extra key to prevent continuous key repeat
                # 2. Release the shift key
                if keycode == CODE_KEY and len(pressed)>1:
                    logging.info(f"Also releasing {coded_key} and SHIFT")
                    ui.write(e.EV_KEY, coded_key, 0)
                    ui.write(e.EV_KEY, e.KEY_LEFTSHIFT, 0)
                # If SHIFT was released while another is still being held down, also release this extra key to prevent continuous key repeat
                if keycode == SHIFT_KEY and len(pressed)>1:
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
