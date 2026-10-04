"""T03 - light whole rows one after another, using the scanning thread.

Learns that the picture is built row by row. Try:
  * ON_US small  -> dim row
  * ON_US large  -> brighter, but with a long frame time (flicker!)
Compare PIPELINED = False / True: it should look the same.
"""
from display import Display, ROWS, COLS
from utime import sleep_ms

PIPELINED = True
ON_US = 300

d = Display()
d.on_us = ON_US
try:
    for row in list(range(ROWS)) + list(range(ROWS - 2, 0, -1)):
        d.clear()
        for c in range(COLS):
            d.pixel(c, row)
        d.start(pipelined=PIPELINED)
        sleep_ms(400)
finally:
    d.off()
