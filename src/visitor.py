"""
    this is a visitor module
    to specify AST visitor funcs for all AST types
"""

from abc import ABC, abstractmethod
from collections import deque
from glob import glob
from itertools import product
from abstract_syntax_tree import (
    Call,
    DoubleQuote,
    RedirectIn,
    RedirectOut,
    SingleQuote,
    Substitution,
)
from appsFactory import AppsFactory
from parsercombinator import command


class Visitor(ABC):
    """
    this is a visitor abstract class
    """

    @abstractmethod
    def visit_single_quote(self, single_quote):
        """visit singlequote"""

    @abstractmethod
    def visit_double_quote(self, double_quote):
        """visit doublequote"""

    @abstractmethod
    def visit_sub(self, sub):
        """visit substitution"""

    @abstractmethod
    def visit_redirect_in(self, redirect_in):
        """visit redirectin"""

    @abstractmethod
    def visit_redirect_out(self, redirect_out, stdin=None):
        """visit redirectout"""

    @abstractmethod
    def visit_call(self, call, in_put=None):
        """visit call"""

    @abstractmethod
    def visit_seq(self, seq):
        """visit sequence"""

    @abstractmethod
    def visit_pipe(self, pipe):
        """visit pipe"""


class ASTVisitor(Visitor):

    """
    :param singleQuote: this is a AST().SingleQuote object
    :returns: this is a dictionary of srdout, stderr and exit_code
    """

    def visit_single_quote(self, single_quote):
        assert isinstance(single_quote, SingleQuote)

        quoted_part = single_quote.quotedPart
        res_deque = deque()
        res_deque.append(quoted_part)

        return {"stdout": res_deque, "stderr": deque(), "exit_code": 0}

    """
    :param doubleQuote: this is a AST().DoubleQuote object
    :returns: this is a dictionary of srdout, stderr and exit_code
    """

    def visit_double_quote(self, double_quote):
        assert isinstance(double_quote, DoubleQuote)

        contain_substitution, quoted_part = (
            double_quote.containSubstitution,
            double_quote.quotedPart,
        )
        assert isinstance(contain_substitution, bool)
        assert isinstance(quoted_part, list)

        res = deque()
        err = deque()

        if not contain_substitution:
            res.append("".join(quoted_part))
        else:
            for part in quoted_part:
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

    def visit_sub(self, sub):
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

    def visit_redirect_in(self, redirectIn):
        assert isinstance(redirectIn, RedirectIn)

        out = deque()

        fs = glob(redirectIn.arg)
        assert isinstance(fs, list)

        if len(fs) < 1:
            raise FileNotFoundError
        assert len(fs) >= 1

        for i in fs:
            with open(i, "r") as f:
                out.extend(f.readlines())

        return {"stdout": out, "stderr": deque(), "exit_code": 0}

    """
    :param redirectOut: this is a AST().RedirectOut object
    :keyword stdin: this is optional, default as None; output file name
    :returns: this is a dictionary of srdout, stderr and exit_code
    """

    def visit_redirect_out(self, redirect_out, stdin=None):

        fs = glob(redirect_out.arg) or [redirect_out.arg]
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

    def visit_call(self, call, in_put=None):
        assert isinstance(call, Call)

        redirects = call.redirects
        app_name = call.appName
        args = call.args

        factory = AppsFactory()
        out = deque()
        err = deque()

        # "`echo echo` foo"
        app_name = self._getAppName(app_name)
        assert app_name is not None
        app = factory.getApp(app_name)

        try:
            stdin, redirect_out = self._getRedirects(redirects)
        except Exception as e:
            raise e

        # otherwise, stdin will overwrite input from last call result piped in
        if not stdin:
            stdin = in_put or deque()
        assert stdin is not None

        parsed_arg, glob_index, globbed_result = self._getArgs(args)

        if len(glob_index) > 0:
            final_args_lst = self._getGlobbedArg(parsed_arg, glob_index, globbed_result)
        else:
            final_args_lst = [parsed_arg]

        for final_args in final_args_lst:
            executed = app.exec(final_args, stdin=stdin)
            out.extend(executed["stdout"])
            err.extend(executed["stderr"])
        assert isinstance(out, deque)
        assert isinstance(err, deque)

        if redirect_out:
            redirect_out.accept(self, stdin=out)
            return {"stdout": deque(), "stderr": err, "exit_code": len(err)}
        else:
            return {"stdout": out, "stderr": err, "exit_code": len(err)}

    """
    :param seq: this is a AST().Seq object
    :returns: this is a dictionary of srdout, stderr and exit_code
    """

    def visit_seq(self, seq):
        left = seq.left
        right = seq.right

        out_left = left.accept(self)
        out_right = right.accept(self)

        out_left["stdout"].extend(out_right["stdout"])
        out_left["stderr"].extend(out_right["stderr"])

        assert isinstance(out_left["stdout"], deque)
        assert isinstance(out_left["stderr"], deque)

        return {
            "stdout": out_left["stdout"],
            "stderr": out_left["stderr"],
            "exit_code": out_left["exit_code"] or out_right["exit_code"],
        }

    """
    :param pipe: this is a AST().Pipe object
    :returns: this is a dictionary of srdout, stderr and exit_code
    """

    def visit_pipe(self, pipe):
        left = pipe.left
        right = pipe.right

        out_left = left.accept(self)
        out_right = right.accept(self, input=out_left["stdout"])
        out_left["stderr"].extend(out_right["stderr"])

        assert isinstance(out_left["stdout"], deque)
        assert isinstance(out_left["stderr"], deque)

        return {
            "stdout": out_right["stdout"],
            "stderr": out_left["stderr"],
            "exit_code": out_left["exit_code"] or out_right["exit_code"],
        }

    # check if args includes double quote that needs to further eval
    # check glob in args and decode args
    # args: [[],[]]
    def _getArgs(self, args):

        globbed_result = []
        parsed_arg = []
        glob_index = []

        for n, arg in enumerate(args):

            # arg: []
            arg_out = deque()
            for sub_arg in arg:
                arg_out_new, glob_index = self._getSubArg(sub_arg, glob_index, n)
                arg_out.extend(arg_out_new)

            parsed_arg.append("".join(arg_out))
            if n in glob_index:
                globbed_result.append(glob(parsed_arg[-1]))

        return (parsed_arg, glob_index, globbed_result)

    def _getSubArg(self, sub_arg, glob_index, n):
        arg_out = deque()

        if isinstance(sub_arg, (DoubleQuote, SingleQuote, Substitution)):
            executed_process = sub_arg.accept(self)

            if executed_process["exit_code"]:
                raise Exception(executed_process["stderr"])
            arg_out.append("".join(executed_process["stdout"]))

        # ['a','*.py']
        elif isinstance(sub_arg, str) and "*" in sub_arg:
            glob_index.append(n)
            arg_out.append(sub_arg)

        else:
            arg_out.append(sub_arg)

        return (arg_out, glob_index)

    def _getAppName(self, app_name):

        if isinstance(app_name, Substitution):
            sub_executed = app_name.accept(self)
            if sub_executed["exit_code"] != 0:
                raise Exception(f"Cannot substitute {app_name} as app name")

            assert len(sub_executed["stderr"]) == 0
            app_name = "".join(sub_executed["stdout"]).strip(" \n")

        return app_name

    def _getRedirects(self, redirects):

        stdin, redirect_out = None, None

        for r in redirects:
            if isinstance(r, RedirectIn) and not stdin:
                stdin = r.accept(self)["stdout"]
            elif isinstance(r, RedirectOut) and not redirect_out:
                redirect_out = r
            else:
                # not related to unsafe app, the error of system
                raise Exception("invalid redirections")

        return (stdin, redirect_out)

    def _getGlobbedArg(self, parsedArg, glob_index, globbed_result):

        args_lst = []
        glob_pairs = product(*globbed_result)

        for pair in glob_pairs:
            args_for_this_pair = []
            count = 0

            for arg_index in range(len(parsedArg)):

                if arg_index in glob_index:
                    args_for_this_pair.append(pair[count])
                    count += 1
                else:
                    args_for_this_pair.append(parsedArg[arg_index])

            args_lst.append(args_for_this_pair)

        return args_lst
