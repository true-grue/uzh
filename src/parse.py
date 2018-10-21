# Uzh
# Author: Peter Sovietov

import ast
from .tools import error, type_name
from .term import *

OPERATORS = dict(
  And="&&",
  Or="||",
  Add="+",
  Sub="-",
  Mult="*",
  LShift="<<",
  RShift=">>",
  BitOr="|",
  BitXor="^",
  BitAnd="&",
  Invert="~",
  Not="!",
  USub="-",
  Eq="==",
  NotEq="!=",
  Lt="<",
  LtE="<=",
  Gt=">",
  GtE="<="
)

def ast_error(t):
  pos = ", line %s" % t.lineno if hasattr(t, "lineno") else ""
  error(("unsupported AST node '%s'" + pos) % type_name(t))

def make_parser(c):
  MOD_G = dict(host=lambda f: f)

  many = lambda t: [parse_ast(x) for x in t]

  def compare(t):
    if len(t.ops) == 1 and len(t.comparators) == 1:
      return BinOp(
        parse_op(t.ops[0]), parse_ast(t.left), parse_ast(t.comparators[0]),
        line=t.lineno
      )
    ast_error(t)

  def bool_op(t):
    op, r = parse_op(t.op), parse_ast(t.values[0])
    for v in t.values[1:]:
      r = BinOp(op, r, parse_ast(v), line=t.lineno)
    return r

  def subscript(t):
    if isinstance(t.slice, ast.Index):
      return Index(parse_ast(t.value), parse_ast(t.slice.value), line=t.lineno)
    ast_error(t)

  def assign(t):
    if len(t.targets) == 1 and \
        isinstance(t.targets[0], (ast.Name, ast.Subscript)):
      return Assign(parse_ast(t.targets[0]), parse_ast(t.value), line=t.lineno)
    ast_error(t)

  def aug_assign(t):
    target = parse_ast(t.target)
    return Assign(
      target, BinOp(parse_op(t.op), target, parse_ast(t.value), line=t.lineno),
      line=t.lineno
    )

  def while_stmt(t):
    if not t.orelse:
      return While(parse_ast(t.test), many(t.body), line=t.lineno)
    ast_error(t)

  def for_stmt(t):
    if not t.orelse:
      return For(
        parse_ast(t.target), parse_ast(t.iter), many(t.body), line=t.lineno
      )
    ast_error(t)

  def is_macro(n):
    return n in c.macros and c.macros[n]["val"][0] == "macro"

  def eval_args(args):
    return [eval(compile(ast.Expression(body=x), c.filename, "eval"),
      MOD_G) for x in args]

  def call_macro(t):
    if isinstance(t.func, ast.Name) and is_macro(t.func.id):
      return c.macros[t.func.id]["func"](c, *eval_args(t.args))
    return Call(parse_ast(t.func), many(t.args), line=t.lineno)

  def parse_op(t):
    n = type_name(t)
    if n in OPERATORS:
      return OPERATORS[n]
    ast_error(t)

  def parse_ast(t):
    n = type_name(t)
    if n in AST:
      return AST[n](t)
    ast_error(t)

  AST = dict(
    Name=lambda t: Id(t.id, line=t.lineno),
    Num=lambda t: Int(int(t.n), line=t.lineno),
    NameConstant=lambda t: Int(1 if t.value else 0, line=t.lineno),
    BinOp=lambda t: BinOp(
      parse_op(t.op), parse_ast(t.left), parse_ast(t.right), line=t.lineno
    ),
    UnaryOp=lambda t: UnOp(
      parse_op(t.op), parse_ast(t.operand), line=t.lineno
    ),
    Expr=lambda t: parse_ast(t.value),
    Call=call_macro,
    Return=lambda t: Return(
      parse_ast(t.value) if t.value else None, line=t.lineno
    ),
    If=lambda t: If(
      parse_ast(t.test), many(t.body), many(t.orelse), line=t.lineno
    ),
    Compare=compare,
    BoolOp=bool_op,
    Subscript=subscript,
    Assign=assign,
    AugAssign=aug_assign,
    While=while_stmt,
    For=for_stmt,
    Pass=lambda t: Nop(line=t.lineno)
  )

  def parse_elem(x):
    if isinstance(x, (int, float)):
      return int(x)
    error("unsupported data type %s" % type(x))

  def parse_data(data):
    if isinstance(data, list):
      return Array([parse_elem(x) for x in data])
    return Const(parse_elem(data))

  def make_var(t):
    n = t.targets[0].id
    val = parse_data(MOD_G[n])
    return dict(
      name=n,
      val=val,
      offs=None
    )

  def make_func(t):
    val = Func([x.arg for x in t.args.args], many(t.body), line=t.lineno)
    return dict(
      name=t.name,
      val=val,
      offs=None,
      args=len(val[1]),
      locs=dict([(v, i) for i, v in enumerate(val[1])]),
      ret=None
    )

  def parse_module(body):
    g = {}
    for t in body:
      exec(compile(ast.Module(body=[t]), c.filename, "exec"), MOD_G)
      if isinstance(t, ast.Assign) and len(t.targets) == 1:
        if isinstance(t.targets[0], ast.Name):
          g[t.targets[0].id] = make_var(t)
      elif isinstance(t, ast.FunctionDef) and not t.decorator_list:
        g[t.name] = make_func(t)
    return g

  return lambda: parse_module(ast.parse(c.source, filename=c.filename).body)
