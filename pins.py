"""Pin assignment of Waveshare Pico-Clock-Green (taken from the original firmware)."""

# --- LED matrix: 2x SM16106 (columns, 32-bit shift register + latch) + SM5166P (row decoder)
SDI = 11          # serial data into the shift register
CLK = 10          # shift clock (data is taken on the rising edge)
LE = 12           # latch enable: shift register -> outputs (pulse 1 -> 0)
OE = 13           # output enable, ACTIVE LOW: 0 = LEDs on, 1 = all off
ROW_ADDR = (16, 18, 22)   # A0, A1, A2 of the row decoder (binary row number 0..7)

# --- other hardware on the board
LIGHT_ADC = 26    # photoresistor (higher raw value = darker)
BUZZER = 14       # active buzzer (1 = sounds)
BUTTONS = (2, 17, 15)     # buttons 1, 2, 3 (pressed = 0, internal pull-up)
I2C_SDA = 6       # DS3231 (not used in the lab)
I2C_SCL = 7
