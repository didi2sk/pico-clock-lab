"""T08 - other hardware: buttons, light sensor, internal temperature, buzzer.

Press the three buttons (the buzzer beeps and a block of the display lights up),
cover the photoresistor and note the raw values (needed for brightness calibration;
HIGHER raw value = DARKER).
"""
from machine import Pin, ADC
from display import Display
from utime import sleep_ms
import pins

buttons = [Pin(p, Pin.IN, Pin.PULL_UP) for p in pins.BUTTONS]
light = ADC(pins.LIGHT_ADC)
chip = ADC(4)
buzzer = Pin(pins.BUZZER, Pin.OUT, value=0)

d = Display()
d.on_us = 300
d.start()
last = None
n = 0
try:
    while True:
        pressed = [b.value() == 0 for b in buttons]
        d.clear()
        for i, p in enumerate(pressed):
            if p:
                for x in range(2 + i * 7, 2 + i * 7 + 6):
                    for y in range(1, 8):
                        d.pixel(x, y)
        if any(pressed):
            buzzer.value(1)
        else:
            buzzer.value(0)
        raw = sum(light.read_u16() for _ in range(16)) // 16
        temp = 27 - (chip.read_u16() * 3.3 / 65535 - 0.706) / 0.001721
        n += 1
        if n % 5 == 0 or pressed != last:
            print("buttons", pressed, "light raw", raw, "chip temp %.1f C" % temp)
            last = pressed
        sleep_ms(100)
finally:
    buzzer.value(0)
    d.off()
