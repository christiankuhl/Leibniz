"""
This module contains the most basic types of algebraic Leibniz expressions
"""

import collections
from .formatting import ExpressionFormatter, DotFormatter, ConstantFormatter, VariableFormatter

class Expression(ExpressionFormatter):
    "Base class for Leibniz expressions"
    subexpr_names = ()
    needs_parentheses = False
    def simplify(self):
        return self
    def __repr__(self):
        return str(self)
    def __add__(self, other):
        from .operators import Plus
        return Plus(self, other)
    def __mul__(self, other):
        from .operators import Times
        return Times(self, other)
    def __sub__(self, other):
        from .operators import Minus
        return Minus(self, other)
    def __neg__(self):
        from .operators import UnaryMinus
        return UnaryMinus(self)
    def __truediv__(self, other):
        from .operators import Divide
        return Divide(self, other)
    def __pow__(self, other):
        from .operators import Power
        return Power(self, other)
    def __le__(self, other):
        from .sorting import _sort_key
        return _sort_key(self) <= _sort_key(other)
    def evaluate_at(self, expression):                                      # pylint: disable=unused-argument
        return self
    @property
    def subexpressions(self):
        subexprs = []
        for sub_name in self.__class__.subexpr_names:
            subexpr = getattr(self, sub_name)
            if isinstance(subexpr, collections.Iterable):
                subexprs += [sub for sub in subexpr]
            else:
                subexprs.append(subexpr)
        return subexprs
    @property
    def variables(self):
        return set(var for subexpr in self.subexpressions
                   for var in subexpr.variables)
    def free_of(self, variable):
        return variable not in self.variables
    def sort(self):
        return self
    def pyfunction(self):
        variables = sorted(list(self.variables))
        signature = ",".join(variables)
        call_dict = ",".join(f"'{var}': {var}" for var in variables)
        code = f"lambda {signature}: self.evaluate({{{call_dict}}})"
        function = eval(code, {'self': self})                               # pylint: disable=eval-used
        function.__doc__ = f"({signature}) -> {self:py}"
        return function
    @property
    def derivative(self):
        return self.partial(None).simplify()                                # pylint: disable=no-member
    def substitute(self, variable, expression):                             # pylint: disable=unused-argument
        return self

class Dot(DotFormatter, Expression):
    "Represents an implicit argument, as in Cos = Cos(·)"
    def evaluate_at(self, expression):
        return expression
    def partial(self, variable):
        if variable:
            return Constant(0)
        return Constant(1)

class Constant(ConstantFormatter, Expression):
    "Represents a constant value"
    def __init__(self, value):
        self.value = value
    def __eq__(self, other):
        if isinstance(other, Constant):
            return self.value == other.value
        return False
    def partial(self, variable):                                            # pylint: disable=unused-argument
        return Constant(0)
    def evaluate(self, environment={}):                                     # pylint: disable=unused-argument, dangerous-default-value
        return self.value
    @property
    def variables(self):
        return set()

class Variable(VariableFormatter, Expression):
    "Represents a single scalar variable"
    def __init__(self, name):
        assert name
        self.name = name
    def __eq__(self, other):
        if isinstance(other, Variable):
            return self.name == other.name
        else:
            return False
    def partial(self, variable):
        if self.name == variable:
            return Constant(1)
        else:
            return Constant(0)
    def evaluate(self, environment={}):                                     # pylint: disable=dangerous-default-value
        return environment[self.name]
    @property
    def variables(self):
        return set(self.name)
    def substitute(self, variable, expression):
        if self == variable:
            return expression
        else:
            return self

class Vector(Expression):
    "Represents a vector of Leibniz expressions"
    def __init__(self, components):
        self.components = components
    @property
    def dimension(self):
        return len(self.components)
    def partial(self, variable):
        return Vector([c.partial(variable) for c in self.components])
    def evaluate(self, environment={}):                                     # pylint: disable=dangerous-default-value
        return [c.evaluate(environment) for c in self.components]
    def evaluate_at(self, expression):
        return [c.evaluate_at(expression) for c in self.components]
    def sort(self):
        return [c.sort() for c in self.components]
    @property
    def variables(self):
        return set(var for c in self.components for var in c.variables)

def partial(expression, variable):
    return expression.partial(variable).simplify()

def simplify(expression):
    return expression.simplify()

def evaluate(expression, environment={}):                                   # pylint: disable=dangerous-default-value
    return expression.evaluate(environment)

def gradient(expression, variables, environment=None):
    partials = [partial(expression, var) for var in variables]
    if not environment:
        return partials
    return [partial.evaluate(environment) for partial in partials]

def jacobian(function, variables, environment=None):
    return [gradient(expr, variables, environment) for expr in function]
