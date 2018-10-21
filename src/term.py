# Uzh
# Author: Peter Sovietov

class Head(dict):
  def __eq__(self, right):
    return self["tag"] == right
  def __ne__(self, right):
    return not self.__eq__(right)

def make_term(tag):
  return lambda *a, **k: (Head(tag=tag, **k),) + a

is_term = lambda x: isinstance(x, tuple)
is_term_list = lambda x: isinstance(x, list)

Id = make_term("Id")
Int = make_term("Int")
BinOp = make_term("BinOp")
UnOp = make_term("UnOp")
Index = make_term("Index")
Assign = make_term("Assign")
Call = make_term("Call")
If = make_term("If")
While = make_term("While")
For = make_term("For")
Return = make_term("Return")
Const = make_term("Const")
Array = make_term("Array")
Func = make_term("Func")

Local = make_term("Local")
Global = make_term("Global")
Push = make_term("Push")
Load = make_term("Load")
Store = make_term("Store")
Label = make_term("Label")
Goto = make_term("Goto")
GotoIf0 = make_term("GotoIf0")
ShlConst = make_term("ShlConst")
ShrConst = make_term("ShrConst")
Nop = make_term("Nop")
Asm = make_term("Asm")
