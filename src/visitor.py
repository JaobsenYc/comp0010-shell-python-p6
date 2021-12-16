from abc import ABC, abstractmethod
from posixpath import supports_unicode_filenames
from abstract_syntax_tree import (
    Call,
    DoubleQuote,
    RedirectIn,
    RedirectOut,
    SingleQuote,
    Substitution,
)
from parsercombinator import command
from glob import glob
from appsFactory import AppsFactory
from collections import deque
from itertools import product


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
    # def visitSingleQuote(self, singleQuote):
    #     quotedPart = singleQuote.quotedPart

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

        res_deque = deque()
        res_deque.append(res)
        return res_deque

    def visitSingleQuote(self, singleQuote):
        res = deque()
        res.append(singleQuote.quotedPart)
        return res

    def visitSub(self, sub):
        ast = command.parse(sub.quoted)
        out = ast.accept(self)

        return out

    def visitRedirectIn(self, redirectIn):
        out = deque()

        fs = glob(redirectIn.arg)

        for i in fs:
            with open(i) as f:
                out.extend(f.readlines())

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
        glob_index = []
        globbed_result = []

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
        # check glob in args
        for n, arg in enumerate(args):
            if isinstance(arg, DoubleQuote):
                args[n] = arg.accept(self).pop()
            elif isinstance(arg, Substitution):
                arg[n] = arg.accept(self).pop()
                # print(arg, arg[n])
            elif isinstance(arg, SingleQuote):
                arg[n] = arg.accept(self).pop()
            elif isinstance(arg, str) and "*" in arg:
                glob_index.append(n)
                globbed_result.append(glob(arg))

        app = factory.getApp(appName)

        if len(glob_index) > 0:
            # in case have multiple glob
            glob_pairs = product(globbed_result)

            count = 0
            for pair in glob_pairs:
                argsForThisPair = []
                for arg_index in range(len(args)):
                    if arg_index in glob_index:
                        argsForThisPair.append(pair[count])
                    else:
                        argsForThisPair.append(args[arg_index])

                if len(args) == 1:
                    argsForThisPair = argsForThisPair[0]

                out.extend(app.exec(argsForThisPair, stdin=stdin))
        else:
            out.extend(app.exec(args, stdin=stdin))

        if redirectOut:
            redirectOut.accept(self, stdin=out)
        else:
            return out

    def visitSeq(self, seq):
        left = seq.left
        right = seq.right

        outLeft = left.accept(self)
        outRight = right.accept(self)

        outLeft.extend(outRight)
        return outLeft

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
