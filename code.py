# All the imports
import time

import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.mouse import Mouse

from adafruit_macropad import MacroPad

from rainbowio import colorwheel
import displayio
import terminalio
from adafruit_display_text import bitmap_label as label
from adafruit_displayio_layout.layouts.grid_layout import GridLayout

import board
from adafruit_seesaw import seesaw, rotaryio, digitalio, neopixel


# set up rotary breakouts using the built-in STEMMA QT connector on a microcontroller

i2c = board.STEMMA_I2C()

qt_enc1 = seesaw.Seesaw(i2c, addr=0x36)
qt_enc2 = seesaw.Seesaw(i2c, addr=0x38)

qt_enc1.pin_mode(24, qt_enc1.INPUT_PULLUP)
button1 = digitalio.DigitalIO(qt_enc1, 24)
button_held1 = False

qt_enc2.pin_mode(24, qt_enc2.INPUT_PULLUP)
button2 = digitalio.DigitalIO(qt_enc2, 24)
button_held2 = False

encoder1 = rotaryio.IncrementalEncoder(qt_enc1)
last_position1 = None

encoder2 = rotaryio.IncrementalEncoder(qt_enc2)
last_position2 = None

pixel1 = neopixel.NeoPixel(qt_enc1, 6, 1)
pixel1.brightness = 0.2
pixel1.fill(0xFF0000)

pixel2 = neopixel.NeoPixel(qt_enc2, 6, 1)
pixel2.brightness = 0.2
pixel2.fill(0x00FF00)

last_position1 = -encoder1.position
last_position2 = -encoder2.position

# set up macropad
macropad = MacroPad()
macropad.pixels.brightness = 0.5

last_position = macropad.encoder

# create keyboard

keyboard = Keyboard(usb_hid.devices)
keyboard_layout = KeyboardLayoutUS(keyboard)

# shortcut titles and colours

shortcuts_list = ["focus", "top", "front","right",
                  "zoom", "l cut", "cam", "shear",
                  "sel+-", "tbd", "tbd", "tbd",
                  "xray", "apply", "tbd", "tbd",]
pixel_colours = [ 0x0000FF, 0x00FF00, 0xFF0000,
                  0xFF7F50, 0xDFFF00, 0xE74C3C,
                  0xE74C3C, 0xE74C3C, 0xE74C3C,
                  0xE74C3C, 0xE74C3C, 0x6495ED,]
button_keycodes = [[Keycode.KEYPAD_SEVEN], [Keycode.KEYPAD_ONE], [Keycode.KEYPAD_THREE],
                   [Keycode.CONTROL, Keycode.R], [Keycode.KEYPAD_ZERO], [Keycode.KEYPAD_THREE],
                   [Keycode.KEYPAD_SEVEN], [Keycode.KEYPAD_ONE], [Keycode.KEYPAD_THREE],
                   [Keycode.CONTROL, Keycode.A], [Keycode.KEYPAD_ONE], [Keycode.KEYPAD_THREE],]

# create display as grid
main_group = displayio.Group()
macropad.display.show(main_group)
title = label.Label(
    y=4,
    font=terminalio.FONT,
    color=0x0,
    text="      SHORTCUTS      ",
    background_color=0xFFFFFF,
)
layout = GridLayout(x=0, y=10, width=128, height=54, grid_size=(4, 4), cell_padding=1)
labels = []
for shortcut in shortcuts_list:
    labels.append(label.Label(terminalio.FONT, text=str(shortcut)))

for index in range(16):
    x = index % 4
    y = index // 4
    layout.add_content(labels[index], grid_position=(x, y), cell_size=(1, 1))

main_group.append(title)
main_group.append(layout)

while True:

    # handle key presses
    for pixel in range(12):
        macropad.pixels[pixel] = pixel_colours[pixel]

    key_event = macropad.keys.events.get()

    if key_event and key_event.pressed:
        if len(button_keycodes[key_event.key_number]) > 1:
            keyboard.press(
                button_keycodes[key_event.key_number][0],
                button_keycodes[key_event.key_number][1],
            )
            time.sleep(0.09)
            keyboard.release(
                button_keycodes[key_event.key_number][0],
                button_keycodes[key_event.key_number][1],
            )
        else:
            keyboard.press(button_keycodes[key_event.key_number][0])
            time.sleep(0.09)
            keyboard.release(button_keycodes[key_event.key_number][0])
    # read macropad encoder
    
    position = macropad.encoder
    position_change = last_position - position

    if position_change != 0:
        modulo_position = position % 3
        if modulo_position == 0:
            keyboard.press(Keycode.ONE)
            time.sleep(0.09)
            keyboard.release(Keycode.ONE)
        elif modulo_position == 1:
            keyboard.press(Keycode.TWO)
            time.sleep(0.09)
            keyboard.release(Keycode.TWO)
        elif modulo_position == 2:
            keyboard.press(Keycode.THREE)
            time.sleep(0.09)
            keyboard.release(Keycode.THREE)

    last_position = position
    
    # use macropad encoder button
    
    macropad.encoder_switch_debounced.update()
    if macropad.encoder_switch_debounced.pressed:
        keyboard.press(Keycode.O)
    if macropad.encoder_switch_debounced.released:
        keyboard.release(Keycode.O)
        

    # read frirst encoder change and do a thing

    position1 = -encoder1.position
    position_change1 = last_position1 - position1

    if position_change1 > 0:
        for _ in range(position_change1):
            keyboard.press(Keycode.KEYPAD_PLUS)
            time.sleep(0.09)
            keyboard.release(Keycode.KEYPAD_PLUS)

    elif position_change1 < 0:
        for _ in range(-position_change1):
            keyboard.press(Keycode.KEYPAD_MINUS)
            time.sleep(0.09)
            keyboard.release(Keycode.KEYPAD_MINUS)

    last_position1 = position1

    # press encoder 1

    if not button1.value and not button_held1:
        button_held1 = True
        pixel1.brightness = 0.5
        keyboard.press(Keycode.KEYPAD_PERIOD)

    if button1.value and button_held1:
        button_held1 = False
        pixel1.brightness = 0.1
        keyboard.release(Keycode.KEYPAD_PERIOD)

    # read second encoder change and do a thing

    position2 = -encoder2.position
    position_change2 = last_position2 - position2

    if position_change2 > 0:
        for _ in range(position_change2):
            keyboard.press(Keycode.CONTROL, Keycode.KEYPAD_PLUS)
            time.sleep(0.09)
            keyboard.release(Keycode.CONTROL, Keycode.KEYPAD_PLUS)

    elif position_change2 < 0:
        for _ in range(-position_change2):
            keyboard.press(Keycode.CONTROL, Keycode.KEYPAD_MINUS)
            time.sleep(0.09)
            keyboard.release(Keycode.CONTROL, Keycode.KEYPAD_MINUS)

    last_position2 = position2

    # handle encoder 2 button

    if not button2.value and not button_held2:
        button_held2 = True
        pixel2.brightness = 0.5
        keyboard.press(Keycode.SHIFT, Keycode.Z)

    if button2.value and button_held2:
        button_held2 = False
        pixel2.brightness = 0.1
        keyboard.release(Keycode.SHIFT, Keycode.Z)
