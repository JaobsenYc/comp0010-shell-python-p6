from abc import ABC, abstractmethod
from abstract_syntax_tree import (
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


class ASTVisitor(Visitor):

    """
    :param singleQuote: this is a AST().SingleQuote object
    :returns: this is a dictionary of srdout, stderr and exit_code
    """

    def visitSingleQuote(self, singleQuote):
        quotedPart = singleQuote.quotedPart
        res_deque = deque()
        res_deque.append(quotedPart)

        return {"stdout": res_deque, "stderr": deque(), "exit_code": 0}

    """
    :param doubleQuote: this is a AST().DoubleQuote object
    :returns: this is a dictionary of srdout, stderr and exit_code
    """

    def visitDoubleQuote(self, doubleQuote):
        containSubstitution, quotedPart = (
            doubleQuote.containSubstitution,
            doubleQuote.quotedPart,
        )

        res = deque()
        err = deque()

        if not containSubstitution:
            res.append("".join(quotedPart))
        else:
            for part in quotedPart:
                if not isinstance(part, Substitution):
                    res.append(part)
                else:
                    executed = part.accept(self)
                    out = executed["stdout"]
                    err.extend(executed["stderr"])
                    res.extend("".join(out))

        return {
            "stdout": res,
            "stderr": err,
            "exit_code": len(err),
        }

    """
    :param sub: this is a AST().Substitution object
    :returns: this is a dictionary of srdout, stderr and exit_code
    """

    def visitSub(self, sub):
        ast = command.parse(sub.quoted)
        executed = ast.accept(self)

        out = executed["stdout"]
        out_new = deque("".join(out).strip("\n ").replace("\n", " "))

        return {
            "stdout": out_new,
            "stderr": executed["stderr"],
            "exit_code": executed["exit_code"],
        }

    """
    :param redirectIn: this is a AST().RedirectIn object
    :returns: this is a dictionary of srdout, stderr and exit_code
    """

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

    """
    :param redirectOut: this is a AST().RedirectOut object
    :keyword stdin: this is optional, default as None; output file name
    :returns: this is a dictionary of srdout, stderr and exit_code
    """

    def visitRedirectOut(self, redirectOut, stdin=None):
        fs = glob(redirectOut.arg) or [redirectOut.arg]
        n = len(fs)

        if n > 1:
            raise Exception("invalid redirection out")

        stdout_f = fs[0]
        with open(stdout_f, "w") as f:
            while len(stdin) > 0:
                line = stdin.popleft()
                f.write(line)

    """
    :param call: this is a AST().Call object
    :keyword input: this is optional, default as None; io redirection and pipe content
    :returns: this is a dictionary of srdout, stderr and exit_code
    """

    def visitCall(self, call, input=None):
        redirects = call.redirects
        appName = call.appName
        args = call.args

        # "`echo echo` foo"
        if isinstance(appName, Substitution):
            subExecuted = appName.accept(self)
            if subExecuted["exit_code"] != 0:
                raise Exception(f"Cannot substitute {appName} as app name")
            appName = "".join(subExecuted["stdout"]).strip(" \n")

        stdin, redirectOut = None, None
        out = deque()
        err = deque()
        glob_index = []
        globbed_result = []
        parsedArg = []

        factory = AppsFactory()

        for r in redirects:
            if isinstance(r, RedirectIn) and not stdin:
                stdin = r.accept(self)["stdout"]
            elif isinstance(r, RedirectOut) and not redirectOut:
                redirectOut = r
            else:
                # not related to unsafe app, the error of system
                raise Exception("invalid redirections")

        # otherwise, stdin will overwrite input from last call result piped in
        if input and not stdin:
            stdin = input

        # check if args includes double quote that needs to further eval
        # check glob in args and decode args
        # args: [[],[]]
        for n, arg in enumerate(args):
            argOut = deque()

            # arg: []
            for subArg in arg:

                if (
                    isinstance(subArg, DoubleQuote)
                    or isinstance(subArg, Substitution)
                    or isinstance(subArg, SingleQuote)
                ):
                    executedProcess = subArg.accept(self)

                    if executedProcess["exit_code"]:
                        raise Exception(executedProcess["stderr"])
                    else:
                        argOut.append("".join(executedProcess["stdout"]))

                # ['a','*.py']
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

            # in case have multiple glob
            if len(glob_index) > 1:
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

                executed = app.exec(argsForThisPair, stdin=stdin)
                out.extend(executed["stdout"])
                err.extend(executed["stderr"])
        else:
            executed = app.exec(parsedArg, stdin=stdin)
            out.extend(executed["stdout"])
            err.extend(executed["stderr"])

        if redirectOut:
            redirectOut.accept(self, stdin=out)
            return {"stdout": deque(), "stderr": err, "exit_code": len(err)}
        else:
            return {"stdout": out, "stderr": err, "exit_code": len(err)}

    """
    :param seq: this is a AST().Seq object
    :returns: this is a dictionary of srdout, stderr and exit_code
    """

    def visitSeq(self, seq):
        left = seq.left
        right = seq.right

        outLeft = left.accept(self)
        outRight = right.accept(self)

        outLeft["stdout"].extend(outRight["stdout"])
        outLeft["stderr"].extend(outRight["stderr"])

        return {
            "stdout": outLeft["stdout"],
            "stderr": outLeft["stderr"],
            "exit_code": outLeft["exit_code"] or outRight["exit_code"],
        }

    """
    :param pipe: this is a AST().Pipe object
    :returns: this is a dictionary of srdout, stderr and exit_code
    """

    def visitPipe(self, pipe):
        left = pipe.left
        right = pipe.right

        outLeft = left.accept(self)
        outRight = right.accept(self, input=outLeft["stdout"])
        outLeft["stderr"].extend(outRight["stderr"])

        return {
            "stdout": outRight["stdout"],
            "stderr": outLeft["stderr"],
            "exit_code": outLeft["exit_code"] or outRight["exit_code"],
        }
