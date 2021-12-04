from abc import ABC, abstractmethod
from abstract_syntax_tree import Call, RedirectIn, RedirectOut
from parsercombinator import command
from glob import glob
from appsFactory import AppsFactory
from collections import deque


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
    def visitCall(self, call, input=None, needPipeReturn=False):
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

        fs = glob(redirectIn.arg)
        # for file in fs:
        #     with open(file) as f:
        #         content = f.read()
        #         out += content  # Do we need spaces or not?
        return fs

    def visitRedirectOut(self, redirectOut):
        fs = glob(redirectOut.arg)
        n = len(fs)

        if n > 1:
            raise Exception("invalid redirection out")  # or other error handling?

        return fs[0] if n == 1 else None  # incase '>' has nothing followed

    def visitCall(self, call, input=None, needPipeReturn=False):
        redirects = call.redirects
        appName = call.appName
        args = call.args

        stdin, stdout = None, None
        out = deque()

        factory = AppsFactory()

        for r in redirects:
            if isinstance(r, RedirectIn) and not stdin:  # check type
                stdin = r.accept(self)
                # print(stdin)
            elif isinstance(r, RedirectOut) and not stdout:
                stdout = r.accept(self)
            else:
                raise Exception("invalid redirections")

        # otherwise, stdin will overwrite input from last call result piped in
        if input and not stdin:
            stdin = input

        app = factory.getApp(appName)
        if stdin:
            for i in stdin:
                out.extend(app.exec(args, stdin=i))
        else:
            out = app.exec(args, stdin=stdin)

        if stdout:
            with open(stdout) as f:
                while len(out) > 0:
                    line = out.popleft()
                    # print(line)
                    f.write(line)
        elif not needPipeReturn:
            while len(out) > 0:
                line = out.popleft()
                print(line, end="")
        elif needPipeReturn:
            return out

    def visitSeq(self, seq):
        left = seq.left
        right = seq.right

        left.accept(self)
        right.accept(self)

    def visitPipe(self, pipe):  # what if | has redirectOut before?
        left = pipe.left
        right = pipe.right

        outLeft = left.accept(self, notPrint=True)
        outRight = right.accept(self, input=outLeft)


if __name__ == "__main__":
    visitor = ASTVisitor()
    call = Call(redirects=[], appName="echo", args=["hello"])
    call.accept(visitor)
