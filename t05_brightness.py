"""T05 - brightness = how long each row is lit (ON_US).

Sweeps ON_US up and down. Watch and note:
  * the lowest ON_US where you can still see the picture
  * where you start to see flicker
  * in PIPELINED mode ON_US smaller than the shift time makes no difference
    (the row is lit at least as long as the shifting takes) - run t06 to see the shift time
"""
from display import Display
from utime import sleep_ms

PIPELINED = True
STEPS = [5, 10, 20, 50, 100, 200, 400, 800, 1500, 2500]

d = Display()
d.fill(1)
try:
    d.start(pipelined=PIPELINED)
    for on_us in STEPS + STEPS[::-1]:
        d.on_us = on_us
        print("ON_US", on_us)
        sleep_ms(1200)
finally:
    d.off()
