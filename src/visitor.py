from abc import ABC, abstractmethod
from posixpath import supports_unicode_filenames
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
        containSubstitution, quotedPart = (
            doubleQuote.containSubstitution,
            doubleQuote.quotedPart,
        )

        res = ""

        if not containSubstitution:
            res = "{}".format("".join(quotedPart))
        else:
            for part in quotedPart:
                if not isinstance(part, Substitution):
                    res += part
                else:
                    out = part.accept(self)
                    while len(out) > 0:
                        line = out.popleft()
                        res += line
        return res

    def visitSub(self, sub):
        ast = command.parse(sub.quoted)
        out = ast.accept(self, needPipeReturn=True)

        return out

    def visitRedirectIn(self, redirectIn):
        out = deque()

        fs = glob(redirectIn.arg)

        for i in fs:
            with open(i) as f:
                content = ""
                lines = f.readlines()
                for line in lines:
                    content += line
            out.extend(content)

        return out

    def visitRedirectOut(self, redirectOut, stdin=None):
        fs = glob(redirectOut.arg) or [redirectOut.arg]
        n = len(fs)

        if n > 1:
            raise Exception("invalid redirection out")  # or other error handling?

        stdout_f = fs[0]
        with open(stdout_f, "w") as f:
            while len(stdin) > 0:
                line = stdin.popleft()
                f.write(line)

    def visitCall(self, call, input=None):
        redirects = call.redirects
        appName = call.appName
        args = call.args

        stdin, redirectOut = None, None
        out = deque()

        factory = AppsFactory()

        for r in redirects:
            if isinstance(r, RedirectIn) and not stdin:  # check type
                stdin = r.accept(self)
            elif isinstance(r, RedirectOut) and not redirectOut:
                redirectOut = r
            else:
                raise Exception("invalid redirections")

        # otherwise, stdin will overwrite input from last call result piped in
        if input and not stdin:
            stdin = input

        # check if args includes double quote that needs to further eval
        for n, arg in enumerate(args):
            if isinstance(arg, DoubleQuote):
                args[n] = arg.accept(self).pop()

        app = factory.getApp(appName)

        # check glob in args
        if "*" in args[-1]:
            files = glob(args[-1])

        if files:
            for file_arg in files:
                args_new = args[: len(args) - 1]
                args_new.append(file_arg)
                out.extend(app.exec(args_new, stdin=stdin))
        else:
            out.extend(app.exec(args), stdin=stdin)

        if redirectOut:
            redirectOut.accept(self, stdin=out)
        else:
            return out

    def visitSeq(self, seq):
        left = seq.left
        right = seq.right

        outLeft = left.accept(self)
        outRight = right.accept(self)

        return outLeft.extend(outRight)

    def visitPipe(self, pipe):  # what if | has redirectOut before?
        left = pipe.left
        right = pipe.right

        outLeft = left.accept(self)
        outRight = right.accept(self, input=outLeft)

        return outRight


if __name__ == "__main__":
    visitor = ASTVisitor()
    call = Call(
        redirects=[],
        appName="echo",
        args=[DoubleQuote(["a", " ", Substitution('echo "b"')], True)],
    )
    call.accept(visitor)
