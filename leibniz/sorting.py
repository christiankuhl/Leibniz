"""
Simplification capabilities for expressions largely depend on the definition of a canonical
form for expressions. This module takes care of that.
"""

from .base import Constant, Variable, Dot
from .operators import Sum, Plus, Minus, Product, Times, Divide, Power, UnaryMinus
from .functions import ScalarFunction

SORT_ORDER = {
    Constant: 1,
    Variable: 2,
    Dot: 2,
    Sum: 4,
    Plus: 3,
    Minus: 5,
    UnaryMinus: 5,
    Product: 7,
    Times: 6,
    Divide: 8,
    Power: 9,
    ScalarFunction: 10
}

def _sort_key(expression):
    return SORT_ORDER[_class(expression)]

def _class(expression):
    if isinstance(expression, ScalarFunction):
        return ScalarFunction
    else:
        return expression.__class__
