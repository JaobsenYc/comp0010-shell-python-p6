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


# @singleton
class ASTVisitor(Visitor):
    def visitSingleQuote(self, singleQuote):
        quotedPart = singleQuote.quotedPart
        res_deque = deque()
        res_deque.append(quotedPart)
        return {"stdout": res_deque, "stderr": deque(), "exit_code": 0}

    def visitDoubleQuote(self, doubleQuote):
        containSubstitution, quotedPart = (
            doubleQuote.containSubstitution,
            doubleQuote.quotedPart,
        )

        res = ""
        err = None

        if not containSubstitution:
            res = "{}".format("".join(quotedPart))
        else:
            for part in quotedPart:
                if not isinstance(part, Substitution):
                    res += part
                else:
                    executed = part.accept(self)
                    out = executed["stdout"]
                    err = executed["stderr"]
                    res = "".join(out)

        res_deque = deque()
        res_deque.append(res)
        return {
            "stdout": res_deque,
            "stderr": deque() if not err else err,
            "exit_code": 0 if not err else 1,
        }

    # def visitSingleQuote(self, singleQuote):
    #     res = deque()
    #     res.append(singleQuote.quotedPart)
    #     return {"stdout": res, "stderr": deque(), "exit_code": 0}

    def visitSub(self, sub):
        ast = command.parse(sub.quoted)
        executed = ast.accept(self)
        # if not out["exit_code"]:
        out = executed["stdout"]
        out_new = deque("".join(out["stdout"]).strip("\n ").replace("\n", " "))
        return {
            "stdout": out_new,
            "stderr": executed["stderr"],
            "exit_code": executed["exit_code"],
        }
        # else:
        #     return out

    def visitRedirectIn(self, redirectIn):
        out = deque()

        fs = glob(redirectIn.arg)

        for i in fs:
            try:
                with open(i) as f:
                    out.extend(f.readlines())
            except FileNotFoundError as fnfe:
                raise fnfe

        return {"stdout": out, "stderr": deque(), "exit_code": 0}

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
        err = deque()
        glob_index = []
        globbed_result = []
        parsedArg = []

        factory = AppsFactory()

        for r in redirects:
            if isinstance(r, RedirectIn) and not stdin:  # check type
                stdin = r.accept(self)["stdout"]
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
                    if executedProcess["exit_code"]:
                        # print(executedProcess["stderr"].pop())
                        raise Exception(executedProcess["stderr"])
                    else:
                        argOut.append("".join(executedProcess["stdout"]))
                elif isinstance(subArg, str) and "*" in subArg:
                    glob_index.append(n)
                    argOut.append(subArg)
                else:
                    argOut.append(subArg)

            parsedArg.append("".join(argOut))
            if n in glob_index:
                globbed_result.append(glob(parsedArg[-1]))

        app = factory.getApp(appName)

        if len(glob_index) > 0:
            if len(glob_index) > 1:
                # in case have multiple glob
                glob_pairs = product(globbed_result)
            else:
                glob_pairs = globbed_result[0]

            for pair in glob_pairs:
                argsForThisPair = []
                count = 0
                for arg_index in range(len(parsedArg)):
                    if arg_index in glob_index:
                        if len(glob_index) == 1:
                            argsForThisPair.append(pair)
                        else:
                            argsForThisPair.append(pair[count])
                    else:
                        argsForThisPair.append(parsedArg[arg_index])
                    count += 1

                # if len(glob_index) == 1:
                #     argsForThisPair = argsForThisPair[0]
                executed = app.exec(argsForThisPair, stdin=stdin)
                out.extend(executed["stdout"])
                err.extend(executed["stderr"])
        else:
            executed = app.exec(parsedArg, stdin=stdin)
            out.extend(executed["stdout"])
            err.extend(executed["stderr"])

        # print("call: {}, out: {}", call, out)

        if redirectOut:
            redirectOut.accept(self, stdin=out)
            return {"stdout": deque(), "stderr": err, "exit_code": len(err)}
        else:
            return {"stdout": out, "stderr": err, "exit_code": len(err)}

    def visitSeq(self, seq):
        left = seq.left
        right = seq.right

        outLeft = left.accept(self)
        outRight = right.accept(self)

        return {
            "stdout": outLeft["stdout"].extend(outRight["stdout"]),
            "stderr": outLeft["stderr"].extend(outRight["stderr"]),
            "exit_code": outLeft["exit_code"] or outRight["exit_code"],
        }

    def visitPipe(self, pipe):  # what if | has redirectOut before?
        left = pipe.left
        right = pipe.right

        outLeft = left.accept(self)
        outRight = right.accept(self, input=outLeft["stdout"])

        return {
            "stdout": outRight["stdout"],
            "stderr": outLeft["stderr"].extend(outRight["stderr"]),
            "exit_code": outLeft["exit_code"] or outRight["exit_code"],
        }


if __name__ == "__main__":
    visitor = ASTVisitor()
    call = Call(
        redirects=[],
        appName=SingleQuote,
        args=[DoubleQuote(["a", " ", Substitution('echo "b"')], True)],
    )
    call.accept(visitor)
