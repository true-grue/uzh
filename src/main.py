# Uzh
# Author: Peter Sovietov

from .tools import error, apply_rule
from .parse import make_parser
from .macro import MACROS
from .ir import ir
from .opt import opt
from .gen import gen

class Compiler:
  def __init__(self):
    self.parse = make_parser(self)
    self.filename = None
    self.source = None
    self.code = []
    self.data = [0, 0, 0]
    self.globs = {}
    self.macros = MACROS
    self.entry = None
    self.ir = []
    self.labels = {}
    self.patches = []

def parse(c, filename, source):
  c.filename, c.source = filename, source
  c.globs.update(c.parse())

def check_main(c):
  if "main" not in c.globs or c.globs["main"]["val"][0] != "Func":
    error("'main' function not found")

def compile(c):
  for n, c.entry in c.globs.items():
    val = c.entry["val"]
    if val[0] == "Func":
      c.entry["offs"] = len(c.code)
      c.ir.extend(apply_rule(ir, val[2], c=c))
    else:
      c.entry["offs"] = len(c.data)
      c.data.extend(val[1] if val[0] == "Array" else [val[1]])
  check_main(c)
  opt(c)
  gen(c)
  for f in c.patches:
    f()
  return c
