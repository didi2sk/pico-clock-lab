"""T04 - full-screen test patterns (all on, checkerboard, border, diagonal, columns).

Look for: dead LEDs, swapped/mirrored columns, ghosting (faint LEDs in a
neighbouring row), uneven brightness.
Set PIPELINED = False to compare with the original scanning method.
"""
from display import Display, ROWS, VISIBLE
from utime import sleep

PIPELINED = True
ON_US = 300
SECONDS = 3

d = Display()
d.on_us = ON_US


def all_on():
    d.fill(1)


def checkerboard():
    d.clear()
    for y in range(ROWS):
        for x in range(VISIBLE):
            d.pixel(x, y, (x + y) & 1)


def border():
    d.clear()
    for x in range(VISIBLE):
        d.pixel(x, 0)
        d.pixel(x, ROWS - 1)
    for y in range(ROWS):
        d.pixel(0, y)
        d.pixel(VISIBLE - 1, y)


def diagonal():
    d.clear()
    for x in range(VISIBLE):
        d.pixel(x, int(x * (ROWS - 1) / (VISIBLE - 1)))


def stripes():
    d.clear()
    for x in range(0, VISIBLE, 2):
        for y in range(ROWS):
            d.pixel(x, y)


try:
    d.start(pipelined=PIPELINED)
    for name, fn in (("all on", all_on), ("checkerboard", checkerboard), ("border", border),
                     ("diagonal", diagonal), ("column stripes", stripes)):
        print(name)
        fn()
        sleep(SECONDS)
finally:
    d.off()
