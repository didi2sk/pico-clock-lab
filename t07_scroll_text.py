"""T07 - scrolling text (4x7 font from the original firmware).

Edit TEXT. Letters A-Z, digits and . : - / are available.
"""
from display import Display
from gfx import text_columns, draw_columns
from utime import sleep_ms

TEXT = "HELLO PICO 0123456789"
SPEED_MS = 80
ON_US = 300
PIPELINED = True

d = Display()
d.on_us = ON_US
cols = text_columns(TEXT)
try:
    d.start(pipelined=PIPELINED)
    while True:
        for offset in range(-22, len(cols)):
            draw_columns(d, cols, offset)
            sleep_ms(SPEED_MS)
finally:
    d.off()
