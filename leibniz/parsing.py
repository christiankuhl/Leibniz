from lark import Lark, Transformer, v_args
from .functions import *
from .base import Constant, Variable
from .session import Session, DEBUG
from .equations import Equation, Assertion

_function_terminals = "\n".join(f'{f.upper()}: "{f}"' for f in FUNCTION_NAMES)
_function_names = "\n| ".join(f"{f.upper()} -> func" for f in FUNCTION_NAMES)

_GRAMMAR = f"""
    ?start: expr | var_assign | equation
    ?var_assign: var ":=" expr
    ?equation: expr "=" expr
    ?expr: sum
    ?parexpr: "(" expr ")"
    {_function_terminals}
    ?funcname: {_function_names}
                | funcname "'"                                      -> deriv
    ?funcappl: (funcname) parexpr
    ?power: atom "^" atom                                           -> pow
    ?atom: atom_nonum
         | NUMBER                                                   -> number
    ?product: neg_atom "*" product                                  -> mul
         | neg_atom atom_nonum                                      -> mul
         | product "/" atom                                         -> div
         | neg_atom
    ?sum: product "+" sum                                           -> add
         | product "-" sum                                          -> sub
         | product
    ?var: NAME                                                      -> var
    ?atom_nonum: var
         | parexpr
         | power
         | funcappl
         | funcname
    ?neg_atom: "-" atom                                             -> neg
         | atom
    %import common.CNAME -> NAME
    %import common.NUMBER
    %import common.WS_INLINE
    %ignore WS_INLINE
"""

@v_args(inline=True)
class LeibnizTree(Transformer):
    from operator import add, sub, mul, truediv as div, neg, pow
    def __init__(self, session):
        self.session = session
    def var_assign(self, variable, value):
        self.session.vars[variable.name] = value
        return Assertion(variable, value)
    def number(self, value):
        return Constant(float(value))
    def var(self, name):
        return Variable(str(name))
    def func(self, name):
        return globals()[str(name)]()
    def deriv(self, function):
        return function.derivative
    def funcappl(self, function, argument):
        return function.evaluate_at(argument)
    def equation(self, left, right):
        return Equation(left, right)

SESSION = Session()
PARSER = Lark(_GRAMMAR, parser='lalr', start="start", transformer=LeibnizTree(SESSION), debug=DEBUG)
parse = PARSER.parse
