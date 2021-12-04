from abc import ABC, abstractmethod
from abstract_syntax_tree import RedirectIn, RedirectOut
from parsercombinator import command
from glob import glob
from appsFactory import AppsFactory


class Visitor(ABC):
    @abstractmethod
    def visitSub(self, sub):
        pass

    @abstractmethod
    def visitRedirectIn(self, redirectIn):
        pass

    @abstractmethod
    def visitRedirectOut(self, redirectOut):
        pass

    @abstractmethod
    def visitCall(self, call, input=None):
        pass

    @abstractmethod
    def visitSeq(self, seq):
        pass

    @abstractmethod
    def visitPipe(self, pipe):
        pass


# @singleton # or use an instance?
class ASTVisitor(Visitor):
    # def __init__(self):
    #     factory = AppsFactory()

    def visitSub(self, sub):
        ast = command.parse(sub)
        out = ast.accept(self)

        return out

    def visitRedirectIn(self, redirectIn):
        out = ""

        fs = glob(redirectIn)
        for file in fs:
            with open(file) as f:
                content = f.read()
                out += content  # Do we need spaces or not?

        return out

    def visitRedirectOut(self, redirectOut):
        fs = glob(redirectOut)

        if len(fs) > 1:
            raise Exception("invalid redirection out")  # or other error handling?

        with open(fs[0]) as f:
            f.write()

    def visitCall(self, call):
        redirects = call.redirects
        appName = call.appName
        args = call.args

        stdin, stdout = None

        factory = AppsFactory()

        for r in redirects:
            if type(r) == RedirectIn and not stdin:  # check type
                stdin = r.accept(self)
            elif type(r) == RedirectOut and not stdout:
                stdout = r.accept(self)
            else:
                raise Exception("invalid redirections")

        app = factory.getApp(appName)
        out = app.exec(app.exec(stdin=stdin, args=args))

        return out

    def visitSeq(self, seq):
        left = seq.left
        right = seq.right

        outLeft = left.accept(self)
        outRight = right.accept(self)

        print(outLeft)
        print(outRight)

    def visitPipe(self, pipe):  # what if | has redirectOut before?
        left = pipe.left
        right = pipe.right

        outLeft = left.accept(self)
        outRight = right.accept(self)

        return outRight
