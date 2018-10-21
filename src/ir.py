# Uzh
# Author: Peter Sovietov

from .tools import *
from .trans import trans

line = lambda t: t[0]["line"]

def ir_error(t, msg, line=None):
  pos = ", line %d" % line if line is not None else ""
  error("%s: %s%s" % (t.c.entry["name"], msg, pos))

def lookup(t):
  n = t.out[1]
  for scope in t.c.entry["locs"], t.c.globs, t.c.macros:
    if n in scope:
      return scope[n]
  ir_error(t, "unknown name '%s'" % n, line(t.out))

def make_return(t, ret):
  if t.c.entry["ret"] is not None and t.c.entry["ret"] != ret:
    ir_error(t, "return value mismatch")
  t.c.entry["ret"] = ret
  return Return(t.c.entry["name"])

def epilog(t):
  t.out = [Func(t.c.entry["name"])] + t.out
  if t.out[-1][0] != "Return":
    t.out.append(make_return(t, 0))
  return True

def local(t):
  locs = t.c.entry["locs"]
  if t.out not in locs:
    locs[t.out] = len(locs)
  return True

def label(t):
  t.out = len(t.c.labels)
  t.c.labels[t.out] = None
  return True

def ident(t):
  n = t.out[1]
  locs = t.c.entry["locs"]
  if n in locs:
    t.out = [Push(Local(locs[n])), Load()]
  elif n in t.c.globs:
    t.out = [Push(Global(n))]
  else:
    ir_error(t, "unknown name '%s'" % n, line(t.out))
  return True

@act
def return_act(t, X):
  t.out = [make_return(t, 0)] if X is None else [X, make_return(t, 1)]
  return True

@act
def args(t, Y, Z):
  e = lookup(t)
  if e["val"][0] in ("Func", "prim") and e["args"] != len(Y):
    ir_error(t, "argument mismatch in '%s'" % e["name"], line(Z))
  return True

@act
def prim_call(t, Y, Z):  
  n = t.out[1]
  if not lookup(t)["val"][0] == "prim":
    return False
  t.out = t.c.macros[n]["func"](t.c, *Y)
  return True

expr = delay(lambda: expr)
block = delay(lambda: block)

if_stmt = rule(If(let(X=expr), let(Y=block), let(Z=block)),
  let(L1=label), to(lambda v: v.Z), alt(
    seq([], to(lambda v: [v.X, GotoIf0(v.L1), v.Y, Label(v.L1)])),
    seq(let(L2=label), to(lambda v: [
      v.X,
      GotoIf0(v.L1),
      v.Y,
      Goto(v.L2),
      Label(v.L1),
      v.Z,
      Label(v.L2)
    ]))
))

call_expr = rule(Call(Z, let(Y=each(expr))), to(lambda v: v.Z),
  opt(seq(Id(id), args)), alt(
    prim_call,
    seq(let(X=expr), to(lambda v: [v.Y, v.X, Call()]))
))

expr = rule(alt(
  seq(Id(id), ident),
  seq(let(X=Int(id)), to(lambda v: [Push(v.X)])),
  seq(UnOp(X, let(Y=expr)), to(lambda v: [v.Y, UnOp(v.X)])),
  seq(BinOp(let(X=one_of("+ - * & | ^ < > ==")), let(Y=expr), let(Z=expr)),
    to(lambda v: [v.Y, v.Z, BinOp(v.X)])),
  seq(BinOp("&&", X, Y), to(lambda v: If(v.X, [v.Y], [Int(0)])), if_stmt),
  seq(BinOp("||", X, Y), to(lambda v: If(v.X, [Int(1)], [v.Y])), if_stmt),
  seq(BinOp("<<", let(X=expr), Int(Y)), to(lambda v: [v.X, ShlConst(v.Y)])),
  seq(BinOp(">>", let(X=expr), Int(Y)), to(lambda v: [v.X, ShrConst(v.Y)])),
  seq(Index(let(X=expr), let(Y=expr)),
    to(lambda v: [v.X, v.Y, BinOp("+"), Load()])),
  call_expr
))

assign_stmt = rule(Assign(let(X=seq(opt(Id(local)), expr)), let(Y=expr)),
  to(lambda v: [v.Y, v.X[:-1], Store()]))

while_stmt = rule(While(let(X=expr), let(Y=block)),
  let(L1=label), let(L2=label), to(lambda v: [
    Label(v.L1),
    v.X,
    GotoIf0(v.L2),
    v.Y,
    Goto(v.L1),
    Label(v.L2)
  ])
)

return_stmt = rule(Return(let(X=alt(None, expr))), return_act)

stmt = alt(
  assign_stmt,
  if_stmt,
  while_stmt,
  return_stmt,
  call_expr,
  block,
  term_of("Nop Asm")
)

block = each(stmt)

ir = seq(trans, block, flatten, epilog)
