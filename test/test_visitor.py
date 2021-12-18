import unittest

from visitor import ASTVisitor
from collections import deque
from abstract_syntax_tree import (
    DoubleQuote,
    Substitution,
    SingleQuote,
    RedirectIn,
    RedirectOut,
    Call,
    Seq,
    Pipe,
)
import os
import subprocess


class TestASTVisitor(unittest.TestCase):
    def setUp(self) -> None:
        self.visitor = ASTVisitor()
        with open("file1.txt", "w") as f1:
            f1.write("abc\nadc\nabc\ndef")
        with open("file2.txt", "w") as f2:
            f2.write("file2\ncontent")

    # for single quote
    def test_visit_singlequote_empty(self):
        i = SingleQuote("''")
        out = self.visitor.visitSingleQuote(i)
        self.assertEqual("".join(out["stdout"]), "")
        self.assertEqual("".join(out["stderr"]), "")
        self.assertEqual("".join(out["exit_code"]), 0)

    def test_visit_singlequote_space(self):
        i = SingleQuote("'  '")
        out = self.visitor.visitSingleQuote(i)
        self.assertEqual("".join(out["stdout"]), "  ")
        self.assertEqual("".join(out["stderr"]), "")
        self.assertEqual("".join(out["exit_code"]), 0)

    def test_visit_singlequote_disable_doublequote(self):
        i = SingleQuote("'\"\"'")
        out = self.visitor.visitSingleQuote(i)
        self.assertEqual("".join(out["stdout"]), '""')
        self.assertEqual("".join(out["stderr"]), "")
        self.assertEqual("".join(out["exit_code"]), 0)

    def test_visit_singlequote_backquote(self):
        i = SingleQuote("'`echo hello`'")
        out = self.visitor.visitSingleQuote(i)
        self.assertEqual("".join(out["stdout"]), "`echo hello`")
        self.assertEqual("".join(out["stderr"]), "")
        self.assertEqual("".join(out["exit_code"]), 0)

    def test_visit_singlequote_substitution_error(self):
        i = SingleQuote("'`echo hello`'")
        out = self.visitor.visitSingleQuote(i)
        self.assertEqual("".join(out["stdout"]), "")
        self.assertEqual(
            "".join(out["stderr"]), "wrong number of command line arguments"
        )
        self.assertEqual("".join(out["exit_code"]), 1)

    def test_visit_doublequote_no_substitution(self):
        i = DoubleQuote(["a", "b"])
        out = self.visitor.visitDoubleQuote(i)
        self.assertEqual("".join(out["stdout"]), "ab")
        self.assertEqual("".join(out["stderr"]), "")
        self.assertEqual("".join(out["exit_code"]), 0)

    def test_visit_doublequote_has_substitution(self):
        i = DoubleQuote(["a", "b", Substitution("echo c")])
        out = self.visitor.visitDoubleQuote(i)
        self.assertEqual("".join(out["stdout"]), "abc")
        self.assertEqual("".join(out["stderr"]), "")
        self.assertEqual("".join(out["exit_code"]), 0)

    # singlequote in doubleqoute?

    def test_visit_doublequote_error(self):
        i = DoubleQuote(["a", Substitution("ls a b"), "b"])
        out = self.visitor.visitDoubleQuote(i)
        self.assertEqual("".join(out["stdout"]), "")
        self.assertEqual(
            "".join(out["stderr"]), "wrong number of command line arguments"
        )
        self.assertEqual("".join(out["exit_code"]), 1)

    def test_visit_substitution(self):
        i = Substitution("echo foo")
        out = self.visitor.visitSub(i)
        self.assertEqual("".join(out["stdout"]), "foo")
        self.assertEqual("".join(out["stderr"]), "")
        self.assertEqual("".join(out["exit_code"]), 0)

    def test_visit_substitution_error(self):
        i = Substitution("ls a b")
        out = self.visitor.visitSub(i)
        self.assertEqual("".join(out["stdout"]), "")
        self.assertEqual("".join(out["stderr"]), "")
        self.assertEqual("".join(out["exit_code"]), 0)

    def test_visit_redirectin(self):
        i = RedirectIn("file1.txt")
        out = self.visitor.visitRedirectIn(i)
        self.assertEqual("".join(out["stdout"]), "abc\nadc\nabc\ndef")
        self.assertEqual("".join(out["stderr"]), "")
        self.assertEqual("".join(out["exit_code"]), 0)

    def test_visit_redirectin_glob(self):
        i = RedirectIn("*.txt")
        out = self.visitor.visitRedirectIn(i)
        self.assertEqual(
            "".join(out["stdout"]), ["abc\nadc\nabc\ndef", "file2\ncontent"]
        )
        self.assertEqual("".join(out["stderr"]), "")
        self.assertEqual("".join(out["exit_code"]), 0)

    def test_visit_redirectin_error(self):
        self.assertRaises(
            FileNotFoundError,
            self.visitor.visitRedirectIn,
            RedirectIn("file3.txt"),
        )

    def test_visit_redirectout(self):
        i = RedirectOut("testRedirectout.txt", stdin="aaa\nbbb\nccc")
        self.visitor.visitRedirectOut(i)
        with open("testRedirectout.txt") as f:
            lines = f.readlines()
        self.assertEqual("".join(lines), "aaa\nbbb\nccc")

    # what's the best result?
    def test_visit_redirectout_no_stdin(self):
        i = RedirectOut("testRedirectoutEmpty.txt")
        self.visitor.visitRedirectOut(i)
        with open("testRedirectoutEmpty.txt") as f:
            lines = f.readlines()
        self.assertEqual("".join(lines), "")

    def test_visit_redirectout_error(self):
        with self.assertRaises(Exception) as context:
            self.visitor.visitRedirectIn(RedirectIn("*.txt"))
        self.assertTrue("invalid redirection out" in context.exception)

    def test_visit_call_appname_substitution(self):
        i = Call(
            redirects=[],
            appName=Substitution("echo echo"),
            args=[["hello world"]],
        )
        out = self.visitor.visitCall(i)
        self.assertEqual("".join(out["stdout"]), "hello world")
        self.assertEqual("".join(out["stderr"]), "")
        self.assertEqual("".join(out["exit_code"]), 0)

    def test_visit_call_appname_substitution_error(self):
        i = Call(
            redirects=[],
            appName=Substitution("cat notExist.txt"),
            args=[["hello world"]],
        )
        with self.assertRaises(Exception) as context:
            self.visitor.visitCall(i)
        self.assertTrue(
            "Cannot substitute cat notExist.txt as app name" in context.exception
        )

    def test_visit_call_redirectin(self):
        i = Call(
            redirects=[RedirectIn("file1.txt")],
            appName="echo",
            args=[],
        )
        out = self.visitor.visitCall(i)
        self.assertEqual("".join(out["stdout"]), "abc\nadc\nabc\ndef")
        self.assertEqual("".join(out["stderr"]), "")
        self.assertEqual("".join(out["exit_code"]), 0)

    def test_visit_call_redirectout_return(self):
        i = Call(
            redirects=[RedirectOut("testRedirectoutReturn.txt")],
            appName="echo",
            args=[["call\nredirectout"]],
        )
        out = self.visitor.visitCall(i)
        self.assertEqual("".join(out["stdout"]), "")
        self.assertEqual("".join(out["stderr"]), "")

    def test_visit_call_redirection_invalid(self):
        i = Call(
            redirects=["not redirection type"],
            appName="echo",
            args=[["call\nredirectout"]],
        )
        with self.assertRaises(Exception) as context:
            self.visitor.visitCall(i)
        self.assertTrue("invalid redirections" in context.exception)

    def test_visit_call_no_redirectin_but_input(self):
        i = Call(
            redirects=[],
            appName="echo",
            args=[],
            input="input\ncontent",
        )
        out = self.visitor.visitCall(i)
        self.assertEqual("".join(out["stdout"]), "input\ncontent")
        self.assertEqual("".join(out["stderr"]), "")
        self.assertEqual("".join(out["exit_code"]), 0)

    def test_visit_call_redirectin_overwrite_input(self):
        with open("testRedirectinOverwriteInput.txt", "w") as f:
            f.write("redirectin\ncontent")
        i = Call(
            redirects=[RedirectIn("testRedirectinOverwriteInput.txt")],
            appName="echo",
            args=[],
            input="input\ncontent",
        )
        out = self.visitor.visitCall(i)
        self.assertEqual("".join(out["stdout"]), "redirectin\ncontent")
        self.assertEqual("".join(out["stderr"]), "")
        self.assertEqual("".join(out["exit_code"]), 0)

    def test_visit_call_args_doublequote(self):
        i = Call(
            redirects=[],
            appName="echo",
            args=[["aa", DoubleQuote("bb")]],
        )
        out = self.visitor.visitCall(i)
        self.assertEqual("".join(out["stdout"]), "aabb")
        self.assertEqual("".join(out["stderr"]), "")
        self.assertEqual("".join(out["exit_code"]), 0)

    def test_visit_call_args_singlequote(self):
        i = Call(
            redirects=[],
            appName="echo",
            args=[["aa"], [SingleQuote("bb")]],
        )
        out = self.visitor.visitCall(i)
        self.assertEqual("".join(out["stdout"]), "aa bb")
        self.assertEqual("".join(out["stderr"]), "")
        self.assertEqual("".join(out["exit_code"]), 0)

    def test_visit_call_args_substitution(self):
        i = Call(
            redirects=[],
            appName="echo",
            args=[[Substitution("echo arg_sub_content")]],
        )
        out = self.visitor.visitCall(i)
        self.assertEqual("".join(out["stdout"]), "echo arg_sub_content")
        self.assertEqual("".join(out["stderr"]), "")
        self.assertEqual("".join(out["exit_code"]), 0)

    def test_visit_call_args_exec_error(self):
        i = Call(
            redirects=[],
            appName="echo",
            args=[[Substitution("cat notExist.txt")]],
        )
        with self.assertRaises(Exception) as context:
            self.visitor.visitCall(i)
        self.assertTrue(
            "Cat: notExist.txt: No such file or directory" in context.exception
        )

    def test_visit_call_args_glob(self):
        i = Call(
            redirects=[],
            appName="cat",
            args=[["*.txt"]],
        )
        out = self.visitor.visitCall(i)
        output = subprocess.run(["cat", "*.txt"], capture_output=True, text=True).stdout
        self.assertEqual("".join(out["stdout"]), output)
        self.assertEqual("".join(out["stderr"]), "")
        self.assertEqual("".join(out["exit_code"]), 0)

    def test_visit_call_args_multiple_glob(self):
        i = Call(
            redirects=[],
            appName="cat",
            args=[["*.txt"], ["file?.txt"]],
        )
        out = self.visitor.visitCall(i)
        output = subprocess.run(
            ["cat", "*.txt", "file?.txt"], capture_output=True, text=True
        ).stdout
        self.assertEqual("".join(out["stdout"]), output)
        self.assertEqual("".join(out["stderr"]), "")
        self.assertEqual("".join(out["exit_code"]), 0)

    def test_visit_seq_left_error_unsafe(self):
        i = Seq(
            Call(
                redirects=[],
                appName="_ls",
                args=[["notExist"]],
            ),
            Call(
                redirects=[],
                appName="echo",
                args=[["right\noutput"]],
            ),
        )
        out = self.visitor.visitSeq(i)
        self.assertEqual("".join(out["stdout"]), "right\noutput")
        self.assertEqual("".join(out["stderr"]), "Ls: notExist: No such directory")
        self.assertEqual("".join(out["exit_code"]), 1)

    def test_visit_seq_right_error_unsafe(self):
        i = Seq(
            Call(
                redirects=[],
                appName="echo",
                args=[["left\noutput"]],
            ),
            Call(
                redirects=[],
                appName="_ls",
                args=[["notExist"]],
            ),
        )
        out = self.visitor.visitSeq(i)
        self.assertEqual("".join(out["stdout"]), "left\noutput")
        self.assertEqual("".join(out["stderr"]), "Ls: notExist: No such directory")
        self.assertEqual("".join(out["exit_code"]), 1)

    def test_visit_seq_left_error_right_error_unsafe(self):
        i = Seq(
            Call(
                redirects=[],
                appName="_ls",
                args=[["notExist1"]],
            ),
            Call(
                redirects=[],
                appName="_ls",
                args=[["notExist2"]],
            ),
        )
        out = self.visitor.visitSeq(i)
        self.assertEqual("".join(out["stdout"]), "")
        self.assertEqual(
            "".join(out["stderr"]),
            "Ls: notExist1: No such directoryLs: notExist2: No such directory",
        )
        self.assertEqual("".join(out["exit_code"]), 1)

    def test_visit_seq_no_error(self):
        i = Seq(
            Call(
                redirects=[],
                appName="echo",
                args=[["left\noutput"]],
            ),
            Call(
                redirects=[],
                appName="echo",
                args=[["right\noutput"]],
            ),
        )
        out = self.visitor.visitSeq(i)
        self.assertEqual("".join(out["stdout"]), "left\noutputright\noutput")
        self.assertEqual("".join(out["stderr"]), "")
        self.assertEqual("".join(out["exit_code"]), 0)

    def test_visit_pipe_with_outleft(self):
        i = Pipe(
            Call(
                redirects=[],
                appName="echo",
                args=[["left\noutput"]],
            ),
            Call(
                redirects=[],
                appName="echo",
                args=[],
            ),
        )
        out = self.visitor.visitPipe(i)
        self.assertEqual("".join(out["stdout"]), "left\noutput")
        self.assertEqual("".join(out["stderr"]), "")
        self.assertEqual("".join(out["exit_code"]), 0)

    def test_visit_pipe_outright_error_unsafe(self):
        i = Pipe(
            Call(
                redirects=[],
                appName="echo",
                args=[["notExist"]],
            ),
            Call(
                redirects=[],
                appName="_ls",
                args=[],
            ),
        )
        out = self.visitor.visitPipe(i)
        self.assertEqual("".join(out["stdout"]), "")
        self.assertEqual("".join(out["stderr"]), "notExist: No such directory")
        self.assertEqual("".join(out["exit_code"]), 1)

    def tearDown(self) -> None:
        os.remove("file1.txt")
        os.remove("file2.txt")
        os.remove("testRedirectout.txt")
        os.remove("testRedirectoutEmpty.txt")
        os, os.remove("testRedirectoutReturn.txt")
        os, os.remove("testRedirectinOverwriteInput.txt")


if __name__ == "__main__":
    unittest.main()
