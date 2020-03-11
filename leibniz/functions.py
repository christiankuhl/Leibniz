import math        

STANDARD_FUNCTIONS = ["log", "exp", "cos", "sin", "tan", "cosh", "sinh", "tanh", "sqrt", "atan", "atanh"]

from .base import *
from .operators import Plus, Minus, Times, Divide, Power
from .formatting import *

class ScalarFunction(ScalarFunctionFormatter, Expression):
    subexpr_names = ("argument",)
    def __init__(self, argument):
        self.argument = argument
    def simplify(self):
        self.argument = self.argument.simplify()
        if isinstance(self.argument, Constant):
            return Constant(self.__class__.function(self.argument.value))
        return self
    def evaluate(self, environment={}):
        argument = self.argument.evaluate(environment)
        return self.__class__.pyfunction(argument)
    def evaluate_at(self, expression):
        return self.__class__(self.argument.evaluate_at(expression))
    def partial(self, variable):
        return Times(self.__class__.derivative.evaluate_at(self.argument), self.argument.partial(variable))
    def sort(self):
        return self.__class__(self.argument.sort())
       
for function in STANDARD_FUNCTIONS:
    classname = function.capitalize()
    fp = getattr(globals()["math"],function)
    globals()[classname] = type(classname, (ScalarFunction,), {"name": classname, "pyfunction": fp})

Log.derivative = Divide(Constant(1), Dot())
Ln = Log
Ln.name = "Ln"
Exp.derivative = Exp(Dot())    
Sin.derivative = Cos(Dot())
Cos.derivative = Times(Constant(-1), Sin(Dot()))
Tan.derivative = Plus(Constant(1), Power(Tan(Dot()), Constant(2)))    
Sinh.derivative = Cosh(Dot())
Cosh.derivative = Sinh(Dot())
Tanh.derivative = Minus(Constant(1), Power(Tanh(Dot()), Constant(2)))
Sqrt.derivative = Divide(Constant(1), Times(Constant(2), Sqrt(Dot())))
Atan.derivative = Divide(Constant(1), Plus(Constant(1), Power(Dot(), Constant(2))))
Atanh.derivative = Divide(Constant(1), Minus(Constant(1), Power(Dot(), Constant(2))))
