"""
This module defines basic unary and binary operators and their behaviour.
It handles associativity via casting nested operations to their respective
collections, i.e. Plus(a, Plus(b, c)) gets cast to Sum(a, b, c) etc.
"""

from operator import add, sub, mul, truediv as div, neg
from .base import Expression, Constant
from .formatting import BinaryOperatorFormatter, AbelianCollectionFormatter, UnaryMinusFormatter, \
                        DivisionFormatter, PowerFormatter

class BinaryOperator(BinaryOperatorFormatter, Expression):
    "Base class for binary operators"
    subexpr_names = ("left", "right")
    left_identity = None
    right_identity = None
    left_null = None
    right_null = None
    needs_parentheses = False
    def __init__(self, left, right):
        self.needs_parentheses = self.__class__.needs_parentheses
        self.left = left
        self.right = right
    def simplify(self):
        self.left = self.left.simplify()
        self.right = self.right.simplify()
        if isinstance(self.left, Constant) and isinstance(self.right, Constant):
            return Constant(self.__class__.pyoperator(self.left.value,      # pylint: disable=no-member
                                                      self.right.value))
        if self.__class__.left_identity:
            if self.left == self.__class__.left_identity:
                return self.right
        if self.__class__.right_identity:
            if self.right == self.__class__.right_identity:
                return self.left
        if self.__class__.left_null:
            if self.left == self.__class__.left_null:
                return self.__class__.left_null
        if self.__class__.right_null:
            if self.right == self.__class__.right_null:
                return self.__class__.right_null
        return self.__class__(self.left, self.right)
    def evaluate(self, environment={}):                                     # pylint: disable=dangerous-default-value
        left = self.left.evaluate(environment)
        right = self.right.evaluate(environment)
        return self.__class__.pyoperator(left, right)                       # pylint: disable=no-member
    def evaluate_at(self, expression):
        return self.__class__(self.left.evaluate_at(expression),
                              self.right.evaluate_at(expression))

class AbelianCollection(AbelianCollectionFormatter, Expression):
    """
    Represents a concatenation of an abelian operation such as in
    Plus(a, Plus(b, c)) -> Sum(a, b, c)
    """
    subexpr_names = ("terms",)
    def __init__(self, *terms):
        self.needs_parentheses = self.__class__.binaryoperator.needs_parentheses # pylint: disable=no-member
        self.terms = terms
    def evaluate(self, environment={}):                                     # pylint: disable=dangerous-default-value
        operator = self.__class__.binaryoperator                            # pylint: disable=no-member
        if not self.terms:
            return operator.right_identity
        tree = self.left_to_right()
        return tree.evaluate(environment)
    def evaluate_at(self, expression):
        return self.__class__(*(t.evaluate_at(expression) for t in self.terms))
    def left_to_right(self):
        operator = self.__class__.binaryoperator                            # pylint: disable=no-member
        left, right = self.terms[0], self.terms[1:]
        if right:
            right = self.__class__(*right)
            return operator(left, right.left_to_right())
        return left
    def sort(self):
        from .sorting import _sort_key                                      # pylint: disable=import-outside-toplevel
        self.terms = sorted([t.sort() for t in self.terms], key=_sort_key)
        return self
    def simplify(self):
        self.sort()
        operator = self.__class__.binaryoperator                            # pylint: disable=no-member
        terms = [term.simplify() for term in self.terms]
        if len(terms) == 1:
            return terms[0]
        if len(terms) == 0:
            return operator.left_identity
        inner = [term for term in terms if isinstance(term, self.__class__)]
        terms = [inner_term for term in inner for inner_term in term.terms] \
                + [term for term in terms if term not in inner]
        inverses = [t for t in terms if isinstance(t, operator.inverse)]
        numerators = [term.left for term in inverses]
        denominators = [term.right for term in inverses]
        terms = numerators + [t for t in terms
                              if not isinstance(t, operator.inverse)]
        constants = [t for t in terms if isinstance(t, Constant)]
        variable_terms = [t for t in terms if not isinstance(t, Constant)]
        if constants:
            constant = Constant(self.__class__(*constants).evaluate())
            expression = self.__class__(*([constant] + variable_terms))
            if operator.left_null:
                if constant == operator.left_null:
                    return operator.left_null
            if operator.left_identity:
                if constant == operator.left_identity:
                    expression = self.__class__(*variable_terms)
        else:
            expression = self.__class__(*variable_terms)
        if denominators:
            denominator = self.__class__(*denominators).simplify()
            expression = operator.inverse(expression, denominator)
        return expression

class AbelianBinaryOperator(BinaryOperator):
    "Base class for abelian binary operations"
    needs_parentheses = False
    def simplify(self):
        simplified = super().simplify()
        if isinstance(simplified, AbelianBinaryOperator):
            return simplified.collect().simplify()
        return simplified
    def collect(self):
        "Collect 'self' into corresponding AbelianCollection object"
        terms = []
        if isinstance(self.left, self.__class__):
            terms += self.left.collect().terms
        elif isinstance(self.left, self.__class__.collection):              # pylint: disable=no-member
            terms += self.left.terms
        else:
            terms.append(self.left)
        if isinstance(self.right, self.__class__):
            terms += self.right.collect().terms
        elif isinstance(self.right, self.__class__.collection):             # pylint: disable=no-member
            terms += self.right.terms
        else:
            terms.append(self.right)
        return self.__class__.collection(*terms)                            # pylint: disable=no-member
    def sort(self):
        if self.left <= self.right:
            return self
        return self.__class__(self.right, self.left)

class Sum(AbelianCollection):
    "It is what it says on the tin"
    def partial(self, variable):
        return Sum(*(term.partial(variable) for term in self.terms)).simplify()

class Product(AbelianCollection):
    "It is what it says on the tin"
    def partial(self, variable):
        return Sum(*(Product(*(term if idx != p_idx else p.partial(variable)
                               for (idx, term) in enumerate(self.terms)))
                     for (p_idx, p) in enumerate(self.terms))
                   ).simplify()

class Plus(AbelianBinaryOperator):
    "It is what it says on the tin"
    symbol = py_symbol = " + "
    tex_symbol = "+"
    pyoperator = add
    collection = Sum
    left_identity = Constant(0)
    right_identity = Constant(0)
    def partial(self, variable):
        return Plus(self.left.partial(variable),
                    self.right.partial(variable)).simplify()

Sum.binaryoperator = Plus

class Minus(BinaryOperator):
    "It is what it says on the tin"
    symbol = py_symbol = " - "
    tex_symbol = "-"
    pyoperator = sub
    right_identity = Constant(0)
    inverse = Plus
    def __init__(self, left, right):
        super().__init__(left, right)
        if isinstance(right, (Plus, Sum)):
            self.right.needs_parentheses = True
    def partial(self, variable):
        return Minus(self.left.partial(variable),
                     self.right.partial(variable)).simplify()
    def simplify(self):
        simplified = super().simplify()
        if not isinstance(simplified, Minus):
            return simplified
        if simplified.left == Constant(0):
            return Times(Constant(-1), simplified.right)
        return simplified

Plus.inverse = Minus

class UnaryMinus(UnaryMinusFormatter, Expression):
    "It is what it says on the tin. Mainly for convenience reasons."
    subexpr_names = ('expression',)
    pyoperator = neg
    def __init__(self, expression):
        self.expression = expression
    def partial(self, variable):
        return UnaryMinus(self.expression.partial(variable)).simplify()
    def evaluate(self, environment):
        return -self.expression.evaluate(environment)
    def evaluate_at(self, expression):
        return UnaryMinus(self.expression.evaluate_at(expression))
    def simplify(self):
        if isinstance(self.expression, UnaryMinus):
            return self.expression
        return Times(Constant(-1), self.expression).simplify()

class Times(AbelianBinaryOperator):
    "It is what it says on the tin"
    symbol = py_symbol = " * "
    tex_symbol = "\\cdot "
    needs_parentheses = False
    pyoperator = mul
    collection = Product
    left_identity = Constant(1)
    right_identity = Constant(1)
    left_null = Constant(0)
    right_null = Constant(0)
    def partial(self, variable):
        uprime = self.left.partial(variable)
        vprime = self.right.partial(variable)
        return Plus(Times(uprime, self.right),
                    Times(self.left, vprime)).simplify()

Product.binaryoperator = Times

class Divide(DivisionFormatter, BinaryOperator):
    "It is what it says on the tin"
    symbol = py_symbol = " / "
    needs_parentheses = False
    pyoperator = div
    right_identity = Constant(1)
    left_null = Constant(0)
    inverse = Times
    def __init__(self, left, right):
        super().__init__(left, right)
        if isinstance(left, (Plus, Sum)):
            self.left.needs_parentheses = True
        if isinstance(right, (Plus, Times, AbelianCollection)):
            self.right.needs_parentheses = True
    def simplify(self):
        simplified = super().simplify()
        if not isinstance(simplified, Divide):
            return simplified
        numerators, denominators = [], []
        if isinstance(simplified.left, Divide):
            numerators.append(simplified.left.left)
            denominators.append(simplified.left.right)
        else:
            numerators.append(simplified.left)
        if isinstance(simplified.right, Divide):
            numerators.append(simplified.right.right)
            denominators.append(simplified.right.left)
        else:
            denominators.append(simplified.right)
        return Divide(Product(*numerators).simplify(),
                      Product(*denominators).simplify())
    def partial(self, variable):
        uprime = self.left.partial(variable)
        vprime = self.right.partial(variable)
        return Divide(Minus(Times(uprime, self.right),
                            Times(self.left, vprime)),
                      Power(self.right, Constant(2))).simplify()

Times.inverse = Divide

class Power(PowerFormatter, BinaryOperator):
    "It is what it says on the tin"
    symbol = "^"
    py_symbol = "**"
    needs_parentheses = False
    pyoperator = pow
    right_identity = Constant(1)
    left_null = Constant(0)
    def __init__(self, left, right):
        super().__init__(left, right)
        if isinstance(left, (BinaryOperator, AbelianCollection)):
            self.left.needs_parentheses = True
        if isinstance(right, (BinaryOperator, AbelianCollection)):
            self.right.needs_parentheses = True
    def simplify(self):
        simplified = super().simplify()
        if not isinstance(simplified, Power):
            return simplified
        if simplified.right == Constant(0):
            return Constant(1)
        if simplified.left == Constant(1):
            return Constant(1)
        if simplified.left == Constant(0):
            return Constant(0)
        return simplified
    def partial(self, variable):
        from .functions import Ln                                           # pylint: disable=no-name-in-module
        self.right = self.right.simplify()
        self.left = self.left.simplify()
        if self.right.free_of(variable):
            return Product(self.right,
                           self.left.partial(variable),
                           Power(self.left, Minus(self.right, Constant(1)))
                           ).simplify()
        if self.left.free_of(variable):
            uprime = self.right.partial(variable)
            return Times(Times(Ln(self.left), uprime), self).simplify()
        uprime = self.left.partial(variable)
        vprime = self.right.partial(variable)
        return Times(Plus(Divide(Times(self.right, uprime), self.left),
                          Times(Ln(self.left), vprime)),
                     self).simplify()

Sum.up = Times
Product.up = Power
