load keyboard.py on boot:

1. Copy keyboard python script to /etc/keyboard.py
2. Add this line to /etc/rc.local:
   python3 /etc/keyboard.py &


Special key mappings:

SHIFT BS = DEL  : unsend KEY_LEFTSHIFT, send KEY_DELETE
SHIFT [ = "]"   : unsend KEY_LEFTSHIFT, send KEY_RIGHTBRACE
CODE / = "\"    :   send KEY_BACKSLASH
CODE 1 = "|"    :   send KEY_LEFTSHIFT + KEY_BACKSLASH
CODE 9 = "{"    :   send KEY_LEFTSHIFT + KEY_LEFTBRACE
CODE 0 = "}"    :   send KEY_LEFTSHIFT + KEY_RIGHTBRACE
CODE F5 = F9
CODE F6 = F10
CODE F7 = F11
CODE F8 = F12

