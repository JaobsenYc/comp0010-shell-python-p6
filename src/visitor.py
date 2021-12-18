from abc import ABC, abstractmethod, abstractproperty
from src.abstract_syntax_tree import (
    DoubleQuote,
    RedirectIn,
    RedirectOut,
    SingleQuote,
    Substitution,
    Call,
)
from src.parsercombinator import command
from glob import glob
from src.appsFactory import AppsFactory
from collections import deque
from itertools import product


class Visitor(ABC):
    @abstractproperty
    def visitSingleQuote(self, singleQuote):
        """visit singlequote"""

    @abstractproperty
    def visitDoubleQuote(self, doubleQuote):
        """visit doublequote"""

    @abstractproperty
    def visitSub(self, sub):
        """visit substitution"""

    @abstractproperty
    def visitRedirectIn(self, redirectIn):
        """visit redirectin"""

    @abstractproperty
    def visitRedirectOut(self, redirectOut):
        """visit redirectout"""

    @abstractproperty
    def visitCall(self, call, input=None):
        """visit call"""

    @abstractproperty
    def visitSeq(self, seq):
        """visit sequence"""

    @abstractproperty
    def visitPipe(self, pipe):
        """visit pipe"""


class ASTVisitor(Visitor):

    """
    :param singleQuote: this is a AST().SingleQuote object
    :returns: this is a dictionary of srdout, stderr and exit_code
    """

    def visitSingleQuote(self, singleQuote):
        assert isinstance(singleQuote, SingleQuote)

        quotedPart = singleQuote.quotedPart
        res_deque = deque()
        res_deque.append(quotedPart)

        return {"stdout": res_deque, "stderr": deque(), "exit_code": 0}

    """
    :param doubleQuote: this is a AST().DoubleQuote object
    :returns: this is a dictionary of srdout, stderr and exit_code
    """

    def visitDoubleQuote(self, doubleQuote):
        assert isinstance(doubleQuote, DoubleQuote)

        containSubstitution, quotedPart = (
            doubleQuote.containSubstitution,
            doubleQuote.quotedPart,
        )
        assert isinstance(containSubstitution, bool)
        assert isinstance(quotedPart, list)

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
                    assert isinstance(out, deque)
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
        assert isinstance(out, deque)
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
        assert isinstance(redirectIn, RedirectIn)

        out = deque()

        fs = glob(redirectIn.arg)
        assert isinstance(fs, list)

        if len(fs) < 1:
            raise FileNotFoundError
        assert len(fs) >= 1

        for i in fs:
            with open(i) as f:
                out.extend(f.readlines())

        return {"stdout": out, "stderr": deque(), "exit_code": 0}

    """
    :param redirectOut: this is a AST().RedirectOut object
    :keyword stdin: this is optional, default as None; output file name
    :returns: this is a dictionary of srdout, stderr and exit_code
    """

    def visitRedirectOut(self, redirectOut, stdin=None):
        assert stdin

        fs = glob(redirectOut.arg) or [redirectOut.arg]
        n = len(fs)
        assert isinstance(fs, list)

        if n > 1:
            raise Exception("invalid redirection out")
        assert n <= 1

        stdout_f = fs[0]
        with open(stdout_f, "w") as f:
            while len(stdin) > 0:
                line = stdin.popleft()
                f.write(line)

    """
    :param call: this is a AST().Call object
    :keyword input: this is optional, default as None;
                    io redirection and pipe content
    :returns: this is a dictionary of srdout, stderr and exit_code
    """

    def visitCall(self, call, input=None):
        redirects = call.redirects
        appName = call.appName
        args = call.args

        factory = AppsFactory()
        out = deque()
        err = deque()

        # "`echo echo` foo"
        appName = self._getAppName(appName)
        app = factory.getApp(appName)

        try:
            stdin, redirectOut = self._getRedirects(redirects)
        except Exception as e:
            raise e

        # otherwise, stdin will overwrite input from last call result piped in
        if input and not stdin:
            stdin = input

        parsedArg, glob_index, globbed_result = self._getArgs(args)

        if len(glob_index) > 0:
            final_args_lst = self._getGlobbedArg(parsedArg, glob_index, globbed_result)
        else:
            final_args_lst = [parsedArg]

        for final_args in final_args_lst:
            executed = app.exec(final_args, stdin=stdin)
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

    # check if args includes double quote that needs to further eval
    # check glob in args and decode args
    # args: [[],[]]
    def _getArgs(self, args):

        glob_index = []
        globbed_result = []
        parsedArg = []

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

        return (parsedArg, glob_index, globbed_result)

    def _getAppName(self, appName):

        if isinstance(appName, Substitution):
            subExecuted = appName.accept(self)
            if subExecuted["exit_code"] != 0:
                raise Exception(f"Cannot substitute {appName} as app name")

            appName = "".join(subExecuted["stdout"]).strip(" \n")

        return appName

    def _getRedirects(self, redirects):

        stdin, redirectOut = None, None

        for r in redirects:
            if isinstance(r, RedirectIn) and not stdin:
                stdin = r.accept(self)["stdout"]
            elif isinstance(r, RedirectOut) and not redirectOut:
                redirectOut = r
            else:
                # not related to unsafe app, the error of system
                raise Exception("invalid redirections")

        return (stdin, redirectOut)

    def _getGlobbedArg(self, parsedArg, glob_index, globbed_result):

        args_lst = []
        glob_pairs = product(*globbed_result)

        for pair in glob_pairs:
            argsForThisPair = []
            count = 0

            for arg_index in range(len(parsedArg)):

                if arg_index in glob_index:
                    argsForThisPair.append(pair[count])
                    count += 1
                else:
                    argsForThisPair.append(parsedArg[arg_index])

            args_lst.append(argsForThisPair)

        return args_lst


if __name__ == "__main__":
    i = Call(
        redirects=[],
        appName=Substitution("echo echo"),
        args=[["hello world"]],
    )
    out = ASTVisitor().visitCall(i)
    assert "".join(out["stdout"]).strip("\n") == "hello world"
