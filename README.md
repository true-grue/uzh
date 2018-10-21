# Uzh

Uzh is a tiny compiler for FPGA soft processor Zmey (32-bit stack-based architecture with multithreading support).

Uzh language is a statically compiled subset of Python.

Uzh is based on [raddsl](https://github.com/true-grue/raddsl) toolset.

Simple example.

```python
# a function with host decorator is for compile-time execution
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

```
