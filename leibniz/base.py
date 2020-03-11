import collections
from .formatting import *

class Expression(ExpressionFormatter):
    subexpr_names = ()
    needs_parentheses = False
    def simplify(self):
        return self
    def __repr__(self):
        return str(self)
    def __add__(self, other):
        return Plus(self, other)
    def __mul__(self, other):
        return Times(self, other)
    def __sub__(self, other):
        return Minus(self, other)
    def __div__(self, other):
        return Divide(self, other)    
    def __le__(self, other):
        from .sorting import _sort_key
        return _sort_key(self) <= _sort_key(other)
    def evaluate_at(self, expression):
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
        return set(var for subexpr in self.subexpressions for var in subexpr.variables)
    def free_of(self, variable):
        return variable not in self.variables
    def sort(self):
        return self
    def pyfunc(self):
        vars = sorted(list(self.variables))
        signature = ",".join(vars)
        call_dict = ",".join(f"'{var}': {var}" for var in vars)
        code = f"lambda {signature}: self.evaluate({{{call_dict}}})"
        function = eval(code, {'self': self})
        function.__doc__ = f"({signature}) -> {self:py}"
        return function

class Dot(DotFormatter, Expression):
    def evaluate_at(self, expression):
        return expression

class Constant(ConstantFormatter, Expression):
    def __init__(self, value):
        self.value = value
    def __eq__(self, other):
        if isinstance(other, Constant):
            return self.value == other.value
        else:
            return False
    def partial(self, variable):
        return Constant(0)
    def evaluate(self, environment={}):
        return self.value
    @property
    def variables(self):
        return set()
        
class Variable(Expression, VariableFormatter):
    def __init__(self, name):
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
    def evaluate(self, environment={}):
        return environment[self.name]
    @property
    def variables(self):
        return set(self.name)
        
class Vector(Expression):
    def __init__(self, components):
        self.components = components
    @property
    def dimension(self):
        return len(self.components)
    def partial(self, variable):
        return Vector([c.partial(variable) for c in self.components])
    def evaluate(self, environment={}):
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

def evaluate(expression, environment={}):
    return expression.evaluate(environment)

def gradient(expression, variables, environment=None):
    partials = [partial(expression, var) for var in variables]
    if not environment:
        return partials
    else:
        return [partial.evaluate(environment) for partial in partials]

def jacobian(function, variables, environment=None):
    return [gradient(expr, variables, environment) for expr in function]