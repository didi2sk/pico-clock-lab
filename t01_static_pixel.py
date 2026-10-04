"""T01 - light ONE LED statically (no scanning).

Learns: the three things you need to light an LED - the row (decoder address),
the column (bit in the shift register) and the output enable.

Change ROW and COL and press F5 again. Which LED lights up?
Stop with the Stop button; the display is switched off on exit.
"""
from display import Display
from utime import sleep

ROW = 3       # 0..7
COL = 10      # 0..31  (0..23 are visible, see t02)

d = Display()
d.light_static(ROW, [COL])
print("row", ROW, "column", COL, "- Ctrl+C to finish")
try:
    while True:
        sleep(1)
finally:
    d.off()
