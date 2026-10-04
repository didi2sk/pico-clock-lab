"""Tiny text helpers on top of Display (4x7 font, scrolling)."""
from font import FONT


def text_columns(text):
    """Convert text to a list of columns; each column is a 7-bit number (bit 0 = top)."""
    cols = []
    for ch in text.upper():
        width, rows = FONT.get(ch, FONT[" "])
        for c in range(width):
            bits = 0
            for r in range(7):
                if (rows[r] >> c) & 1:
                    bits |= 1 << r
            cols.append(bits)
        cols.append(0)          # one empty column between characters
    return cols


def draw_columns(disp, cols, offset, x0=2, width=22, y0=1):
    """Draw a window of `cols` starting at `offset` into the frame buffer."""
    disp.clear()
    for x in range(width):
        i = offset + x
        if 0 <= i < len(cols):
            bits = cols[i]
            for r in range(7):
                if (bits >> r) & 1:
                    disp.pixel(x0 + x, y0 + r)
