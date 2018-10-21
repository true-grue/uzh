# Uzh
# Author: Peter Sovietov

from .tools import *

@act
def fold_const(t, X):
  if X in t.c.globs:
    e = t.c.globs[X]
    if e["val"][0] == "Const":
      t.out = Int(e["val"][1])
  return True

@act
def fold_binop(t, O, X, Y):
  r = 0
  x, y = X[1], Y[1]
  if O == "+":
    r = x + y
  elif O == "-":
    r = x - y
  elif O == "&":
    r = x & y
  elif O == "|":
    r = x | y
  elif O == "^":
    r = x ^ y
  elif O == "*":
    r = x * y
  elif O == "<<":
    r = x << y
  elif O == ">>":
    r = x >> y
  elif O == "<":
    r = x < y
  elif O == ">":
    r = x > y
  elif O == "<=":
    r = x <= y
  elif O == ">=":
    r = x >= y
  elif O == "==":
    r = x == y
  elif O == "!=":
    r = x != y
  elif O == "&&":
    r = x and y
  elif O == "||":
    r = x or y
  else:
    return False
  t.out = Int(int(r))
  return True

@act
def fold_unop(t, O, X):
  r = 0
  x = X[1]
  if O == "-":
    r = -x
  elif O == "~":
    r = ~x
  elif O == "!":
    r = not x
  else:
    return False
  t.out = Int(int(r))
  return True

fold = bottomup(opt(rule(
  seq(Id(X), fold_const),
  seq(UnOp(let(O=id), let(X=Int(id))), fold_unop),
  seq(BinOp(let(O=id), let(X=Int(id)), let(Y=Int(id))), fold_binop),
  seq(BinOp(one_of("+ - | ^ << >>"), X, Int(0)), to(lambda v: v.X)),
  seq(BinOp(one_of("+ - | ^ << >>"), Int(0), X), to(lambda v: v.X)),
  seq(BinOp("*", X, Int(1)), to(lambda v: v.X)),
  seq(BinOp("*", Int(1), X), to(lambda v: v.X)),
)))

trans_op = topdown(repeat(rule(alt(
  seq(BinOp("!=", X, Y), to(lambda v: UnOp("!", BinOp("==", v.X, v.Y)))),
  seq(BinOp("<=", X, Y), to(lambda v: UnOp("!", BinOp(">", v.X, v.Y)))),
  seq(BinOp(">=", X, Y), to(lambda v: UnOp("!", BinOp("<", v.X, v.Y)))),
  seq(UnOp("-", X), to(lambda v: BinOp("-", Int(0), v.X))),
  seq(UnOp("!", X), to(lambda v: BinOp("==", v.X, Int(0))))
))))

trans_for = topdown(opt(rule(
  For(Id(X), Call(Id("range"), [Y]), Z), to(lambda v: [
    Assign(Id(v.X), Int(0)),
    While(BinOp("<", Id(v.X), v.Y),
      v.Z + [Assign(Id(v.X), BinOp("+", Id(v.X), Int(1)))])
  ])
)))

trans = seq(fold, trans_for, trans_op)
