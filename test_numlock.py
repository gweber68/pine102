import evdev

while(True):
    if 0 in (evdev.InputDevice('/dev/input/event5').leds()):
        print("NumLock set!")
    elif (offflag == 0):
        print("Numlock reset")




