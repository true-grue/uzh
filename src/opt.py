# Uzh
# Author: Peter Sovietov

from .tools import *

def peep_ir(f):
  def walk(t):
    t.pos, t.pat_size = 0, 0
    ir = t.out
    while t.pos < len(ir):
      t.out = ir
      if perform(t, f):
        ir[t.pos:t.pos + t.pat_size] = t.out
      else:
        t.pos += 1
    t.out = flatten_term(ir)
    return True
  return walk

def peep(pat):
  def walk(t):
    t.pat_size = len(pat)
    t.out = t.out[t.pos:t.pos + t.pat_size]
    return perform(t, pat)
  return walk

def opt(c):
  c.ir = apply_rule(peep_ir(opt_rules), c.ir, c=c)

opt_rules = alt(
  rule(peep([X, Push(Int(0)), BinOp("+")]), to(lambda v: [v.X])),
  rule(peep([Nop()]), to(lambda v: []))
)
