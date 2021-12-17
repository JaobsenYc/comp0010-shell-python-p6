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
    def visitSingleQuote(self, singleQuote):
        pass

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
    def visitSingleQuote(self, singleQuote):
        quotedPart = singleQuote.quotedPart
        res_deque = deque()
        res_deque.append(quotedPart)
        return {"stdout": res_deque, "stderr": deque(), "exitcode": 0}

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
        return {"stdout": res_deque, "stderr": deque(), "exitcode": 0}

    def visitSingleQuote(self, singleQuote):
        res = deque()
        res.append(singleQuote.quotedPart)
        return {"stdout": res, "stderr": deque(), "exitcode": 0}

    def visitSub(self, sub):
        ast = command.parse(sub.quoted)
        out = ast.accept(self)
        if not out["exitcode"]:
            out["stdout"] = deque(
                "".join(out["stdout"]).strip("\n ").replace("\n", " ")
            )
            return {"stdout": out, "stderr": deque(), "exitcode": 0}
        else:
            return out

    def visitRedirectIn(self, redirectIn):
        out = deque()

        fs = glob(redirectIn.arg)

        for i in fs:
            try:
                with open(i) as f:
                    out.extend(f.readlines())
            except FileNotFoundError as fnfe:
                return {
                    "stdout": deque(),
                    "stderr": deque().append("No such file or directory"),
                    "exitcode": 1,
                }

        return {"stdout": out, "stderr": deque(), "exitcode": 0}

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

        # "`echo echo` foo"
        if isinstance(appName, Substitution):
            appName = "".join(appName.accept(self)).strip(" \n")

        stdin, redirectOut = None, None
        out = deque()
        glob_index = []
        globbed_result = []
        parsedArg = []

        factory = AppsFactory()

        for r in redirects:
            if isinstance(r, RedirectIn) and not stdin:  # check type
                try:
                    stdin = r.accept(self)
                except FileNotFoundError as fnfe:
                    details = fnfe.args[0]
                    print(details["stderr"].pop())
            elif isinstance(r, RedirectOut) and not redirectOut:
                redirectOut = r
            else:
                # not related to unsafe app
                raise Exception("invalid redirections")

        # otherwise, stdin will overwrite input from last call result piped in
        if input and not stdin:
            stdin = input

        # check if args includes double quote that needs to further eval
        # check glob in args
        # decode args
        for n, arg in enumerate(args):
            argOut = deque()
            hasGlobing = False
            for subArg in arg:
                # ['a','*.py'] c.py d.py a
                # ['*.py']
                # ac.py ad.py
                # appName 'a'*.py

                if (
                    isinstance(subArg, DoubleQuote)
                    or isinstance(subArg, Substitution)
                    or isinstance(subArg, SingleQuote)
                ):
                    executedProcess = subArg.accept(self)
                    if executedProcess["exitcode"]:
                        print(executedProcess["stderr"].pop())
                    else:
                        argOut.append("".join(executedProcess["stdout"]))
                elif isinstance(subArg, str) and "*" in subArg:
                    glob_index.append(n)
                    argOut.append(subArg)
                else:
                    argOut.append(subArg)

            parsedArg.append("".join(argOut))
            globbed_result.append(glob(parsedArg[-1]))

        app = factory.getApp(appName)

        if len(glob_index) > 0:
            # in case have multiple glob
            glob_pairs = product(globbed_result)

            count = 0
            for pair in glob_pairs:
                argsForThisPair = []
                for arg_index in range(len(parsedArg)):
                    if arg_index in glob_index:
                        argsForThisPair.append(pair[count])
                    else:
                        argsForThisPair.append(parsedArg[arg_index])

                if len(parsedArg) == 1:
                    argsForThisPair = argsForThisPair[0]

                out.extend(app.newExec(argsForThisPair, stdin=stdin))
        else:
            temp = app.newExec(parsedArg, stdin=stdin)
            out.extend(temp)

        # print("call: {}, out: {}", call, out)

        if redirectOut:
            redirectOut.accept(self, stdin=out)
            return {"stdout": deque(), "stderr": deque(), "exitcode": 0}
        else:
            return {"stdout": out, "stderr": deque(), "exitcode": 0}

    def visitSeq(self, seq):
        left = seq.left
        right = seq.right

        outLeft = left.accept(self)
        outRight = right.accept(self)

        outLeft.extend(outRight)
        return {"stdout": outLeft, "stderr": deque(), "exitcode": 0}

    def visitPipe(self, pipe):  # what if | has redirectOut before?
        left = pipe.left
        right = pipe.right

        outLeft = left.accept(self)
        outRight = right.accept(self, input=outLeft)

        return {"stdout": outRight, "stderr": deque(), "exitcode": 0}


if __name__ == "__main__":
    visitor = ASTVisitor()
    call = Call(
        redirects=[],
        appName=SingleQuote,
        args=[DoubleQuote(["a", " ", Substitution('echo "b"')], True)],
    )
    call.accept(visitor)
