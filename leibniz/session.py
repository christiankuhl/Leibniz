import sys
from .formatting import FSTRINGS

DEBUG = False
if "--debug" in sys.argv:
    import logging
    logging.basicConfig(level=logging.DEBUG)
    DEBUG = True

class Session:
    def __init__(self):
        self.vars = {}
        self.format = "py"
    def input(self):
        s = input('> ')
        if s:
            from .parsing import parse
            x = parse(s).simplify()
            print(FSTRINGS[self.format].format(x))

def repl():
    from .parsing import SESSION
    while True:
        try:
            SESSION.input()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break
        except Exception as e:
            if not DEBUG:
                print(f"{type(e)}: {e}")
            else:
                import traceback
                import pdb
                traceback.print_exc()
                pdb.set_trace()
