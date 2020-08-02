from .base import Expression
from .operators import Minus
from .formatting import EquationFormatter, AssertionFormatter

class Equation(EquationFormatter, Expression):
    subexpr_names = ("expr",)
    def __init__(self, left, right):
        self.expr = Minus(left, right)

class Assertion(AssertionFormatter, Expression):
    subexpr_names = ("variable", "value")
    def __init__(self, variable, value):
        self.variable = variable
        self.value = value
