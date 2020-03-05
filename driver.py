import os
import RPi.GPIO as io
import json
import time

# https://gist.github.com/willwade/30895e766273f606f821568dadebcc1c#file-keyboardhook-py-L42
import keycode

#str1 = '\x00\x00\x04\x00\x00\x00\x00\x00'
#str2 = '\x00\x00\x00\x00\x00\x00\x00\x00'

allKeys = []

class Key:
    gpio = 0
    mode = ""
    command = ""

    def __init__(self, gpio, mode, command):
        self.gpio = gpio
        self.mode = mode
        self.command = command

def keyInterrupt(channel):
    global allKeys

    #print("Key interrupt!")
    
    for key in allKeys:
        if key.gpio == channel:
            if key.mode == 'shortcut':
                writeToKeyboard(key.command)
            elif key.mode == 'text':
                writeTextToKeyboard(key.command)

            break

def writeTextToKeyboard(text):
    #print('Write text to keyboard:')
    #print(text)

    empty = '\x00\x00\x00\x00\x00\x00\x00\x00'
    
    dev = os.open("/dev/hidg0", os.O_RDWR)
    for char in text:
        dictChar = char
        if char == ' ':
            dictChar = 'SPACE'
        elif char == '-':
            dictChar = 'MINUS'
        elif char == '.':
            dictChar = 'DOT'
        elif char == '/':
            dictChar = 'SLASH'

        keycodeChar = keycode.keycodeDict['KEY_' + dictChar.upper()]

        finalOutput = '\x00\x00' + keycodeChar + '\x00\x00\x00\x00\x00'

        os.write(dev, finalOutput.encode())
        os.write(dev, empty.encode())
        
    os.close(dev)

def writeToKeyboard(command):
    empty = '\x00\x00\x00\x00\x00\x00\x00\x00'

    #print("Writing command...")
    #print(command)

    dev = os.open("/dev/hidg0", os.O_RDWR)
    os.write(dev, command.encode())
    os.write(dev, empty.encode())
    os.close(dev)

# Load json from file
jsonFile = open('config.json')
datas = json.load(jsonFile)
jsonFile.close()

# Load json data
for keyData in datas:
    newKey = Key(keyData['gpio'], keyData['mode'], keyData['command'])
    allKeys.append(newKey)

# Setup GPIO
io.setmode(io.BCM)

# The following pin supports pull down mode
# 2, 3, 4, 7, 8, 9, 10, 11, 14, 15, 17, 18, 22, 23, 24, 25, 27, 28, 29, 30, 31
for key in allKeys:
    io.setup(key.gpio, io.IN, io.PUD_DOWN)
    io.add_event_detect(key.gpio, io.RISING, callback=keyInterrupt, bouncetime=300)

try: 
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    io.cleanup()
    print("Keyboard interrupt! Exiting!")
