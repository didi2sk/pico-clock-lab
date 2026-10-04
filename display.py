"""Low level driver of the 8 x (32) LED matrix, written for learning.

How the matrix works (see README.md):
  * only ONE row is lit at a time (row decoder SM5166P, address pins A0..A2)
  * the columns of that row come from a 32-bit shift register + latch (2x SM16106)
  * the rows are scanned so fast that the eye sees the whole picture

Every hardware signal has its own tiny method (blank/show/select_row/shift/latch),
so the tests can use them one by one.
"""
import _thread
from machine import Pin
from utime import sleep_us, sleep_ms, ticks_us, ticks_diff

import pins

ROWS = 8
COLS = 32       # shift positions of the two SM16106 chips
VISIBLE = 24    # columns 0..23 are the visible ones (see t02_pixel_walk.py)


class Display:
    def __init__(self):
        self.addr = [Pin(p, Pin.OUT, value=0) for p in pins.ROW_ADDR]
        self.oe = Pin(pins.OE, Pin.OUT, value=1)    # 1 = off
        self.sdi = Pin(pins.SDI, Pin.OUT, value=0)
        self.clk = Pin(pins.CLK, Pin.OUT, value=0)
        self.le = Pin(pins.LE, Pin.OUT, value=0)

        self.frame = [[0] * COLS for _ in range(ROWS)]   # frame[row][col] = 0/1
        self.on_us = 200            # how long one row is lit
        self.pipelined = True       # see scan_frame_pipelined()
        self.frames = 0
        self._run = False
        self._stopped = True

    # ---------- frame buffer ----------
    def clear(self):
        for row in self.frame:
            for i in range(COLS):
                row[i] = 0

    def fill(self, value=1):
        for row in self.frame:
            for i in range(COLS):
                row[i] = value

    def pixel(self, x, y, value=1):
        if 0 <= x < COLS and 0 <= y < ROWS:
            self.frame[y][x] = value

    # ---------- hardware primitives ----------
    def blank(self):
        self.oe.value(1)            # all LEDs off

    def show(self):
        self.oe.value(0)            # LEDs on (the selected row, latched columns)

    def select_row(self, r):
        for bit, pin in enumerate(self.addr):
            pin.value((r >> bit) & 1)

    def shift(self, bits):
        """Clock 32 bits into the shift register. bits[0] goes in first."""
        clk, sdi = self.clk, self.sdi
        for v in bits:
            clk.value(0)
            sdi.value(v)
            clk.value(1)

    def latch(self):
        self.le.value(1)            # shift register -> outputs
        self.le.value(0)

    # ---------- static (no scanning) - for experiments ----------
    def light_static(self, row, cols):
        """Light the given columns of ONE row and keep it lit (no scanning)."""
        self.stop()
        bits = [0] * COLS
        for c in cols:
            bits[c] = 1
        self.blank()
        self.shift(bits)
        self.latch()
        self.select_row(row)
        self.show()

    def off(self):
        self.stop()
        self.blank()

    # ---------- scanning ----------
    def scan_frame_simple(self):
        """Original method: shift while dark, then light the row and wait."""
        f = self.frame
        for r in range(ROWS):
            self.blank()
            self.shift(f[r])
            self.latch()
            self.select_row(r)
            self.show()
            sleep_us(self.on_us)
            self.blank()

    def prime(self):
        """Pipelined mode: put row 0 into the latch before the first frame."""
        self.blank()
        self.shift(self.frame[0])
        self.latch()

    def scan_frame_pipelined(self):
        """Shift the NEXT row while the current row is lit.

        The latch keeps the outputs stable while new bits are shifted into the
        shift register, so the shifting time does not take away light time.
        (Assumes the SM16106 shift register and latch are independent.)
        """
        f = self.frame
        for r in range(ROWS):
            self.select_row(r)              # latch already holds row r, LEDs still off
            self.show()
            t0 = ticks_us()
            self.shift(f[(r + 1) % ROWS])   # prepare row r+1 while row r is lit
            rest = self.on_us - ticks_diff(ticks_us(), t0)
            if rest > 0:
                sleep_us(rest)
            self.blank()
            self.latch()                    # row r+1 -> outputs (LEDs are off, no ghosts)

    def _loop(self):
        try:
            if self.pipelined:
                self.prime()
            while self._run:
                if self.pipelined:
                    self.scan_frame_pipelined()
                else:
                    self.scan_frame_simple()
                self.frames += 1
        except Exception as e:
            print("display thread error:", e)
        self.blank()
        self._stopped = True

    def start(self, pipelined=None):
        """Scan the frame buffer continuously on the second core."""
        self.stop()
        if pipelined is not None:
            self.pipelined = pipelined
        self._run = True
        self._stopped = False
        _thread.start_new_thread(self._loop, ())

    def stop(self):
        if self._run:
            self._run = False
            for _ in range(300):
                if self._stopped:
                    break
                sleep_ms(1)
        self.blank()

    # ---------- measurements ----------
    def time_shift(self, n=50):
        """Microseconds needed to shift one row (32 bits)."""
        self.stop()
        bits = [1, 0] * (COLS // 2)
        t0 = ticks_us()
        for _ in range(n):
            self.shift(bits)
        dt = ticks_diff(ticks_us(), t0)
        self.blank()
        return dt / n

    def measure(self, pipelined, on_us, frames=50):
        """Microseconds per whole frame (8 rows), scanning in this thread."""
        self.stop()
        self.on_us = on_us
        if pipelined:
            self.prime()
        t0 = ticks_us()
        for _ in range(frames):
            if pipelined:
                self.scan_frame_pipelined()
            else:
                self.scan_frame_simple()
        dt = ticks_diff(ticks_us(), t0)
        self.blank()
        return dt / frames
