"""
This module provides a REPL to interact with Leibniz functionality.
"""

from lark import Lark, Transformer, v_args
from .functions import *                                                    # pylint: disable=unused-wildcard-import, wildcard-import
from .base import Constant, Variable
from .session import Session, DEBUG
from .equations import Equation, Assertion

def _build_grammar():
    function_terminals = "\n".join(f'{f.upper()}: "{f}"' for f in FUNCTION_NAMES)
    function_names = "\n| ".join(f"{f.upper()} -> func" for f in FUNCTION_NAMES)
    return f"""
        ?start: expr | var_assign | equation | cmd
        cmd: "$"(DEBUG|SESSION|VARS|PYTHON)
        DEBUG: "debug"
        SESSION: "session"
        VARS: "vars"
        PYTHON: "python"                                                  
        ?var_assign: var ":=" expr
        ?equation: expr "=" expr
        ?expr: sum
        ?parexpr: "(" expr ")"
        {function_terminals}
        ?funcname: {function_names}
                    | funcname "'"                                      -> deriv
        ?funcappl: (funcname) parexpr
        ?power: atom "^" atom                                           -> pow
        ?atom: atom_nonum
            | NUMBER                                                    -> number
        ?product: neg_atom "*" product                                  -> mul
            | neg_atom atom_nonum                                       -> mul
            | product "/" atom                                          -> div
            | neg_atom
        ?sum: sum "+" product                                           -> add
            | sum "-" product                                           -> sub
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

_GRAMMAR = _build_grammar()

@v_args(inline=True)
class LeibnizTree(Transformer):
    "Transforms parse tree nodes into Leibniz expressions and session commands"
    from operator import add, sub, mul, truediv as div, neg, pow
    def __init__(self, session):
        super().__init__()
        self.session = session
    def var_assign(self, variable, value):                                  # pylint: disable=no-self-use
        self.session.vars[variable.name] = value
        return Assertion(variable, value)
    def number(self, value):                                                # pylint: disable=no-self-use
        return Constant(float(value))
    def var(self, name):                                                    # pylint: disable=no-self-use
        return Variable(str(name))
    def func(self, name):                                                   # pylint: disable=no-self-use
        return globals()[str(name)]()
    def deriv(self, function):                                              # pylint: disable=no-self-use
        return function.derivative
    def funcappl(self, function, argument):                                 # pylint: disable=no-self-use
        return function.evaluate_at(argument)
    def equation(self, left, right):                                        # pylint: disable=no-self-use
        return Equation(left, right)
    def cmd(self, cmd):
        getattr(self.session, cmd)()

SESSION = Session()
PARSER = Lark(_GRAMMAR, parser='lalr', start="start", transformer=LeibnizTree(SESSION), debug=DEBUG)
parse = PARSER.parse
