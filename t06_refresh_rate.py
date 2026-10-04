"""T06 - measure the shift time and the refresh rate (no display needed, just numbers).

Prints, for several ON_US values:
  * frame time (8 rows)
  * refresh rate in Hz  (below ~100 Hz you may see flicker)
  * duty = fraction of the frame in which the LEDs are lit
for both scanning methods, so you can see what pipelining brings.

Set CPU_MHZ to 125 / 200 / 250 to see how the CPU speed changes the shift time.
"""
import machine
from display import Display, ROWS

CPU_MHZ = 250

machine.freq(CPU_MHZ * 1_000_000)
d = Display()
d.fill(1)

shift = d.time_shift()
print("CPU %d MHz, shifting 32 bits takes %.0f us (this is dead time in the simple method)" % (CPU_MHZ, shift))
print()
print("%8s | %-34s | %-34s" % ("ON_US", "simple: frame us / Hz / duty", "pipelined: frame us / Hz / duty"))
for on_us in (10, 50, 100, 200, 400, 800, 1500):
    cols = []
    for pipelined in (False, True):
        frame = d.measure(pipelined, on_us)
        lit = ROWS * (on_us if not pipelined else max(on_us, shift))
        cols.append("%7.0f / %5.0f / %4.1f%%" % (frame, 1_000_000 / frame, 100 * lit / frame))
    print("%8d | %-34s | %-34s" % (on_us, cols[0], cols[1]))
d.off()
