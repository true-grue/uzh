# Uzh
# Author: Peter Sovietov

import sys
from src.main import Compiler, parse, compile
from src import stream

c = Compiler()
for filename in sys.argv[1:]:
  with open(filename) as f:
    parse(c, filename, f.read()) 
compile(c)
with open("stream.bin", "wb") as f:
  f.write(stream.make(c.code, c.data))
