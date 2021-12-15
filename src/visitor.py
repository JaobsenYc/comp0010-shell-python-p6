from abc import ABC, abstractmethod
from abstract_syntax_tree import (
    Call,
    DoubleQuote,
    RedirectIn,
    RedirectOut,
    Substitution,
)
from parsercombinator import command
from glob import glob
from appsFactory import AppsFactory
from collections import deque


class Visitor(ABC):
    @abstractmethod
    def visitDoubleQuote(self, doubleQuote):
        pass

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
    def visitDoubleQuote(self, doubleQuote):
        hasSub = doubleQuote.hasSub
        quoted = doubleQuote.quoted

        res = ""

        if not hasSub:
            res = "{}".format("".join(quoted))
        else:
            for i in quoted:
                if not isinstance(i, Substitution):
                    res += i
                else:
                    out = i.accept(self)
                    while len(out) > 0:
                        line = out.popleft()
                        res += line
        return res

    def visitSub(self, sub):
        ast = command.parse(sub.quoted)
        out = ast.accept(self, needPipeReturn=True)

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

        return fs[0] if n == 1 else redirectOut.arg  # incase '>' has nothing followed

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

        # check if args includes double quote that needs to further eval
        for n, arg in enumerate(args):
            if isinstance(arg, DoubleQuote):
                args[n] = arg.accept(self)

        app = factory.getApp(appName)
        if stdin:
            stdin_content = []
            for i in stdin:
                with open(i) as f:
                    content = ""
                    lines = f.readlines()
                    for line in lines:
                        content += line
                stdin_content.append(content)
            out.extend(app.exec(args), stdin=stdin_content)
        else:
            out = app.exec(args, stdin=[stdin])

        if stdout:
            with open(stdout, "w") as f:
                while len(out) > 0:
                    line = out.popleft()
                    # print(line)
                    f.write(line)
        elif not needPipeReturn and out:
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

        outLeft = left.accept(self, needPipeReturn=True)
        outRight = right.accept(self, input=outLeft)


if __name__ == "__main__":
    visitor = ASTVisitor()
    call = Call(
        redirects=[],
        appName="echo",
        args=[DoubleQuote(["a", " ", Substitution('echo "b"')], True)],
    )
    call.accept(visitor)
