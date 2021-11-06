from apps import *


class Expression:
    def __init__(self, expression):
        self.expression = expression

    def eval(self, out):
        app_token, args = self.expression
        app = {
            "pwd": Pwd(),
            "cd": Cd(),
            "echo": Echo(),
            "ls": Ls(),
            "cat": Cat(),
            "head": Head(),
            "tail": Tail(),
            "grep": Grep(),
        }.get(app_token, NotSupported(app_token))
        app.exec(out, args)


class SemiColon:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def eval(self, out):
        self.left.eval(out)
        self.right.eval(out)
