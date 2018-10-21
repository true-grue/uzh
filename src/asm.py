# Uzh
# Author: Peter Sovietov

OPCODES = dict(
  NOP=0,
  LOOP=4,
  NOT=16,
  SHL=17,
  SHR=18,
  SHRA=19,
  INPORT=20,
  SWAP=21,
  SHL8=22,
  SHR8=23,
  UPDATE=25,
  FROMR=26,
  RETB=27,
  DUP=32,
  OVER=33,
  SAVEA=35,
  SAVEB=36,
  LOCALR=37,
  GETSP=38,
  LIT0=39,
  LITM1=40,
  GETFP=41,
  KEY=42,
  DEPTH=43,
  GETTEMP=44,
  PLUS=64,
  MINUS=65,
  AND=66,
  OR=67,
  XOR=68,
  EQUAL=69,
  ULESS=70,
  UGREATER=71,
  MULT=72,
  CALL=73,
  DROP=80,
  JMP=81,
  RJMP=82,
  SETDEPTH=83,
  TOR=84,
  SETTEMP=85,
  RIF=86,
  UNTIL=87,
  ARGFETCH=88,
  FETCH=89,
  STORE=90,
  ARGSTORE=91,
  OUTPORT=92,
  SETTABLE=93,
  IF=94,
  SETRP=95,
  LIT1=45,
  LOCK=29,
  UNLOCK=96,
  TID=46,
  STARTMULT=31
)

LITS = {0: "LIT0", 1: "LIT1", -1: "LITM1"}

def lit(x):
  x &= 0xffffffff
  if x & (1 << 31):
    x |= -1 << 31
  r = [] 
  while x not in (0, 1, -1):
    r.append(int(x & 127) | 128)
    x >>= 7
  return [OPCODES[LITS[x]]] + list(reversed(r))

def asm(text):
  r = []
  for x in text.split():
    r.extend([OPCODES[x]] if x in OPCODES else lit(int(x)))
  return r
