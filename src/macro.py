# Uzh
# Author: Peter Sovietov

from .tools import *

MACROS = {}

def macro(args, ret, name=None):
  def add(f):
    n = name if name else f.__name__
    MACROS[n] = dict(name=n, val=("macro",), args=args, ret=ret, func=f)
  return add

def prim(args, ret, name=None):
  def add(f):
    n = name if name else f.__name__
    MACROS[n] = dict(name=n, val=("prim",), args=args, ret=ret, func=f)
  return add

@macro(1, 1, name="len")
def len1(c, x):
  return Int(len(x))

@macro(1, 0)
def nops(c, x):
  return Asm("NOP " * x)

@prim(1, 1)
def digital_read(c, port):
  return [x, Asm("INPORT")]

@prim(2, 0)
def digital_write(c, port, val):
  return [val, port, Asm("SETTEMP OUTPORT")]
