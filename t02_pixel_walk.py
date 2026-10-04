"""T02 - walk ONE lit LED through all 8 x 32 positions.

Learns the real mapping between shift position (COL) and the physical column:
  * which COLs are visible (should be 24 of the 32)
  * the direction: does COL 0 appear on the left or on the right?
  * what does row 0 look like (day-of-week strip) and which rows are the text area

Write down what you see. Printed: "row r col c".
"""
from display import Display, ROWS, COLS
from utime import sleep_ms

DELAY_MS = 150

d = Display()
try:
    for row in range(ROWS):
        for col in range(COLS):
            print("row", row, "col", col)
            d.light_static(row, [col])
            sleep_ms(DELAY_MS)
finally:
    d.off()
print("done")
