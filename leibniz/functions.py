import math
from .base import *
from .operators import Plus, Minus, Times, Divide, Power, UnaryMinus
from .formatting import *

STANDARD_FUNCTIONS = ["log", "exp", "cos", "sin", "tan", "cosh", "sinh",
                      "tanh", "sqrt", "atan", "atanh", "asin", "acos"]

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
    @classmethod
    def evaluate_at(self, expression):
        if isinstance(self, ScalarFunction):
            return self.__class__(self.argument.evaluate_at(expression))
        else:
            return self(expression)
    def partial(self, variable):
        return Times(self.__class__.derivative.evaluate_at(self.argument),
                     self.argument.partial(variable))
    def sort(self):
        return self.__class__(self.argument.sort())

for _function in STANDARD_FUNCTIONS:
    _classname = _function.capitalize()
    _fp = getattr(globals()["math"], _function)
    globals()[_classname] = type(_classname, (ScalarFunction,),
                                 {"name": _classname, "pyfunction": _fp})

Log.derivative = Divide(Constant(1), Dot())
Exp.derivative = Exp(Dot())
Sin.derivative = Cos(Dot())
Cos.derivative = UnaryMinus(Sin(Dot()))
Tan.derivative = Plus(Constant(1), Power(Tan(Dot()), Constant(2)))
Sinh.derivative = Cosh(Dot())
Cosh.derivative = Sinh(Dot())
Tanh.derivative = Minus(Constant(1), Power(Tanh(Dot()), Constant(2)))
Sqrt.derivative = Divide(Constant(1), Times(Constant(2), Sqrt(Dot())))
Atan.derivative = Divide(Constant(1), Plus(Constant(1),
                                           Power(Dot(), Constant(2))))
Atanh.derivative = Divide(Constant(1), Minus(Constant(1),
                                             Power(Dot(), Constant(2))))
Asin.derivative = Divide(Constant(1), Sqrt(Minus(Constant(1),
                                                 Power(Variable("x"),
                                                       Constant(2)))))
Acos.derivative = Divide(Constant(-1), Sqrt(Minus(Constant(1),
                                                  Power(Variable("x"),
                                                        Constant(2)))))

ALIASES = {"Ln": Log, "Arctan": Atan, "Arctanh": Atanh, "Arccos": Acos,
           "Arcsin": Asin}
for _classname, _original in ALIASES.items():
    globals()[_classname] = _original
    globals()[_classname].name = _classname

FUNCTION_NAMES = [f.capitalize() for f in STANDARD_FUNCTIONS] \
                    + list(ALIASES.keys())
