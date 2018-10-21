import math

# constants (read-only)
D1 = 10
D2 = 25

# "WS_PORT" will be placed in the data memory
WS_PORT = [0]

def delay(n):
  while n:
    n -= 1

def ws_set_port(addr):
  WS_PORT[0] = addr

def ws_send_8(x):
  i = 8
  while i:
    if x & 128:
      digital_write(WS_PORT[0], 1)
      nops(D2)
      digital_write(WS_PORT[0], 0)
      nops(D1)
    else:
      digital_write(WS_PORT[0], 1)
      nops(D1)
      digital_write(WS_PORT[0], 0)
      nops(D2)
    x <<= 1
    i -= 1

def ws_fill(r, g, b, size):
  while size:
    ws_send_8(g)
    ws_send_8(r)
    ws_send_8(b)
    size -= 1

def ws_send_buf(buf, size):
  while size:
    ws_send_8(buf[1] >> 1)
    ws_send_8(buf[0] >> 1)
    ws_send_8(buf[2] >> 1)
    buf += 3
    size -= 1

# a host function is for compile-time execution
# you may use all Python features here
@host
def make_sine_table(size):
  return [127 * math.sin(2 * math.pi * i / size) + 127 for i in range(size)]

# sine_table will be placed in the data memory
sine_table = make_sine_table(32)

# buf will be placed in the data memory
buf = [0, 0, 0] * 54

# main function will be placed in the code memory
# and will be called on startup
def main():
  phase = 0
  ws_set_port(17004)
  while True:
    for i in range(len(buf)):
      buf[i * 3] = sine_table[(i + phase) & (len(sine_table) - 1)]
    ws_send_buf(buf, len(buf))
    phase += 1
    delay(10000)
