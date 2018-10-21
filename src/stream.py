# Uzh
# Author: Peter Sovietov

def get_val(x, by_4):
  r = []
  for i in range(by_4):
    r.append((x & 0xf) | (i << 4))
    x >>= 4
  return r

def make(code, data, core=0):
  stream = [224 + core, 243, 240]
  for x in data:
    stream += get_val(x, 8) + [245, 242]
  stream.append(240)
  for x in code:
    stream += get_val(x, 2) + [241, 242]
  stream.append(244)
  return bytearray(stream)
