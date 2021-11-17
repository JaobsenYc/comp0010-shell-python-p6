from apps import *


class Expression:
    def __init__(self, expression):
        self.expression = expression

    def eval(self, stdin, out):
        app_token, args = self.expression
        # print("app_token: " + app_token)
        # print("args: " + args)
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

# class Call:
#     def __init__(self, expressions, redirections):
#         self.expressions = expressions
#         self.redirections = redirections

#     def eval(self, out, stdin):

class Redirection:
    def __init__(self):
        self.input = ""
        self.output = ""

    def eval(self, out, stdin, tokens):
        dir = tokens[0]
        fileName = tokens[1]
        if dir == "<":
            try:
                with open(fileName) as f:
                    for line in f:
                        out.append(line.strip()+" ")
            except:
                raise ValueError("wrong input file name")
        else:
            with open(os.getcwd()+fileName) as f:


    def get(self):
        return (self.input, self.output)




class SemiColon:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def eval(self, out):
        self.left.eval(out)
        self.right.eval(out)
