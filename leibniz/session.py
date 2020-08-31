"""
This module encapsulates data and functionality used in an interactive Leibniz session.
"""

import sys
from .formatting import FSTRINGS

DEBUG = False
if "--debug" in sys.argv:
    import logging
    logging.basicConfig(level=logging.DEBUG)
    DEBUG = True

class Session:
    "Interactive Leibniz session"
    def __init__(self):
        self._vars = {}
        self._format = "tree"
    def vars(self):
        return self._vars
    @property
    def format(self):
        "Set output format"
        return self._format
    def interact(self):
        "Leibniz REPL"
        user_input = input('> ')
        if user_input:
            from .parsing import parse
            leibniz_expr = parse(user_input)
            if leibniz_expr:
                simplified = leibniz_expr.simplify()
                print(FSTRINGS[self.format].format(simplified))
    def python(self):
        "Drops into a Python REPL"
        from code import InteractiveConsole
        console = InteractiveConsole(locals={"SESSION": self})
        console.push("from leibniz import *")
        console.interact(
            ("Welcome. You're in an interactive python shell. Feel free to poke around "
             "in your current Leibniz session, which is available under the name SESSION."),
            "Dropping you back into Leibniz session.")

def print_traceback():
    import traceback
    traceback.print_exc()

def debug():
    import pdb
    pdb.set_trace()


def repl():
    from .parsing import SESSION
    while True:
        try:
            SESSION.interact()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break
        except Exception as exception:                                      # pylint: disable=broad-except
            if not DEBUG:
                print(f"{type(exception)}: {exception}")
            else:
                print_traceback()
                debug()
