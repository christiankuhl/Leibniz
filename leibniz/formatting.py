"""
This module contains mixin classes responsible for the output formatting of Leibniz expressions.
"""

PLAINTEXT = {"p", "plain", ""}
TEX = {"t", "tex"}
RAW = {"r", "raw"}
PYTHON = {"py", "python"}
TREE = {"tree"}

FSTRINGS = {"plain": "{:p}", "tex": "{:t}", "python": "{:py}", "raw": "{:r}",
            "tree": "{:tree}", "py": "{:py}"}
SYMBOLS = {"plain": "symbol", "tex": "tex_symbol", "python": "py_symbol",
           "py": "py_symbol"}

class ExpressionFormatter:
    "Base class for expression formatting"
    def texformat(self):
        return str(self)
    def pyformat(self):
        return str(self)
    def treeformat(self, indent=""):
        result = "\n" + indent + self.nodeinfo
        for index, subexpr in enumerate(self.subexpressions):               # pylint: disable=no-member
            last = (len(self.subexpressions) == index + 1)                  # pylint: disable=no-member
            indent = indent.replace("└─", "  ").replace("├─", "│ ")
            new_indent = indent + ("  └─ " if last else "  ├─ ")
            result += subexpr.treeformat(new_indent)
        return result
    def __format__(self, format_spec=""):
        if format_spec in PLAINTEXT:
            return str(self)
        elif format_spec in TEX:
            return self.texformat()
        elif format_spec in RAW:
            return self.rawformat()                                         # pylint: disable=no-member
        elif format_spec in PYTHON:
            return self.pyformat()
        elif format_spec in TREE:
            return self.treeformat()
    def parenthesise(self, representation):
        if self.needs_parentheses:                                          # pylint: disable=no-member
            return f"({representation})"
        else:
            return representation
    @property
    def nodeinfo(self):
        return self.__class__.__name__

class DotFormatter:
    def __str__(self):
        return "·"
    def texformat(self):
        return "\\cdot"
    def rawformat(self):
        return "Dot()"

class ConstantFormatter:
    def __str__(self):
        return str(self.value)                                              # pylint: disable=no-member
    def rawformat(self):
        return f"Constant({self.value})"                                    # pylint: disable=no-member
    @property
    def nodeinfo(self):
        return f"{self:raw}"

class VariableFormatter:
    def __str__(self):
        return self.name                                                    # pylint: disable=no-member
    def rawformat(self):
        return f"Variable('{self.name}')"                                   # pylint: disable=no-member
    @property
    def nodeinfo(self):
        return f"{self:raw}"

class BinaryOperatorFormatter:
    def _format(self, spec):
        symbol = getattr(self.__class__, SYMBOLS[spec])
        left = FSTRINGS[spec].format(self.left)                             # pylint: disable=no-member
        right = FSTRINGS[spec].format(self.right)                           # pylint: disable=no-member
        return self.parenthesise(f"{left}{symbol}{right}")                  # pylint: disable=no-member
    def __str__(self):
        return self._format("plain")
    def pyformat(self):
        return self._format("py")
    def texformat(self):
        return self._format("tex")
    def rawformat(self):
        return f"{self.__class__.__name__}({self.left:r}, {self.right:r})"  # pylint: disable=no-member

class AbelianCollectionFormatter:
    def _format(self, spec):
        symbol = getattr(self.__class__.binaryoperator, SYMBOLS[spec])          # pylint: disable=no-member
        collection = symbol.join(FSTRINGS[spec].format(t) for t in self.terms)  # pylint: disable=no-member
        return self.parenthesise(collection)                                    # pylint: disable=no-member
    def __str__(self):
        return self._format("plain")
    def pyformat(self):
        return self._format("py")
    def texformat(self):
        return self._format("tex")
    def rawformat(self):
        name = self.__class__.__name__
        collection = ",".join(f"{term:r}" for term in self.terms)           # pylint: disable=no-member
        return f"{name}({collection})"

class DivisionFormatter:
    def texformat(self):
        return f"\\frac{{{self.left:t}}}{{{self.right:t}}}"                 # pylint: disable=no-member

class PowerFormatter:
    def texformat(self):
        if self.right.needs_parentheses:                                    # pylint: disable=no-member
            exponent = f"{self.right:t}"[1:-1]                              # pylint: disable=no-member
            return f"{self.left:t}^{{{exponent}}}"                          # pylint: disable=no-member
        else:
            return f"{self.left:t}^{self.right:t}"                          # pylint: disable=no-member

class ScalarFunctionFormatter:
    def __str__(self):
        name = self.__class__.name                                          # pylint: disable=no-member
        return f"{name}({self.argument})"                                   # pylint: disable=no-member
    def pyformat(self):
        name = self.__class__.name.lower()                                  # pylint: disable=no-member
        return f"{name}({self.argument:py})"                                # pylint: disable=no-member
    def texformat(self):
        name = self.__class__.name.lower()                                  # pylint: disable=no-member
        return f"\\{name}({self.argument:t})"                               # pylint: disable=no-member
    def rawformat(self):
        name = self.__class__.name                                          # pylint: disable=no-member
        return f"{name}({self.argument:r})"                                 # pylint: disable=no-member

class UnaryMinusFormatter:
    def __str__(self):
        return f"-{self.expression}"                                        # pylint: disable=no-member
    def pyformat(self):
        return f"-{self.expression:py}"                                     # pylint: disable=no-member
    def texformat(self):
        return f"-{self.expression:t}"                                      # pylint: disable=no-member
    def rawformat(self):
        return f"UnaryMinus({self.expression:r})"                           # pylint: disable=no-member

class AssertionFormatter:
    def _format(self, spec):
        if spec == "py":
            symbol = " = "
        else:
            symbol = " := "
        return FSTRINGS[spec].format(self.variable) + symbol + FSTRINGS[spec].format(self.value)    # pylint: disable=no-member
    def __str__(self):
        return self._format("plain")
    def pyformat(self):
        return self._format("py")
    def texformat(self):
        return self._format("tex")
    def rawformat(self):
        return f"Assertion({self.variable:r}, {self.value:r})"              # pylint: disable=no-member

class EquationFormatter:
    def _format(self, spec):
        if spec == "py":
            rhs = " == 0"
        else:
            rhs = " = 0"
        return FSTRINGS[spec].format(self.expr) + rhs                       # pylint: disable=no-member
    def __str__(self):
        return self._format("plain")
    def pyformat(self):
        return self._format("py")
    def texformat(self):
        return self._format("tex")
    def rawformat(self):
        name = self.__class__.__name__
        collection = ",".join(f"{term:r}" for term in self.terms)           # pylint: disable=no-member
        return f"{name}({collection})"
