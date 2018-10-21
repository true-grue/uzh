# Uzh
# Author: Peter Sovietov

import sys
from raddsl.rewrite import *
from .term import *

X, Y, Z = let(X=id), let(Y=id), let(Z=id)

type_name = lambda t: type(t).__name__

term_list = lambda t: is_term_list(t.out)

def error(msg):
  print("error: %s" % msg)
  sys.exit(1)

def apply_rule(rule, node, **kwargs):
  t = Tree(node)
  for k in kwargs:
    setattr(t, k, kwargs[k])
  if not perform(t, rule):
    error("unsupported term")
  return t.out

def flatten_term(node):
  if is_term(node):
    map(flatten_term, node)
  elif is_term_list(node):
    lst = []
    for x in node:
      y = flatten_term(x)
      lst.extend(y if is_term_list(x) else [y])
    node[:] = lst
  return node

flatten = build(lambda t: flatten_term(t.out))

def one_of(words):
  w = words.split()
  return lambda t: t.out in w

def term_of(words):
  w = words.split()
  return lambda t: is_term(t.out) and t.out[0] in w
