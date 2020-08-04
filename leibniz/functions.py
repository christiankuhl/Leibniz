"""
This module is responsible for creating the standard mathematical functions as Leibniz objects
as well as providing their derivatives. Actual evaluation in the meantime is handled by the
standard library math module.
"""

import math                                                                 # pylint:disable=unused-import
from .base import Expression, Constant, Dot, Variable
from .operators import Plus, Minus, Times, Divide, Power, UnaryMinus
from .formatting import ScalarFunctionFormatter

STANDARD_FUNCTIONS = ["log", "exp", "cos", "sin", "tan", "cosh", "sinh",
                      "tanh", "sqrt", "atan", "atanh", "asin", "acos"]

class ScalarFunction(ScalarFunctionFormatter, Expression):
    "Base class for scalar functions"
    subexpr_names = ("argument",)
    def __init__(self, argument=Dot()):
        self.argument = argument
    def simplify(self):
        self.argument = self.argument.simplify()
        if isinstance(self.argument, Constant):
            return Constant(self.__class__.pyfunction(self.argument.value))
        return self
    def evaluate(self, environment={}):                                     # pylint:disable=dangerous-default-value 
        argument = self.argument.evaluate(environment)
        return self.__class__.pyfunction(argument)
    @classmethod
    def evaluate_at(cls, expression):
        if isinstance(cls, ScalarFunction):
            return cls.__class__(cls.argument.evaluate_at(expression))      # pylint:disable=no-member
        return cls(expression)
    def partial(self, variable):
        return Times(self.__class__.derivative.evaluate_at(self.argument),  # pylint:disable=no-member
                     self.argument.partial(variable))
    def sort(self):
        return self.__class__(self.argument.sort())

def _create_functions():
    for function in STANDARD_FUNCTIONS:
        classname = function.capitalize()
        func_ptr = getattr(globals()["math"], function)
        globals()[classname] = type(classname, (ScalarFunction,),
                                    {"name": classname, "pyfunction": func_ptr})

_create_functions()

Log.derivative = Divide(Constant(1), Dot())                                 # pylint:disable=undefined-variable
Exp.derivative = Exp(Dot())                                                 # pylint:disable=undefined-variable
Sin.derivative = Cos(Dot())                                                 # pylint:disable=undefined-variable
Cos.derivative = UnaryMinus(Sin(Dot()))                                     # pylint:disable=undefined-variable
Tan.derivative = Plus(Constant(1), Power(Tan(Dot()), Constant(2)))          # pylint:disable=undefined-variable
Sinh.derivative = Cosh(Dot())                                               # pylint:disable=undefined-variable
Cosh.derivative = Sinh(Dot())                                               # pylint:disable=undefined-variable
Tanh.derivative = Minus(Constant(1), Power(Tanh(Dot()), Constant(2)))       # pylint:disable=undefined-variable
Sqrt.derivative = Divide(Constant(1), Times(Constant(2), Sqrt(Dot())))      # pylint:disable=undefined-variable
Atan.derivative = Divide(Constant(1), Plus(Constant(1),                     # pylint:disable=undefined-variable
                                           Power(Dot(), Constant(2))))
Atanh.derivative = Divide(Constant(1), Minus(Constant(1),                   # pylint:disable=undefined-variable
                                             Power(Dot(), Constant(2))))
Asin.derivative = Divide(Constant(1), Sqrt(Minus(Constant(1),               # pylint:disable=undefined-variable
                                                 Power(Variable("x"),
                                                       Constant(2)))))      # pylint:disable=undefined-variable
Acos.derivative = Divide(Constant(-1), Sqrt(Minus(Constant(1),              # pylint:disable=undefined-variable
                                                  Power(Variable("x"),
                                                        Constant(2)))))

ALIASES = {"Ln": Log, "Arctan": Atan, "Arctanh": Atanh, "Arccos": Acos,     # pylint:disable=undefined-variable
           "Arcsin": Asin}                                                  # pylint:disable=undefined-variable
for _classname, _original in ALIASES.items():
    globals()[_classname] = _original
    globals()[_classname].name = _classname

FUNCTION_NAMES = [f.capitalize() for f in STANDARD_FUNCTIONS] \
                    + list(ALIASES.keys())
