from lark import Lark, Transformer, v_args
from .functions import *
from .base import Constant, Variable

_function_grammar = "\n | ".join(f'"{f}" parexpr -> _{f.lower()}' for f in FUNCTION_NAMES)

_GRAMMAR = f"""
    ?expr: sum
    ?parexpr: "(" expr ")"
    ?function: {_function_grammar}
    ?power: atom "^" atom           -> pow
    ?product: atom "*" product      -> mul
         | atom "/" product         -> div
         | atom
    ?sum: product "+" sum           -> add
         | product "-" sum          -> sub
         | product
    ?atom: NUMBER                   -> number
         | "-" atom                 -> neg
         | NAME                     -> var
         | parexpr
         | power
         | function
    %import common.CNAME -> NAME
    %import common.NUMBER
    %import common.WS_INLINE
    %ignore WS_INLINE
"""

@v_args(inline=True)
class LeibnizTree(Transformer):
    from operator import add, sub, mul, truediv as div, neg, pow
    for function in FUNCTION_NAMES:
        _code = f"_{function.lower()} = lambda self, expr: {function}(expr)"
        exec(_code)
    def __init__(self):
        self.vars = {}
    def assign_var(self, name, value):
        self.vars[name] = value
        return value
    def number(self, value):
        return Constant(float(value))
    def var(self, name):
        return Variable(name)

PARSER = Lark(_GRAMMAR, parser='lalr', transformer=LeibnizTree(), start="expr")
parse = PARSER.parse

def repl():
    while True:
        try:
            s = input('> ')
        except EOFError:
            break
        print(f"{parse(s):tree}")

