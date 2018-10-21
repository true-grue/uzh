# Uzh
# Author: Peter Sovietov

from .tools import *
from .asm import asm

DATA_SIZE = 4096
DSTACK_SIZE = 32
RSTACK_SIZE = 128

STUB = asm("NOP NOP NOP")

STARTUP = asm("""
SHL8 SHL8 SHL8 SHL8 FETCH SAVEA SETDEPTH
1 FETCH SAVEA SETRP
2 FETCH SAVEA 0 0 SETTEMP STORE JMP
""")

def get_loc_offset(t, x):
  args = t.c.entry["args"]
  return len(t.c.entry["locs"]) - (args - x - 1 if x < args else x)

def make_patch(code, pc, val):
  if len(val) > len(STUB):
    error("address size %d is too big" % len(val))
  code[pc:pc + len(val)] = val

@act
def func(t, X):
  t.c.entry = t.c.globs[X]
  t.c.entry["offs"] = len(t.c.code)
  args = t.c.entry["args"]
  temps_size = len(t.c.entry["locs"]) - args
  t.out = asm("TOR " * args)
  if temps_size:
    t.out += asm("GETSP %d PLUS SETRP" % temps_size)
  return True

@act
def label(t, X):
  t.c.labels[X] = len(t.c.code)
  t.out = []
  return True

@act
def epilog(t, X):
  locs_size = len(t.c.entry["locs"])
  t.out = asm("FROMR RETB")
  if locs_size:
    t.out = asm("GETSP %d MINUS SETRP" % locs_size) + t.out
  return True

@act
def push_local(t, X):
  t.out = asm("GETSP %d MINUS" % get_loc_offset(t, X))
  return True

@act
def push_global(t, X):
  e = t.c.globs[X]
  pc = len(t.c.code)
  t.c.patches.append(lambda: make_patch(t.c.code, pc, asm("%d" % e["offs"])))
  t.out = STUB[:]
  return True

def push_label(t, x):
  labels = t.c.labels
  pc = len(t.c.code)
  t.c.patches.append(lambda: make_patch(t.c.code, pc, asm("%d" % labels[x])))
  t.out = STUB[:]

@act
def goto_if_0(t, X):
  push_label(t, X)
  t.out += asm("SETTEMP IF")
  return True

@act
def goto(t, X):
  push_label(t, X)
  t.out += asm("JMP")
  return True

@act
def shl_const(t, X):
  r = [asm("SHL8") for i in range(X // 8)]
  t.out = sum(r + [asm("SHL") for i in range(X % 8)], [])
  return True

@act
def shr_const(t, X):
  r = [asm("SHR8") for i in range(X // 8)]
  t.out = sum(r + [asm("SHR") for i in range(X % 8)], [])
  return True

stmt = rule(alt(
  seq(Push(Int(X)), to(lambda v: asm("%d" % v.X))),
  seq(Push(Local(X)), push_local),
  seq(Push(Global(X)), push_global),
  seq(Load(), to(lambda v: asm("FETCH SAVEA"))),
  seq(Store(), to(lambda v: asm("SETTEMP STORE"))),
  seq(Call(), to(lambda v: asm("CALL"))),
  seq(BinOp("+"), to(lambda v: asm("PLUS"))),
  seq(BinOp("-"), to(lambda v: asm("MINUS"))),
  seq(BinOp("&"), to(lambda v: asm("AND"))),
  seq(BinOp("|"), to(lambda v: asm("OR"))),
  seq(BinOp("^"), to(lambda v: asm("XOR"))),
  seq(BinOp("*"), to(lambda v: asm("STARTMULT NOP NOP NOP NOP MULT"))),
  seq(BinOp("<"), to(lambda v: asm("ULESS"))),
  seq(BinOp(">"), to(lambda v: asm("UGREATER"))),
  seq(BinOp("=="), to(lambda v: asm("EQUAL"))),
  seq(BinOp("~"), to(lambda v: asm("NOT"))),
  seq(ShlConst(X), shl_const),
  seq(ShrConst(X), shr_const),
  seq(Func(X), func),
  seq(Label(X), label),
  seq(Return(X), epilog),
  seq(GotoIf0(X), goto_if_0),
  seq(Goto(X), goto),
  seq(Nop(), to(lambda v: asm("NOP"))),
  seq(Asm(X), to(lambda v: asm(v.X)))
))

def startup(c):
  c.code.extend(STARTUP)
  sp = DATA_SIZE - DSTACK_SIZE
  c.data[0] = sp
  sp -= RSTACK_SIZE
  c.data[1] = sp

def gen(c):
  startup(c)
  for x in c.ir:
    c.code.extend(apply_rule(stmt, x, c=c))
  c.data[2] = c.globs["main"]["offs"]
