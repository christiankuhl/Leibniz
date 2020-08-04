"""
This module contains classes handling the logic involved in dealing with
equations and variable assignment
"""

from .base import Expression
from .operators import Minus
from .formatting import EquationFormatter, AssertionFormatter

class Equation(EquationFormatter, Expression):
    "Represents equations as expressions with zero on the right hand side"
    subexpr_names = ("expr",)
    def __init__(self, left, right):
        self.expr = Minus(left, right)

class Assertion(AssertionFormatter, Expression):
    "Represents variable assignments"
    subexpr_names = ("variable", "value")
    def __init__(self, variable, value):
        self.variable = variable
        self.value = value
